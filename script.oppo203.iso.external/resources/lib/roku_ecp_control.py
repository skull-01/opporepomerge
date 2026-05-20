"""Roku ECP input-switching helper for v2.9.10 Build 7.

This module is intentionally small and dependency-free.  It only sends
allowlisted local Roku ECP keypress requests and does not perform discovery,
polling, or credential handling.  Failures raise ``RokuEcpError`` so the
existing TV-switching wrapper can keep playback non-fatal.
"""
from __future__ import annotations

import urllib.error
import urllib.request

DEFAULT_ROKU_ECP_PORT = 8060

# Roku TV input key names are passed as a path segment to /keypress/<key>.
# Keep this list intentionally narrow so user-provided keys cannot inject
# additional URL path/query content.
ALLOWED_ROKU_ECP_KEYS = (
    "InputHDMI1",
    "InputHDMI2",
    "InputHDMI3",
    "InputHDMI4",
    "InputAV1",
    "InputTuner",
)


class RokuEcpError(RuntimeError):
    """Raised when a Roku ECP request cannot be prepared or completed."""


def normalize_roku_key(key: str) -> str:
    """Return a validated Roku ECP key or raise ``RokuEcpError``.

    The validation is allowlist-based rather than character-sanitizing.  This
    prevents path injection such as ``InputHDMI1/../../query`` or strings with
    query delimiters from ever being placed in the ECP URL path.
    """
    if not isinstance(key, str):
        raise RokuEcpError("Roku ECP key must be a string.")
    normalized = key.strip()
    if normalized not in ALLOWED_ROKU_ECP_KEYS:
        raise RokuEcpError(f"Roku ECP key is not allowlisted: {normalized}")
    return normalized


def _parse_port(value: object) -> int:
    try:
        port = int(str(value).strip() or DEFAULT_ROKU_ECP_PORT)
    except (TypeError, ValueError):
        raise RokuEcpError(f"Invalid Roku ECP port: {value}")
    if port < 1 or port > 65535:
        raise RokuEcpError(f"Invalid Roku ECP port: {port}")
    return port


def build_keypress_url(settings: object, key: str) -> str:
    """Build a local Roku ECP keypress URL after strict validation."""
    try:
        host = str(settings.get("tv_ip", "")).strip()  # type: ignore[attr-defined]
        port_value = settings.get("roku_ecp_port", str(DEFAULT_ROKU_ECP_PORT))  # type: ignore[attr-defined]
    except AttributeError as exc:
        raise RokuEcpError("Roku ECP settings object must provide get().") from exc
    if not host:
        raise RokuEcpError("TV IP is required for Roku ECP backend.")
    if "/" in host or "?" in host or "#" in host:
        raise RokuEcpError("TV IP/host must not contain URL path or query characters.")
    port = _parse_port(port_value)
    validated_key = normalize_roku_key(key)
    return f"http://{host}:{port}/keypress/{validated_key}"


def send_keypress(settings: object, key: str, urlopen=None, timeout: int = 10) -> str:
    """POST an allowlisted Roku ECP keypress request and return response text."""
    opener = urlopen or urllib.request.urlopen
    url = build_keypress_url(settings, key)
    request = urllib.request.Request(url, data=b"", method="POST")
    try:
        with opener(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            status = int(getattr(response, "status", 200))
            if status >= 400:
                raise RokuEcpError(f"Roku ECP returned HTTP {status}: {body}")
            return body
    except RokuEcpError:
        raise
    except urllib.error.URLError as exc:
        raise RokuEcpError(f"Roku ECP request failed: {exc}") from exc


def switch_input(settings: object, key: str, urlopen=None) -> str:
    """Switch a Roku TV input by sending one allowlisted ECP keypress."""
    injected = None
    try:
        injected = settings.get("_roku_urlopen", None)  # type: ignore[attr-defined]
    except AttributeError:
        injected = None
    return send_keypress(settings, key, urlopen=injected or urlopen)
