"""Onkyo / Integra / Pioneer eISCP AVR helper for v2.9.10 Build 14.

This module is intentionally narrow: it implements only eISCP frame construction
and guarded socket command helpers behind the disabled-by-default AVR framework.
It opens and closes a socket for each command, uses short timeouts, treats
Pioneer as experimental/unverified metadata, and returns nonfatal ``AvrResult``
objects instead of raising into playback/control callers.
"""
from __future__ import annotations

import socket
import struct
from typing import Callable, Protocol

try:
    from .avr_types import AVR_BACKEND_ONKYO_EISCP, AVR_BACKEND_PIONEER_EISCP, AvrResult
except ImportError:  # top-level/audit/test compatibility
    from avr_types import AVR_BACKEND_ONKYO_EISCP, AVR_BACKEND_PIONEER_EISCP, AvrResult  # type: ignore

DEFAULT_EISCP_PORT = 60128
DEFAULT_EISCP_TIMEOUT = 3.0
EISCP_MAGIC = b"ISCP"
EISCP_HEADER_SIZE = 16
EISCP_VERSION = 1
EISCP_POWER_ON_PAYLOAD = "!1PWR01"
EISCP_INPUT_SELECT_PREFIX = "!1SLI"
EISCP_LINE_ENDING = "\r"
VALID_EISCP_INPUT_CHARS = frozenset("0123456789abcdefABCDEF")

SocketFactory = Callable[[tuple[str, int], float], object]


class SocketLike(Protocol):
    def sendall(self, data: bytes) -> None: ...
    def recv(self, size: int) -> bytes: ...
    def close(self) -> None: ...


def _clean_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def eiscp_port(value: object, default: int = DEFAULT_EISCP_PORT) -> int:
    try:
        parsed = int(_clean_text(value) or default)
    except (TypeError, ValueError):
        return int(default)
    if parsed < 1 or parsed > 65535:
        return int(default)
    return parsed


def eiscp_timeout(value: object, default: float = DEFAULT_EISCP_TIMEOUT) -> float:
    try:
        parsed = float(_clean_text(value) or default)
    except (TypeError, ValueError):
        return float(default)
    if parsed <= 0 or parsed > 30:
        return float(default)
    return parsed


def validate_eiscp_input(input_code: object) -> str:
    raw = "" if input_code is None else str(input_code)
    if raw != raw.strip():
        raise ValueError("invalid_eiscp_input")
    text = raw.upper()
    if len(text) != 2 or any(char not in VALID_EISCP_INPUT_CHARS for char in text):
        raise ValueError("invalid_eiscp_input")
    return text


def build_power_on_payload() -> str:
    return EISCP_POWER_ON_PAYLOAD


def build_input_select_payload(input_code: object) -> str:
    return EISCP_INPUT_SELECT_PREFIX + validate_eiscp_input(input_code)


def build_eiscp_frame(command_payload: object) -> bytes:
    payload_text = "" if command_payload is None else str(command_payload)
    if payload_text != payload_text.strip() or not payload_text or "\r" in payload_text or "\n" in payload_text:
        raise ValueError("invalid_eiscp_payload")
    payload = (payload_text + EISCP_LINE_ENDING).encode("ascii", errors="strict")
    header = (
        EISCP_MAGIC
        + struct.pack(">I", EISCP_HEADER_SIZE)
        + struct.pack(">I", len(payload))
        + bytes([EISCP_VERSION, 0, 0, 0])
    )
    return header + payload


def parse_eiscp_response(frame: bytes | str) -> str:
    if isinstance(frame, str):
        raw = frame.encode("ascii", errors="replace")
    else:
        raw = bytes(frame)
    if len(raw) < EISCP_HEADER_SIZE:
        raise ValueError("malformed_eiscp_response_short")
    if raw[:4] != EISCP_MAGIC:
        raise ValueError("malformed_eiscp_response_magic")
    header_size = struct.unpack(">I", raw[4:8])[0]
    data_size = struct.unpack(">I", raw[8:12])[0]
    if header_size < EISCP_HEADER_SIZE or len(raw) < header_size + data_size:
        raise ValueError("malformed_eiscp_response_size")
    payload = raw[header_size : header_size + data_size]
    return payload.decode("ascii", errors="replace").replace("\r", "").replace("\n", "").strip()[:160]


def _close_socket(sock: object) -> None:
    close = getattr(sock, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass


def _backend_for(experimental_pioneer: bool) -> str:
    return AVR_BACKEND_PIONEER_EISCP if experimental_pioneer else AVR_BACKEND_ONKYO_EISCP


def send_eiscp_command(
    host: object,
    command_payload: object,
    *,
    port: object = DEFAULT_EISCP_PORT,
    timeout: object = DEFAULT_EISCP_TIMEOUT,
    socket_factory: SocketFactory | None = None,
    read_response: bool = True,
    experimental_pioneer: bool = False,
) -> AvrResult:
    """Send one eISCP command and return a nonfatal result."""
    backend = _backend_for(experimental_pioneer)
    host_text = _clean_text(host)
    if not host_text:
        return AvrResult(False, "eiscp_command", backend, "avr_host_missing", ("avr_config_incomplete",), True, False, False)
    try:
        frame = build_eiscp_frame(command_payload)
    except (UnicodeEncodeError, ValueError):
        return AvrResult(False, "eiscp_command", backend, "invalid_eiscp_payload", ("invalid_eiscp_payload",), True, False, False)

    parsed_port = eiscp_port(port)
    parsed_timeout = eiscp_timeout(timeout)
    factory = socket_factory or socket.create_connection
    sock: object | None = None
    try:
        sock = factory((host_text, parsed_port), parsed_timeout)
        settimeout = getattr(sock, "settimeout", None)
        if callable(settimeout):
            settimeout(parsed_timeout)
        getattr(sock, "sendall")(frame)
        response_text = ""
        if read_response:
            try:
                response_text = parse_eiscp_response(getattr(sock, "recv")(1024))
            except socket.timeout:
                return AvrResult(
                    ok=True,
                    action="eiscp_command",
                    backend=backend,
                    message="avr_response_timeout_nonfatal",
                    warnings=("avr_response_timeout_nonfatal",),
                    nonfatal=True,
                    hardware_validation_claimed=False,
                    command_sent=True,
                )
            except ValueError as exc:
                return AvrResult(
                    ok=False,
                    action="eiscp_command",
                    backend=backend,
                    message=str(exc),
                    warnings=("malformed_eiscp_response_nonfatal",),
                    nonfatal=True,
                    hardware_validation_claimed=False,
                    command_sent=True,
                )
        return AvrResult(
            ok=True,
            action="eiscp_command",
            backend=backend,
            message=response_text or "eiscp_command_sent",
            warnings=("pioneer_eiscp_experimental_unverified",) if experimental_pioneer else (),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=True,
        )
    except (OSError, TimeoutError, socket.timeout) as exc:
        return AvrResult(
            ok=False,
            action="eiscp_command",
            backend=backend,
            message=exc.__class__.__name__,
            warnings=("avr_network_error_nonfatal",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    except Exception as exc:
        return AvrResult(
            ok=False,
            action="eiscp_command",
            backend=backend,
            message=exc.__class__.__name__,
            warnings=("avr_driver_error_nonfatal",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    finally:
        if sock is not None:
            _close_socket(sock)


class OnkyoEiscpAvrController:
    """Small command adapter for Onkyo/Integra and experimental Pioneer eISCP."""

    def __init__(
        self,
        host: object,
        *,
        port: object = DEFAULT_EISCP_PORT,
        timeout: object = DEFAULT_EISCP_TIMEOUT,
        player_input: object = "",
        socket_factory: SocketFactory | None = None,
        experimental_pioneer: bool = False,
    ) -> None:
        self.host = _clean_text(host)
        self.port = eiscp_port(port)
        self.timeout = eiscp_timeout(timeout)
        self.player_input = _clean_text(player_input)
        self.socket_factory = socket_factory
        self.experimental_pioneer = bool(experimental_pioneer)
        self.backend = _backend_for(self.experimental_pioneer)

    def send(self, payload: object, *, read_response: bool = True) -> AvrResult:
        return send_eiscp_command(
            self.host,
            payload,
            port=self.port,
            timeout=self.timeout,
            socket_factory=self.socket_factory,
            read_response=read_response,
            experimental_pioneer=self.experimental_pioneer,
        )

    def power_on(self) -> AvrResult:
        return self.send(build_power_on_payload())

    def select_input(self, input_code: object | None = None) -> AvrResult:
        try:
            payload = build_input_select_payload(self.player_input if input_code is None else input_code)
        except ValueError:
            return AvrResult(
                ok=False,
                action="eiscp_input_select",
                backend=self.backend,
                message="invalid_eiscp_input",
                warnings=("invalid_eiscp_input",),
                nonfatal=True,
                hardware_validation_claimed=False,
                command_sent=False,
            )
        return self.send(payload)

    def run(self, action: str, **kwargs: object) -> AvrResult:
        normalized = _clean_text(action).lower()
        if normalized in {"power_on", "on"}:
            return self.power_on()
        if normalized in {"input_select", "select_input", "input"}:
            return self.select_input(kwargs.get("input_name") or kwargs.get("input_code"))
        return AvrResult(
            ok=False,
            action=normalized or "unknown",
            backend=self.backend,
            message="unsupported_eiscp_action",
            warnings=("unsupported_eiscp_action",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )


# Alias makes the shared family explicit for tests/docs while keeping one driver.
IntegraEiscpAvrController = OnkyoEiscpAvrController
PioneerEiscpAvrController = OnkyoEiscpAvrController
