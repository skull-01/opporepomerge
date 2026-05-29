"""Lightweight diagnostic summary helper for OPPO ISO External.

v2.5.0 Build 6 adds a read-only support helper that summarizes version,
setup completeness, key configuration state, and obvious path/dependency
warnings.  It intentionally does not launch players, touch hardware, mutate
settings, or require Kodi modules.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import cast

try:  # pragma: no cover - import style varies under Kodi and pytest
    from .settings_reader import Settings, read_settings
except Exception:  # pragma: no cover
    from settings_reader import Settings, read_settings  # type: ignore

REQUIRED_SETTINGS = (
    "python_path",
    "oppo_ip",
    "oppo_port",
    "oppo_start_mode",
    "playback_architecture",
)

PATH_SETTINGS = ("python_path",)


def _as_settings(settings: object = None, addon_data_dir: str | None = None) -> Settings:
    """Return a Settings object without mutating persistent settings."""
    if isinstance(settings, Settings):
        return settings
    if isinstance(settings, dict):
        return Settings(settings)
    if addon_data_dir:
        return read_settings(addon_data_dir)
    return Settings({})


def addon_version(root_dir: str | None = None) -> str:
    """Return addon.xml version when available, else ``unknown``."""
    if not root_dir:
        return "unknown"
    addon_xml = Path(root_dir) / "addon.xml"
    try:
        return ET.parse(str(addon_xml)).getroot().attrib.get("version") or "unknown"
    except Exception:
        return "unknown"


def _path_status(
    settings: Settings, exists: Callable[[str], object] | None = None
) -> dict[str, dict[str, object]]:
    exists = exists or os.path.exists
    result: dict[str, dict[str, object]] = {}
    for key in PATH_SETTINGS:
        value = settings.get_path(key)
        configured = bool(value)
        try:
            present = bool(exists(value)) if configured else False
        except Exception:
            present = False
        # Do not expose full local paths by default.  Basename plus status is
        # enough for first-line support triage and avoids noisy/sensitive logs.
        result[key] = {
            "configured": configured,
            "exists": present,
            "name": os.path.basename(value) if value else "",
        }
    return result


def build_summary(
    settings: object = None,
    *,
    addon_data_dir: str | None = None,
    root_dir: str | None = None,
    path_exists: Callable[[str], object] | None = None,
) -> dict[str, object]:
    """Build a non-invasive diagnostic summary for support and AI handoff.

    The helper is deliberately read-only.  It only inspects supplied settings,
    optionally reads settings.xml through the existing tolerant reader, and
    optionally checks whether configured path-like dependencies exist.
    """
    cfg = _as_settings(settings=settings, addon_data_dir=addon_data_dir)
    validation: dict[str, object] = (
        cfg.validation_summary()
        if hasattr(cfg, "validation_summary")
        else {"missing": [], "warnings": []}
    )
    missing = list(cast("list[object]", validation.get("missing", [])))
    warnings = list(cast("list[object]", validation.get("warnings", [])))
    paths = _path_status(cfg, exists=path_exists)

    if paths.get("python_path", {}).get("configured") and not paths["python_path"].get("exists"):
        warnings.append("python_path_not_found")

    setup_complete = not missing and "settings_read_error" not in warnings
    summary = {
        "addon_version": addon_version(root_dir),
        "setup_complete": setup_complete,
        "ok": setup_complete and not warnings,
        "missing": missing,
        "warnings": warnings,
        "configuration": {
            "playback_architecture": cfg.get("playback_architecture"),
            "oppo_ip_configured": bool(str(cfg.get("oppo_ip", "")).strip()),
            "oppo_port": cfg.get_int("oppo_port", 23, minimum=1, maximum=65535),
            "hardware_model": cfg.get("oppo_hardware_model"),
            "wizard_last_exit": cfg.get("wizard_last_exit", ""),
            "wizard_recovery_available": cfg.get_bool("wizard_recovery_available", False),
        },
        "paths": paths,
    }
    return summary


def format_summary(summary: dict[str, object]) -> str:
    """Render a summary into a compact support-friendly text block."""
    if not isinstance(summary, dict):
        return "OPPO203 diagnostic summary unavailable"
    cfg = cast("dict[str, object]", summary.get("configuration", {}) or {})
    lines = [
        "OPPO203 Diagnostic Summary",
        f"Version: {summary.get('addon_version', 'unknown')}",
        f"Setup complete: {'yes' if summary.get('setup_complete') else 'no'}",
        f"Overall OK: {'yes' if summary.get('ok') else 'no'}",
        f"Playback architecture: {cfg.get('playback_architecture', 'unknown')}",
        f"Hardware model: {cfg.get('hardware_model', 'unknown')}",
        f"OPPO IP configured: {'yes' if cfg.get('oppo_ip_configured') else 'no'}",
        f"OPPO port: {cfg.get('oppo_port', 'unknown')}",
    ]
    missing = cast("list[object]", summary.get("missing") or [])
    warnings = cast("list[object]", summary.get("warnings") or [])
    if missing:
        lines.append("Missing: " + ", ".join(str(item) for item in missing))
    if warnings:
        lines.append("Warnings: " + ", ".join(str(item) for item in warnings))
    return "\n".join(lines)
