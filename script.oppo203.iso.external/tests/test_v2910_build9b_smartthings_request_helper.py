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


class FakeResponse:
    def __init__(self, status=200, body='{"ok":true}'):
        self.status = status
        self._body = body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


def _ack_settings():
    settings = dict(settings_reader.DEFAULTS)
    settings.update(
        {
            "tv_backend": "smartthings",
            "smartthings_experimental_acknowledged": "true",
            "smartthings_token": "abcdef1234567890",
            "smartthings_device_id": "device/with spaces",
            "smartthings_oppo_input_id": "HDMI1",
            "smartthings_kodi_input_id": "HDMI2",
            "smartthings_api_base_url": "https://example.invalid/v1",
        }
    )
    return settings


def test_smartthings_request_helper_requires_ack_before_network_call():
    calls = []

    def opener(*args, **kwargs):
        calls.append(args)
        return FakeResponse()

    result = tv_smartthings_control.switch_input(
        {"smartthings_token": "abcdef1234567890", "smartthings_device_id": "device-1"},
        "HDMI1",
        opener=opener,
    )
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["network_called"] is False
    assert result["error_code"] == "experimental_acknowledgement_required"
    assert calls == []
    assert "abcdef1234567890" not in str(result)


def test_smartthings_request_helper_posts_sanitized_fake_api_request():
    captured = {}

    def opener(request, timeout=0):
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["body"] = request.data.decode("utf-8")
        captured["authorization"] = request.headers.get("Authorization")
        captured["timeout"] = timeout
        return FakeResponse(200, '{"status":"ACCEPTED"}')

    settings = _ack_settings()
    result = tv_smartthings_control.switch_input(settings, "HDMI1", opener=opener, timeout=3)
    assert result["ok"] is True
    assert result["nonfatal"] is True
    assert result["network_called"] is True
    assert result["status_code"] == 200
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/devices/device%2Fwith%20spaces/commands")
    assert '"command":"setInputSource"' in captured["body"]
    assert '"HDMI1"' in captured["body"]
    assert captured["authorization"] == "Bearer abcdef1234567890"
    assert captured["timeout"] == 3
    assert "abcdef1234567890" not in str(result)
    assert result["token_redacted"] == "abcd...90"


def test_smartthings_request_helper_handles_401_403_without_leaking_token():
    import urllib.error

    def opener(request, timeout=0):
        raise urllib.error.HTTPError(
            request.full_url, 403, "Forbidden abcdef1234567890", hdrs=None, fp=None
        )

    settings = _ack_settings()
    result = tv_smartthings_control.switch_input(settings, "HDMI1", opener=opener)
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["network_called"] is True
    assert result["status_code"] == 403
    assert result["error_code"] == "smartthings_auth_failed"
    assert "abcdef1234567890" not in str(result)
    assert "<redacted>" in str(result)


def test_tv_control_uses_guarded_smartthings_helper_nonfatally_without_ack():
    settings = _ack_settings()
    settings["smartthings_experimental_acknowledged"] = "false"
    result = tv_control.switch_to_oppo(settings)
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["network_called"] is False
    assert result["error_code"] == "experimental_acknowledgement_required"
    assert result["hardware_validation_claimed"] is False
    assert "abcdef1234567890" not in str(result)


def test_build10_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.17 Final"
    assert version.BUILD_NUMBER == 26
    for rel in ("addon.xml", "README.md", "reference.md", "web-references.md"):
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 11" in text
        assert "SmartThings experimental" in text


def test_smartthings_helper_validation_failure_paths_are_nonfatal_and_sanitized():
    acknowledged = {"smartthings_experimental_acknowledged": "true"}
    assert tv_smartthings_control.is_acknowledged(object()) is False
    assert tv_smartthings_control.redact_token(None) == ""
    assert tv_smartthings_control.redact_secret_in_text(None, None) == ""
    assert tv_smartthings_control.sanitized_settings({"other": "ok"}) == {"other": "ok"}

    missing_token = tv_smartthings_control.switch_input(
        {**acknowledged, "smartthings_device_id": "device-1"}, "HDMI1"
    )
    assert missing_token["error_code"] == "smartthings_token_missing"
    assert missing_token["network_called"] is False

    missing_device = tv_smartthings_control.switch_input(
        {**acknowledged, "smartthings_token": "abcdef1234567890"}, "HDMI1"
    )
    assert missing_device["error_code"] == "smartthings_device_id_missing"
    assert "abcdef1234567890" not in str(missing_device)

    missing_input = tv_smartthings_control.switch_input(
        {
            **acknowledged,
            "smartthings_token": "abcdef1234567890",
            "smartthings_device_id": "device-1",
        },
        "",
    )
    assert missing_input["error_code"] == "smartthings_input_id_missing"
    assert "abcdef1234567890" not in str(missing_input)


def test_smartthings_request_helper_handles_non_auth_http_network_and_target_paths():
    import urllib.error

    settings = _ack_settings()

    result_202 = tv_smartthings_control.switch_target(
        settings, "kodi", opener=lambda request, timeout=0: FakeResponse(202, '{"status":"queued"}')
    )
    assert result_202["ok"] is True
    assert result_202["status_code"] == 202

    result_500 = tv_smartthings_control.switch_input(
        settings,
        "HDMI1",
        opener=lambda request, timeout=0: FakeResponse(500, "server error abcdef1234567890"),
    )
    assert result_500["ok"] is False
    assert result_500["error_code"] == "smartthings_http_error"
    assert "abcdef1234567890" not in str(result_500)

    def http_500(request, timeout=0):
        raise urllib.error.HTTPError(
            request.full_url, 500, "Server abcdef1234567890", hdrs=None, fp=None
        )

    result_http_error = tv_smartthings_control.switch_input(settings, "HDMI1", opener=http_500)
    assert result_http_error["error_code"] == "smartthings_http_error"
    assert result_http_error["status_code"] == 500
    assert "abcdef1234567890" not in str(result_http_error)

    def url_error(request, timeout=0):
        raise urllib.error.URLError("network abcdef1234567890")

    result_url_error = tv_smartthings_control.switch_input(settings, "HDMI1", opener=url_error)
    assert result_url_error["error_code"] == "smartthings_network_error"
    assert "abcdef1234567890" not in str(result_url_error)


def test_tv_control_smartthings_acknowledged_path_still_returns_nonfatal_result_without_credentials():
    settings = dict(settings_reader.DEFAULTS)
    settings["tv_backend"] = "smartthings"
    settings["smartthings_experimental_acknowledged"] = "true"
    result = tv_control.switch_to_kodi(settings)
    assert result["ok"] is False
    assert result["nonfatal"] is True
    assert result["error_code"] == "smartthings_token_missing"


def test_smartthings_and_command_registry_warning_branches_are_covered():
    original = tv_presets.TV_PRESETS["samsung_smartthings_experimental"]
    mutated = dict(original)
    mutated.update(
        {
            "backend": "adb",
            "experimental": False,
            "requires_explicit_acknowledgement": False,
            "live_api_calls_enabled": False,
            "request_helper_available": False,
            "token_redaction_required": False,
        }
    )
    tv_presets.TV_PRESETS["samsung_smartthings_experimental"] = mutated
    try:
        warnings = tv_presets.validate_preset_registry()
        assert any("smartthings_not_smartthings_backend" in item for item in warnings)
        assert any("smartthings_not_experimental" in item for item in warnings)
        assert any("smartthings_acknowledgement_not_required" in item for item in warnings)
        assert any("smartthings_live_api_disabled_in_9b" in item for item in warnings)
        assert any("smartthings_request_helper_unavailable" in item for item in warnings)
        assert any("smartthings_token_redaction_not_required" in item for item in warnings)
    finally:
        tv_presets.TV_PRESETS["samsung_smartthings_experimental"] = original

    original_command = tv_presets.TV_PRESETS["generic_custom_command"]
    mutated_command = dict(original_command)
    mutated_command.update(
        {
            "backend": "adb",
            "command_template_editable": False,
            "missing_command_validation_warning": False,
            "native_protocol_added": True,
        }
    )
    tv_presets.TV_PRESETS["generic_custom_command"] = mutated_command
    try:
        warnings = tv_presets.validate_preset_registry()
        assert any("command_tv_unexpected_backend" in item for item in warnings)
        assert any("command_template_not_editable" in item for item in warnings)
        assert any("missing_command_warning_absent" in item for item in warnings)
        assert any("native_protocol_added" in item for item in warnings)
    finally:
        tv_presets.TV_PRESETS["generic_custom_command"] = original_command
