"""v2.9.10 Build 16 - Denon/Marantz AVR driver."""
from __future__ import annotations

import socket
from pathlib import Path

from resources.lib import avr_control, avr_denon_marantz, avr_presets, settings_reader, version

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


class FakeSocket:
    def __init__(self, response: bytes = b"PWON\r"):
        self.response = response
        self.sent: list[bytes] = []
        self.closed = False
        self.timeout = None

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendall(self, data: bytes) -> None:
        self.sent.append(data)

    def recv(self, size: int) -> bytes:
        return self.response

    def close(self) -> None:
        self.closed = True


class RecvTimeoutSocket(FakeSocket):
    def recv(self, size: int) -> bytes:
        raise socket.timeout("timed out")


def test_build12_denon_command_builders_are_safe_and_expected():
    assert avr_denon_marantz.build_power_on_command() == "PWON"
    assert avr_denon_marantz.build_input_select_command("bd") == "SIBD"
    assert avr_denon_marantz.build_input_select_command("sat/cbl") == "SISAT/CBL"
    assert avr_denon_marantz.build_query_power_command() == "PW?"
    assert avr_denon_marantz.build_query_input_command() == "SI?"
    for bad in ("", "BD\nPWSTANDBY", "BD\rPWSTANDBY", "too long " * 8):
        try:
            avr_denon_marantz.build_input_select_command(bad)
        except ValueError as exc:
            assert str(exc) == "invalid_denon_marantz_input"
        else:  # pragma: no cover - defensive assertion path
            raise AssertionError(f"bad input accepted: {bad!r}")


def test_build12_factory_returns_denon_controller_only_when_enabled_and_complete():
    disabled = settings_reader.Settings({})
    assert avr_control.controller_factory(disabled) is None
    incomplete = settings_reader.Settings({"avr_control_enabled": "true", "avr_backend": "denon_marantz"})
    assert avr_control.controller_factory(incomplete) is None
    validation = avr_control.validate_avr_settings(incomplete).as_dict()
    assert validation["ok"] is False
    assert validation["driver_available"] is True
    assert validation["missing"] == ("avr_host", "avr_player_input")

    complete = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "denon_marantz",
        "avr_host": "192.168.1.80",
        "avr_player_input": "BD",
    })
    controller = avr_control.controller_factory(complete)
    assert isinstance(controller, avr_denon_marantz.DenonMarantzAvrController)
    validation = avr_control.validate_avr_settings(complete).as_dict()
    assert validation["ok"] is True
    assert validation["driver_available"] is True
    assert validation["hardware_validation_claimed"] is False


def test_build12_denon_controller_opens_and_closes_socket_per_command():
    sockets: list[FakeSocket] = []

    def factory(address, timeout):
        assert address == ("192.168.1.81", 23)
        assert timeout == 3.0
        sock = FakeSocket(b"PWON\r")
        sockets.append(sock)
        return sock

    controller = avr_denon_marantz.DenonMarantzAvrController(
        "192.168.1.81", player_input="BD", socket_factory=factory
    )
    power = controller.power_on().as_dict()
    selected = controller.select_input().as_dict()
    assert power["ok"] is True
    assert selected["ok"] is True
    assert sockets[0].sent == [b"PWON\r"]
    assert sockets[1].sent == [b"SIBD\r"]
    assert all(sock.closed for sock in sockets)
    assert len(sockets) == 2


def test_build12_denon_query_helpers_send_expected_tokens():
    sockets: list[FakeSocket] = []

    def factory(address, timeout):
        sock = FakeSocket(b"SIHDMI1\r")
        sockets.append(sock)
        return sock

    controller = avr_denon_marantz.DenonMarantzAvrController("avr.local", socket_factory=factory)
    assert controller.query_power().as_dict()["command_sent"] is True
    assert controller.query_input().as_dict()["command_sent"] is True
    assert sockets[0].sent == [b"PW?\r"]
    assert sockets[1].sent == [b"SI?\r"]


def test_build12_denon_timeout_and_network_errors_are_nonfatal():
    def timeout_factory(address, timeout):
        return RecvTimeoutSocket()

    timeout_result = avr_denon_marantz.send_denon_command(
        "192.168.1.82", "PWON", socket_factory=timeout_factory
    ).as_dict()
    assert timeout_result["ok"] is True
    assert timeout_result["nonfatal"] is True
    assert timeout_result["command_sent"] is True
    assert "avr_response_timeout_nonfatal" in timeout_result["warnings"]

    def error_factory(address, timeout):
        raise OSError("no route")

    error_result = avr_denon_marantz.send_denon_command(
        "192.168.1.82", "PWON", socket_factory=error_factory
    ).as_dict()
    assert error_result["ok"] is False
    assert error_result["nonfatal"] is True
    assert error_result["command_sent"] is False
    assert error_result["hardware_validation_claimed"] is False
    assert "avr_network_error_nonfatal" in error_result["warnings"]


def test_build12_denon_driver_metadata_does_not_enable_avr_by_default_or_hook_playback():
    defaults = settings_reader.DEFAULTS
    assert defaults["avr_control_enabled"] == "false"
    assert defaults["avr_power_off_enabled"] == "false"
    assert defaults["avr_volume_automation_enabled"] == "false"
    preset = avr_presets.get_avr_preset("denon_marantz")
    assert preset["driver_available"] is True
    assert preset["power_on_command"] == "PWON"
    assert preset["input_select_prefix"] == "SI"
    summary = avr_presets.avr_support_summary()
    assert summary["driver_execution_added"] is True
    assert summary["driver_execution_families"] == ("denon_marantz", "yamaha_yxc", "onkyo_eiscp", "pioneer_eiscp", "sony_audio_api")
    assert summary["playback_sequencing_hooked"] is True
    assert summary["hardware_validation_claimed"] is False


def test_build12_non_denon_families_remain_metadata_only():
    for backend in ("sony_audio_api",):
        settings = settings_reader.Settings({
            "avr_control_enabled": "true",
            "avr_backend": backend,
            "avr_host": "192.168.1.83",
            "avr_player_input": "BD",
        })
        validation = avr_control.validate_avr_settings(settings).as_dict()
        assert validation["ok"] is False
        assert validation["driver_available"] is True
        assert "sony_audio_api_experimental_acknowledgement_required" in validation["warnings"]
        assert avr_control.controller_factory(settings) is None


def test_build12_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.13 Final"
    assert version.BUILD_NUMBER == 22
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 12" in addon
    assert "Denon / Marantz AVR driver" in addon
    assert (ROOT / "resources/lib/avr_denon_marantz.py").exists()
    for rel in ["README.md", "reference.md", "web-references.md"]:
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 12" in text
        assert "Denon / Marantz AVR driver" in text
    assert (ROOT / "BUILD_NOTES_v2.9.10_BUILD12.md").exists() or (ROOT / "docs" / "release-history" / "BUILD_NOTES_v2.9.10_BUILD12.md").exists()
    assert (ROOT / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD12.md").exists() or (ROOT / "docs" / "release-history" / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD12.md").exists()

class CloseRaisesSocket(FakeSocket):
    def close(self) -> None:
        self.closed = True
        raise RuntimeError("close failed")


class NoTimeoutSocket(FakeSocket):
    settimeout = None


def test_build12_denon_edge_parsing_and_no_response_paths():
    assert avr_denon_marantz.denon_port("bad") == 23
    assert avr_denon_marantz.denon_port("70000") == 23
    assert avr_denon_marantz.denon_timeout("bad") == 3.0
    assert avr_denon_marantz.denon_timeout("0") == 3.0
    assert avr_denon_marantz.denon_timeout("31") == 3.0
    assert avr_denon_marantz._sanitize_response("PWON\r\n") == "PWON"

    sockets: list[FakeSocket] = []

    def factory(address, timeout):
        sock = CloseRaisesSocket("SIBD\r")
        sockets.append(sock)
        return sock

    result = avr_denon_marantz.send_denon_command(
        "avr.local", "PWON", socket_factory=factory, read_response=False
    ).as_dict()
    assert result["ok"] is True
    assert result["message"] == "denon_marantz_command_sent"
    assert sockets[0].sent == [b"PWON\r"]
    assert sockets[0].closed is True


def test_build12_denon_missing_host_invalid_command_and_driver_error_are_nonfatal():
    missing = avr_denon_marantz.send_denon_command("", "PWON").as_dict()
    assert missing["ok"] is False
    assert missing["message"] == "avr_host_missing"
    assert missing["command_sent"] is False

    invalid = avr_denon_marantz.send_denon_command("avr.local", "PWON\nSIXX").as_dict()
    assert invalid["ok"] is False
    assert "invalid_denon_marantz_command" in invalid["warnings"]

    class BrokenSocket:
        def sendall(self, data):
            raise RuntimeError("boom")
        def close(self):
            pass

    def broken_factory(address, timeout):
        return BrokenSocket()

    broken = avr_denon_marantz.send_denon_command(
        "avr.local", "PWON", socket_factory=broken_factory
    ).as_dict()
    assert broken["ok"] is False
    assert "avr_driver_error_nonfatal" in broken["warnings"]


def test_build12_denon_run_dispatch_and_invalid_input_paths():
    sockets: list[FakeSocket] = []

    def factory(address, timeout):
        sock = NoTimeoutSocket(b"OK\r")
        sockets.append(sock)
        return sock

    controller = avr_denon_marantz.DenonMarantzAvrController(
        "avr.local", player_input="BD", socket_factory=factory
    )
    assert controller.run("on").as_dict()["command_sent"] is True
    assert controller.run("select_input", input_name="game").as_dict()["command_sent"] is True
    assert controller.run("power_query").as_dict()["command_sent"] is True
    assert controller.run("input_query").as_dict()["command_sent"] is True
    bad_input = controller.select_input("BD\nPWSTANDBY").as_dict()
    assert bad_input["ok"] is False
    assert bad_input["command_sent"] is False
    assert "invalid_denon_marantz_input" in bad_input["warnings"]
    unsupported = controller.run("mute").as_dict()
    assert unsupported["ok"] is False
    assert "unsupported_denon_marantz_action" in unsupported["warnings"]
