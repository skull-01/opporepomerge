"""Diagnostics dashboard (v1.0.9).

A single one-shot pre-flight that gathers everything needed for a
support ticket and either renders a dialog or saves a timestamped
report to addon_data/.

Every external dependency (TCP, HTTP, UDP, Kodi APIs) flows through
injection points so the suite is fully unit-testable without sockets,
without files, and without Kodi.

Public API
----------
- run(host, port, mac=None, *, http_check=None, tcp_check=None,
      svm_check=None, wol_check=None, kodi_info=None, capabilities=None,
      now=None) -> dict
- format_report(result) -> str  (human-readable text, ready to write)
- save_report(result, root_dir, *, now=None, writer=None) -> str
                                  (returns the absolute path written)
- default_path(root_dir, now=None) -> str
- redact(text) -> str            (mask MACs and IPv4 addresses)
"""

from __future__ import annotations

import os
import posixpath
import re
import time as _time
from typing import Any, Callable, cast

# Probe callables are injected and may take any positional args; they return a
# result mapping with at least an "ok" key.
Probe = Callable[..., "dict[str, Any]"]
# writer(path, text) -> None, an optional injection point for save_report.
Writer = Callable[[str, str], None]

_MAC_RE = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def redact(text: str | None) -> str | None:
    """Mask MAC and IPv4 addresses for shareable reports."""
    if not text:
        return text
    text = _MAC_RE.sub("xx:xx:xx:xx:xx:xx", text)
    text = _IPV4_RE.sub("x.x.x.x", text)
    return text


def _ts(now: float | Callable[[], float] | None = None) -> str:
    # UTC keeps exported support-report filenames deterministic across timezones.
    t = _time.gmtime(now() if callable(now) else (now if now else _time.time()))
    return _time.strftime("%Y%m%d-%H%M%S", t)


def default_path(root_dir: str, now: float | Callable[[], float] | None = None) -> str:
    # Forward-slash join keeps addon-data paths portable; os.path.join would emit
    # "\" on Windows, which Kodi add-on paths do not use.
    return posixpath.join(root_dir, "diagnostics-" + _ts(now) + ".txt")


def _safe(
    call: Callable[[], dict[str, Any]], default: dict[str, Any] | None = None
) -> dict[str, Any]:
    try:
        return call()
    except Exception as exc:
        return {"ok": False, "error": str(exc)} if default is None else default


def run(
    host: str,
    port: int,
    mac: str | None = None,
    *,
    http_check: Probe | None = None,
    tcp_check: Probe | None = None,
    svm_check: Probe | None = None,
    wol_check: Probe | None = None,
    kodi_info: Probe | None = None,
    capabilities: Probe | None = None,
    now: float | Callable[[], float] | None = None,
) -> dict[str, object]:
    """Run the full pre-flight. All probes are injected.

    Each probe callable returns a dict with at least an "ok" boolean.
    Missing probes default to {"ok": None, "skipped": True}.
    """

    def _skip(reason: str = "not provided") -> dict[str, object]:
        return {"ok": None, "skipped": True, "reason": reason}

    result: dict[str, object] = {
        "host": host,
        "port": int(port) if port is not None else None,
        "mac": mac,
        "timestamp": _ts(now),
        "tcp": _safe(lambda: tcp_check(host, int(port))) if tcp_check else _skip(),
        "http": _safe(lambda: http_check(host)) if http_check else _skip(),
        "svm": _safe(lambda: svm_check(host, int(port))) if svm_check else _skip(),
        "wol": _safe(lambda: wol_check(mac)) if (wol_check and mac) else _skip("no MAC"),
        "kodi": _safe(lambda: kodi_info()) if kodi_info else _skip(),
        "capabilities": _safe(lambda: capabilities()) if capabilities else _skip(),
    }
    # Top-level overall: True iff every non-skipped probe is ok.
    overall = True
    any_run = False
    for k in ("tcp", "http", "svm", "wol", "kodi", "capabilities"):
        v = cast("dict[str, object]", result[k])
        if isinstance(v, dict) and v.get("skipped"):
            continue
        any_run = True
        if not v.get("ok"):
            overall = False
    result["overall_ok"] = bool(any_run and overall)
    return result


def format_report(result: object) -> str:
    """Render a `run()` result as a human-readable text block."""
    if not isinstance(result, dict):
        return "<invalid result>"
    lines = []
    lines.append("OPPO ISO External - Diagnostics Report")
    lines.append("=" * 44)
    lines.append("Timestamp:  " + str(result.get("timestamp", "")))
    lines.append("Host:       " + str(result.get("host", "")))
    lines.append("Port:       " + str(result.get("port", "")))
    lines.append("MAC:        " + str(result.get("mac", "") or "(not set)"))
    lines.append("Overall OK: " + ("yes" if result.get("overall_ok") else "no"))
    lines.append("")
    for k in ("tcp", "http", "svm", "wol", "kodi", "capabilities"):
        v = result.get(k, {})
        lines.append("[" + k.upper() + "]")
        if v.get("skipped"):
            lines.append("  skipped: " + str(v.get("reason", "")))
        else:
            lines.append("  ok:    " + str(v.get("ok")))
            for kk, vv in v.items():
                if kk in ("ok", "skipped", "reason"):
                    continue
                lines.append("  " + str(kk) + ": " + str(vv))
        lines.append("")
    return "\n".join(lines)


def save_report(
    result: object,
    root_dir: str,
    *,
    now: float | Callable[[], float] | None = None,
    writer: Writer | None = None,
) -> str:
    """Write the formatted report to addon_data/diagnostics-<ts>.txt.

    `writer` is an optional callable(path, text) for tests; the default
    creates the directory and writes the file.  Returns the path.
    """
    path = default_path(root_dir, now=now)
    text = format_report(result)
    if writer is None:
        os.makedirs(root_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        writer(path, text)
    return path
