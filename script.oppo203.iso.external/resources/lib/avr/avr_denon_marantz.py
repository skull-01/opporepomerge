"""Denon/Marantz AVR Telnet-style command helper for v2.9.10 Build 12.

This module is intentionally narrow: it implements only the Denon/Marantz
socket command helper behind the disabled-by-default AVR framework.  It opens
and closes a socket for each command, uses short timeouts, and returns nonfatal
``AvrResult`` objects instead of raising into playback/control callers.
"""

from __future__ import annotations

import re
import socket
from typing import Callable, Protocol, cast

try:
    from .avr_types import AVR_BACKEND_DENON_MARANTZ, AvrResult
except ImportError:  # pragma: no cover - top-level/audit/test compatibility
    from avr_types import AVR_BACKEND_DENON_MARANTZ, AvrResult  # type: ignore

DEFAULT_DENON_MARANTZ_PORT = 23
DEFAULT_DENON_MARANTZ_TIMEOUT = 3.0
DENON_LINE_ENDING = "\r"
VALID_DENON_INPUT_RE = re.compile(r"^[A-Za-z0-9_/-]{1,32}$")

SocketFactory = Callable[[tuple[str, int], float], object]


class SocketLike(Protocol):
    def sendall(self, data: bytes) -> None: ...
    def recv(self, size: int) -> bytes: ...
    def close(self) -> None: ...


def _clean_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def denon_port(value: object, default: int = DEFAULT_DENON_MARANTZ_PORT) -> int:
    try:
        parsed = int(_clean_text(value) or default)
    except (TypeError, ValueError):
        return int(default)
    if parsed < 1 or parsed > 65535:
        return int(default)
    return parsed


def denon_timeout(value: object, default: float = DEFAULT_DENON_MARANTZ_TIMEOUT) -> float:
    try:
        parsed = float(_clean_text(value) or default)
    except (TypeError, ValueError):
        return float(default)
    if parsed <= 0 or parsed > 30:
        return float(default)
    return parsed


def validate_denon_input(input_name: object) -> str:
    text = _clean_text(input_name).upper()
    if not VALID_DENON_INPUT_RE.fullmatch(text):
        raise ValueError("invalid_denon_marantz_input")
    return text


def build_power_on_command() -> str:
    return "PWON"


def build_input_select_command(input_name: object) -> str:
    return "SI" + validate_denon_input(input_name)


def build_query_power_command() -> str:
    return "PW?"


def build_query_input_command() -> str:
    return "SI?"


def _sanitize_response(response: bytes | str) -> str:
    if isinstance(response, bytes):
        text = response.decode("ascii", errors="replace")
    else:
        text = str(response)
    return text.replace("\r", "").replace("\n", "").strip()[:120]


def _close_socket(sock: object) -> None:
    close = getattr(sock, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass


def send_denon_command(
    host: object,
    command: str,
    *,
    port: object = DEFAULT_DENON_MARANTZ_PORT,
    timeout: object = DEFAULT_DENON_MARANTZ_TIMEOUT,
    socket_factory: SocketFactory | None = None,
    read_response: bool = True,
) -> AvrResult:
    """Send one Denon/Marantz command and return a nonfatal result.

    The helper never raises socket errors to callers.  A new socket is opened
    for each command and closed in ``finally`` to keep future playback sequencing
    from depending on a persistent AVR connection.
    """
    host_text = _clean_text(host)
    if not host_text:
        return AvrResult(
            ok=False,
            action="denon_marantz_command",
            backend=AVR_BACKEND_DENON_MARANTZ,
            message="avr_host_missing",
            warnings=("avr_config_incomplete",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    if "\r" in command or "\n" in command or not command:
        return AvrResult(
            ok=False,
            action="denon_marantz_command",
            backend=AVR_BACKEND_DENON_MARANTZ,
            message="invalid_denon_marantz_command",
            warnings=("invalid_denon_marantz_command",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )

    parsed_port = denon_port(port)
    parsed_timeout = denon_timeout(timeout)
    factory = socket_factory or socket.create_connection
    sock: SocketLike | None = None
    payload = (command + DENON_LINE_ENDING).encode("ascii", errors="strict")
    try:
        sock = cast("SocketLike", factory((host_text, parsed_port), parsed_timeout))
        settimeout = getattr(sock, "settimeout", None)
        if callable(settimeout):
            settimeout(parsed_timeout)
        sock.sendall(payload)
        response_text = ""
        if read_response:
            try:
                response_text = _sanitize_response(sock.recv(256))
            except socket.timeout:
                return AvrResult(
                    ok=True,
                    action="denon_marantz_command",
                    backend=AVR_BACKEND_DENON_MARANTZ,
                    message="avr_response_timeout_nonfatal",
                    warnings=("avr_response_timeout_nonfatal",),
                    nonfatal=True,
                    hardware_validation_claimed=False,
                    command_sent=True,
                )
        return AvrResult(
            ok=True,
            action="denon_marantz_command",
            backend=AVR_BACKEND_DENON_MARANTZ,
            message=response_text or "denon_marantz_command_sent",
            warnings=(),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=True,
        )
    except (OSError, TimeoutError, socket.timeout) as exc:
        return AvrResult(
            ok=False,
            action="denon_marantz_command",
            backend=AVR_BACKEND_DENON_MARANTZ,
            message=exc.__class__.__name__,
            warnings=("avr_network_error_nonfatal",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    except Exception as exc:
        return AvrResult(
            ok=False,
            action="denon_marantz_command",
            backend=AVR_BACKEND_DENON_MARANTZ,
            message=exc.__class__.__name__,
            warnings=("avr_driver_error_nonfatal",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    finally:
        if sock is not None:
            _close_socket(sock)


class DenonMarantzAvrController:
    """Small command adapter for Denon/Marantz AVR families."""

    backend = AVR_BACKEND_DENON_MARANTZ

    def __init__(
        self,
        host: object,
        *,
        port: object = DEFAULT_DENON_MARANTZ_PORT,
        timeout: object = DEFAULT_DENON_MARANTZ_TIMEOUT,
        player_input: object = "",
        socket_factory: SocketFactory | None = None,
    ) -> None:
        self.host = _clean_text(host)
        self.port = denon_port(port)
        self.timeout = denon_timeout(timeout)
        self.player_input = _clean_text(player_input)
        self.socket_factory = socket_factory

    def send(self, command: str, *, read_response: bool = True) -> AvrResult:
        return send_denon_command(
            self.host,
            command,
            port=self.port,
            timeout=self.timeout,
            socket_factory=self.socket_factory,
            read_response=read_response,
        )

    def power_on(self) -> AvrResult:
        return self.send(build_power_on_command())

    def select_input(self, input_name: object | None = None) -> AvrResult:
        try:
            command = build_input_select_command(
                self.player_input if input_name is None else input_name
            )
        except ValueError:
            return AvrResult(
                ok=False,
                action="denon_marantz_input_select",
                backend=AVR_BACKEND_DENON_MARANTZ,
                message="invalid_denon_marantz_input",
                warnings=("invalid_denon_marantz_input",),
                nonfatal=True,
                hardware_validation_claimed=False,
                command_sent=False,
            )
        return self.send(command)

    def query_power(self) -> AvrResult:
        return self.send(build_query_power_command())

    def query_input(self) -> AvrResult:
        return self.send(build_query_input_command())

    def run(self, action: str, **kwargs: object) -> AvrResult:
        normalized = _clean_text(action).lower()
        if normalized in {"power_on", "on"}:
            return self.power_on()
        if normalized in {"input_select", "select_input", "input"}:
            return self.select_input(kwargs.get("input_name"))
        if normalized in {"query_power", "power_query"}:
            return self.query_power()
        if normalized in {"query_input", "input_query"}:
            return self.query_input()
        return AvrResult(
            ok=False,
            action=normalized or "unknown",
            backend=AVR_BACKEND_DENON_MARANTZ,
            message="unsupported_denon_marantz_action",
            warnings=("unsupported_denon_marantz_action",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
