"""v2.9.10 Build 18 - unified TV + AVR playback sequencing."""
from __future__ import annotations

from resources.lib import avr_control, avr_diagnostics, avr_presets, avr_sequence, version
from resources.lib.settings_reader import Settings
import external_player as external_player


class FakeAvrController:
    def __init__(self, fail_on: str | None = None):
        self.calls: list[tuple[str, object | None]] = []
        self.fail_on = fail_on

    def power_on(self):
        self.calls.append(("power_on", None))
        if self.fail_on == "power_on":
            raise RuntimeError("avr power failed")
        return {"ok": True, "action": "power_on", "nonfatal": True}

    def select_input(self, input_name=None):
        self.calls.append(("select_input", input_name))
        if self.fail_on == "select_input":
            raise RuntimeError("avr input failed")
        return {"ok": True, "action": "select_input", "nonfatal": True}


def _settings(**overrides):
    data = {
        "playback_architecture": "external_player",
        "avr_control_enabled": "true",
        "avr_backend": "denon_marantz",
        "avr_host": "192.168.1.81",
        "avr_player_input": "BD",
        "avr_power_on_enabled": "true",
        "avr_restore_enabled": "true",
        "avr_restore_input": "TV",
    }
    data.update(overrides)
    return Settings(data)


def test_build18_metadata_identity_and_summary_flags():
    assert version.BUILD_ID == "v2.9.11 Final"
    assert version.BUILD_NUMBER == 20
    assert avr_sequence.sequencing_metadata()["playback_sequencing_hooked"] is True
    assert avr_control.avr_settings_summary(_settings())["playback_sequencing_hooked"] is True
    assert avr_diagnostics.wizard_capabilities()["playback_sequencing_hooked"] is True
    assert avr_presets.avr_support_summary()["playback_sequencing_hooked"] is True


def test_build18_avr_disabled_path_is_noop_and_does_not_create_controller(monkeypatch):
    calls = []
    monkeypatch.setattr(avr_sequence, "controller_factory", lambda settings: calls.append("factory"))
    result = avr_sequence.pre_playback_sequence(_settings(avr_control_enabled="false"))
    assert result.ok is True
    assert result.skipped is True
    assert "avr_control_disabled" in result.warnings
    assert calls == []


def test_build18_avr_sequence_runs_only_for_external_player_handoff():
    controller = FakeAvrController()
    result = avr_sequence.pre_playback_sequence(
        _settings(playback_architecture="service_interception"),
        controller=controller,
    )
    assert result.ok is True
    assert result.skipped is True
    assert "avr_sequence_ineligible_external_player" in result.warnings
    assert controller.calls == []


def test_build18_pre_sequence_powers_on_and_selects_player_input_when_enabled():
    controller = FakeAvrController()
    result = avr_sequence.pre_playback_sequence(_settings(), controller=controller)
    assert result.ok is True
    assert result.actions == ("power_on", "select_input")
    assert controller.calls == [("power_on", None), ("select_input", None)]


def test_build18_avr_failure_is_nonfatal_and_does_not_raise():
    controller = FakeAvrController(fail_on="select_input")
    result = avr_sequence.pre_playback_sequence(_settings(), controller=controller)
    assert result.ok is False
    assert result.nonfatal is True
    assert "avr_pre_sequence_failed_nonfatal" in result.warnings
    assert controller.calls == [("power_on", None), ("select_input", None)]


def test_build18_optional_restore_runs_only_when_enabled_and_configured():
    disabled_controller = FakeAvrController()
    disabled = avr_sequence.post_playback_sequence(
        _settings(avr_restore_enabled="false"),
        controller=disabled_controller,
    )
    assert disabled.ok is True
    assert disabled.skipped is True
    assert disabled_controller.calls == []

    missing_controller = FakeAvrController()
    missing = avr_sequence.post_playback_sequence(
        _settings(avr_restore_enabled="true", avr_restore_input=""),
        controller=missing_controller,
    )
    assert missing.ok is False
    assert missing.skipped is True
    assert missing_controller.calls == []

    controller = FakeAvrController()
    restored = avr_sequence.post_playback_sequence(_settings(), controller=controller)
    assert restored.ok is True
    assert restored.actions == ("restore_input",)
    assert controller.calls == [("select_input", "TV")]


def test_build18_external_player_order_keeps_tv_first_then_avr_then_oppo(monkeypatch):
    calls = []
    settings = _settings()
    monkeypatch.setattr(external_player, "switch_to_oppo", lambda s: calls.append("tv_to_oppo"))
    monkeypatch.setattr(external_player, "pre_playback_sequence", lambda s: calls.append("avr_pre") or avr_sequence.AvrSequenceResult(True, "pre"))
    monkeypatch.setattr(external_player, "start_oppo_after_optional_delay", lambda s, f, preflight_result=None: calls.append("oppo_start"))
    external_player.fast_start(settings, "/media/movie.iso")
    assert calls == ["tv_to_oppo", "avr_pre", "oppo_start"]


def test_build18_external_player_tv_and_avr_failures_do_not_block_oppo_start(monkeypatch):
    calls = []
    settings = _settings()
    monkeypatch.setattr(external_player, "switch_to_oppo", lambda s: (_ for _ in ()).throw(RuntimeError("tv failed")))
    monkeypatch.setattr(external_player, "pre_playback_sequence", lambda s: avr_sequence.AvrSequenceResult(False, "pre", warnings=("avr failed",)))
    monkeypatch.setattr(external_player, "start_oppo_after_optional_delay", lambda s, f, preflight_result=None: calls.append("oppo_start"))
    external_player.fast_start(settings, "/media/movie.iso")
    assert calls == ["oppo_start"]


def test_build18_external_player_return_preserves_stop_avr_restore_and_tv_restore(monkeypatch):
    calls = []
    settings = _settings()
    monkeypatch.setattr(external_player, "run_configured_commands", lambda s, key: calls.append(("stop", key)))
    monkeypatch.setattr(external_player, "post_playback_sequence", lambda s: calls.append(("avr_post", None)) or avr_sequence.AvrSequenceResult(True, "post"))
    monkeypatch.setattr(external_player, "switch_to_kodi", lambda s: calls.append(("tv_to_kodi", None)))
    external_player.fast_return(settings)
    assert calls == [("stop", "oppo_stop_commands"), ("avr_post", None), ("tv_to_kodi", None)]


def test_build18_sony_restore_uses_sony_restore_uri_when_available():
    controller = FakeAvrController()
    settings = _settings(
        avr_backend="sony_audio_api",
        sony_avr_experimental_acknowledged="true",
        avr_restore_input="ignored",
        sony_avr_restore_input_uri="extInput:hdmi?port=4",
    )
    result = avr_sequence.post_playback_sequence(settings, controller=controller)
    assert result.ok is True
    assert controller.calls == [("select_input", "extInput:hdmi?port=4")]


def test_build18_sequence_result_and_settings_edge_paths(monkeypatch):
    assert avr_sequence.AvrSequenceResult(True, "pre").as_dict()["hardware_validation_claimed"] is False
    assert avr_sequence._settings_dict(None) == {}

    class BrokenItems:
        def items(self):
            raise TypeError("broken")

    assert avr_sequence._settings_dict(BrokenItems()) == {}
    assert avr_sequence._truthy(True) is True
    assert avr_sequence._truthy("", default=True) is True
    assert avr_sequence.eligible_for_external_player_avr_sequence({}) is True

    monkeypatch.setattr(avr_sequence, "controller_factory", lambda settings: None)
    unavailable = avr_sequence.pre_playback_sequence(_settings())
    assert unavailable.ok is False
    assert unavailable.skipped is True
    assert "avr_controller_unavailable_nonfatal" in unavailable.warnings


def test_build18_controller_run_fallback_and_post_failure_paths():
    class RunOnlyController:
        def __init__(self):
            self.calls = []
        def run(self, action, **kwargs):
            self.calls.append((action, kwargs))
            return {"ok": True}

    run_only = RunOnlyController()
    result = avr_sequence.pre_playback_sequence(_settings(avr_power_on_enabled="false"), controller=run_only)
    assert result.ok is True
    assert result.actions == ("select_input",)
    assert run_only.calls == [("select_input", {})]

    post_run_only = RunOnlyController()
    restored = avr_sequence.post_playback_sequence(_settings(), controller=post_run_only)
    assert restored.ok is True
    assert post_run_only.calls == [("select_input", {"input_name": "TV", "input_code": "TV"})]

    broken = FakeAvrController(fail_on="select_input")
    failed = avr_sequence.post_playback_sequence(_settings(), controller=broken)
    assert failed.ok is False
    assert failed.nonfatal is True
    assert "avr_post_sequence_failed_nonfatal" in failed.warnings

    class EmptyController:
        pass

    missing_method = avr_sequence.pre_playback_sequence(_settings(avr_power_on_enabled="false"), controller=EmptyController())
    assert missing_method.ok is False
    assert "avr_pre_sequence_failed_nonfatal" in missing_method.warnings


def test_build18_post_sequence_disabled_ineligible_and_unavailable_paths(monkeypatch):
    controller = FakeAvrController()
    ineligible = avr_sequence.post_playback_sequence(
        _settings(playback_architecture="service_interception"),
        controller=controller,
    )
    assert ineligible.ok is True
    assert ineligible.skipped is True
    assert controller.calls == []

    disabled = avr_sequence.post_playback_sequence(_settings(avr_control_enabled="false"), controller=controller)
    assert disabled.ok is True
    assert disabled.skipped is True

    monkeypatch.setattr(avr_sequence, "controller_factory", lambda settings: None)
    unavailable = avr_sequence.post_playback_sequence(_settings())
    assert unavailable.ok is False
    assert unavailable.skipped is True
    assert "avr_controller_unavailable_nonfatal" in unavailable.warnings
