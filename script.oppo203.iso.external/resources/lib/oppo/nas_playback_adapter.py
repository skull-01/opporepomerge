"""OPPO/Chinoppo NAS playback trigger adapter.

v2.5.2 Build 4 adds a family-aware adapter for the NAS playback roadmap.
It composes the v2.5.2 Build 1 capability gates and the v2.5.2 Build 3
path-mapping helper, then prepares or executes a playback trigger through the
existing OPPO HTTP API surface.  The adapter is intentionally narrow: it does
not change the canonical OPPO command map, does not alter the wizard, and keeps
all hardware-facing calls injectable for tests and future model-specific work.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Callable

try:  # package import when running under Kodi/tests as package
    from ..kodi.settings_reader import nas_playback_capability
    from .path_mapper import PathMappingRule, explain_path_mapping, rules_from_settings
except Exception:  # pragma: no cover - top-level fallback for legacy tests
    from path_mapper import (  # type: ignore
        PathMappingRule,
        explain_path_mapping,
        rules_from_settings,
    )
    from settings_reader import nas_playback_capability  # type: ignore


SUPPORTED_TRIGGER_MODES = {"http_api", "dry_run"}


class NasPlaybackAdapterError(RuntimeError):
    """Base error for NAS playback adapter failures."""


class NasPlaybackNotReady(NasPlaybackAdapterError):
    """Raised by strict callers when capability, mapping, or config blocks playback."""


@dataclass(frozen=True)
class NasPlaybackAdapter:
    """Family-specific NAS playback adapter description."""

    name: str
    family: str
    wake_command: str
    trigger_mode: str = "http_api"


def _get(settings: Any, key: str, default: Any = "") -> Any:
    if hasattr(settings, "get"):
        return settings.get(key, default)
    try:
        return dict(settings).get(key, default)
    except Exception:
        return default


def _get_bool(settings: Any, key: str, default: bool = False) -> bool:
    if hasattr(settings, "get_bool"):
        try:
            return bool(settings.get_bool(key, default))
        except Exception:
            return default
    value = _get(settings, key, default)
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "on"}:
        return True
    if text in {"false", "0", "no", "off", ""}:
        return False
    return default


def _capability_from_settings(settings: Any) -> dict[str, Any]:
    return nas_playback_capability(
        _get(settings, "oppo_hardware_model", "udp_203"),
        firmware=_get(settings, "oppo_firmware_version", ""),
        jailbreak=_get_bool(settings, "oppo_jailbreak_enabled", False),
        confirmed=_get_bool(settings, "nas_playback_confirmed", False),
    )


def adapter_for_capability(
    capability: dict[str, Any], *, trigger_mode: str = "http_api"
) -> NasPlaybackAdapter:
    """Return the family adapter for a capability result."""
    family = str(capability.get("family") or "unknown_oppo_compatible")
    if family == "oppo20x_jailbroken":
        name = "Oppo20xJailbrokenNasAdapter"
    elif family == "chinoppo_family":
        name = "ChinoppoNasAdapter"
    else:
        name = "UnsupportedNasAdapter"
    return NasPlaybackAdapter(
        name=name,
        family=family,
        wake_command=str(capability.get("wake_command") or "#PON"),
        trigger_mode=trigger_mode,
    )


def build_nas_playback_plan(
    settings: Any,
    kodi_path: str,
    rules: Iterable[PathMappingRule | dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a dry-run NAS playback plan without touching hardware.

    The plan is intended for diagnostics, wizard previews, and tests.  It shows
    which family adapter would be used, the mapped player path, wake command,
    trigger mode, warnings, and blockers.
    """
    capability = _capability_from_settings(settings)
    trigger_mode = (
        str(_get(settings, "nas_playback_trigger_mode", "http_api") or "http_api").strip()
        or "http_api"
    )
    adapter = adapter_for_capability(capability, trigger_mode=trigger_mode)
    candidate_rules = list(rules) if rules is not None else rules_from_settings(settings)
    mapping = explain_path_mapping(kodi_path, candidate_rules)

    blockers = list(capability.get("blockers") or [])
    warnings = list(capability.get("warnings") or [])
    if trigger_mode not in SUPPORTED_TRIGGER_MODES:
        blockers.append("unsupported_nas_playback_trigger_mode")
    if not mapping.get("matched"):
        blockers.append("no_matching_nas_path_mapping_rule")
    if not str(_get(settings, "oppo_ip", "")).strip():
        blockers.append("oppo_ip_required")

    return {
        "ready": not blockers,
        "kodi_path": "" if kodi_path is None else str(kodi_path),
        "player_path": mapping.get("player_path"),
        "mapping": mapping,
        "capability": capability,
        "adapter": {
            "name": adapter.name,
            "family": adapter.family,
            "wake_command": adapter.wake_command,
            "trigger_mode": adapter.trigger_mode,
        },
        "wake_command": adapter.wake_command,
        "trigger_mode": trigger_mode,
        "warnings": warnings,
        "blockers": blockers,
    }


def _default_wake_client(settings: Any, wake_command: str) -> list[str]:
    try:
        from .oppo_control import send_commands
    except Exception:  # pragma: no cover - legacy top-level fallback
        from oppo_control import send_commands  # type: ignore
    host = _get(settings, "oppo_ip", "")
    port = int(_get(settings, "oppo_port", "23"))
    timeout = float(_get(settings, "oppo_socket_timeout", "3.0"))
    delay = float(_get(settings, "oppo_command_delay", "0.1"))
    return send_commands(host, port, [wake_command], timeout=timeout, delay=delay)


def _default_playback_client(settings: Any, player_path: str) -> Any:
    try:
        from .oppo_control import activate_http_api, play_media_http_api, signin_http_api
    except Exception:  # pragma: no cover - legacy top-level fallback
        from oppo_control import (  # type: ignore
            activate_http_api,
            play_media_http_api,
            signin_http_api,
        )
    activate_http_api(settings)
    signin_http_api(settings)
    return play_media_http_api(settings, player_path)


def trigger_nas_playback(
    settings: Any,
    kodi_path: str,
    rules: Iterable[PathMappingRule | dict[str, Any]] | None = None,
    *,
    wake_client: Callable[[Any, str], Any] | None = None,
    playback_client: Callable[[Any, str], Any] | None = None,
    dry_run: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    """Plan and optionally execute NAS playback for OPPO/Chinoppo families.

    ``wake_client`` and ``playback_client`` are injectable so tests and future
    hardware-specific adapters can validate behavior without contacting real
    devices.  When ``dry_run`` is true, no wake or playback calls are made.
    """
    plan = build_nas_playback_plan(settings, kodi_path, rules)
    result = dict(plan)
    result.update(
        {"success": False, "action": "planned", "wake_result": None, "playback_result": None}
    )

    if dry_run or plan["trigger_mode"] == "dry_run":
        result["success"] = bool(plan["ready"])
        result["action"] = "dry_run"
        return result

    if not plan["ready"]:
        result["action"] = "blocked"
        if strict:
            raise NasPlaybackNotReady(", ".join(plan["blockers"]) or "NAS playback is not ready")
        return result

    wake_fn = wake_client or _default_wake_client
    play_fn = playback_client or _default_playback_client
    if _get_bool(settings, "nas_playback_power_on_before_trigger", True):
        result["wake_result"] = wake_fn(settings, str(plan["wake_command"]))
    result["playback_result"] = play_fn(settings, str(plan["player_path"]))
    result["success"] = True
    result["action"] = "triggered"
    return result
