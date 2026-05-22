"""Capability helpers for the v2.9.10 unified hardware registry.

Build 4 keeps these helpers read-only while adding user-facing player
class guidance on top of the Build 3 safety gates: stock OPPO models, Chinoppo-style clones, experimental clones, and
OPPO-like successors have separate capability decisions.  This module does not
call hardware, mutate settings, route playback, or change command-map data.
"""

from __future__ import annotations

try:
    from .hardware_profiles import (
        HARDWARE_CLASS_CHINOPPO_CLONE,
        HARDWARE_CLASS_EXPERIMENTAL_CLONE,
        HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR,
        HARDWARE_CLASS_STOCK_OPPO,
        HARDWARE_ROLE_AVR,
        HARDWARE_ROLE_PLAYER,
        HARDWARE_ROLE_TV,
        get_profile,
        list_profiles,
        list_roles,
        normalize_profile_key,
        profiles_by_role,
    )
except ImportError:  # top-level/audit import compatibility
    from hardware_profiles import (  # type: ignore
        HARDWARE_CLASS_CHINOPPO_CLONE,
        HARDWARE_CLASS_EXPERIMENTAL_CLONE,
        HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR,
        HARDWARE_CLASS_STOCK_OPPO,
        HARDWARE_ROLE_AVR,
        HARDWARE_ROLE_PLAYER,
        HARDWARE_ROLE_TV,
        get_profile,
        list_profiles,
        list_roles,
        normalize_profile_key,
        profiles_by_role,
    )

STOCK_OPPO_MODELS = ("UDP-203", "UDP-205")

CHINOPPO_STYLE_MODELS = (
    "M9702",
    "M9200",
    "M9201",
    "M9203",
    "M9205",
    "M9205C",
    "CineUltra-V203",
    "CineUltra-V204",
)

EXPERIMENTAL_CLONE_MODELS = ("IPUK-UHD8592", "GIEC-BDP-G5300")

# Build 3 required NAS/direct-playback clone-family gate.  These models may be
# treated as OPPO/Chinoppo-style clone-family devices for clone-safe wake and
# NAS-mounted playback readiness, but still require tester confirmation.
CHINOPPO_NAS_PLAYBACK_MODELS = (
    "M9702",
    "M9200",
    "M9201",
    "M9203",
    "M9205",
    "M9205C",
    "CineUltra-V203",
    "CineUltra-V204",
    "IPUK-UHD8592",
    "GIEC-BDP-G5300",
)

OPPO_LIKE_SUCCESSOR_WARNING_MODELS = (
    "Reavon-UBR-X100",
    "Reavon-UBR-X110",
    "Reavon-UBR-X200",
    "Magnetar-UDP800",
    "Magnetar-UDP900",
)


def normalize_hardware_key(key: str) -> str:
    """Normalize a hardware key/alias through the central registry."""
    return normalize_profile_key(key)


def hardware_registry_summary() -> dict[str, object]:
    """Return a dependency-free summary for diagnostics, audit, and tests."""
    by_role = profiles_by_role()
    return {
        "roles": list_roles(),
        "profiles_by_role": by_role,
        "player_count": len(by_role.get(HARDWARE_ROLE_PLAYER, ())),
        "tv_count": len(by_role.get(HARDWARE_ROLE_TV, ())),
        "avr_count": len(by_role.get(HARDWARE_ROLE_AVR, ())),
        "stock_oppo_models": STOCK_OPPO_MODELS,
        "clone_nas_playback_models": CHINOPPO_NAS_PLAYBACK_MODELS,
        "warning_only_successor_models": OPPO_LIKE_SUCCESSOR_WARNING_MODELS,
        "runtime_behavior_changed": False,
        "hardware_validation_claimed": False,
    }


def profile_class(key: str) -> str:
    """Return the class for a profile key, or an empty string if unknown."""
    return str(get_profile(key).get("hardware_class", ""))


def is_stock_oppo(key: str) -> bool:
    return profile_class(key) == HARDWARE_CLASS_STOCK_OPPO


def is_chinoppo_style_clone(key: str) -> bool:
    return profile_class(key) == HARDWARE_CLASS_CHINOPPO_CLONE


def is_experimental_clone(key: str) -> bool:
    return profile_class(key) == HARDWARE_CLASS_EXPERIMENTAL_CLONE


def is_clone_family(key: str) -> bool:
    return profile_class(key) in (HARDWARE_CLASS_CHINOPPO_CLONE, HARDWARE_CLASS_EXPERIMENTAL_CLONE)


def is_warning_only_successor(key: str) -> bool:
    return (
        normalize_hardware_key(key) in OPPO_LIKE_SUCCESSOR_WARNING_MODELS
        or profile_class(key) == HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR
    )


def supports_clone_safe_wake(key: str) -> bool:
    """Return True only for clone-family devices that may use #EJT wake."""
    return normalize_hardware_key(
        key
    ) in CHINOPPO_NAS_PLAYBACK_MODELS and not is_warning_only_successor(key)


def allows_automatic_oppo_commands(key: str) -> bool:
    """Return whether automatic OPPO command-map behavior is allowed by class.

    Stock OPPO and clone-family hardware may use the existing OPPO command-map
    path.  OPPO-like successors are warning-only until real compatibility is
    recorded and must not be silently treated as stock or clone devices.
    """
    canonical = normalize_hardware_key(key)
    return canonical in STOCK_OPPO_MODELS or supports_clone_safe_wake(canonical)


def requires_autoscript_for_nas_direct_playback(key: str) -> bool:
    """Return whether NAS direct-playback handoff needs AutoScript/equivalent support."""
    canonical = normalize_hardware_key(key)
    return canonical in STOCK_OPPO_MODELS or canonical in CHINOPPO_NAS_PLAYBACK_MODELS


def nas_direct_playback_gate(key: str) -> dict[str, object]:
    """Return a read-only NAS/direct-playback gate summary for diagnostics."""
    canonical = normalize_hardware_key(key)
    successor = canonical in OPPO_LIKE_SUCCESSOR_WARNING_MODELS
    clone = canonical in CHINOPPO_NAS_PLAYBACK_MODELS
    stock = canonical in STOCK_OPPO_MODELS
    return {
        "model": canonical,
        "stock_oppo": stock,
        "clone_family": clone,
        "warning_only_successor": successor,
        "basic_ip_control_allowed": stock or clone,
        "automatic_oppo_command_map_allowed": (stock or clone) and not successor,
        "clone_safe_wake_allowed": clone and not successor,
        "nas_direct_playback_supported_by_family": (stock or clone) and not successor,
        "requires_autoscript_or_equivalent": (stock or clone) and not successor,
        "requires_real_hardware_validation": True,
        "hardware_validation_claimed": False,
    }


def player_setup_guidance(key: str) -> dict[str, object]:
    """Return user-facing setup/readiness guidance for one player model.

    Build 4 centralizes wording for the wizard, installer/readiness report, and
    tests.  It is intentionally read-only: it does not change settings, route
    playback, send OPPO commands, or claim hardware validation.
    """
    canonical = normalize_hardware_key(key)
    gate = nas_direct_playback_gate(canonical)
    profile = get_profile(canonical)
    hardware_class = str(profile.get("hardware_class", "unknown"))
    if hardware_class == HARDWARE_CLASS_STOCK_OPPO:
        title = "Stock OPPO player"
        summary = (
            "This model is treated as a stock OPPO UDP-203/UDP-205 player. "
            "Basic IP control can use stock OPPO #PON/#POW power behavior. "
            "NAS-based direct playback still requires OPPO AutoScript/jailbroken firmware support and real hardware validation before confirmed support is claimed."
        )
    elif hardware_class in (HARDWARE_CLASS_CHINOPPO_CLONE, HARDWARE_CLASS_EXPERIMENTAL_CLONE):
        title = "OPPO/Chinoppo-style clone"
        summary = (
            "This model is treated as an OPPO/Chinoppo-style clone. "
            "Basic IP control and clone-safe wake commands can be used. "
            "NAS-based direct playback requires the player to mount the NAS path locally through AutoScript or equivalent clone firmware support. "
            "Hardware validation is still required before claiming confirmed support."
        )
    elif canonical.startswith("Magnetar-"):
        title = "Magnetar OPPO-like successor"
        summary = (
            "Magnetar UDP800/UDP900 are treated as OPPO-like successor players, not confirmed OPPO command-compatible clones. "
            "Automatic OPPO command-map behavior is disabled unless hardware validation confirms compatibility."
        )
    elif canonical.startswith("Reavon-"):
        title = "Reavon warning-only successor"
        summary = (
            "Reavon UBR-X100/X110/X200 remain warning-only successor profiles. "
            "Do not assume stock OPPO command compatibility."
        )
    else:
        title = "Unknown OPPO-compatible player"
        summary = (
            "This player model is not in the v2.9.10 software registry. "
            "Use conservative stock OPPO assumptions only after real hardware validation."
        )
    return {
        "model": canonical,
        "title": title,
        "hardware_class": hardware_class,
        "protocol_stance": profile.get("protocol_stance", "unknown"),
        "summary": summary,
        "nas_mount_question_status": "documented_readiness_gate",
        "nas_mount_guidance": (
            "NAS/direct playback is a readiness gate, not a universal claim. "
            "Confirm AutoScript or equivalent local NAS mount support on the real player before recording hardware pass."
        ),
        "automatic_oppo_command_map_allowed": bool(gate.get("automatic_oppo_command_map_allowed")),
        "clone_safe_wake_allowed": bool(gate.get("clone_safe_wake_allowed")),
        "warning_only_successor": bool(gate.get("warning_only_successor")),
        "hardware_validation_claimed": False,
    }


def format_player_setup_guidance(key: str) -> str:
    """Render player setup guidance as wizard/readiness text."""
    guidance = player_setup_guidance(key)
    lines = [
        str(guidance.get("title", "Player hardware guidance")),
        str(guidance.get("summary", "")),
        "",
        "Readiness notes:",
        "- Hardware class: " + str(guidance.get("hardware_class", "unknown")),
        "- Protocol stance: " + str(guidance.get("protocol_stance", "unknown")),
        "- Automatic OPPO command-map behavior: "
        + ("allowed" if guidance.get("automatic_oppo_command_map_allowed") else "disabled"),
        "- Clone-safe wake: "
        + ("allowed" if guidance.get("clone_safe_wake_allowed") else "not used"),
        "- Hardware validation claimed: no",
        "- " + str(guidance.get("nas_mount_guidance", "")),
    ]
    return "\n".join(lines)


def supported_profile_keys() -> tuple[str, ...]:
    """Return all registry keys for audit-style smoke checks."""
    return list_profiles()
