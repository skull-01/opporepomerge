"""v2.9.10 Build 16 - Sony AVR experimental request helper."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError

from resources.lib import avr_control, avr_presets, avr_sony_audio, settings_reader, version

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


def _sony_settings(**overrides):
    data = {
        "avr_control_enabled": "true",
        "avr_backend": "sony_audio_api",
        "avr_host": "192.168.1.120",
        "avr_timeout": "2.5",
        "avr_player_input": "extInput:hdmi?port=1",
        "sony_avr_experimental_acknowledged": "true",
        "sony_avr_psk": "supersecretpsk",
        "sony_avr_api_path": "/sony/audio",
        "sony_avr_player_input_uri": "extInput:hdmi?port=1",
    }
    data.update(overrides)
    return settings_reader.Settings(data)


def test_build16_sony_preset_and_validation_enable_guarded_helper_only():
    sony = avr_presets.get_avr_preset("sony_audio_api")
    assert sony["backend"] == "sony_audio_api"
    assert sony["software_support_level"] == "experimental_request_helper_build15b"
    assert sony["driver_available"] is True
    assert sony["request_helper_available"] is True
    assert sony["requires_experimental_acknowledgement"] is True
    assert sony["hardware_validation_claimed"] is False

    validation = avr_control.validate_avr_settings(_sony_settings()).as_dict()
    assert validation["ok"] is True
    assert validation["driver_available"] is True
    assert validation["hardware_validation_claimed"] is False

    summary = avr_presets.avr_support_summary()
    assert "sony_audio_api" in summary["driver_execution_families"]
    assert summary["experimental_request_helper_families"] == ("sony_audio_api",)
    assert summary["playback_sequencing_hooked"] is True


def test_build16_acknowledgement_required_before_any_request():
    calls = []

    def fake_post(url, payload, headers, timeout):
        calls.append((url, payload, headers, timeout))
        return b'{"result":[]}'

    settings = _sony_settings(sony_avr_experimental_acknowledged="false")
    result = avr_sony_audio.send_sony_audio_request(
        settings, "setPowerStatus", [{"status": "active"}], action="power_on", post=fake_post
    ).as_dict()
    assert result["ok"] is False
    assert result["command_sent"] is False
    assert result["nonfatal"] is True
    assert "sony_audio_api_refused_without_acknowledgement" in result["warnings"]
    assert calls == []


def test_build16_fake_api_post_success_uses_json_and_does_not_export_psk():
    calls = []

    def fake_post(url, payload, headers, timeout):
        calls.append((url, payload, headers, timeout))
        assert url == "http://192.168.1.120/sony/audio"
        assert headers["X-Auth-PSK"] == "supersecretpsk"
        assert headers["Content-Type"].startswith("application/json")
        body = json.loads(payload.decode("utf-8"))
        assert body["method"] == "setPowerStatus"
        assert body["params"] == [{"status": "active"}]
        assert timeout == 2.5
        return b'{"result":[]}'

    controller = avr_control.controller_factory(_sony_settings(), sony_post=fake_post)
    assert controller is not None
    result = controller.power_on().as_dict()
    assert result["ok"] is True
    assert result["command_sent"] is True
    assert result["backend"] == "sony_audio_api"
    assert result["hardware_validation_claimed"] is False
    assert "supersecretpsk" not in str(result)
    assert len(calls) == 1


def test_build16_set_input_and_status_helpers_are_fakeable():
    methods = []

    def fake_post(url, payload, headers, timeout):
        methods.append(json.loads(payload.decode("utf-8"))["method"])
        return '{"status":"ok"}'

    controller = avr_sony_audio.SonyAudioApiAvrController(_sony_settings(), post=fake_post)
    assert controller.select_input().as_dict()["ok"] is True
    assert controller.query_power().as_dict()["ok"] is True
    assert methods == ["setPlayContent", "getPowerStatus"]


def test_build16_http_401_403_and_network_errors_are_nonfatal():
    def fake_401(url, payload, headers, timeout):
        raise HTTPError(url, 401, "Unauthorized", {}, None)

    def fake_timeout(url, payload, headers, timeout):
        raise TimeoutError("boom")

    auth_result = avr_sony_audio.send_sony_audio_request(_sony_settings(), "getPowerStatus", [], post=fake_401).as_dict()
    assert auth_result["ok"] is False
    assert auth_result["command_sent"] is False
    assert auth_result["warnings"] == ("sony_audio_api_auth_error_nonfatal",)
    assert auth_result["nonfatal"] is True

    timeout_result = avr_sony_audio.send_sony_audio_request(_sony_settings(), "getPowerStatus", [], post=fake_timeout).as_dict()
    assert timeout_result["ok"] is False
    assert timeout_result["warnings"] == ("avr_network_error_nonfatal",)
    assert timeout_result["nonfatal"] is True


def test_build16_invalid_json_api_error_and_secret_echo_are_sanitized():
    settings = _sony_settings()

    def invalid_json(url, payload, headers, timeout):
        return "not-json supersecretpsk"

    result = avr_sony_audio.send_sony_audio_request(settings, "getPowerStatus", [], post=invalid_json).as_dict()
    assert result["ok"] is False
    assert result["warnings"] == ("sony_audio_api_invalid_json_nonfatal",)
    assert "supersecretpsk" not in str(result)

    def api_error(url, payload, headers, timeout):
        return json.dumps({"error": "bad supersecretpsk"})

    error_result = avr_sony_audio.send_sony_audio_request(settings, "getPowerStatus", [], post=api_error).as_dict()
    assert error_result["ok"] is False
    assert error_result["warnings"] == ("sony_audio_api_error_nonfatal",)
    assert "supersecretpsk" not in str(error_result)
    assert avr_sony_audio.SONY_SECRET_REDACTION in error_result["message"]


def test_build16_url_payload_validation_and_incomplete_config_are_nonfatal():
    assert avr_sony_audio.build_sony_audio_url("sony.local") == "http://sony.local/sony/audio"
    assert avr_sony_audio.build_sony_audio_url("http://sony.local", "/sony/audio") == "http://sony.local/sony/audio"
    assert json.loads(avr_sony_audio.build_power_on_payload().decode("utf-8"))["method"] == "setPowerStatus"
    assert json.loads(avr_sony_audio.build_set_input_payload("extInput:hdmi?port=1").decode("utf-8"))["method"] == "setPlayContent"
    assert json.loads(avr_sony_audio.build_status_payload().decode("utf-8"))["method"] == "getPowerStatus"

    incomplete = avr_sony_audio.send_sony_audio_request(
        _sony_settings(sony_avr_psk=""), "getPowerStatus", [], post=lambda *a: b'{"result":[]}'
    ).as_dict()
    assert incomplete["ok"] is False
    assert incomplete["command_sent"] is False
    assert "avr_config_incomplete" in incomplete["warnings"]


def test_build16_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.13 Final"
    assert version.BUILD_NUMBER == 22
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 18" in addon
    assert "Sony AVR experimental request helper" in addon
    for rel in ["README.md", "reference.md", "web-references.md"]:
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 18" in text
        assert "Sony AVR experimental request helper" in text
    assert (ROOT / "BUILD_NOTES_v2.9.10_BUILD16.md").exists() or (ROOT / "docs" / "release-history" / "BUILD_NOTES_v2.9.10_BUILD16.md").exists()
    assert (ROOT / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD16.md").exists() or (ROOT / "docs" / "release-history" / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD16.md").exists()


def test_build16_sony_edge_paths_raise_no_secrets_and_remain_nonfatal():
    class UnknownSettings:
        pass

    class BrokenItems:
        def items(self):
            raise TypeError("broken")

    assert avr_sony_audio.validation_metadata(UnknownSettings())["missing"] == (
        "avr_host", "sony_avr_player_input_uri", "sony_avr_psk"
    )
    assert avr_sony_audio.validation_metadata(BrokenItems())["host_configured"] is False
    assert avr_sony_audio.is_experimental_acknowledged({"sony_avr_experimental_acknowledged": ""}) is False
    assert avr_sony_audio.send_sony_audio_request(_sony_settings(avr_timeout="bad"), "getPowerStatus", [], post=lambda *a: "{}").as_dict()["ok"] is True
    assert avr_sony_audio.send_sony_audio_request(_sony_settings(avr_timeout="99"), "getPowerStatus", [], post=lambda *a: "{}").as_dict()["ok"] is True

    for host, path in (("", "/sony/audio"), ("sony.local/path", "/sony/audio"), ("sony.local", "../bad")):
        result = avr_sony_audio.send_sony_audio_request(
            _sony_settings(avr_host=host, sony_avr_api_path=path), "getPowerStatus", [], post=lambda *a: b'{"result":[]}'
        ).as_dict()
        assert result["ok"] is False
        assert result["nonfatal"] is True
        assert result["command_sent"] is False

    assert avr_sony_audio.send_sony_audio_request(_sony_settings(), "bad/method", [], post=lambda *a: b'{}').as_dict()["ok"] is False
    try:
        avr_sony_audio.build_set_input_payload("")
    except ValueError as exc:
        assert str(exc) == "invalid_sony_audio_input_uri"
    else:  # pragma: no cover
        raise AssertionError("expected invalid input URI")

    def boom(url, payload, headers, timeout):
        raise RuntimeError("driver boom")

    result = avr_sony_audio.send_sony_audio_request(_sony_settings(), "getPowerStatus", [], post=boom).as_dict()
    assert result["ok"] is False
    assert result["warnings"] == ("avr_driver_error_nonfatal",)
    assert "supersecretpsk" not in str(result)

    no_input = avr_sony_audio.SonyAudioApiAvrController(_sony_settings(sony_avr_player_input_uri="", avr_player_input=""))
    assert no_input.select_input().as_dict()["message"] == "invalid_sony_audio_input_uri"


def test_build16_onkyo_eiscp_edge_paths_stay_nonfatal():
    from resources.lib import avr_onkyo_eiscp

    assert avr_onkyo_eiscp.parse_eiscp_response(avr_onkyo_eiscp.build_eiscp_frame("!1PWR01").decode("ascii", errors="ignore")).startswith("!1PWR01")

    for frame in (b"", b"BADC" + b"\x00" * 12, b"ISCP" + b"\x00\x00\x00\x10" + b"\x00\x00\x00\xff" + b"\x01\x00\x00\x00"):
        try:
            avr_onkyo_eiscp.parse_eiscp_response(frame)
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError("expected malformed frame")

    assert avr_onkyo_eiscp.send_eiscp_command("", "!1PWR01").as_dict()["warnings"] == ("avr_config_incomplete",)
    assert avr_onkyo_eiscp.send_eiscp_command("avr.local", "bad\n", socket_factory=lambda *a: object()).as_dict()["warnings"] == ("invalid_eiscp_payload",)

    class ClosingSocket:
        def sendall(self, data):
            self.data = data
        def recv(self, size):
            return avr_onkyo_eiscp.build_eiscp_frame("!1PWR01")
        def close(self):
            raise RuntimeError("close ignored")

    ok = avr_onkyo_eiscp.send_eiscp_command("avr.local", "!1PWR01", socket_factory=lambda *a: ClosingSocket()).as_dict()
    assert ok["ok"] is True

    controller = avr_onkyo_eiscp.OnkyoEiscpAvrController("avr.local", player_input="", socket_factory=lambda *a: ClosingSocket())
    assert controller.select_input().as_dict()["warnings"] == ("invalid_eiscp_input",)
    assert controller.run("unsupported").as_dict()["warnings"] == ("unsupported_eiscp_action",)
