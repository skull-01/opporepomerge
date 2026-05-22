"""Yamaha MusicCast / YXC AVR HTTP command helper for v2.9.10 Build 13.

This module is intentionally narrow: it implements only Yamaha MusicCast/YXC
HTTP GET helpers behind the disabled-by-default AVR framework.  It does not add
playback sequencing, discovery, polling, volume automation, or hardware
validation claims.  Every network/API failure is represented as a nonfatal
``AvrResult`` so future optional AVR sequencing cannot destabilize OPPO/Kodi
playback routing.
"""

from __future__ import annotations

import json
import re
from typing import Callable
from urllib import parse, request

try:
    from .avr_types import AVR_BACKEND_YAMAHA_YXC, AvrResult
except ImportError:  # top-level/audit/test compatibility
    from avr_types import AVR_BACKEND_YAMAHA_YXC, AvrResult  # type: ignore

DEFAULT_YAMAHA_YXC_PORT = 80
DEFAULT_YAMAHA_YXC_TIMEOUT = 3.0
YAMAHA_YXC_SET_POWER_PATH = "/YamahaExtendedControl/v1/main/setPower"
YAMAHA_YXC_SET_INPUT_PATH = "/YamahaExtendedControl/v1/main/setInput"
YAMAHA_YXC_GET_STATUS_PATH = "/YamahaExtendedControl/v1/main/getStatus"
VALID_YAMAHA_INPUT_RE = re.compile(r"^[A-Za-z0-9_/-]{1,64}$")

HttpGet = Callable[[str, float], bytes | str]


def _clean_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def yamaha_port(value: object, default: int = DEFAULT_YAMAHA_YXC_PORT) -> int:
    try:
        parsed = int(_clean_text(value) or default)
    except (TypeError, ValueError):
        return int(default)
    if parsed < 1 or parsed > 65535:
        return int(default)
    return parsed


def yamaha_timeout(value: object, default: float = DEFAULT_YAMAHA_YXC_TIMEOUT) -> float:
    try:
        parsed = float(_clean_text(value) or default)
    except (TypeError, ValueError):
        return float(default)
    if parsed <= 0 or parsed > 30:
        return float(default)
    return parsed


def validate_yamaha_input(input_name: object) -> str:
    text = _clean_text(input_name)
    if not VALID_YAMAHA_INPUT_RE.fullmatch(text):
        raise ValueError("invalid_yamaha_yxc_input")
    return text


def build_yamaha_base_url(host: object, port: object = DEFAULT_YAMAHA_YXC_PORT) -> str:
    host_text = _clean_text(host).rstrip("/")
    if not host_text:
        raise ValueError("avr_host_missing")
    if "/" in host_text and not host_text.startswith(("http://", "https://")):
        raise ValueError("invalid_yamaha_yxc_host")
    if host_text.startswith(("http://", "https://")):
        return host_text
    parsed_port = yamaha_port(port)
    if parsed_port == 80:
        return f"http://{host_text}"
    return f"http://{host_text}:{parsed_port}"


def build_power_on_url(host: object, *, port: object = DEFAULT_YAMAHA_YXC_PORT) -> str:
    return (
        build_yamaha_base_url(host, port)
        + YAMAHA_YXC_SET_POWER_PATH
        + "?"
        + parse.urlencode({"power": "on"})
    )


def build_input_select_url(
    host: object, input_name: object, *, port: object = DEFAULT_YAMAHA_YXC_PORT
) -> str:
    safe_input = validate_yamaha_input(input_name)
    return (
        build_yamaha_base_url(host, port)
        + YAMAHA_YXC_SET_INPUT_PATH
        + "?"
        + parse.urlencode({"input": safe_input})
    )


def build_status_url(host: object, *, port: object = DEFAULT_YAMAHA_YXC_PORT) -> str:
    return build_yamaha_base_url(host, port) + YAMAHA_YXC_GET_STATUS_PATH


def _default_http_get(url: str, timeout: float) -> bytes:
    with request.urlopen(
        url, timeout=timeout
    ) as response:  # nosec B310 - user-configured local AVR endpoint; guarded/optional.
        return response.read()


def _decode_response(payload: bytes | str) -> dict[str, object]:
    if isinstance(payload, bytes):
        text = payload.decode("utf-8", errors="replace")
    else:
        text = str(payload)
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("yamaha_yxc_json_not_object")
    return parsed


def _response_code_message(response_code: object) -> str:
    try:
        code = int(response_code)
    except (TypeError, ValueError):
        return "yamaha_yxc_response_code_invalid"
    return f"yamaha_yxc_response_code_{code}"


def send_yamaha_get(
    host: object,
    path_url: str,
    *,
    port: object = DEFAULT_YAMAHA_YXC_PORT,
    timeout: object = DEFAULT_YAMAHA_YXC_TIMEOUT,
    http_get: HttpGet | None = None,
) -> AvrResult:
    """Run one Yamaha YXC HTTP GET and return a nonfatal result."""
    parsed_timeout = yamaha_timeout(timeout)
    getter = http_get or _default_http_get
    try:
        url = (
            path_url
            if path_url.startswith(("http://", "https://"))
            else build_yamaha_base_url(host, port) + path_url
        )
    except ValueError as exc:
        return AvrResult(
            ok=False,
            action="yamaha_yxc_command",
            backend=AVR_BACKEND_YAMAHA_YXC,
            message=str(exc),
            warnings=("avr_config_incomplete",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    try:
        payload = getter(url, parsed_timeout)
        decoded = _decode_response(payload)
        message = _response_code_message(decoded.get("response_code"))
        ok = message == "yamaha_yxc_response_code_0"
        return AvrResult(
            ok=ok,
            action="yamaha_yxc_command",
            backend=AVR_BACKEND_YAMAHA_YXC,
            message=message,
            warnings=() if ok else ("yamaha_yxc_nonzero_response_code",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=True,
        )
    except json.JSONDecodeError:
        return AvrResult(
            ok=False,
            action="yamaha_yxc_command",
            backend=AVR_BACKEND_YAMAHA_YXC,
            message="yamaha_yxc_invalid_json",
            warnings=("yamaha_yxc_invalid_json",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=True,
        )
    except (OSError, TimeoutError) as exc:
        return AvrResult(
            ok=False,
            action="yamaha_yxc_command",
            backend=AVR_BACKEND_YAMAHA_YXC,
            message=exc.__class__.__name__,
            warnings=("avr_network_error_nonfatal",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    except Exception as exc:
        return AvrResult(
            ok=False,
            action="yamaha_yxc_command",
            backend=AVR_BACKEND_YAMAHA_YXC,
            message=exc.__class__.__name__,
            warnings=("avr_driver_error_nonfatal",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )


class YamahaYxcAvrController:
    """Small HTTP GET adapter for Yamaha MusicCast/YXC AVR families."""

    backend = AVR_BACKEND_YAMAHA_YXC

    def __init__(
        self,
        host: object,
        *,
        port: object = DEFAULT_YAMAHA_YXC_PORT,
        timeout: object = DEFAULT_YAMAHA_YXC_TIMEOUT,
        player_input: object = "",
        http_get: HttpGet | None = None,
    ) -> None:
        self.host = _clean_text(host)
        self.port = yamaha_port(port)
        self.timeout = yamaha_timeout(timeout)
        self.player_input = _clean_text(player_input)
        self.http_get = http_get

    def send_url(self, url: str) -> AvrResult:
        return send_yamaha_get(
            self.host,
            url,
            port=self.port,
            timeout=self.timeout,
            http_get=self.http_get,
        )

    def power_on(self) -> AvrResult:
        try:
            url = build_power_on_url(self.host, port=self.port)
        except ValueError as exc:
            return AvrResult(
                False,
                "yamaha_yxc_power_on",
                AVR_BACKEND_YAMAHA_YXC,
                str(exc),
                ("avr_config_incomplete",),
                True,
                False,
                False,
            )
        return self.send_url(url)

    def select_input(self, input_name: object | None = None) -> AvrResult:
        try:
            url = build_input_select_url(
                self.host, self.player_input if input_name is None else input_name, port=self.port
            )
        except ValueError:
            return AvrResult(
                ok=False,
                action="yamaha_yxc_input_select",
                backend=AVR_BACKEND_YAMAHA_YXC,
                message="invalid_yamaha_yxc_input",
                warnings=("invalid_yamaha_yxc_input",),
                nonfatal=True,
                hardware_validation_claimed=False,
                command_sent=False,
            )
        return self.send_url(url)

    def get_status(self) -> AvrResult:
        try:
            url = build_status_url(self.host, port=self.port)
        except ValueError as exc:
            return AvrResult(
                False,
                "yamaha_yxc_get_status",
                AVR_BACKEND_YAMAHA_YXC,
                str(exc),
                ("avr_config_incomplete",),
                True,
                False,
                False,
            )
        return self.send_url(url)

    def run(self, action: str, **kwargs: object) -> AvrResult:
        normalized = _clean_text(action).lower()
        if normalized in {"power_on", "on"}:
            return self.power_on()
        if normalized in {"input_select", "select_input", "input"}:
            return self.select_input(kwargs.get("input_name"))
        if normalized in {"get_status", "status", "query_status"}:
            return self.get_status()
        return AvrResult(
            ok=False,
            action=normalized or "unknown",
            backend=AVR_BACKEND_YAMAHA_YXC,
            message="unsupported_yamaha_yxc_action",
            warnings=("unsupported_yamaha_yxc_action",),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
