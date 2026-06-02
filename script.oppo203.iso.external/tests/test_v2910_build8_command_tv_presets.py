"""v2.9.10 Build 16 - command/custom TV preset polish."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file

LIB = ROOT / "resources" / "lib"
for path in (ROOT, LIB):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import tv_presets  # noqa: E402
from tv_backends import (  # noqa: E402
    TV_BACKEND_CUSTOM_COMMAND,
    TV_BACKEND_LG_COMMAND,
    TV_BACKEND_SAMSUNG_COMMAND,
)

from resources.lib import version  # noqa: E402

REQUIRED_COMMAND_PRESETS = {
    "lg_webos_command": TV_BACKEND_LG_COMMAND,
    "samsung_command": TV_BACKEND_SAMSUNG_COMMAND,
    "panasonic_custom_command": TV_BACKEND_CUSTOM_COMMAND,
    "vizio_custom_command": TV_BACKEND_CUSTOM_COMMAND,
    "generic_custom_command": TV_BACKEND_CUSTOM_COMMAND,
}


def test_command_tv_preset_ids_are_present_and_stable():
    assert set(tv_presets.list_command_tv_presets()) == set(REQUIRED_COMMAND_PRESETS)
    assert set(REQUIRED_COMMAND_PRESETS).issubset(set(tv_presets.list_presets()))


def test_command_tv_presets_use_expected_existing_backends_only():
    for preset_id, backend in REQUIRED_COMMAND_PRESETS.items():
        preset = tv_presets.get_preset(preset_id)
        assert preset["backend"] == backend
        assert preset["editable"] is True
        assert preset["software_preset_only"] is True
        assert preset["hardware_validation_claimed"] is False
        assert preset["native_protocol_added"] is False
        assert preset["nonfatal_in_playback_flow"] is True


def test_command_tv_presets_preserve_editable_command_template_behavior():
    for preset in tv_presets.command_tv_support_matrix():
        assert preset["command_template_editable"] is True
        assert preset["tv_ip_placeholder_supported"] is True
        assert preset["missing_command_validation_warning"] is True
        fields = preset["command_fields"]
        assert isinstance(fields, tuple)
        assert len(fields) == 2
        assert all(field.endswith("_command") for field in fields)


def test_command_presets_are_backend_filterable():
    assert "lg_webos_command" in tv_presets.presets_for_backend(TV_BACKEND_LG_COMMAND)
    assert "samsung_command" in tv_presets.presets_for_backend(TV_BACKEND_SAMSUNG_COMMAND)
    custom_ids = set(tv_presets.presets_for_backend(TV_BACKEND_CUSTOM_COMMAND))
    assert {"panasonic_custom_command", "vizio_custom_command", "generic_custom_command"}.issubset(
        custom_ids
    )


def test_preset_registry_validates_command_tv_polish_without_warnings():
    warnings = tv_presets.validate_preset_registry()
    assert warnings == []
    summary = tv_presets.preset_registry_summary()
    assert summary["command_tv_preset_count"] == len(REQUIRED_COMMAND_PRESETS)
    assert set(summary["command_tv_preset_ids"]) == set(REQUIRED_COMMAND_PRESETS)
    assert summary["hardware_validation_claimed"] is False


def test_build8_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.14 Final"
    assert version.BUILD_NUMBER == 23
    for rel in ("addon.xml", "README.md", "reference.md", "web-references.md"):
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 11" in text
        assert (
            "Command TV preset polish" in text
            or "command TV preset polish" in text
            or "command/custom TV preset" in text
        )


def test_build8_preserves_prior_tv_preset_layers():
    assert set(tv_presets.list_android_google_tv_presets()).issubset(set(tv_presets.list_presets()))
    assert set(tv_presets.list_roku_tv_presets()).issubset(set(tv_presets.list_presets()))
    assert tv_presets.preset_registry_summary()["universal_hdmi_command_claimed"] is False
