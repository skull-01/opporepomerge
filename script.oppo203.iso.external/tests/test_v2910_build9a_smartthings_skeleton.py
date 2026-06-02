"""v2.9.10 Build 16 - SmartThings experimental settings skeleton."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file

LIB = ROOT / "resources" / "lib"
for path in (ROOT, LIB):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import tv_control  # noqa: E402
import tv_presets  # noqa: E402
import tv_smartthings_control  # noqa: E402
from tv_backends import (  # noqa: E402
    TV_BACKEND_SMARTTHINGS,
    backend_target_setting,
    get_backend,
    is_supported_backend,
    list_backends,
    normalize_backend_id,
)

from resources.lib import settings_reader, version  # noqa: E402

REQUIRED_SMARTTHINGS_PRESETS = {
    "samsung_smartthings_experimental",
    "generic_smartthings_experimental",
}


def test_smartthings_backend_metadata_is_registered_but_experimental_only():
    assert TV_BACKEND_SMARTTHINGS == "smartthings"
    assert TV_BACKEND_SMARTTHINGS in list_backends()
    assert normalize_backend_id("samsung_smartthings") == TV_BACKEND_SMARTTHINGS
    assert normalize_backend_id("smartthings_experimental") == TV_BACKEND_SMARTTHINGS
    assert is_supported_backend(TV_BACKEND_SMARTTHINGS) is True

    backend = get_backend(TV_BACKEND_SMARTTHINGS)
    assert backend["experimental"] is True
    assert backend["requires_explicit_acknowledgement"] is True
    assert backend["live_api_calls_enabled"] is True
    assert backend["token_redaction_required"] is True
    assert backend["nonfatal_in_playback_flow"] is True
    assert backend_target_setting(TV_BACKEND_SMARTTHINGS, "oppo") == "smartthings_oppo_input_id"
    assert backend_target_setting(TV_BACKEND_SMARTTHINGS, "kodi") == "smartthings_kodi_input_id"


def test_smartthings_presets_are_metadata_only_and_ack_gated():
    assert set(tv_presets.list_smartthings_experimental_presets()) == REQUIRED_SMARTTHINGS_PRESETS
    for preset in tv_presets.smartthings_experimental_support_matrix():
        assert preset["backend"] == TV_BACKEND_SMARTTHINGS
        assert preset["experimental"] is True
        assert preset["software_preset_only"] is True
        assert preset["requires_explicit_acknowledgement"] is True
        assert preset["live_api_calls_enabled"] is True
        assert preset["token_redaction_required"] is True
        assert preset["hardware_validation_claimed"] is False
        assert preset["nonfatal_in_playback_flow"] is True


def test_smartthings_registry_validation_has_no_warnings():
    assert tv_presets.validate_preset_registry() == []
    summary = tv_presets.preset_registry_summary()
    assert summary["smartthings_experimental_preset_count"] == len(REQUIRED_SMARTTHINGS_PRESETS)
    assert set(summary["smartthings_experimental_preset_ids"]) == REQUIRED_SMARTTHINGS_PRESETS
    assert summary["hardware_validation_claimed"] is False


def test_smartthings_settings_defaults_and_enum_placeholders_exist():
    defaults = settings_reader.DEFAULTS
    assert defaults["smartthings_experimental_acknowledged"] == "false"
    assert defaults["smartthings_token"] == ""
    assert defaults["smartthings_device_id"] == ""
    assert defaults["smartthings_oppo_input_id"] == ""
    assert defaults["smartthings_kodi_input_id"] == ""
    assert "smartthings" in settings_reader.ENUM_VALUES["tv_backend"]

    xml = (ROOT / "resources" / "settings.xml").read_text(encoding="utf-8")
    assert "smartthings_experimental_acknowledged" in xml
    assert "smartthings_token" in xml
    assert "smartthings_device_id" in xml


def test_smartthings_token_redaction_and_validation_metadata_never_expose_token():
    token = "abcdef1234567890"
    assert tv_smartthings_control.redact_token(token) == "abcd...90"
    assert tv_smartthings_control.redact_token("short") == "<redacted>"
    sanitized = tv_smartthings_control.sanitized_settings(
        {"smartthings_token": token, "other": "ok"}
    )
    assert sanitized["smartthings_token"] == "abcd...90"
    assert token not in str(sanitized)

    metadata = tv_smartthings_control.validation_metadata(
        {
            "smartthings_experimental_acknowledged": "true",
            "smartthings_token": token,
            "smartthings_device_id": "device-1",
        }
    )
    assert metadata["acknowledged"] is True
    assert metadata["live_api_calls_enabled"] is True
    assert metadata["token_redacted"] == "abcd...90"
    assert token not in str(metadata)
    assert metadata["warnings"] == ()


def test_smartthings_validation_requires_ack_token_and_device_without_network_io():
    metadata = tv_smartthings_control.validation_metadata({})
    assert metadata["experimental"] is True
    assert metadata["hardware_validation_claimed"] is False
    assert metadata["live_api_calls_enabled"] is True
    assert set(metadata["warnings"]) == {
        "smartthings_experimental_acknowledgement_required",
        "smartthings_token_missing",
        "smartthings_device_id_missing",
    }


def test_tv_control_returns_nonfatal_smartthings_result_without_ack_in_build10():
    settings = dict(settings_reader.DEFAULTS)
    settings["tv_backend"] = "smartthings"
    result = tv_control.switch_to_oppo(settings)
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["network_called"] is False
    assert result["error_code"] == "experimental_acknowledgement_required"


def test_build10_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.14 Final"
    assert version.BUILD_NUMBER == 23
    for rel in ("addon.xml", "README.md", "reference.md", "web-references.md"):
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 11" in text
        assert "SmartThings experimental" in text
