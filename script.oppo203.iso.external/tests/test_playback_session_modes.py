"""run_playback_session -- the shared six-option session engine.

The three routings (playercorefactory, service-interception, http_handoff) call
this one function, so these pin that:

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
from resources.lib.oppo import playback_monitor_http as httpmod
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


def test_status_carries_session_identity_and_phases(monkeypatch, tmp_path):
    writes = []
    real_write = ps._write_status
    monkeypatch.setattr(ps, "_write_status", lambda s, st: writes.append(st) or real_write(s, st))
    _patch_ep(monkeypatch, [])
    ps.run_playback_session(_settings(tmp_path), "/m.iso", "playercorefactory")
    # three writes -- launching -> monitoring -> ended -- sharing one session_id + started_at.
    assert [w["phase"] for w in writes] == ["launching", "monitoring", "ended"]
    assert len({w["session_id"] for w in writes}) == 1
    assert next(iter({w["session_id"] for w in writes}))  # non-empty id
    assert len({w["started_at"] for w in writes}) == 1
    assert all(isinstance(w["updated_at"], float) for w in writes)
    final = _read_status(tmp_path)
    assert final["phase"] == "ended"
    assert final["session_state"] == "stopped"


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


# -- http_handoff routing (run_playback_session launch branch) --------------


def test_http_handoff_routing_uses_fast_start_http(monkeypatch, tmp_path):
    calls = []
    _patch_ep(monkeypatch, calls)
    monkeypatch.setattr(ep, "fast_start_http", lambda s, f: calls.append(("fast_start_http", f)))
    rc = ps.run_playback_session(
        _settings(tmp_path, playback_architecture_preset="http_handoff_legacy"),
        "/mnt/nfs1/m.iso",
        "playercorefactory",
    )
    assert rc == 0
    assert ("fast_start_http", "/mnt/nfs1/m.iso") in calls
    assert not any(isinstance(c, tuple) and c[0] == "fast_start" for c in calls)
    assert "hold" in calls  # legacy monitor still runs after the HTTP launch


def test_http_handoff_svm3_launches_http_then_svm3_monitor(monkeypatch, tmp_path):
    monkeypatch.setattr(svm3mod, "OppoSvm3PlaybackMonitor", FakeMonitor)
    calls = []
    _patch_ep(monkeypatch, calls)
    monkeypatch.setattr(ep, "fast_start_http", lambda s, f: calls.append(("fast_start_http", f)))
    ps.run_playback_session(
        _settings(tmp_path, playback_architecture_preset="http_handoff_svm3"),
        "/mnt/nfs1/m.iso",
        "playercorefactory",
    )
    status = _read_status(tmp_path)
    assert status["routing_mode"] == "http_handoff"
    assert status["monitor_mode"] == "svm3"
    assert ("fast_start_http", "/mnt/nfs1/m.iso") in calls
    assert "hold" not in calls  # svm3 monitor, not the legacy hold


# -- http monitor (run_playback_session dispatch branch) --------------------


class FakeHttpMonitor:
    last: "FakeHttpMonitor"

    def __init__(self, settings, **kwargs):
        self.settings = settings
        self.kwargs = kwargs
        FakeHttpMonitor.last = self

    def run(self):
        return {
            "monitor_mode": "http",
            "confirmed_playback": True,
            "confirmed_progress": True,
            "confirmed": True,
            "oppo_playback_state": "STOP",
            "stop_reason": "oppo_idle",
        }


class UnreachableHttpMonitor(FakeHttpMonitor):
    def run(self):
        return None


def test_http_monitor_runs_and_skips_legacy_hold(monkeypatch, tmp_path):
    monkeypatch.setattr(httpmod, "OppoHttpPlaybackMonitor", FakeHttpMonitor)
    calls = []
    _patch_ep(monkeypatch, calls)
    monkeypatch.setattr(ep, "fast_start_http", lambda s, f: calls.append(("fast_start_http", f)))
    rc = ps.run_playback_session(
        _settings(tmp_path, playback_architecture_preset="http_handoff_http"),
        "/mnt/nfs1/m.iso",
        "playercorefactory",
    )
    assert rc == 0
    assert "hold" not in calls  # the http monitor ran, not the legacy hold
    status = _read_status(tmp_path)
    assert status["routing_mode"] == "http_handoff"
    assert status["monitor_mode"] == "http"
    assert status["confirmed_playback"] is True
    assert ("fast_start_http", "/mnt/nfs1/m.iso") in calls


def test_http_monitor_unreachable_falls_back_to_legacy_hold(monkeypatch, tmp_path):
    monkeypatch.setattr(httpmod, "OppoHttpPlaybackMonitor", UnreachableHttpMonitor)
    calls = []
    _patch_ep(monkeypatch, calls)
    monkeypatch.setattr(ep, "fast_start_http", lambda s, f: calls.append(("fast_start_http", f)))
    rc = ps.run_playback_session(
        _settings(tmp_path, playback_architecture_preset="http_handoff_http"),
        "/m.iso",
        "playercorefactory",
    )
    assert rc == 0
    assert "hold" in calls  # unreachable -> fell back to the legacy hold


# -- external_player.fast_start_http / _start_oppo_http (the real launch) ----


class _AvrResult:
    def __init__(self, ok=True, skipped=True):
        self.ok = ok
        self.skipped = skipped
        self.warnings: list[str] = []


def _patch_http(monkeypatch, *, play=None):
    # Patch the exact oppo_control module object _start_oppo_http resolves via
    # _oppo_control_module(); under a serial run the ENH-#43 stub-context tests purge + re-import
    # oppo_control, so patching it by name (importlib) can miss the live object.
    play_fn = play or (lambda s, f: "@OK")
    oc = ep._oppo_control_module()
    monkeypatch.setattr(oc, "activate_http_api", lambda s: True, raising=False)
    monkeypatch.setattr(oc, "signin_http_api", lambda s: "", raising=False)
    monkeypatch.setattr(oc, "play_media_http_api", play_fn, raising=False)
    # PR3 orchestration primitives: safe no-ops + a "playing" confirm so the wake, mount,
    # BDMV-probe, auto-heal, and confirm steps never reach a real device in these tests.
    monkeypatch.setattr(oc, "send_remote_key_http", lambda s, k: "OK", raising=False)
    monkeypatch.setattr(oc, "get_global_info", lambda s: {"is_playing": True}, raising=False)
    monkeypatch.setattr(oc, "global_info_is_playing", lambda i: True, raising=False)
    monkeypatch.setattr(oc, "detect_nfs", lambda s: False, raising=False)
    monkeypatch.setattr(oc, "login_smb", lambda s, *a, **k: {}, raising=False)
    monkeypatch.setattr(oc, "login_nfs", lambda s, *a, **k: {}, raising=False)
    monkeypatch.setattr(oc, "mount_smb", lambda s, *a, **k: {}, raising=False)
    monkeypatch.setattr(oc, "mount_nfs", lambda s, *a, **k: {}, raising=False)
    monkeypatch.setattr(oc, "check_folder_has_bdmv", lambda s, f: False, raising=False)
    # The one-shot ISO auto-heal sleeps before its confirm; keep tests instant. Tests that assert
    # on sleeps re-patch ep.time.sleep AFTER calling _patch_http.
    monkeypatch.setattr(ep.time, "sleep", lambda *_a: None, raising=False)


def test_fast_start_http_runs_tv_avr_then_http_launch(monkeypatch):
    order = []
    monkeypatch.setattr(ep, "log", lambda m: None)
    monkeypatch.setattr(ep, "_safe_tv_switch", lambda s, t: order.append(("tv", t)))
    monkeypatch.setattr(ep, "pre_playback_sequence", lambda s: order.append("avr") or _AvrResult())
    _patch_http(monkeypatch, play=lambda s, f: order.append(("play", f)) or "@OK")
    ep.fast_start_http(sr.Settings({}), "/mnt/nfs1/m.iso")
    assert order == [("tv", "oppo"), "avr", ("play", "/mnt/nfs1/m.iso")]


def test_start_oppo_http_failure_is_nonfatal(monkeypatch):
    logs = []
    monkeypatch.setattr(ep, "log", lambda m: logs.append(m))

    def boom(s, f):
        raise RuntimeError("http down")

    _patch_http(monkeypatch, play=boom)
    ep._start_oppo_http(sr.Settings({}), "/mnt/nfs1/m.iso")  # must not raise
    assert any("HTTP handoff failed" in m for m in logs)


def test_start_oppo_http_honors_startup_delay(monkeypatch):
    slept = []
    monkeypatch.setattr(ep, "log", lambda m: None)
    _patch_http(monkeypatch)
    # re-patch sleep AFTER _patch_http (which no-ops it) so we record only the startup delay;
    # the ISO auto-heal is disabled here so it does not add a second sleep.
    monkeypatch.setattr(ep.time, "sleep", lambda n: slept.append(n))
    ep._start_oppo_http(
        sr.Settings({"startup_delay": "1", "oppo_http_iso_autoheal": "false"}), "/m.iso"
    )
    assert slept == [1]


def test_fast_start_http_logs_avr_warning_nonfatal(monkeypatch):
    logs = []
    monkeypatch.setattr(ep, "log", lambda m: logs.append(m))
    monkeypatch.setattr(ep, "_safe_tv_switch", lambda s, t: None)
    monkeypatch.setattr(ep, "pre_playback_sequence", lambda s: _AvrResult(ok=False, skipped=False))
    _patch_http(monkeypatch)
    ep.fast_start_http(
        sr.Settings({"fast_changeover": "false"}), "/m.iso"
    )  # also covers no-changeover
    assert any("AVR pre-playback sequence warning" in m for m in logs)


# -- hdmi_switch_mode ordering (PR5) ----------------------------------------


def test_hdmi_immediate_mode_keeps_tv_first_then_avr_then_play(monkeypatch):
    order = []
    monkeypatch.setattr(ep, "log", lambda m: None)
    monkeypatch.setattr(ep, "_safe_tv_switch", lambda s, t: order.append(("tv", t)))
    monkeypatch.setattr(ep, "pre_playback_sequence", lambda s: order.append("avr") or _AvrResult())
    monkeypatch.setattr(
        ep,
        "start_oppo_after_optional_delay",
        lambda s, f, preflight_result=None: order.append("play"),
    )
    ep.fast_start(sr.Settings({}), "/media/film.iso")  # default mode = immediate (frozen order)
    assert order == [("tv", "oppo"), "avr", "play"]


def test_hdmi_delayed_mode_plays_first_then_switches_tv_with_disc_floor(monkeypatch):
    order = []
    slept = []
    monkeypatch.setattr(ep, "log", lambda m: None)
    monkeypatch.setattr(ep, "_safe_tv_switch", lambda s, t: order.append(("tv", t)))
    monkeypatch.setattr(ep, "pre_playback_sequence", lambda s: order.append("avr") or _AvrResult())
    monkeypatch.setattr(
        ep,
        "start_oppo_after_optional_delay",
        lambda s, f, preflight_result=None: order.append("play"),
    )
    monkeypatch.setattr(ep.time, "sleep", lambda n: slept.append(n))
    ep.fast_start(
        sr.Settings({"hdmi_switch_mode": "delayed", "play_delay_hdmi": "3", "av_delay_hdmi": "2"}),
        "/media/film.iso",
    )
    assert order == ["avr", "play", ("tv", "oppo")]  # player first, then the TV switch
    assert slept == [6, 2]  # ISO floors the play delay at 6; then the 2s AVR stagger


def test_hdmi_delayed_mode_zero_delays_skip_sleeps(monkeypatch):
    order = []
    slept = []
    monkeypatch.setattr(ep, "log", lambda m: None)
    monkeypatch.setattr(ep, "_safe_tv_switch", lambda s, t: order.append(("tv", t)))
    monkeypatch.setattr(ep, "pre_playback_sequence", lambda s: _AvrResult())
    monkeypatch.setattr(
        ep,
        "start_oppo_after_optional_delay",
        lambda s, f, preflight_result=None: order.append("play"),
    )
    monkeypatch.setattr(ep.time, "sleep", lambda n: slept.append(n))
    ep.fast_start(
        sr.Settings({"hdmi_switch_mode": "delayed", "play_delay_hdmi": "0", "av_delay_hdmi": "0"}),
        "/media/film.mkv",
    )
    assert order == ["play", ("tv", "oppo")]
    assert slept == []  # zero delays -> no sleeps


def test_hdmi_delayed_mode_applies_to_http_launch(monkeypatch):
    order = []
    monkeypatch.setattr(ep, "log", lambda m: None)
    monkeypatch.setattr(ep, "_safe_tv_switch", lambda s, t: order.append(("tv", t)))
    monkeypatch.setattr(ep, "pre_playback_sequence", lambda s: order.append("avr") or _AvrResult())
    monkeypatch.setattr(ep, "_start_oppo_http", lambda s, f: order.append("http"))
    monkeypatch.setattr(ep.time, "sleep", lambda n: None)
    ep.fast_start_http(sr.Settings({"hdmi_switch_mode": "delayed"}), "/m/film.mkv")
    assert order == ["avr", "http", ("tv", "oppo")]


# -- status writer edges ----------------------------------------------------


def test_write_status_noop_without_addon_data():
    ps._write_status(sr.Settings({}), {"x": 1})  # no addon_data_dir -> no-op, no raise


def test_write_status_swallows_oserror(tmp_path):
    bad = sr.Settings({"addon_data_dir": str(tmp_path / "missing" / "deep")})
    ps._write_status(bad, {"x": 1})  # parent dir absent -> OSError -> swallowed
    assert not (tmp_path / "missing").exists()
