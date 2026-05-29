"""v2.9.10 Build 16 - Unified TV + AVR playback sequencing."""

from __future__ import annotations

import json
from pathlib import Path

from resources.lib import avr_control, avr_diagnostics, settings_reader, version

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


def _sony_settings(**overrides):
    data = dict(settings_reader.DEFAULTS)
    data.update(
        {
            "avr_control_enabled": "true",
            "avr_backend": "sony_audio_api",
            "avr_host": "192.168.1.120",
            "avr_port": "80",
            "avr_player_input": "extInput:hdmi?port=1",
            "sony_avr_experimental_acknowledged": "true",
            "sony_avr_psk": "supersecretpsk",
            "sony_avr_api_path": "/sony/audio",
            "sony_avr_player_input_uri": "extInput:hdmi?port=1",
        }
    )
    data.update(overrides)
    return data


def test_build16_wizard_capabilities_cover_required_avr_setup_surface():
    meta = avr_diagnostics.wizard_capabilities()
    assert meta["supports_skip_avr_setup"] is True
    assert meta["supports_family_selection"] is True
    assert meta["supports_host_and_port"] is True
    assert meta["supports_player_input"] is True
    assert meta["supports_optional_restore_input"] is True
    assert meta["supports_optional_sound_mode_metadata"] is True
    assert meta["supports_sony_experimental_acknowledgement"] is True
    assert meta["avr_enabled_by_default"] is False
    assert meta["query_only_tests_change_state"] is False
    assert meta["power_input_tests_require_explicit_user_action"] is True
    assert meta["playback_sequencing_hooked"] is True
    assert meta["hardware_validation_claimed"] is False

    options = avr_diagnostics.wizard_family_options()
    ids = {item["id"] for item in options}
    assert {
        "disabled",
        "denon_marantz",
        "yamaha_yxc",
        "onkyo_eiscp",
        "pioneer_eiscp",
        "sony_audio_api",
    } <= ids
    sony = [item for item in options if item["id"] == "sony_audio_api"][0]
    assert sony["requires_sony_experimental_acknowledgement"] is True
    assert sony["hardware_validation_claimed"] is False


def test_build16_apply_wizard_selection_supports_skip_and_disabled_defaults():
    updated = avr_diagnostics.apply_wizard_selection(
        {
            "avr_control_enabled": "true",
            "avr_backend": "denon_marantz",
            "avr_power_off_enabled": "true",
        },
        {"skip_avr_setup": True},
    )
    assert updated["avr_control_enabled"] == "false"
    assert updated["avr_backend"] == "disabled"
    assert updated["selected_avr_preset_id"] == "disabled"
    assert updated["avr_power_off_enabled"] == "false"
    assert updated["avr_volume_automation_enabled"] == "false"
    assert avr_control.controller_factory(updated) is None


def test_build16_apply_wizard_selection_supports_family_host_port_inputs_without_commands():
    updated = avr_diagnostics.apply_wizard_selection(
        {},
        {
            "avr_backend": "yamaha_yxc",
            "avr_host": "192.168.1.80",
            "avr_port": "80",
            "avr_player_input": "hdmi1",
            "avr_restore_enabled": "true",
            "avr_restore_input": "tv",
            "avr_sound_mode": "straight",
        },
    )
    assert updated["avr_control_enabled"] == "true"
    assert updated["avr_backend"] == "yamaha_yxc"
    assert updated["avr_host"] == "192.168.1.80"
    assert updated["avr_player_input"] == "hdmi1"
    assert updated["avr_restore_enabled"] == "true"
    assert updated["avr_restore_input"] == "tv"
    assert updated["avr_sound_mode"] == "straight"
    assert updated["avr_power_off_enabled"] == "false"
    assert updated["avr_volume_automation_enabled"] == "false"


def test_build16_diagnostic_report_is_sanitized_and_states_no_hardware_claim():
    settings = _sony_settings()
    report = avr_diagnostics.build_diagnostic_report(settings)
    rendered = avr_diagnostics.format_report(report, settings)
    assert "OPPO203 AVR Diagnostic Report" in rendered
    assert '"hardware_validation_claimed": false' in rendered
    assert '"playback_sequencing_hooked": true' in rendered
    assert "supersecretpsk" not in rendered
    assert "sup...sk" in rendered
    assert "sony_avr_psk" in rendered


def test_build16_query_only_test_action_does_not_change_avr_state():
    calls: list[str] = []

    class FakeController:
        def query_power(self):
            calls.append("query_power")
            return {
                "ok": True,
                "action": "query_power",
                "backend": "denon_marantz",
                "command_sent": True,
                "raw_response": "safe",
            }

        def power_on(self):  # pragma: no cover - must not be called by query-only path
            calls.append("power_on")
            return {"ok": True, "action": "power_on", "command_sent": True}

    settings = {
        "avr_control_enabled": "true",
        "avr_backend": "denon_marantz",
        "avr_host": "192.168.1.81",
        "avr_player_input": "BD",
    }
    result = avr_diagnostics.run_query_only_test(settings, "power", controller=FakeController())
    assert result["ok"] is True
    assert result["query_only"] is True
    assert result["state_changing"] is False
    assert result["hardware_validation_claimed"] is False
    assert calls == ["query_power"]


def test_build16_power_and_input_test_actions_require_explicit_user_action():
    calls: list[str] = []

    class FakeController:
        def power_on(self):
            calls.append("power_on")
            return {
                "ok": True,
                "action": "power_on",
                "backend": "denon_marantz",
                "command_sent": True,
            }

        def select_input(self):
            calls.append("select_input")
            return {
                "ok": True,
                "action": "select_input",
                "backend": "denon_marantz",
                "command_sent": True,
            }

    settings = {
        "avr_control_enabled": "true",
        "avr_backend": "denon_marantz",
        "avr_host": "192.168.1.82",
        "avr_player_input": "BD",
    }
    blocked = avr_diagnostics.run_explicit_test_action(
        settings, "power_on", explicit_user_action=False, controller=FakeController()
    )
    assert blocked["ok"] is False
    assert blocked["command_sent"] is False
    assert "explicit_user_action_required" in blocked["warnings"]
    assert calls == []

    allowed = avr_diagnostics.run_explicit_test_action(
        settings, "select_input", explicit_user_action=True, controller=FakeController()
    )
    assert allowed["ok"] is True
    assert allowed["state_changing"] is True
    assert allowed["explicit_user_action"] is True
    assert allowed["hardware_validation_claimed"] is False
    assert calls == ["select_input"]


def test_build16_export_avr_diagnostic_report_uses_writer_and_sanitizes():
    calls = []
    path = avr_diagnostics.export_avr_diagnostic_report(
        _sony_settings(),
        "/tmp/addon-data",
        now=0,
        writer=lambda output_path, text: calls.append((output_path, text)),
    )
    assert path.endswith("avr-diagnostics-19700101-000000.json")
    assert calls and calls[0][0] == path
    payload = json.loads(calls[0][1])
    assert payload["hardware_validation_claimed"] is False
    assert "supersecretpsk" not in calls[0][1]


def test_build16_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.13 Final"
    assert version.BUILD_NUMBER == 22
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 18" in addon
    assert "Unified TV + AVR playback sequencing" in addon
    for rel in ["README.md", "reference.md", "web-references.md"]:
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 18" in text
        assert "Unified TV + AVR playback sequencing" in text
    assert (ROOT / "BUILD_NOTES_v2.9.10_BUILD16.md").exists() or (
        ROOT / "docs" / "release-history" / "BUILD_NOTES_v2.9.10_BUILD16.md"
    ).exists()
    assert (ROOT / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD16.md").exists() or (
        ROOT / "docs" / "release-history" / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD16.md"
    ).exists()


def test_build16_avr_diagnostics_edge_paths_are_nonfatal_and_redacted():
    invalid = avr_diagnostics.run_query_only_test(
        {"avr_control_enabled": "true", "avr_backend": "unknown"}, "input"
    )
    assert invalid["ok"] is False
    assert invalid["nonfatal"] is True
    assert invalid["hardware_validation_claimed"] is False

    class BrokenController:
        def query_input(self):
            raise RuntimeError("boom supersecretpsk")

    settings = _sony_settings(avr_backend="sony_audio_api")
    result = avr_diagnostics.run_query_only_test(settings, "input", controller=BrokenController())
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert "supersecretpsk" not in str(result)


def test_build16_sanitizer_and_mapping_edge_paths_for_coverage(tmp_path):
    class DataObj:
        data = {"sony_avr_psk": "tiny", "raw_response": "tiny"}

    class BrokenItems:
        def items(self):
            raise TypeError("broken")

    assert avr_diagnostics._settings_dict(None) == {}
    assert avr_diagnostics._settings_dict(DataObj()) == {
        "sony_avr_psk": "tiny",
        "raw_response": "tiny",
    }
    assert avr_diagnostics._settings_dict(BrokenItems()) == {}
    assert avr_diagnostics.redact_value("") == ""
    assert avr_diagnostics.redact_value("short") == "<redacted>"
    assert (
        avr_diagnostics.sanitize_payload(
            {"stdout": "", "items": ["tiny", {"api_key": "abcdefghi"}]}, DataObj()
        )["stdout"]
        == ""
    )
    assert avr_diagnostics.sanitize_text(None) == ""
    assert (
        avr_diagnostics.dry_run_avr_action({"avr_control_enabled": "false"}, "power_off")[
            "requires_explicit_user_action"
        ]
        is True
    )
    report = {"sony_avr_psk": "supersecret", "message": "supersecret"}
    path = avr_diagnostics.save_report(
        report, str(tmp_path), now=0, settings={"sony_avr_psk": "supersecret"}
    )
    assert Path(path).exists()
    assert "supersecret" not in Path(path).read_text(encoding="utf-8")


def test_build16_query_and_explicit_action_edge_paths_for_coverage(monkeypatch):
    # The controller=None call below exercises the real path
    # (controller_factory -> DenonMarantz send -> socket). A unit test must not
    # perform real network I/O: previously it waited ~3s for a SYN timeout to a
    # dead LAN host. Patch socket.create_connection to refuse instantly so the
    # exact failure-handling path is still covered, deterministically and fast.
    import socket as _socket

    def _refuse_connection(*_args, **_kwargs):
        raise ConnectionRefusedError("connection refused (test)")

    monkeypatch.setattr(_socket, "create_connection", _refuse_connection)

    settings = {
        "avr_control_enabled": "true",
        "avr_backend": "denon_marantz",
        "avr_host": "192.168.1.83",
        "avr_player_input": "BD",
    }

    assert (
        avr_diagnostics._result_to_dict(avr_control.build_nonfatal_result("x", settings))[
            "nonfatal"
        ]
        is True
    )
    assert avr_diagnostics._result_to_dict("plain")["message"] == "plain"

    unavailable = avr_diagnostics.run_query_only_test(settings, "power", controller=None)
    assert unavailable["ok"] is False or unavailable["query_only"] is True

    class NoQuery:
        pass

    missing = avr_diagnostics.run_query_only_test(settings, "input", controller=NoQuery())
    assert missing["ok"] is False
    assert "avr_query_method_unavailable" in missing["warnings"]

    class RaisingQuery:
        def query_input(self):
            raise RuntimeError("boom")

    raised = avr_diagnostics.run_query_only_test(settings, "input", controller=RaisingQuery())
    assert raised["ok"] is False
    assert raised["nonfatal"] is True

    disabled = avr_diagnostics.run_explicit_test_action(
        {"avr_control_enabled": "false"}, "status", explicit_user_action=True
    )
    assert disabled["ok"] is False
    assert "avr_test_action_not_available" in disabled["warnings"]

    class NoAction:
        pass

    no_method = avr_diagnostics.run_explicit_test_action(
        settings, "status", explicit_user_action=True, controller=NoAction()
    )
    assert no_method["ok"] is False
    assert "avr_test_method_unavailable" in no_method["warnings"]

    class RaisingAction:
        def power_on(self):
            raise RuntimeError("boom secret")

    raised_action = avr_diagnostics.run_explicit_test_action(
        settings, "power_on", explicit_user_action=True, controller=RaisingAction()
    )
    assert raised_action["ok"] is False
    assert raised_action["nonfatal"] is True
