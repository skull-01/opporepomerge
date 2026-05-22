"""v2.9.10 Build 16 - Sony AVR experimental request helper."""
from __future__ import annotations

from pathlib import Path

from resources.lib import avr_control, avr_presets, avr_sony_audio, settings_reader, version

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


def test_build16_sony_defaults_and_settings_placeholders_are_safe():
    defaults = settings_reader.DEFAULTS
    assert defaults["avr_control_enabled"] == "false"
    assert defaults["avr_power_off_enabled"] == "false"
    assert defaults["avr_volume_automation_enabled"] == "false"
    assert defaults["sony_avr_experimental_acknowledged"] == "false"
    assert defaults["sony_avr_psk"] == ""
    assert defaults["sony_avr_api_path"] == "/sony/audio"
    assert defaults["sony_avr_player_input_uri"] == ""
    assert defaults["sony_avr_restore_input_uri"] == ""

    xml = (ROOT / "resources" / "settings.xml").read_text(encoding="utf-8")
    for key in (
        "sony_avr_experimental_acknowledged",
        "sony_avr_psk",
        "sony_avr_api_path",
        "sony_avr_player_input_uri",
        "sony_avr_restore_input_uri",
    ):
        assert f'id="{key}"' in xml


def test_build16_sony_preset_is_experimental_skeleton_only():
    sony = avr_presets.get_avr_preset("sony_audio_api")
    assert sony["backend"] == "sony_audio_api"
    assert sony["software_support_level"] == "experimental_request_helper_build15b"
    assert sony["driver_available"] is True
    assert sony["skeleton_available"] is True
    assert sony["live_api_calls_enabled"] is True
    assert sony["requires_experimental_acknowledgement"] is True
    assert sony["hardware_validation_claimed"] is False

    summary = avr_presets.avr_support_summary()
    assert summary["driver_execution_families"] == (
        "denon_marantz", "yamaha_yxc", "onkyo_eiscp", "pioneer_eiscp", "sony_audio_api"
    )
    assert summary["experimental_skeleton_families"] == ()
    assert summary["experimental_request_helper_families"] == ("sony_audio_api",)
    assert summary["playback_sequencing_hooked"] is True
    assert summary["hardware_validation_claimed"] is False


def test_build16_sony_acknowledgement_gate_and_validation_metadata():
    settings = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "sony_audio_api",
        "avr_host": "192.168.1.101",
        "avr_player_input": "extInput:hdmi?port=1",
        "sony_avr_psk": "topsecretpsk",
        "sony_avr_player_input_uri": "extInput:hdmi?port=1",
    })
    meta = avr_sony_audio.validation_metadata(settings).copy()
    assert meta["acknowledged"] is False
    assert meta["live_api_calls_enabled"] is True
    assert meta["request_helper_available"] is True
    assert meta["driver_available"] is True
    assert meta["psk_redacted"] == "top...sk"
    assert "sony_audio_api_experimental_acknowledgement_required" in meta["warnings"]
    assert meta["hardware_validation_claimed"] is False

    acknowledged = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "sony_audio_api",
        "avr_host": "192.168.1.101",
        "avr_player_input": "extInput:hdmi?port=1",
        "sony_avr_experimental_acknowledged": "true",
        "sony_avr_psk": "topsecretpsk",
        "sony_avr_player_input_uri": "extInput:hdmi?port=1",
    })
    meta = avr_sony_audio.validation_metadata(acknowledged)
    assert meta["acknowledged"] is True
    assert meta["warnings"] == ()
    assert meta["missing"] == ()


def test_build16_validate_avr_settings_accepts_guarded_sony_helper():
    settings = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "sony_audio_api",
        "avr_host": "192.168.1.102",
        "avr_player_input": "extInput:hdmi?port=1",
        "sony_avr_experimental_acknowledged": "true",
        "sony_avr_psk": "topsecretpsk",
        "sony_avr_player_input_uri": "extInput:hdmi?port=1",
    })
    validation = avr_control.validate_avr_settings(settings).as_dict()
    assert validation["ok"] is True
    assert validation["driver_available"] is True
    assert validation["missing"] == ()
    assert "sony_audio_api_live_calls_not_implemented_build15b" not in validation["warnings"]
    assert "avr_driver_not_implemented_build11" not in validation["warnings"]
    assert validation["hardware_validation_claimed"] is False
    assert avr_control.controller_factory(settings) is not None


def test_build16_sony_refusal_result_never_sends_commands():
    settings = {
        "avr_backend": "sony_audio_api",
        "avr_host": "192.168.1.103",
        "avr_player_input": "extInput:hdmi?port=1",
        "sony_avr_psk": "secretpsk",
    }
    result = avr_sony_audio.build_refusal_result("power_on", settings).as_dict()
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["command_sent"] is False
    assert result["backend"] == "sony_audio_api"
    assert "sony_audio_api_refused_without_acknowledgement" in result["warnings"]
    assert result["hardware_validation_claimed"] is False

    controller = avr_sony_audio.SonyAudioApiAvrController(settings)
    assert controller.power_on().as_dict()["command_sent"] is False
    assert controller.select_input().as_dict()["command_sent"] is False


def test_build16_sony_sanitizers_do_not_export_psk_or_secrets():
    settings = {
        "sony_avr_psk": "supersecretpsk",
        "sony_avr_player_input_uri": "extInput:hdmi?port=1",
        "sony_password": "password123",
        "note": "use supersecretpsk but never leak password123",
    }
    sanitized = avr_sony_audio.sanitized_settings(settings)
    assert sanitized["sony_avr_psk"] != "supersecretpsk"
    assert sanitized["sony_password"] != "password123"
    assert "supersecretpsk" not in sanitized["note"]
    assert "password123" not in sanitized["note"]
    assert avr_sony_audio.SONY_SECRET_REDACTION in sanitized["note"]


def test_build16_existing_avr_drivers_and_defaults_remain_preserved():
    for backend in ("denon_marantz", "yamaha_yxc", "onkyo_eiscp", "pioneer_eiscp", "sony_audio_api"):
        preset = avr_presets.get_avr_preset(backend)
        assert preset["driver_available"] is True
        assert preset["hardware_validation_claimed"] is False

    disabled = settings_reader.Settings({})
    assert avr_control.controller_factory(disabled) is None
    assert avr_control.avr_settings_summary(disabled)["sony_live_api_calls_enabled"] is True
    assert avr_control.avr_settings_summary(disabled)["playback_sequencing_hooked"] is True


def test_build16_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.12 Final"
    assert version.BUILD_NUMBER == 21
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 18" in addon
    assert "Sony AVR experimental request helper" in addon
    assert (ROOT / "resources/lib/avr_sony_audio.py").exists()
    for rel in ["README.md", "reference.md", "web-references.md"]:
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 18" in text
        assert "Sony AVR experimental request helper" in text
    assert (ROOT / "BUILD_NOTES_v2.9.10_BUILD16.md").exists() or (ROOT / "docs" / "release-history" / "BUILD_NOTES_v2.9.10_BUILD16.md").exists()
    assert (ROOT / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD16.md").exists() or (ROOT / "docs" / "release-history" / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD16.md").exists()


def test_build16_sony_edge_paths_raise_no_secrets_or_commands():
    class ItemsLike:
        def items(self):
            return [
                ("sony_avr_experimental_acknowledged", True),
                ("sony_avr_psk", "xy"),
                ("avr_host", "sony.local"),
                ("avr_player_input", "fallback-uri"),
            ]

    class BrokenItems:
        def items(self):
            raise TypeError("broken")

    assert avr_sony_audio.validation_metadata(None)["missing"] == (
        "avr_host", "sony_avr_player_input_uri", "sony_avr_psk"
    )
    assert avr_sony_audio.is_experimental_acknowledged(ItemsLike()) is True
    assert avr_sony_audio.redact_secret("xy") == avr_sony_audio.SONY_SECRET_REDACTION
    assert avr_sony_audio.redact_secret("") == ""
    assert avr_sony_audio.validation_metadata(BrokenItems())["host_configured"] is False
    sanitized = avr_sony_audio.sanitized_settings({"plain": 123, "secret_token": None})
    assert sanitized["plain"] == 123
    assert sanitized["secret_token"] == ""
    custom = avr_sony_audio.build_refusal_result(
        "restore", {"sony_avr_experimental_acknowledged": "true"}, message="custom refusal"
    ).as_dict()
    assert custom["message"] == "custom refusal"
    assert custom["command_sent"] is False
