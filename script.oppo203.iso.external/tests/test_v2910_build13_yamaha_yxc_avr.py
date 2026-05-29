"""v2.9.10 Build 16 - Yamaha MusicCast/YXC AVR driver."""
from __future__ import annotations

from pathlib import Path

from resources.lib import avr_control, avr_presets, avr_yamaha, settings_reader, version

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


def test_build13_yamaha_url_builders_are_expected_and_url_encoded():
    assert avr_yamaha.build_power_on_url("192.168.1.90") == (
        "http://192.168.1.90/YamahaExtendedControl/v1/main/setPower?power=on"
    )
    assert avr_yamaha.build_input_select_url("avr.local", "hdmi1") == (
        "http://avr.local/YamahaExtendedControl/v1/main/setInput?input=hdmi1"
    )
    assert avr_yamaha.build_input_select_url("avr.local", "AV/1") == (
        "http://avr.local/YamahaExtendedControl/v1/main/setInput?input=AV%2F1"
    )
    assert avr_yamaha.build_status_url("avr.local", port="8080") == (
        "http://avr.local:8080/YamahaExtendedControl/v1/main/getStatus"
    )
    assert avr_yamaha.build_power_on_url("http://avr.local:8080") == (
        "http://avr.local:8080/YamahaExtendedControl/v1/main/setPower?power=on"
    )
    for bad in ("", "HDMI1\nother", "../../etc/passwd", "input too long " * 8):
        try:
            avr_yamaha.build_input_select_url("avr.local", bad)
        except ValueError as exc:
            assert str(exc) == "invalid_yamaha_yxc_input"
        else:  # pragma: no cover - defensive assertion path
            raise AssertionError(f"bad Yamaha input accepted: {bad!r}")


def test_build13_factory_returns_yamaha_controller_only_when_enabled_and_complete():
    disabled = settings_reader.Settings({})
    assert avr_control.controller_factory(disabled) is None

    incomplete = settings_reader.Settings({"avr_control_enabled": "true", "avr_backend": "yamaha_yxc"})
    assert avr_control.controller_factory(incomplete) is None
    validation = avr_control.validate_avr_settings(incomplete).as_dict()
    assert validation["ok"] is False
    assert validation["driver_available"] is True
    assert validation["missing"] == ("avr_host", "avr_player_input")

    complete = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "yamaha_yxc",
        "avr_host": "192.168.1.91",
        "avr_player_input": "hdmi1",
    })
    controller = avr_control.controller_factory(complete, http_get=lambda url, timeout: '{"response_code": 0}')
    assert isinstance(controller, avr_yamaha.YamahaYxcAvrController)
    validation = avr_control.validate_avr_settings(complete).as_dict()
    assert validation["ok"] is True
    assert validation["driver_available"] is True
    assert validation["hardware_validation_claimed"] is False


def test_build13_yamaha_controller_uses_get_helpers_and_parses_response_code():
    calls: list[tuple[str, float]] = []

    def fake_get(url: str, timeout: float):
        calls.append((url, timeout))
        return b'{"response_code": 0}'

    controller = avr_yamaha.YamahaYxcAvrController(
        "192.168.1.92", player_input="hdmi2", http_get=fake_get
    )
    power = controller.power_on().as_dict()
    selected = controller.select_input().as_dict()
    status = controller.get_status().as_dict()
    assert power["ok"] is True
    assert selected["ok"] is True
    assert status["ok"] is True
    assert len(calls) == 3
    assert calls[0][0].endswith("/setPower?power=on")
    assert calls[1][0].endswith("/setInput?input=hdmi2")
    assert calls[2][0].endswith("/getStatus")
    assert all(timeout == 3.0 for _, timeout in calls)


def test_build13_yamaha_nonzero_invalid_json_and_network_errors_are_nonfatal():
    nonzero = avr_yamaha.send_yamaha_get(
        "avr.local", "/YamahaExtendedControl/v1/main/getStatus", http_get=lambda url, timeout: '{"response_code": 4}'
    ).as_dict()
    assert nonzero["ok"] is False
    assert nonzero["command_sent"] is True
    assert nonzero["nonfatal"] is True
    assert "yamaha_yxc_nonzero_response_code" in nonzero["warnings"]
    assert nonzero["message"] == "yamaha_yxc_response_code_4"

    invalid_json = avr_yamaha.send_yamaha_get(
        "avr.local", "/YamahaExtendedControl/v1/main/getStatus", http_get=lambda url, timeout: "not-json"
    ).as_dict()
    assert invalid_json["ok"] is False
    assert invalid_json["command_sent"] is True
    assert invalid_json["nonfatal"] is True
    assert "yamaha_yxc_invalid_json" in invalid_json["warnings"]

    def error_get(url: str, timeout: float):
        raise OSError("no route")

    network = avr_yamaha.send_yamaha_get(
        "avr.local", "/YamahaExtendedControl/v1/main/getStatus", http_get=error_get
    ).as_dict()
    assert network["ok"] is False
    assert network["command_sent"] is False
    assert network["nonfatal"] is True
    assert network["hardware_validation_claimed"] is False
    assert "avr_network_error_nonfatal" in network["warnings"]


def test_build13_yamaha_invalid_host_input_dispatch_and_driver_errors_are_nonfatal():
    missing = avr_yamaha.send_yamaha_get("", "/YamahaExtendedControl/v1/main/getStatus").as_dict()
    assert missing["ok"] is False
    assert missing["message"] == "avr_host_missing"
    assert missing["command_sent"] is False

    invalid_host = avr_yamaha.send_yamaha_get("avr.local/path", "/YamahaExtendedControl/v1/main/getStatus").as_dict()
    assert invalid_host["ok"] is False
    assert invalid_host["message"] == "invalid_yamaha_yxc_host"

    def broken_get(url: str, timeout: float):
        raise RuntimeError("boom")

    broken = avr_yamaha.send_yamaha_get(
        "avr.local", "/YamahaExtendedControl/v1/main/getStatus", http_get=broken_get
    ).as_dict()
    assert broken["ok"] is False
    assert "avr_driver_error_nonfatal" in broken["warnings"]

    controller = avr_yamaha.YamahaYxcAvrController("avr.local", player_input="hdmi1", http_get=lambda url, timeout: '{"response_code": 0}')
    assert controller.run("on").as_dict()["command_sent"] is True
    assert controller.run("select_input", input_name="hdmi3").as_dict()["command_sent"] is True
    assert controller.run("status").as_dict()["command_sent"] is True
    unsupported = controller.run("mute").as_dict()
    assert unsupported["ok"] is False
    assert "unsupported_yamaha_yxc_action" in unsupported["warnings"]
    bad_input = controller.select_input("HDMI1\nPWON").as_dict()
    assert bad_input["ok"] is False
    assert bad_input["command_sent"] is False
    assert "invalid_yamaha_yxc_input" in bad_input["warnings"]


def test_build13_yamaha_metadata_defaults_and_other_families_remain_safe():
    defaults = settings_reader.DEFAULTS
    assert defaults["avr_control_enabled"] == "false"
    assert defaults["avr_power_off_enabled"] == "false"
    assert defaults["avr_volume_automation_enabled"] == "false"

    preset = avr_presets.get_avr_preset("yamaha_yxc")
    assert preset["driver_available"] is True
    assert preset["protocol"] == "http_yxc"
    assert preset["http_method"] == "GET"
    assert preset["parses_json_response_code"] is True
    assert preset["hardware_validation_claimed"] is False

    summary = avr_presets.avr_support_summary()
    assert summary["driver_execution_families"] == ("denon_marantz", "yamaha_yxc", "onkyo_eiscp", "pioneer_eiscp", "sony_audio_api")
    assert summary["playback_sequencing_hooked"] is True
    assert summary["hardware_validation_claimed"] is False

    for backend in ("sony_audio_api",):
        settings = settings_reader.Settings({
            "avr_control_enabled": "true",
            "avr_backend": backend,
            "avr_host": "192.168.1.93",
            "avr_player_input": "BD",
        })
        validation = avr_control.validate_avr_settings(settings).as_dict()
        assert validation["ok"] is False
        assert validation["driver_available"] is True
        assert "sony_audio_api_experimental_acknowledgement_required" in validation["warnings"]
        assert avr_control.controller_factory(settings) is None


def test_build13_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.13 Final"
    assert version.BUILD_NUMBER == 22
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 13" in addon
    assert "Yamaha MusicCast / YXC AVR driver" in addon
    assert (ROOT / "resources/lib/avr/avr_yamaha.py").exists()
    for rel in ["README.md", "reference.md", "web-references.md"]:
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 13" in text
        assert "Yamaha MusicCast / YXC AVR driver" in text
    assert (ROOT / "BUILD_NOTES_v2.9.10_BUILD13.md").exists() or (ROOT / "docs" / "release-history" / "BUILD_NOTES_v2.9.10_BUILD13.md").exists()
    assert (ROOT / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD13.md").exists() or (ROOT / "docs" / "release-history" / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD13.md").exists()


def test_build13_yamaha_edge_parsing_default_get_and_bad_json_shapes(monkeypatch):
    assert avr_yamaha.yamaha_port("bad") == 80
    assert avr_yamaha.yamaha_port("70000") == 80
    assert avr_yamaha.yamaha_timeout("bad") == 3.0
    assert avr_yamaha.yamaha_timeout("0") == 3.0
    assert avr_yamaha.yamaha_timeout("31") == 3.0
    assert avr_yamaha._response_code_message("not-int") == "yamaha_yxc_response_code_invalid"
    try:
        avr_yamaha._decode_response("[]")
    except ValueError as exc:
        assert str(exc) == "yamaha_yxc_json_not_object"
    else:  # pragma: no cover - defensive assertion path
        raise AssertionError("non-object JSON accepted")

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b'{"response_code": 0}'

    calls = []

    def fake_urlopen(url, timeout):
        calls.append((url, timeout))
        return FakeResponse()

    monkeypatch.setattr(avr_yamaha.request, "urlopen", fake_urlopen)
    result = avr_yamaha.send_yamaha_get(
        "avr.local", "/YamahaExtendedControl/v1/main/getStatus", http_get=None
    ).as_dict()
    assert result["ok"] is True
    assert calls and calls[0][0].endswith("/getStatus")


def test_build13_yamaha_controller_missing_host_paths_and_settings_object_edges():
    missing = avr_yamaha.YamahaYxcAvrController("")
    assert missing.power_on().as_dict()["message"] == "avr_host_missing"
    assert missing.get_status().as_dict()["message"] == "avr_host_missing"

    class PlainObject:
        pass

    assert avr_control.selected_avr_backend(PlainObject()) == "disabled"
