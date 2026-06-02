"""PR A2: OppoSvm3PlaybackMonitor (verbose-mode-3 playback confirmation).

Hermetic: a deterministic fake socket feeds scripted push lines and a scripted
clock drives the timeout branches, so there is no real device, no real socket,
and no real time. These pin that:

* playback is confirmed only from OPPO push events -- @UPL PLAY sets
  confirmed_playback and an *advancing* @UTC sets confirmed_progress;
* production logging records state changes + periodic summaries but not per-second
  @UTC spam, while full_event_log records every raw line;
* the previous verbose mode is queried (#QVM) and restored (#SVM <prev>), even
  after the socket is gone;
* startup-timeout / session-timeout / connection-closed / stop_event all end the
  loop with an honest stop_reason.
"""

import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from resources.lib.oppo import playback_monitor_svm3 as svm3

TIMEOUT = object()
OSERR = object()


def _line(text):
    return (text + "\r").encode("ascii")


class FakeSocket:
    """recv() pops one scripted item per call: bytes, TIMEOUT, OSERR, or b'' (closed)."""

    def __init__(self, items=None):
        self._items = list(items or [])
        self.sent = []
        self.timeout_value = None
        self.close_calls = 0
        self.close_raises = False

    def settimeout(self, value):
        self.timeout_value = value

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, _bufsize):
        if not self._items:
            raise socket.timeout()
        item = self._items.pop(0)
        if item is TIMEOUT:
            raise socket.timeout()
        if item is OSERR:
            raise OSError("recv boom")
        return item

    def close(self):
        self.close_calls += 1
        if self.close_raises:
            raise OSError("close boom")

    def sent_text(self):
        return [d.decode("ascii").strip() for d in self.sent]


class StepClock:
    """Monotonic stub that advances by a fixed step on each call."""

    def __init__(self, step, start=0.0):
        self.t = start
        self.step = step

    def __call__(self):
        value = self.t
        self.t += self.step
        return value


def _monitor(items, **kwargs):
    sock = FakeSocket(items)
    kwargs.setdefault("monotonic", lambda: 0.0)
    mon = svm3.OppoSvm3PlaybackMonitor("10.0.0.5", 23, sock_factory=lambda: sock, **kwargs)
    mon.connect()
    return mon, sock


# -- parsing helpers --------------------------------------------------------


def test_parse_verbose_mode_accepts_documented_shapes():
    assert svm3._parse_verbose_mode("@QVM OK 2") == "2"
    assert svm3._parse_verbose_mode("QVM OK 3") == "3"
    assert svm3._parse_verbose_mode("OK 0") == "0"
    assert svm3._parse_verbose_mode("garbage") is None
    assert svm3._parse_verbose_mode("") is None
    assert svm3._parse_verbose_mode(None) is None


# -- connection -------------------------------------------------------------


def test_connect_with_factory_sets_recv_timeout():
    mon, sock = _monitor([], recv_timeout=4.0)
    assert sock.timeout_value == 4.0


def test_connect_default_path_uses_create_connection(monkeypatch):
    fake = FakeSocket([])
    monkeypatch.setattr(svm3.socket, "create_connection", lambda addr, timeout: fake)
    mon = svm3.OppoSvm3PlaybackMonitor("1.2.3.4", 23)
    mon.connect()
    assert mon._sock is fake
    assert fake.timeout_value == svm3.DEFAULT_RECV_TIMEOUT


def test_connect_failure_propagates():
    def boom():
        raise OSError("no route")

    mon = svm3.OppoSvm3PlaybackMonitor("1.2.3.4", 23, sock_factory=boom)
    try:
        mon.connect()
    except OSError:
        pass
    else:  # pragma: no cover - failure path must raise
        raise AssertionError("connect should propagate OSError")


# -- QVM / SVM3 / restore ---------------------------------------------------


def test_query_previous_verbose_mode_stores_and_returns():
    mon, sock = _monitor([_line("@QVM OK 2")])
    assert mon.query_previous_verbose_mode() == "2"
    assert mon.previous_verbose_mode == "2"
    assert sock.sent_text() == ["#QVM"]


def test_query_previous_verbose_mode_unparseable_is_none():
    mon, _sock = _monitor([_line("@QVM ERR")])
    assert mon.query_previous_verbose_mode() is None


def test_enable_sends_svm3_and_records_ack():
    mon, sock = _monitor([_line("@SVM OK 3")])
    assert mon.enable() is True
    assert "#SVM 3" in sock.sent_text()
    assert mon.snapshot()["event_count"] == 1


def test_enable_without_ack_records_nothing():
    mon, _sock = _monitor([TIMEOUT])
    assert mon.enable() is True
    assert mon.snapshot()["event_count"] == 0


def test_restore_sends_previous_mode():
    mon, sock = _monitor([_line("@QVM OK 2")])
    mon.query_previous_verbose_mode()
    assert mon.restore() is True
    assert sock.sent_text()[-1] == "#SVM 2"


def test_restore_noop_when_no_previous_mode():
    mon, _sock = _monitor([])
    assert mon.restore() is False


def test_restore_disabled_returns_false():
    mon, _sock = _monitor([_line("@QVM OK 3")], restore_previous_mode=False)
    mon.query_previous_verbose_mode()
    assert mon.restore() is False


def test_restore_after_close_is_safe():
    mon, _sock = _monitor([_line("@QVM OK 2")])
    mon.query_previous_verbose_mode()
    mon.close()
    assert mon.restore() is False  # _send raises OSError -> swallowed


# -- close ------------------------------------------------------------------


def test_close_is_idempotent_and_swallows_errors():
    mon, sock = _monitor([])
    sock.close_raises = True
    mon.close()
    mon.close()  # already None -> no-op
    assert sock.close_calls == 1


# -- @UPL / @UTC parsing ----------------------------------------------------


def test_upl_play_confirms_playback_and_utc_advance_confirms_progress():
    items = [
        _line("@UPL PLAY"),
        _line("@UTC 001 001 C 00:00:01"),
        _line("@UTC 001 001 C 00:00:02"),
        _line("@UPL STOP"),
    ]
    mon, _sock = _monitor(items)
    snap = mon.listen_until_done()
    assert snap["confirmed_playback"] is True
    assert snap["confirmed_progress"] is True
    assert snap["confirmed"] is True
    assert snap["utc_tick_count"] == 2
    assert snap["oppo_playback_state"] == "STOP"
    assert snap["stop_reason"] == "oppo_stop"
    assert snap["previous_verbose_mode"] is None


def test_single_utc_is_a_baseline_not_progress():
    mon, _sock = _monitor([_line("@UPL PLAY"), _line("UTC 001 001 C 00:00:05"), _line("@UPL STOP")])
    snap = mon.listen_until_done()
    assert snap["utc_tick_count"] == 1
    assert snap["confirmed_progress"] is False
    assert snap["first_utc"] == "001 001 C 00:00:05"


def test_repeated_same_utc_does_not_advance():
    items = [_line("@UTC 5"), _line("@UTC 5"), _line("@UTC 5"), _line("@UPL STOP")]
    mon, _sock = _monitor(items)
    snap = mon.listen_until_done()
    assert snap["utc_tick_count"] == 1
    assert snap["confirmed_progress"] is False


def test_blank_utc_payload_is_ignored():
    mon, _sock = _monitor([_line("@UTC"), _line("@UPL STOP")])
    snap = mon.listen_until_done()
    assert snap["utc_tick_count"] == 0
    assert snap["first_utc"] is None


def test_require_progress_false_confirms_on_play_alone():
    mon, _sock = _monitor([_line("@UPL PLAY"), _line("@UPL STOP")], require_progress=False)
    snap = mon.listen_until_done()
    assert snap["confirmed_playback"] is True
    assert snap["confirmed_progress"] is False
    assert snap["confirmed"] is True


def test_loading_is_keepalive_but_does_not_confirm_playback():
    # L1: LOADING is the disc mounting -- keep-alive (non-terminal) but NOT confirmed playback.
    assert svm3._upl_state_label("LOADING") == "LOADING"
    mon, _sock = _monitor([])
    assert mon._handle_upl("LOADING") is False  # non-terminal
    assert mon.playback_state == "LOADING"
    assert mon.confirmed_playback is False


def test_pause_and_menu_are_not_terminal():
    items = [_line("@UPL PAUSE"), _line("@UPL MENU"), _line("@UPL DISC"), _line("@UPL STOP")]
    mon, _sock = _monitor(items)
    snap = mon.listen_until_done()
    # The session ran through pause/menu to the final stop (state == STOP).
    assert snap["oppo_playback_state"] == "STOP"


def test_home_and_mctr_and_no_disc_are_terminal():
    for value, expected in (("HOME", "HOME"), ("MCTR", "MCTR"), ("NO DISC", "STOP")):
        mon, _sock = _monitor([_line(f"@UPL {value}")])
        snap = mon.listen_until_done()
        assert snap["oppo_playback_state"] == expected
        assert snap["stop_reason"] == f"oppo_{expected.lower()}"


def test_unknown_upl_value_and_blank_and_context_lines_are_handled():
    items = [
        _line("@UPL WAT"),  # unknown -> state unknown, non-terminal
        _line("@"),  # bare prefix -> no parts
        _line("@UVO 3840x2160"),  # context event, ignored
        _line("@UPL STOP"),
    ]
    mon, _sock = _monitor(items)
    snap = mon.listen_until_done()
    assert snap["stop_reason"] == "oppo_stop"
    assert snap["event_count"] == 4


def test_multiple_lines_in_one_chunk_are_split():
    # A single recv chunk carrying two CR-terminated lines must yield two events.
    chunk = _line("@UPL PLAY") + _line("@UPL STOP")
    mon, _sock = _monitor([chunk])
    snap = mon.listen_until_done()
    assert snap["confirmed_playback"] is True
    assert snap["oppo_playback_state"] == "STOP"


# -- logging policy ---------------------------------------------------------


def test_production_logging_suppresses_per_second_utc_spam():
    logs = []
    items = [_line(f"@UTC 001 001 C 00:00:{n:02d}") for n in range(1, 9)] + [_line("@UPL STOP")]
    mon, _sock = _monitor(items, logger=logs.append, full_event_log=False, summary_interval=1e9)
    mon.listen_until_done()
    # No raw-per-UTC logging; only the single UPL state change (unknown -> STOP).
    assert not any("raw:" in m for m in logs)
    assert sum("state:" in m for m in logs) == 1


def test_full_event_log_records_every_raw_line():
    logs = []
    items = [_line("@UTC 1"), _line("@UTC 2"), _line("@UPL STOP")]
    mon, _sock = _monitor(items, logger=logs.append, full_event_log=True, summary_interval=1e9)
    mon.listen_until_done()
    assert sum("raw:" in m for m in logs) == 3


def test_periodic_summary_is_emitted():
    logs = []
    items = [_line("@UPL PLAY"), _line("@UTC 1"), _line("@UTC 2"), _line("@UPL STOP")]
    mon, _sock = _monitor(items, logger=logs.append, summary_interval=1.0, monotonic=StepClock(5.0))
    mon.listen_until_done()
    assert any("summary:" in m for m in logs)


# -- ring buffer ------------------------------------------------------------


def test_ring_buffer_caps_recent_events():
    items = [_line("@UTC 1"), _line("@UTC 2"), _line("@UTC 3"), _line("@UPL STOP")]
    mon, _sock = _monitor(items, ring_buffer_size=2)
    snap = mon.listen_until_done()
    assert len(snap["last_raw_events"]) == 2
    assert snap["last_raw_events"][-1] == "@UPL STOP"


# -- loop exits -------------------------------------------------------------


def test_startup_timeout_when_no_events():
    mon, _sock = _monitor([], startup_timeout=30.0, session_timeout=1e9, monotonic=StepClock(20.0))
    snap = mon.listen_until_done()
    assert snap["stop_reason"] == "startup_timeout"
    assert snap["confirmed_playback"] is False


def test_startup_timeout_not_defeated_by_context_chatter():
    # H4: @UVO resolution chatter must NOT reset the startup timeout (only @UPL/@UTC do).
    items = [_line("@UVO 3840x2160"), TIMEOUT, TIMEOUT, TIMEOUT]
    mon, _sock = _monitor(
        items, startup_timeout=30.0, session_timeout=1e9, monotonic=StepClock(20.0)
    )
    snap = mon.listen_until_done()
    assert snap["stop_reason"] == "startup_timeout"
    assert snap["confirmed_playback"] is False


def test_session_timeout_after_activity():
    items = [_line("@UPL PLAY"), TIMEOUT, TIMEOUT, TIMEOUT, TIMEOUT]
    mon, _sock = _monitor(
        items, startup_timeout=1e9, session_timeout=25.0, monotonic=StepClock(10.0)
    )
    snap = mon.listen_until_done()
    assert snap["stop_reason"] == "session_timeout"
    assert snap["confirmed_playback"] is True


def test_connection_closed_ends_loop():
    mon, _sock = _monitor([_line("@UPL PLAY"), b""])
    snap = mon.listen_until_done()
    assert snap["stop_reason"] == "connection_closed"


def test_recv_oserror_ends_loop_as_closed():
    mon, _sock = _monitor([OSERR])
    snap = mon.listen_until_done()
    assert snap["stop_reason"] == "connection_closed"


def test_stop_event_ends_loop():
    class Flag:
        def is_set(self):
            return True

    mon, _sock = _monitor([_line("@UPL PLAY")])
    snap = mon.listen_until_done(stop_event=Flag())
    assert snap["stop_reason"] == "stop_event"


def test_snapshot_shape_is_stable():
    mon, _sock = _monitor([_line("@UPL STOP")])
    snap = mon.listen_until_done()
    assert set(snap) == {
        "monitor_mode",
        "previous_verbose_mode",
        "oppo_playback_state",
        "confirmed_playback",
        "confirmed_progress",
        "confirmed",
        "first_utc",
        "last_utc",
        "utc_tick_count",
        "stop_reason",
        "event_count",
        "last_raw_events",
    }
    assert snap["monitor_mode"] == "svm3"
