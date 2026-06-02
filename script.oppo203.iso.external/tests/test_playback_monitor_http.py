"""PR2 (Xnoppo V3 adoption): OppoHttpPlaybackMonitor -- the http monitor axis.

Hermetic: the info/time fetchers, the clock, and sleep are all injected, so no real device
and no real time. Pins: unreachable-first-poll falls back (run() -> None); playback is only
confirmed from the player's own /getglobalinfo; advancing /getplayingtime sets progress; and the
stop reasons (oppo_idle / startup_timeout / session_timeout / connection_lost).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _p in (str(ROOT), str(LIB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from resources.lib.oppo import oppo_control as oc
from resources.lib.oppo.playback_monitor_http import OppoHttpPlaybackMonitor, _play_time_token


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def monotonic(self) -> float:
        return self.t

    def sleep(self, secs: float) -> None:
        self.t += float(secs)


def _scripted(values):
    """Return a callable yielding queued values; an Exception value is raised; last repeats."""
    seq = list(values)
    box = {"i": 0}

    def call(_settings):
        v = seq[min(box["i"], len(seq) - 1)]
        box["i"] += 1
        if isinstance(v, Exception):
            raise v
        return v

    return call


def _monitor(info_seq, *, time_seq=None, settings=None, **kw):
    clock = FakeClock()
    mon = OppoHttpPlaybackMonitor(
        settings if settings is not None else {},
        fetch_info=_scripted(info_seq),
        fetch_time=_scripted(time_seq if time_seq is not None else [{}]),
        is_playing=oc.global_info_is_playing,
        sleep=clock.sleep,
        monotonic=clock.monotonic,
        **kw,
    )
    return mon, clock


def test_unreachable_first_poll_returns_none():
    mon, _ = _monitor([oc.OppoError("down")])
    assert mon.run() is None


def test_play_then_idle_confirms_and_stops():
    mon, _ = _monitor(
        [{"is_playing": True}, {"is_playing": True}, {"is_playing": False}, {"is_playing": False}],
        idle_confirmations=2,
    )
    snap = mon.run()
    assert snap is not None
    assert snap["monitor_mode"] == "http"
    assert snap["confirmed_playback"] is True
    assert snap["oppo_playback_state"] == "STOP"
    assert snap["stop_reason"] == "oppo_idle"
    assert snap["poll_count"] >= 3


def test_progress_detected_from_advancing_play_time():
    mon, _ = _monitor(
        [{"is_playing": True}, {"is_playing": True}, {"is_playing": False}, {"is_playing": False}],
        time_seq=[{"playtime": "00:00:01"}, {"playtime": "00:00:05"}],
        idle_confirmations=2,
    )
    snap = mon.run()
    assert snap["confirmed_progress"] is True
    assert snap["confirmed"] is True
    assert snap["progress_tick_count"] >= 1


def test_playback_without_progress_is_not_fully_confirmed():
    mon, _ = _monitor(
        [{"is_playing": True}, {"is_playing": False}, {"is_playing": False}],
        time_seq=[{"playtime": "00:00:01"}],
        idle_confirmations=2,
    )
    snap = mon.run()
    assert snap["confirmed_playback"] is True
    assert snap["confirmed_progress"] is False
    assert snap["confirmed"] is False


def test_no_progress_when_play_time_empty():
    mon, _ = _monitor(
        [{"is_playing": True}, {"is_playing": False}, {"is_playing": False}],
        time_seq=[{}],
        idle_confirmations=2,
    )
    snap = mon.run()
    assert snap["confirmed_progress"] is False
    assert snap["first_play_time"] is None


def test_progress_fetch_error_is_nonfatal():
    mon, _ = _monitor(
        [{"is_playing": True}, {"is_playing": False}, {"is_playing": False}],
        time_seq=[oc.OppoError("time down")],
        idle_confirmations=2,
    )
    snap = mon.run()
    assert snap["confirmed_playback"] is True
    assert snap["confirmed_progress"] is False


def test_startup_timeout_when_never_playing():
    mon, _ = _monitor([{"is_playing": False}], startup_timeout=10.0)
    snap = mon.run()
    assert snap["confirmed_playback"] is False
    assert snap["confirmed"] is False
    assert snap["stop_reason"] == "startup_timeout"


def test_session_timeout_when_playback_never_ends():
    mon, _ = _monitor([{"is_playing": True}], session_timeout=20.0)
    snap = mon.run()
    assert snap["confirmed_playback"] is True
    assert snap["stop_reason"] == "session_timeout"


def test_connection_lost_after_repeated_failures():
    mon, _ = _monitor(
        [{"is_playing": True}, oc.OppoError("x"), oc.OppoError("x"), oc.OppoError("x")],
        max_poll_failures=3,
    )
    snap = mon.run()
    assert snap["confirmed_playback"] is True
    assert snap["stop_reason"] == "connection_lost"


def test_transient_failure_recovers():
    # One failure (below the threshold) is shrugged off; playback then ends cleanly on idle.
    mon, _ = _monitor(
        [
            {"is_playing": True},
            oc.OppoError("blip"),
            {"is_playing": True},
            {"is_playing": False},
            {"is_playing": False},
        ],
        idle_confirmations=2,
        max_poll_failures=3,
    )
    snap = mon.run()
    assert snap["stop_reason"] == "oppo_idle"
    assert snap["confirmed_playback"] is True


def test_refresh_seconds_default_and_clamp():
    base = {
        "fetch_info": _scripted([{}]),
        "fetch_time": _scripted([{}]),
        "is_playing": lambda _i: False,
    }
    assert OppoHttpPlaybackMonitor({}, **base)._refresh == 5.0
    assert OppoHttpPlaybackMonitor({"oppo_http_refresh_seconds": "0"}, **base)._refresh == 1.0
    assert OppoHttpPlaybackMonitor({"oppo_http_refresh_seconds": "8"}, **base)._refresh == 8.0


def test_resolve_defaults_to_oppo_control():
    # Identify by name/module rather than object identity: the ENH-#43 stub-context tests purge
    # and re-import oppo_control, so a plain `is` check is flaky under a serial (non-xdist) run.
    fi, ft, ip = OppoHttpPlaybackMonitor({})._resolve()
    assert (fi.__name__, ft.__name__, ip.__name__) == (
        "get_global_info",
        "get_playing_time",
        "global_info_is_playing",
    )
    assert all(f.__module__.endswith("oppo_control") for f in (fi, ft, ip))


def test_play_time_token_helper():
    assert _play_time_token({"playtime": "00:01:00"}) == "00:01:00"
    assert _play_time_token({"elapsed": 42}) == "42"
    assert _play_time_token({"nope": 1}) == ""
    assert _play_time_token("notdict") == ""
