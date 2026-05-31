"""PR A3: run_playback_session -- the shared four-option session engine.

Both routings (playercorefactory and service-interception) call this one
function, so these pin that:

* the sequence is always mark -> fast_start -> monitor -> fast_return -> clear;
* monitor_mode legacy runs the existing hold_playback; svm3 runs the SVM3 monitor
  and falls back to the legacy hold if it cannot connect;
* TV/AVR failures and a fast_return failure stay non-fatal, and the session
  sentinel is cleared on success and on error (rc 1);
* a split-truth status JSON is written, reporting OPPO confirmation honestly
  (never a single success flag).

external_player's helpers are monkeypatched to record call order, so this
exercises the engine without touching real TV/OPPO/AVR code.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import external_player as ep  # bare name -> same module object as resources.lib.kodi.external_player

from resources.lib.kodi import playback_session as ps  # registers the alias finder
from resources.lib.kodi import settings_reader as sr
from resources.lib.oppo import playback_monitor_svm3 as svm3mod


def _settings(tmp_path, **over):
    data = {"addon_data_dir": str(tmp_path)}
    data.update(over)
    return sr.Settings(data)


def _patch_ep(monkeypatch, calls, *, fast_start_raises=False, fast_return_raises=False):
    monkeypatch.setattr(ep, "mark_session_active", lambda s: calls.append("mark"))
    monkeypatch.setattr(ep, "clear_session_active", lambda s: calls.append("clear"))
    monkeypatch.setattr(ep, "hold_playback", lambda s: calls.append("hold"))
    monkeypatch.setattr(ep, "log", lambda m: None)

    def fake_fast_start(s, f, preflight_result=None):
        calls.append(("fast_start", f, preflight_result))
        if fast_start_raises:
            raise RuntimeError("player failed")

    def fake_fast_return(s):
        calls.append("fast_return")
        if fast_return_raises:
            raise RuntimeError("return failed")

    monkeypatch.setattr(ep, "fast_start", fake_fast_start)
    monkeypatch.setattr(ep, "fast_return", fake_fast_return)


class FakeMonitor:
    last: "FakeMonitor"

    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.steps: list[str] = []
        FakeMonitor.last = self

    def connect(self):
        self.steps.append("connect")

    def query_previous_verbose_mode(self):
        self.steps.append("qvm")
        return "2"

    def enable(self):
        self.steps.append("enable")
        return True

    def listen_until_done(self, stop_event=None):
        self.steps.append("listen")
        return {
            "stop_reason": "oppo_stop",
            "confirmed": True,
            "confirmed_playback": True,
            "confirmed_progress": True,
            "oppo_playback_state": "STOP",
            "utc_tick_count": 3,
        }

    def restore(self):
        self.steps.append("restore")
        return True

    def close(self):
        self.steps.append("close")


class FailConnectMonitor(FakeMonitor):
    def connect(self):
        raise OSError("no route to host")


def _read_status(tmp_path):
    return json.loads((tmp_path / ps.STATUS_FILENAME).read_text(encoding="utf-8"))


# -- legacy routing ---------------------------------------------------------


def test_legacy_runs_full_sequence_with_hold(monkeypatch, tmp_path):
    calls = []
    _patch_ep(monkeypatch, calls)
    rc = ps.run_playback_session(_settings(tmp_path), "/m.iso", "playercorefactory")
    assert rc == 0
    assert calls == ["mark", ("fast_start", "/m.iso", None), "hold", "fast_return", "clear"]


def test_preflight_result_is_forwarded_to_fast_start(monkeypatch, tmp_path):
    calls = []
    _patch_ep(monkeypatch, calls)
    ps.run_playback_session(
        _settings(tmp_path), "/m.iso", "playercorefactory", preflight_result={"power_status": "on"}
    )
    assert ("fast_start", "/m.iso", {"power_status": "on"}) in calls


def test_legacy_status_reports_no_confirmation(monkeypatch, tmp_path):
    calls = []
    _patch_ep(monkeypatch, calls)
    ps.run_playback_session(_settings(tmp_path), "/m.iso", "service_interception")
    status = _read_status(tmp_path)
    assert status["monitor_mode"] == "legacy"
    assert status["launch_source"] == "service_interception"
    assert status["confirmed_playback"] is False
    assert status["session_state"] == "stopped"


# -- failure / cleanup ------------------------------------------------------


def test_fast_start_failure_returns_1_and_still_cleans_up(monkeypatch, tmp_path):
    calls = []
    _patch_ep(monkeypatch, calls, fast_start_raises=True)
    rc = ps.run_playback_session(_settings(tmp_path), "/m.iso", "playercorefactory")
    assert rc == 1
    assert "hold" not in calls  # monitor never reached
    assert calls[-2:] == ["fast_return", "clear"]
    assert _read_status(tmp_path)["session_state"] == "failed"


def test_fast_return_failure_is_nonfatal(monkeypatch, tmp_path):
    calls = []
    _patch_ep(monkeypatch, calls, fast_return_raises=True)
    rc = ps.run_playback_session(_settings(tmp_path), "/m.iso", "playercorefactory")
    assert rc == 0  # the session itself succeeded
    assert "clear" in calls  # clear still runs after fast_return raises


# -- svm3 routing -----------------------------------------------------------


def test_svm3_runs_monitor_and_skips_legacy_hold(monkeypatch, tmp_path):
    monkeypatch.setattr(svm3mod, "OppoSvm3PlaybackMonitor", FakeMonitor)
    calls = []
    _patch_ep(monkeypatch, calls)
    rc = ps.run_playback_session(
        _settings(tmp_path, playback_monitor_mode="svm3"), "/m.iso", "playercorefactory"
    )
    assert rc == 0
    assert "hold" not in calls
    assert FakeMonitor.last.steps == ["connect", "qvm", "enable", "listen", "restore", "close"]


def test_svm3_status_carries_confirmation(monkeypatch, tmp_path):
    monkeypatch.setattr(svm3mod, "OppoSvm3PlaybackMonitor", FakeMonitor)
    _patch_ep(monkeypatch, [])
    ps.run_playback_session(
        _settings(tmp_path, playback_monitor_mode="svm3"), "/m.iso", "playercorefactory"
    )
    status = _read_status(tmp_path)
    assert status["monitor_mode"] == "svm3"
    assert status["confirmed_playback"] is True
    assert status["confirmed_progress"] is True
    assert status["oppo_playback_state"] == "STOP"
    assert status["utc_tick_count"] == 3
    assert status["session_state"] == "stopped"


def test_svm3_connect_failure_falls_back_to_legacy_hold(monkeypatch, tmp_path):
    monkeypatch.setattr(svm3mod, "OppoSvm3PlaybackMonitor", FailConnectMonitor)
    calls = []
    _patch_ep(monkeypatch, calls)
    rc = ps.run_playback_session(
        _settings(tmp_path, playback_monitor_mode="svm3"), "/m.iso", "playercorefactory"
    )
    assert rc == 0
    assert "hold" in calls  # fell back to the legacy hold
    # restore/close still ran is not asserted here (connect raised before enable);
    # the fallback path is what matters.


# -- status writer edges ----------------------------------------------------


def test_write_status_noop_without_addon_data():
    ps._write_status(sr.Settings({}), {"x": 1})  # no addon_data_dir -> no-op, no raise


def test_write_status_swallows_oserror(tmp_path):
    bad = sr.Settings({"addon_data_dir": str(tmp_path / "missing" / "deep")})
    ps._write_status(bad, {"x": 1})  # parent dir absent -> OSError -> swallowed
    assert not (tmp_path / "missing").exists()
