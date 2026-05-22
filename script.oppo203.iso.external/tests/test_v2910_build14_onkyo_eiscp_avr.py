"""v2.9.10 Build 16 - Onkyo/Integra/Pioneer eISCP AVR driver."""
from __future__ import annotations

import socket
import struct
from pathlib import Path

from resources.lib import avr_control, avr_onkyo_eiscp, avr_presets, settings_reader, version

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


class FakeSocket:
    def __init__(self, response: bytes | None = None, recv_error: Exception | None = None):
        self.response = response if response is not None else avr_onkyo_eiscp.build_eiscp_frame("!1PWR01")
        self.recv_error = recv_error
        self.sent: list[bytes] = []
        self.closed = False
        self.timeout: float | None = None

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def sendall(self, data: bytes) -> None:
        self.sent.append(data)

    def recv(self, size: int) -> bytes:
        if self.recv_error:
            raise self.recv_error
        return self.response

    def close(self) -> None:
        self.closed = True


def test_build14_eiscp_frame_construction_and_parsing_are_valid():
    frame = avr_onkyo_eiscp.build_eiscp_frame("!1PWR01")
    assert frame[:4] == b"ISCP"
    assert struct.unpack(">I", frame[4:8])[0] == 16
    assert struct.unpack(">I", frame[8:12])[0] == len(b"!1PWR01\r")
    assert frame[12:16] == b"\x01\x00\x00\x00"
    assert frame[16:] == b"!1PWR01\r"
    assert avr_onkyo_eiscp.parse_eiscp_response(frame) == "!1PWR01"


def test_build14_eiscp_payloads_and_input_validation():
    assert avr_onkyo_eiscp.build_power_on_payload() == "!1PWR01"
    assert avr_onkyo_eiscp.build_input_select_payload("10") == "!1SLI10"
    assert avr_onkyo_eiscp.build_input_select_payload("2a") == "!1SLI2A"
    for bad in ("", "1", "100", "GG", "01\r", "../../"):
        try:
            avr_onkyo_eiscp.build_input_select_payload(bad)
        except ValueError as exc:
            assert str(exc) == "invalid_eiscp_input"
        else:  # pragma: no cover - defensive assertion path
            raise AssertionError(f"bad eISCP input accepted: {bad!r}")
    for bad_payload in ("", "!1PWR01\n", "!1SLI10\r"):
        try:
            avr_onkyo_eiscp.build_eiscp_frame(bad_payload)
        except ValueError as exc:
            assert str(exc) == "invalid_eiscp_payload"
        else:  # pragma: no cover - defensive assertion path
            raise AssertionError(f"bad eISCP payload accepted: {bad_payload!r}")


def test_build14_send_eiscp_command_opens_sends_closes_per_command():
    sockets: list[FakeSocket] = []

    def factory(address, timeout):
        assert address == ("192.168.1.94", 60128)
        assert timeout == 3.0
        sock = FakeSocket(avr_onkyo_eiscp.build_eiscp_frame("!1SLI10"))
        sockets.append(sock)
        return sock

    result = avr_onkyo_eiscp.send_eiscp_command("192.168.1.94", "!1SLI10", socket_factory=factory).as_dict()
    assert result["ok"] is True
    assert result["message"] == "!1SLI10"
    assert result["command_sent"] is True
    assert result["hardware_validation_claimed"] is False
    assert len(sockets) == 1
    assert sockets[0].sent == [avr_onkyo_eiscp.build_eiscp_frame("!1SLI10")]
    assert sockets[0].closed is True


def test_build14_malformed_response_timeout_network_and_driver_errors_are_nonfatal():
    malformed = avr_onkyo_eiscp.send_eiscp_command(
        "avr.local",
        "!1PWR01",
        socket_factory=lambda address, timeout: FakeSocket(b"not an eiscp frame"),
    ).as_dict()
    assert malformed["ok"] is False
    assert malformed["command_sent"] is True
    assert malformed["nonfatal"] is True
    assert "malformed_eiscp_response_nonfatal" in malformed["warnings"]

    response_timeout = avr_onkyo_eiscp.send_eiscp_command(
        "avr.local",
        "!1PWR01",
        socket_factory=lambda address, timeout: FakeSocket(recv_error=socket.timeout()),
    ).as_dict()
    assert response_timeout["ok"] is True
    assert response_timeout["command_sent"] is True
    assert "avr_response_timeout_nonfatal" in response_timeout["warnings"]

    def network_error(address, timeout):
        raise OSError("no route")

    network = avr_onkyo_eiscp.send_eiscp_command("avr.local", "!1PWR01", socket_factory=network_error).as_dict()
    assert network["ok"] is False
    assert network["command_sent"] is False
    assert "avr_network_error_nonfatal" in network["warnings"]

    def driver_error(address, timeout):
        raise RuntimeError("boom")

    driver = avr_onkyo_eiscp.send_eiscp_command("avr.local", "!1PWR01", socket_factory=driver_error).as_dict()
    assert driver["ok"] is False
    assert "avr_driver_error_nonfatal" in driver["warnings"]


def test_build14_controller_factory_returns_onkyo_and_pioneer_controllers_only_when_complete():
    disabled = settings_reader.Settings({})
    assert avr_control.controller_factory(disabled) is None

    incomplete = settings_reader.Settings({"avr_control_enabled": "true", "avr_backend": "onkyo_eiscp"})
    assert avr_control.controller_factory(incomplete) is None
    validation = avr_control.validate_avr_settings(incomplete).as_dict()
    assert validation["ok"] is False
    assert validation["driver_available"] is True
    assert validation["missing"] == ("avr_host", "avr_player_input")

    complete = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "onkyo_eiscp",
        "avr_host": "192.168.1.95",
        "avr_player_input": "10",
    })
    controller = avr_control.controller_factory(complete, socket_factory=lambda address, timeout: FakeSocket())
    assert isinstance(controller, avr_onkyo_eiscp.OnkyoEiscpAvrController)
    assert controller.backend == "onkyo_eiscp"
    validation = avr_control.validate_avr_settings(complete).as_dict()
    assert validation["ok"] is True
    assert validation["driver_available"] is True
    assert validation["hardware_validation_claimed"] is False

    pioneer = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "pioneer_eiscp",
        "avr_host": "192.168.1.96",
        "avr_player_input": "10",
    })
    pioneer_controller = avr_control.controller_factory(pioneer, socket_factory=lambda address, timeout: FakeSocket())
    assert isinstance(pioneer_controller, avr_onkyo_eiscp.OnkyoEiscpAvrController)
    assert pioneer_controller.backend == "pioneer_eiscp"
    pioneer_result = pioneer_controller.power_on().as_dict()
    assert pioneer_result["ok"] is True
    assert "pioneer_eiscp_experimental_unverified" in pioneer_result["warnings"]


def test_build14_controller_dispatch_invalid_input_and_unsupported_actions_are_nonfatal():
    controller = avr_onkyo_eiscp.OnkyoEiscpAvrController(
        "avr.local", player_input="10", socket_factory=lambda address, timeout: FakeSocket()
    )
    assert controller.power_on().as_dict()["command_sent"] is True
    assert controller.select_input().as_dict()["command_sent"] is True
    assert controller.run("input", input_code="2B").as_dict()["command_sent"] is True
    bad_input = controller.select_input("GG").as_dict()
    assert bad_input["ok"] is False
    assert bad_input["command_sent"] is False
    assert "invalid_eiscp_input" in bad_input["warnings"]
    unsupported = controller.run("volume_up").as_dict()
    assert unsupported["ok"] is False
    assert unsupported["nonfatal"] is True
    assert "unsupported_eiscp_action" in unsupported["warnings"]


def test_build14_metadata_defaults_and_other_families_remain_safe():
    defaults = settings_reader.DEFAULTS
    assert defaults["avr_control_enabled"] == "false"
    assert defaults["avr_power_off_enabled"] == "false"
    assert defaults["avr_volume_automation_enabled"] == "false"

    onkyo = avr_presets.get_avr_preset("onkyo_eiscp")
    assert onkyo["driver_available"] is True
    assert onkyo["default_port"] == 60128
    assert onkyo["frame_magic"] == "ISCP"
    assert onkyo["power_on_payload"] == "!1PWR01"
    assert onkyo["input_select_prefix"] == "!1SLI"
    assert onkyo["hardware_validation_claimed"] is False

    pioneer = avr_presets.get_avr_preset("pioneer_eiscp")
    assert pioneer["driver_available"] is True
    assert pioneer["experimental"] is True
    assert pioneer["hardware_validation_claimed"] is False

    summary = avr_presets.avr_support_summary()
    assert summary["driver_execution_families"] == (
        "denon_marantz", "yamaha_yxc", "onkyo_eiscp", "pioneer_eiscp", "sony_audio_api"
    )
    assert summary["playback_sequencing_hooked"] is True
    assert summary["hardware_validation_claimed"] is False

    sony = settings_reader.Settings({
        "avr_control_enabled": "true",
        "avr_backend": "sony_audio_api",
        "avr_host": "192.168.1.97",
        "avr_player_input": "BD",
    })
    sony_validation = avr_control.validate_avr_settings(sony).as_dict()
    assert sony_validation["ok"] is False
    assert sony_validation["driver_available"] is True
    assert "sony_audio_api_experimental_acknowledgement_required" in sony_validation["warnings"]
    assert avr_control.controller_factory(sony) is None


def test_build14_metadata_and_documentation_identity():
    assert version.BUILD_ID == "v2.9.13 Final"
    assert version.BUILD_NUMBER == 22
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 14" in addon
    assert "Onkyo / Integra / Pioneer eISCP AVR driver" in addon
    assert (ROOT / "resources/lib/avr_onkyo_eiscp.py").exists()
    for rel in ["README.md", "reference.md", "web-references.md"]:
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 14" in text
        assert "Onkyo / Integra / Pioneer eISCP AVR driver" in text
    assert (ROOT / "BUILD_NOTES_v2.9.10_BUILD14.md").exists() or (ROOT / "docs" / "release-history" / "BUILD_NOTES_v2.9.10_BUILD14.md").exists()
    assert (ROOT / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD14.md").exists() or (ROOT / "docs" / "release-history" / "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD14.md").exists()


def test_build14_port_timeout_and_malformed_response_edges():
    assert avr_onkyo_eiscp.eiscp_port("bad") == 60128
    assert avr_onkyo_eiscp.eiscp_port("70000") == 60128
    assert avr_onkyo_eiscp.eiscp_timeout("bad") == 3.0
    assert avr_onkyo_eiscp.eiscp_timeout("0") == 3.0
    assert avr_onkyo_eiscp.eiscp_timeout("31") == 3.0
    for malformed in (b"", b"ISCP\x00", b"NOPE" + b"\x00" * 12):
        try:
            avr_onkyo_eiscp.parse_eiscp_response(malformed)
        except ValueError as exc:
            assert str(exc).startswith("malformed_eiscp_response")
        else:  # pragma: no cover - defensive assertion path
            raise AssertionError("malformed eISCP response accepted")
