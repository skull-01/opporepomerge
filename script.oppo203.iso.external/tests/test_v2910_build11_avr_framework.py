"""v2.9.10 Build 16 - AVR framework and settings skeleton."""
from __future__ import annotations

from pathlib import Path

from resources.lib import avr_control, avr_presets, avr_types, settings_reader, version

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


def test_build11_avr_defaults_are_disabled_and_safe():
    defaults = settings_reader.DEFAULTS
    assert defaults["avr_control_enabled"] == "false"
    assert defaults["avr_backend"] == "disabled"
    assert defaults["avr_power_off_enabled"] == "false"
    assert defaults["avr_volume_automation_enabled"] == "false"
    assert defaults["avr_power_on_enabled"] == "false"
    assert "avr_backend" in settings_reader.ENUM_VALUES
    assert settings_reader.ENUM_VALUES["avr_backend"] == [
        "disabled",
        "denon_marantz",
        "yamaha_yxc",
        "onkyo_eiscp",
        "pioneer_eiscp",
        "sony_audio_api",
    ]


def test_build11_controller_factory_returns_none_when_disabled():
    settings = settings_reader.Settings({})
    assert avr_control.avr_enabled(settings) is False
    assert avr_control.controller_factory(settings) is None
    validation = avr_control.validate_avr_settings(settings).as_dict()
    assert validation["ok"] is True
    assert validation["enabled"] is False
    assert validation["backend"] == "disabled"
    assert validation["driver_available"] is False
    assert validation["hardware_validation_claimed"] is False
    assert "avr_control_disabled" in validation["warnings"]


def test_build11_incomplete_enabled_config_is_rejected_safely():
    settings = settings_reader.Settings({"avr_control_enabled": "true", "avr_backend": "denon_marantz"})
    validation = avr_control.validate_avr_settings(settings).as_dict()
    assert validation["ok"] is False
    assert validation["enabled"] is True
    assert validation["backend"] == "denon_marantz"
    assert validation["missing"] == ("avr_host", "avr_player_input")
    assert "avr_config_incomplete" in validation["warnings"]
    assert "avr_driver_not_implemented_build11" not in validation["warnings"]
    assert validation["hardware_validation_claimed"] is False
    assert avr_control.controller_factory(settings) is None


def test_build11_complete_yamaha_config_now_uses_build13_driver_without_playback_hook():
    settings = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "yamaha_yxc",
        "avr_host": "192.168.1.70",
        "avr_port": "80",
        "avr_player_input": "hdmi1",
    })
    validation = avr_control.validate_avr_settings(settings).as_dict()
    assert validation["ok"] is True
    assert validation["missing"] == ()
    assert validation["driver_available"] is True
    assert "avr_driver_not_implemented_build11" not in validation["warnings"]
    assert avr_control.controller_factory(settings) is not None
    result = avr_control.build_nonfatal_result("power_on", settings).as_dict()
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["command_sent"] is False
    assert result["hardware_validation_claimed"] is False


def test_build11_avr_presets_are_metadata_only():
    summary = avr_presets.avr_support_summary()
    assert summary["enabled_by_default"] is False
    assert summary["power_off_enabled_by_default"] is False
    assert summary["volume_automation_enabled_by_default"] is False
    assert summary["driver_execution_added"] is True
    assert summary["playback_sequencing_hooked"] is True
    assert summary["hardware_validation_claimed"] is False
    expected = {"disabled", "denon_marantz", "yamaha_yxc", "onkyo_eiscp", "pioneer_eiscp", "sony_audio_api", "sony_audio_api"}
    assert set(avr_presets.list_avr_presets()) == expected
    for preset_id in expected:
        preset = avr_presets.get_avr_preset(preset_id)
        assert preset["backend"] == avr_presets.normalize_avr_backend(preset_id)
        if preset_id in {"denon_marantz", "yamaha_yxc", "onkyo_eiscp", "pioneer_eiscp", "sony_audio_api"}:
            assert preset["driver_available"] is True
        else:
            assert preset["driver_available"] is False
        assert preset["hardware_validation_claimed"] is False


def test_build11_noop_controller_is_explicit_and_non_commanding():
    settings = {
        "avr_control_enabled": "true",
        "avr_backend": "denon_marantz",
        "avr_host": "192.168.1.71",
        "avr_player_input": "BD",
    }
    controller = avr_control.controller_factory(settings, allow_noop=True)
    assert controller is not None
    result = controller.run("input_select").as_dict()
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["command_sent"] is False
    assert result["backend"] == "denon_marantz"
    assert result["hardware_validation_claimed"] is False


def test_build11_settings_schema_and_xml_include_avr_without_visible_enablement_regression():
    settings = settings_reader.Settings({"avr_backend": "not_real", "avr_control_enabled": "maybe"})
    issues = settings.schema_issues()
    issue_codes = {(issue.key, issue.code) for issue in issues}
    assert ("avr_backend", "invalid_choice") in issue_codes
    assert ("avr_control_enabled", "invalid_bool") in issue_codes
    xml = (ROOT / "resources" / "settings.xml").read_text(encoding="utf-8")
    for key in ("avr_control_enabled", "avr_backend", "avr_power_off_enabled", "avr_volume_automation_enabled"):
        assert f'id="{key}"' in xml
    assert 'id="avr_power_off_enabled" type="bool" label="30255" default="false"' in xml
    assert 'id="avr_volume_automation_enabled" type="bool" label="30257" default="false"' in xml


def test_build11_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.12 Final"
    assert version.BUILD_NUMBER == 21
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 11" in addon
    for rel in ["README.md", "reference.md", "web-references.md"]:
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 11" in text
        assert "AVR framework and settings skeleton" in text
    assert (ROOT / "BUILD_NOTES_v2.9.10_BUILD11.md").exists() or (ROOT / "docs" / "release-history" / "BUILD_NOTES_v2.9.10_BUILD11.md").exists()
    assert (ROOT / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD11.md").exists() or (ROOT / "docs" / "release-history" / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD11.md").exists()


def test_build11_avr_edge_paths_cover_mapping_and_truthy_variants():
    class MappingLike:
        def items(self):
            return [("avr_control_enabled", True), ("avr_backend", "pioneer"), ("avr_host", "1.2.3.4"), ("avr_player_input", "BD")]

    class BrokenItems:
        def items(self):
            raise TypeError("broken")

    summary = avr_control.avr_settings_summary(MappingLike())
    assert summary["avr_control_enabled"] is True
    assert summary["avr_backend"] == "pioneer_eiscp"
    assert summary["avr_host_configured"] is True
    assert summary["avr_player_input_configured"] is True
    assert summary["avr_power_off_enabled"] is False
    assert summary["avr_volume_automation_enabled"] is False

    assert avr_control.selected_avr_backend(None) == "disabled"
    assert avr_control.validate_avr_settings(BrokenItems()).as_dict()["backend"] == "disabled"
    assert avr_control.avr_enabled({"avr_control_enabled": True}) is True
    assert avr_control.avr_enabled({"avr_control_enabled": ""}) is False


def test_build11_invalid_backend_and_custom_message_are_nonfatal():
    settings = {
        "avr_control_enabled": "true",
        "avr_backend": "not_a_backend",
        "avr_host": "192.168.1.90",
        "avr_player_input": "BD",
    }
    validation = avr_control.validate_avr_settings(settings).as_dict()
    assert validation["missing"] == ("avr_backend",)
    assert "avr_backend_invalid_or_disabled" in validation["warnings"]
    assert "avr_config_incomplete" in validation["warnings"]
    result = avr_control.build_nonfatal_result("restore", settings, message="manual warning").as_dict()
    assert result["message"] == "manual warning"
    assert "manual warning" in result["warnings"]
    assert result["command_sent"] is False
    assert avr_presets.get_avr_preset("unknown", default={"id": "fallback"}) == {"id": "fallback"}
