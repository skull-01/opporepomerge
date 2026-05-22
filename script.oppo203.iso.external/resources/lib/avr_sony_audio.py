"""Sony Audio Control API experimental helper for v2.9.10 Build 15B.

Build 15B adds a guarded, fakeable JSON POST request helper behind the
Build 15A experimental acknowledgement gate. It remains disabled by default via
the AVR framework, does not hook into playback sequencing, and never exports raw
Sony PSKs, passwords, credentials, tokens, or secrets in helper results.
"""

from __future__ import annotations

import json
from typing import Callable
from urllib import error, request

try:
    from .avr_types import AVR_BACKEND_SONY_AUDIO_API, AvrResult
except ImportError:  # top-level/audit/test compatibility
    from avr_types import AVR_BACKEND_SONY_AUDIO_API, AvrResult  # type: ignore

SONY_AUDIO_API_BACKEND_ID = AVR_BACKEND_SONY_AUDIO_API
SONY_AUDIO_EXPERIMENTAL_ACK_SETTING = "sony_avr_experimental_acknowledged"
SONY_AUDIO_PSK_SETTING = "sony_avr_psk"
SONY_AUDIO_API_PATH_SETTING = "sony_avr_api_path"
SONY_AUDIO_PLAYER_INPUT_URI_SETTING = "sony_avr_player_input_uri"
SONY_AUDIO_RESTORE_INPUT_URI_SETTING = "sony_avr_restore_input_uri"
SONY_AUDIO_LIVE_API_CALLS_ENABLED = True
SONY_AUDIO_REQUEST_HELPER_AVAILABLE = True
SONY_AUDIO_EXPERIMENTAL = True
SONY_SECRET_REDACTION = "<redacted>"
DEFAULT_SONY_AUDIO_API_PATH = "/sony/audio"
DEFAULT_SONY_AUDIO_TIMEOUT = 3.0

_SECRET_KEY_FRAGMENTS = ("psk", "password", "credential", "token", "secret")
SonyPost = Callable[[str, bytes, dict[str, str], float], bytes | str]


def _settings_dict(settings: dict[str, object] | object | None) -> dict[str, object]:
    if settings is None:
        return {}
    if isinstance(settings, dict):
        return dict(settings)
    if hasattr(settings, "data") and isinstance(settings.data, dict):
        return dict(settings.data)
    if hasattr(settings, "items"):
        try:
            return dict(settings.items())  # type: ignore[attr-defined]
        except Exception:
            return {}
    return {}


def _truthy(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = "" if value is None else str(value).strip().lower()
    if text == "":
        return default
    return text in {"1", "true", "yes", "on", "acknowledged"}


def _clean_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _timeout(value: object, default: float = DEFAULT_SONY_AUDIO_TIMEOUT) -> float:
    try:
        parsed = float(_clean_text(value) or default)
    except (TypeError, ValueError):
        return float(default)
    if parsed <= 0 or parsed > 30:
        return float(default)
    return parsed


def is_experimental_acknowledged(settings: dict[str, object] | object | None) -> bool:
    """Return True only when Sony AVR experimental use is explicitly acknowledged."""
    data = _settings_dict(settings)
    return _truthy(data.get(SONY_AUDIO_EXPERIMENTAL_ACK_SETTING, "false"), False)


def redact_secret(value: object, visible_prefix: int = 3, visible_suffix: int = 2) -> str:
    """Return a non-secret support representation for Sony AVR credentials."""
    text = "" if value is None else str(value)
    if not text:
        return ""
    if len(text) <= visible_prefix + visible_suffix + 3:
        return SONY_SECRET_REDACTION
    return f"{text[:visible_prefix]}...{text[-visible_suffix:]}"


def redact_secret_in_text(text: object, settings: dict[str, object] | object | None = None) -> str:
    """Redact configured Sony secrets from arbitrary diagnostic text."""
    safe = "" if text is None else str(text)
    data = _settings_dict(settings)
    for key, value in data.items():
        key_text = str(key).lower()
        value_text = "" if value is None else str(value)
        if value_text and any(fragment in key_text for fragment in _SECRET_KEY_FRAGMENTS):
            safe = safe.replace(value_text, SONY_SECRET_REDACTION)
    return safe


def sanitized_settings(settings: dict[str, object] | object | None) -> dict[str, object]:
    """Return Sony AVR settings safe for diagnostics/export."""
    data = _settings_dict(settings)
    sanitized: dict[str, object] = {}
    for key, value in data.items():
        key_text = str(key).lower()
        if any(fragment in key_text for fragment in _SECRET_KEY_FRAGMENTS):
            sanitized[key] = redact_secret(value)
        else:
            sanitized[key] = redact_secret_in_text(value, data) if isinstance(value, str) else value
    return sanitized


def validation_metadata(settings: dict[str, object] | object | None) -> dict[str, object]:
    """Return validation metadata without contacting a Sony AVR."""
    data = _settings_dict(settings)
    acknowledged = is_experimental_acknowledged(data)
    psk = str(data.get(SONY_AUDIO_PSK_SETTING, "") or "")
    host = str(data.get("avr_host", "") or "")
    input_uri = str(
        data.get(SONY_AUDIO_PLAYER_INPUT_URI_SETTING, data.get("avr_player_input", "")) or ""
    )
    warnings: list[str] = []
    missing: list[str] = []
    if not acknowledged:
        warnings.append("sony_audio_api_experimental_acknowledgement_required")
    if not host:
        missing.append("avr_host")
    if not input_uri:
        missing.append("sony_avr_player_input_uri")
    if not psk:
        missing.append(SONY_AUDIO_PSK_SETTING)
        warnings.append("sony_audio_api_psk_missing")
    return {
        "backend": SONY_AUDIO_API_BACKEND_ID,
        "experimental": True,
        "acknowledged": acknowledged,
        "skeleton_available": True,
        "live_api_calls_enabled": SONY_AUDIO_LIVE_API_CALLS_ENABLED,
        "request_helper_available": SONY_AUDIO_REQUEST_HELPER_AVAILABLE,
        "driver_available": True,
        "psk_redacted": redact_secret(psk),
        "host_configured": bool(host),
        "player_input_uri_configured": bool(input_uri),
        "missing": tuple(dict.fromkeys(missing)),
        "warnings": tuple(dict.fromkeys(warnings)),
        "hardware_validation_claimed": False,
    }


def build_refusal_result(
    action: str, settings: dict[str, object] | object | None, message: str = ""
) -> AvrResult:
    """Return a non-commanding refusal result for unacknowledged Sony AVR actions."""
    meta = validation_metadata(settings)
    warnings = list(meta.get("warnings", ()))
    if not meta.get("acknowledged", False):
        warnings.append("sony_audio_api_refused_without_acknowledgement")
    return AvrResult(
        ok=False,
        action=action,
        backend=SONY_AUDIO_API_BACKEND_ID,
        message=message
        or "Sony Audio Control API is experimental; no command was sent without explicit acknowledgement.",
        warnings=tuple(dict.fromkeys(str(item) for item in warnings)),
        nonfatal=True,
        hardware_validation_claimed=False,
        command_sent=False,
    )


def build_sony_audio_url(host: object, api_path: object = DEFAULT_SONY_AUDIO_API_PATH) -> str:
    host_text = _clean_text(host).rstrip("/")
    if not host_text:
        raise ValueError("avr_host_missing")
    if "/" in host_text and not host_text.startswith(("http://", "https://")):
        raise ValueError("invalid_sony_audio_host")
    path = _clean_text(api_path) or DEFAULT_SONY_AUDIO_API_PATH
    if not path.startswith("/") or ".." in path or "\r" in path or "\n" in path:
        raise ValueError("invalid_sony_audio_api_path")
    if host_text.startswith(("http://", "https://")):
        return host_text + path
    return f"http://{host_text}{path}"


def build_sony_audio_payload(
    method: object, params: object | None = None, *, request_id: int = 1, version: str = "1.0"
) -> bytes:
    method_text = _clean_text(method)
    if not method_text or any(ch in method_text for ch in ("/", "\\", "\r", "\n")):
        raise ValueError("invalid_sony_audio_method")
    params_value: object = [] if params is None else params
    return json.dumps(
        {
            "method": method_text,
            "params": params_value,
            "id": int(request_id),
            "version": str(version),
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def build_power_on_payload() -> bytes:
    return build_sony_audio_payload("setPowerStatus", [{"status": "active"}])


def build_set_input_payload(input_uri: object) -> bytes:
    uri = _clean_text(input_uri)
    if not uri or "\r" in uri or "\n" in uri:
        raise ValueError("invalid_sony_audio_input_uri")
    return build_sony_audio_payload("setPlayContent", [{"uri": uri}])


def build_status_payload() -> bytes:
    return build_sony_audio_payload("getPowerStatus", [])


def _default_post(url: str, payload: bytes, headers: dict[str, str], timeout: float) -> bytes:
    req = request.Request(url, data=payload, headers=headers, method="POST")
    with request.urlopen(req, timeout=timeout) as response:  # nosec - explicit user-configured local API endpoint
        return response.read()


def _parse_response(
    raw: bytes | str, settings: dict[str, object]
) -> tuple[bool, str, tuple[str, ...]]:
    text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
    redacted = redact_secret_in_text(text, settings)
    try:
        parsed = json.loads(text or "{}")
    except Exception:
        return False, "invalid_json", ("sony_audio_api_invalid_json_nonfatal",)
    if isinstance(parsed, dict) and "error" in parsed:
        return (
            False,
            redact_secret_in_text(parsed.get("error", "sony_audio_api_error"), settings),
            ("sony_audio_api_error_nonfatal",),
        )
    if isinstance(parsed, dict) and "result" in parsed:
        return True, "sony_audio_api_command_sent", ()
    if isinstance(parsed, dict) and parsed.get("status") in {"ok", "OK", "success"}:
        return True, "sony_audio_api_command_sent", ()
    if isinstance(parsed, dict) and parsed == {}:
        return True, "sony_audio_api_command_sent", ()
    return (
        False,
        redacted[:120] or "sony_audio_api_unexpected_response",
        ("sony_audio_api_unexpected_response_nonfatal",),
    )


def send_sony_audio_request(
    settings: dict[str, object] | object | None,
    method: object,
    params: object | None = None,
    *,
    action: str = "sony_audio_api_request",
    post: SonyPost | None = None,
) -> AvrResult:
    """Send one guarded Sony Audio API JSON POST request.

    The helper is fakeable for tests, requires the explicit experimental
    acknowledgement flag, never returns raw PSKs/secrets, and converts all API,
    network, timeout, JSON, and driver errors into nonfatal ``AvrResult`` values.
    """
    data = _settings_dict(settings)
    meta = validation_metadata(data)
    if not meta.get("acknowledged", False):
        return build_refusal_result(action, data)
    missing = [
        item for item in meta.get("missing", ()) if item not in {"sony_avr_player_input_uri"}
    ]
    if missing:
        return AvrResult(
            ok=False,
            action=action,
            backend=SONY_AUDIO_API_BACKEND_ID,
            message="sony_audio_api_config_incomplete",
            warnings=tuple(
                dict.fromkeys([*map(str, meta.get("warnings", ())), "avr_config_incomplete"])
            ),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )
    try:
        url = build_sony_audio_url(
            data.get("avr_host", ""),
            data.get(SONY_AUDIO_API_PATH_SETTING, DEFAULT_SONY_AUDIO_API_PATH),
        )
        payload = build_sony_audio_payload(method, params)
        psk = _clean_text(data.get(SONY_AUDIO_PSK_SETTING, ""))
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        if psk:
            headers["X-Auth-PSK"] = psk
        sender = post or _default_post
        raw = sender(
            url, payload, headers, _timeout(data.get("avr_timeout", DEFAULT_SONY_AUDIO_TIMEOUT))
        )
        ok, message, warnings = _parse_response(raw, data)
        return AvrResult(
            ok=ok,
            action=action,
            backend=SONY_AUDIO_API_BACKEND_ID,
            message=message,
            warnings=warnings,
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=ok,
        )
    except error.HTTPError as exc:
        warning = (
            "sony_audio_api_auth_error_nonfatal"
            if exc.code in {401, 403}
            else "sony_audio_api_http_error_nonfatal"
        )
        return AvrResult(
            False, action, SONY_AUDIO_API_BACKEND_ID, warning, (warning,), True, False, False
        )
    except (TimeoutError, OSError) as exc:
        return AvrResult(
            False,
            action,
            SONY_AUDIO_API_BACKEND_ID,
            exc.__class__.__name__,
            ("avr_network_error_nonfatal",),
            True,
            False,
            False,
        )
    except Exception as exc:
        return AvrResult(
            False,
            action,
            SONY_AUDIO_API_BACKEND_ID,
            exc.__class__.__name__,
            ("avr_driver_error_nonfatal",),
            True,
            False,
            False,
        )


class SonyAudioApiAvrController:
    """Guarded experimental Sony Audio Control API adapter."""

    backend = SONY_AUDIO_API_BACKEND_ID

    def __init__(
        self, settings: dict[str, object] | object | None = None, *, post: SonyPost | None = None
    ):
        self.settings = _settings_dict(settings)
        self.post = post

    def run(self, action: str, method: object, params: object | None = None) -> AvrResult:
        return send_sony_audio_request(self.settings, method, params, action=action, post=self.post)

    def power_on(self) -> AvrResult:
        return self.run("power_on", "setPowerStatus", [{"status": "active"}])

    def select_input(self, input_uri: object | None = None) -> AvrResult:
        uri = _clean_text(
            input_uri
            if input_uri is not None
            else self.settings.get(
                SONY_AUDIO_PLAYER_INPUT_URI_SETTING, self.settings.get("avr_player_input", "")
            )
        )
        if not uri:
            return AvrResult(
                False,
                "input_select",
                self.backend,
                "invalid_sony_audio_input_uri",
                ("avr_config_incomplete",),
                True,
                False,
                False,
            )
        return self.run("input_select", "setPlayContent", [{"uri": uri}])

    def query_power(self) -> AvrResult:
        return self.run("query_power", "getPowerStatus", [])
