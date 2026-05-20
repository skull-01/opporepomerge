"""v2.9.10 Build 16 - TV diagnostics and dry-run validator."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)

import tv_diagnostics  # noqa: E402
from resources.lib import settings_reader, version  # noqa: E402


def _smartthings_settings():
    data = dict(settings_reader.DEFAULTS)
    data.update({
        "tv_backend": "smartthings",
        "smartthings_experimental_acknowledged": "true",
        "smartthings_token": "abcdef1234567890",
        "smartthings_device_id": "device-1",
        "smartthings_oppo_input_id": "HDMI1",
        "smartthings_kodi_input_id": "HDMI2",
        "sony_psk": "sony-secret",
        "custom_oppo_command": "curl --header abcdef1234567890 http://example.invalid",
    })
    return data


def test_build10_validates_selected_backend_without_network_io():
    settings = {
        "tv_backend": "roku_ecp",
        "tv_ip": "192.0.2.60",
        "roku_ecp_port": "8060",
        "roku_oppo_key": "InputHDMI1",
        "roku_kodi_key": "InputHDMI2",
    }
    result = tv_diagnostics.validate_tv_settings(settings)
    assert result["backend"] == "roku_ecp"
    assert result["backend_supported"] is True
    assert result["ok"] is True
    assert result["network_called"] is False
    assert result["hardware_validation_claimed"] is False
    assert result["target_fields"]["oppo"]["configured"] is True


def test_build10_command_preset_missing_command_produces_warning():
    result = tv_diagnostics.validate_tv_settings({"tv_backend": "custom_command", "custom_oppo_command": "", "custom_kodi_command": ""})
    assert result["ok"] is False
    assert "missing_command:oppo" in result["warnings"]
    assert "missing_command:kodi" in result["warnings"]
    assert "custom_oppo_command" in result["missing"]
    assert result["network_called"] is False


def test_build10_dry_run_never_calls_backend_or_exports_secrets():
    settings = _smartthings_settings()
    dry_run = tv_diagnostics.dry_run_selected_backend(settings, "oppo")
    text = json.dumps(dry_run, sort_keys=True)
    assert dry_run["backend"] == "smartthings"
    assert dry_run["target"] == "oppo"
    assert dry_run["target_setting"] == "smartthings_oppo_input_id"
    assert dry_run["network_called"] is False
    assert dry_run["dry_run_only"] is True
    assert dry_run["hardware_validation_claimed"] is False
    assert "abcdef1234567890" not in text
    assert "sony-secret" not in text


def test_build10_report_export_is_sanitized_and_states_no_hardware_claim():
    settings = _smartthings_settings()
    report = tv_diagnostics.build_diagnostic_report(settings)
    rendered = tv_diagnostics.format_report(report)
    assert "OPPO203 TV Switching Diagnostic Report" in rendered
    assert '"hardware_validation_claimed": false' in rendered
    assert '"network_called": false' in rendered
    assert "abcdef1234567890" not in rendered
    assert "sony-secret" not in rendered
    assert "curl --header" not in rendered
    assert "smartthings_token" in rendered
    assert "abcd...90" in rendered


def test_build10_explicit_switch_actions_are_nonfatal_and_sanitized():
    settings = _smartthings_settings()

    def failing_switcher(_settings):
        raise RuntimeError("failure with abcdef1234567890 and sony-secret")

    result = tv_diagnostics.test_switch_to_oppo(settings, switcher=failing_switcher)
    assert result["action"] == "switch_to_oppo"
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["hardware_validation_claimed"] is False
    assert "abcdef1234567890" not in str(result)
    assert "sony-secret" not in str(result)

    result_ok = tv_diagnostics.test_switch_to_kodi(settings, switcher=lambda _settings: {"stdout": "abcdef1234567890"})
    assert result_ok["ok"] is True
    assert result_ok["result"]["stdout"] == "<redacted>"


def test_build10_save_report_uses_writer_and_default_name():
    calls = []
    path = tv_diagnostics.export_tv_diagnostic_report(
        {"tv_backend": "adb", "oppo_input_adb_shell": "am start", "kodi_input_adb_shell": "am start"},
        "/tmp/addon-data",
        now=0,
        writer=lambda output_path, text: calls.append((output_path, text)),
    )
    assert path.endswith("tv-diagnostics-19700101-000000.json")
    assert calls and calls[0][0] == path
    assert '"backend": "adb"' in calls[0][1]
    assert '"hardware_validation_claimed": false' in calls[0][1]


def test_build10_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.10 Final"
    assert version.BUILD_NUMBER == 19
    for rel in ("addon.xml", "README.md", "reference.md", "web-references.md"):
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 11" in text
        assert "TV diagnostics" in text


def test_build10_settings_object_and_edge_validation_paths(tmp_path):
    class WithData:
        data = {"tv_backend": "adb", "oppo_input_adb_shell": "am start", "kodi_input_adb_shell": "am start"}

    class BadItems:
        def items(self):
            raise RuntimeError("items failed")

    assert tv_diagnostics.selected_backend_id(None) == "adb"
    assert tv_diagnostics.selected_backend_id(WithData()) == "adb"
    assert tv_diagnostics.sanitize_text("abc", BadItems()) == "abc"
    assert tv_diagnostics.validate_tv_settings({"tv_backend": "does_not_exist"})["warnings"] == ["tv_backend_unsupported"]

    adb_missing = tv_diagnostics.validate_tv_settings({"tv_backend": "adb", "oppo_input_adb_shell": "", "kodi_input_adb_shell": ""})
    assert "missing_oppo_target_setting" in adb_missing["warnings"]
    assert "missing_kodi_target_setting" in adb_missing["warnings"]

    sony_missing = tv_diagnostics.validate_tv_settings({"tv_backend": "sony_bravia", "sony_oppo_hdmi_port": "1", "sony_kodi_hdmi_port": "2"})
    assert "tv_ip_missing" in sony_missing["warnings"]
    assert "sony_psk_missing" in sony_missing["warnings"]

    report = tv_diagnostics.build_diagnostic_report({"tv_backend": "adb", "oppo_input_adb_shell": "am start", "kodi_input_adb_shell": "am start"})
    output = tv_diagnostics.save_report(report, str(tmp_path), now=0)
    assert Path(output).exists()
    assert "hardware_validation_claimed" in Path(output).read_text(encoding="utf-8")
