"""SmartThings experimental safety and request helpers for v2.9.10 Build 9B.

Build 9B adds a guarded request helper that can be exercised with fake API
tests. It remains experimental: requests require explicit acknowledgement,
results are non-fatal, tokens are never returned in diagnostics, and hardware
validation is not claimed.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

SMARTTHINGS_BACKEND_ID = "smartthings"
SMARTTHINGS_ACK_SETTING = "smartthings_experimental_acknowledged"
SMARTTHINGS_TOKEN_SETTING = "smartthings_token"
SMARTTHINGS_DEVICE_ID_SETTING = "smartthings_device_id"
SMARTTHINGS_OPPO_INPUT_SETTING = "smartthings_oppo_input_id"
SMARTTHINGS_KODI_INPUT_SETTING = "smartthings_kodi_input_id"
SMARTTHINGS_API_BASE_URL_SETTING = "smartthings_api_base_url"
SMARTTHINGS_API_BASE_URL = "https://api.smartthings.com/v1"
SMARTTHINGS_LIVE_API_CALLS_ENABLED = True
TOKEN_REDACTION = "<redacted>"
DEFAULT_TIMEOUT_SECONDS = 10

SmartThingsOpener = Callable[..., Any]


def is_acknowledged(settings: dict[str, object] | object) -> bool:
    """Return whether the user explicitly acknowledged experimental status."""
    value = ""
    if hasattr(settings, "get"):
        value = settings.get(SMARTTHINGS_ACK_SETTING, "")  # type: ignore[assignment, call-arg]
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "on", "acknowledged"}


def redact_token(value: object, visible_prefix: int = 4, visible_suffix: int = 2) -> str:
    """Return a non-secret representation of a SmartThings token.

    Empty values stay empty for validation messages. Non-empty values never
    return the full token. Short tokens are fully redacted; longer tokens keep a
    small prefix/suffix to aid support without leaking credentials.
    """
    token = "" if value is None else str(value)
    if not token:
        return ""
    if len(token) <= visible_prefix + visible_suffix + 3:
        return TOKEN_REDACTION
    return f"{token[:visible_prefix]}...{token[-visible_suffix:]}"


def redact_secret_in_text(text: object, token: object = "") -> str:
    """Return text with any known SmartThings token removed."""
    safe_text = "" if text is None else str(text)
    token_text = "" if token is None else str(token)
    if token_text:
        safe_text = safe_text.replace(token_text, TOKEN_REDACTION)
    return safe_text


def sanitized_settings(settings: dict[str, object]) -> dict[str, object]:
    """Return a copy with SmartThings token redacted for diagnostics."""
    sanitized = dict(settings)
    if SMARTTHINGS_TOKEN_SETTING in sanitized:
        sanitized[SMARTTHINGS_TOKEN_SETTING] = redact_token(sanitized.get(SMARTTHINGS_TOKEN_SETTING))
    return sanitized


def _base_result(settings: dict[str, object], input_id: object = "") -> dict[str, object]:
    token = settings.get(SMARTTHINGS_TOKEN_SETTING, "")
    return {
        "backend": SMARTTHINGS_BACKEND_ID,
        "experimental": True,
        "ok": False,
        "nonfatal": True,
        "status_code": None,
        "error_code": "",
        "detail": "",
        "network_called": False,
        "input_id_present": bool(str(input_id or "")),
        "token_redacted": redact_token(token),
        "hardware_validation_claimed": False,
    }


def validation_metadata(settings: dict[str, object]) -> dict[str, object]:
    """Return metadata-only SmartThings validation state without network IO."""
    token = str(settings.get(SMARTTHINGS_TOKEN_SETTING, "") or "")
    device_id = str(settings.get(SMARTTHINGS_DEVICE_ID_SETTING, "") or "")
    acknowledged = is_acknowledged(settings)
    warnings: list[str] = []
    if not acknowledged:
        warnings.append("smartthings_experimental_acknowledgement_required")
    if not token:
        warnings.append("smartthings_token_missing")
    if not device_id:
        warnings.append("smartthings_device_id_missing")
    return {
        "backend": SMARTTHINGS_BACKEND_ID,
        "experimental": True,
        "acknowledged": acknowledged,
        "live_api_calls_enabled": SMARTTHINGS_LIVE_API_CALLS_ENABLED,
        "request_helper_available": True,
        "token_redaction_required": True,
        "token_redacted": redact_token(token),
        "device_id_present": bool(device_id),
        "warnings": tuple(warnings),
        "hardware_validation_claimed": False,
    }


def _build_command_payload(input_id: str) -> bytes:
    payload = {
        "commands": [
            {
                "component": "main",
                "capability": "mediaInputSource",
                "command": "setInputSource",
                "arguments": [input_id],
            }
        ]
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _build_request(settings: dict[str, object], input_id: str) -> urllib.request.Request:
    token = str(settings.get(SMARTTHINGS_TOKEN_SETTING, "") or "")
    device_id = str(settings.get(SMARTTHINGS_DEVICE_ID_SETTING, "") or "")
    base_url = str(settings.get(SMARTTHINGS_API_BASE_URL_SETTING, SMARTTHINGS_API_BASE_URL) or SMARTTHINGS_API_BASE_URL).rstrip("/")
    safe_device_id = urllib.parse.quote(device_id, safe="")
    url = f"{base_url}/devices/{safe_device_id}/commands"
    return urllib.request.Request(
        url,
        data=_build_command_payload(input_id),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
        },
        method="POST",
    )


def switch_input(
    settings: dict[str, object],
    input_id: object,
    opener: SmartThingsOpener | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    """Send a guarded SmartThings input command and return a non-fatal result.

    The function never raises for expected configuration, authorization, HTTP,
    or network failures. It returns sanitized metadata suitable for logs or
    diagnostic exports, and it never includes the raw SmartThings token.
    """
    input_text = str(input_id or "").strip()
    result = _base_result(settings, input_text)
    token = str(settings.get(SMARTTHINGS_TOKEN_SETTING, "") or "")
    device_id = str(settings.get(SMARTTHINGS_DEVICE_ID_SETTING, "") or "")

    if not is_acknowledged(settings):
        result.update({"error_code": "experimental_acknowledgement_required", "detail": "SmartThings experimental acknowledgement is required."})
        return result
    if not token:
        result.update({"error_code": "smartthings_token_missing", "detail": "SmartThings token is required."})
        return result
    if not device_id:
        result.update({"error_code": "smartthings_device_id_missing", "detail": "SmartThings device ID is required."})
        return result
    if not input_text:
        result.update({"error_code": "smartthings_input_id_missing", "detail": "SmartThings input ID is required."})
        return result

    request = _build_request(settings, input_text)
    urlopen = opener or urllib.request.urlopen
    result["request_url"] = request.full_url
    result["request_method"] = request.get_method()

    try:
        with urlopen(request, timeout=timeout) as response:  # type: ignore[misc]
            body = response.read().decode("utf-8", errors="replace")
            status = int(getattr(response, "status", getattr(response, "code", 200)))
            result.update({
                "ok": 200 <= status < 300,
                "status_code": status,
                "detail": redact_secret_in_text(body, token),
                "network_called": True,
            })
            if not result["ok"]:
                result["error_code"] = "smartthings_http_error"
            return result
    except urllib.error.HTTPError as exc:
        status = int(getattr(exc, "code", 0) or 0)
        code = "smartthings_auth_failed" if status in (401, 403) else "smartthings_http_error"
        detail = redact_secret_in_text(getattr(exc, "reason", "") or str(exc), token)
        result.update({"status_code": status, "error_code": code, "detail": detail, "network_called": True})
        return result
    except urllib.error.URLError as exc:
        result.update({
            "error_code": "smartthings_network_error",
            "detail": redact_secret_in_text(getattr(exc, "reason", "") or str(exc), token),
            "network_called": True,
        })
        return result
    except Exception as exc:  # pragma: no cover - defensive for unusual opener failures
        result.update({
            "error_code": "smartthings_request_failed",
            "detail": redact_secret_in_text(str(exc), token),
            "network_called": True,
        })
        return result


def switch_target(
    settings: dict[str, object],
    target: str,
    opener: SmartThingsOpener | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    """Switch to the configured OPPO or Kodi SmartThings input ID."""
    key = SMARTTHINGS_OPPO_INPUT_SETTING if target == "oppo" else SMARTTHINGS_KODI_INPUT_SETTING
    return switch_input(settings, settings.get(key, ""), opener=opener, timeout=timeout)
