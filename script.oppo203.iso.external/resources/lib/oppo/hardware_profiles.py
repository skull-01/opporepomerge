"""Unified hardware profile registry for v2.9.10.

This module is intentionally data-only and side-effect free.  Build 1 adds the
registry foundation so later v2.9.10 builds can describe player, TV, and AVR
hardware without changing playback, OPPO command dispatch, TV switching, or
AVR behavior.
"""

from __future__ import annotations

HARDWARE_ROLE_PLAYER = "player"
HARDWARE_ROLE_TV = "tv"
HARDWARE_ROLE_AVR = "avr"

HARDWARE_CLASS_STOCK_OPPO = "stock_oppo"
HARDWARE_CLASS_CHINOPPO_CLONE = "chinoppo_clone"
HARDWARE_CLASS_EXPERIMENTAL_CLONE = "experimental_clone"
HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR = "oppo_like_successor"
HARDWARE_CLASS_TV_PLATFORM = "tv_platform"
HARDWARE_CLASS_AVR_FAMILY = "avr_family"

PROTOCOL_STANCE_COMPATIBLE = "compatible"
PROTOCOL_STANCE_CLONE_SAFE = "clone_safe"
PROTOCOL_STANCE_EXPERIMENTAL = "experimental"
PROTOCOL_STANCE_WARNING_ONLY = "warning_only"

PLAYER_PROFILE_KEYS = (
    "UDP-203",
    "UDP-205",
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
    "Magnetar-UDP800",
    "Magnetar-UDP900",
    "Reavon-UBR-X100",
    "Reavon-UBR-X110",
    "Reavon-UBR-X200",
)

TV_PROFILE_KEYS = (
    "adb",
    "sony_bravia",
    "lg_command",
    "samsung_command",
    "custom_command",
)

AVR_PROFILE_KEYS = (
    "disabled",
    "denon_marantz",
    "yamaha_yxc",
    "onkyo_eiscp",
    "pioneer_eiscp",
    "sony_audio_api",
)

PROFILE_ALIASES = {
    "m9702_v1": "M9702",
    "m9702-v1": "M9702",
    "chinoppo_m9702_v1": "M9702",
    "m9702_v2": "M9702",
    "m9702-v2": "M9702",
    "chinoppo_m9702_v2": "M9702",
    "m9702_v3": "M9702",
    "m9702-v3": "M9702",
    "chinoppo_m9702_v3": "M9702",
    "m9200": "M9200",
    "chinoppo_m9200": "M9200",
    "m9205": "M9205",
    "chinoppo_m9205": "M9205",
    "cineultra_v203": "CineUltra-V203",
    "cineultra-v203": "CineUltra-V203",
    "v203": "CineUltra-V203",
    "cineultra_v204": "CineUltra-V204",
    "cineultra-v204": "CineUltra-V204",
    "v204": "CineUltra-V204",
    "magnetar_udp800": "Magnetar-UDP800",
    "magnetar-udp800": "Magnetar-UDP800",
    "udp800": "Magnetar-UDP800",
    "magnetar_udp900": "Magnetar-UDP900",
    "magnetar-udp900": "Magnetar-UDP900",
    "udp900": "Magnetar-UDP900",
    "reavon_ubrx100": "Reavon-UBR-X100",
    "reavon-ubr-x100": "Reavon-UBR-X100",
    "reavon_ubrx110": "Reavon-UBR-X110",
    "reavon-ubr-x110": "Reavon-UBR-X110",
    "reavon_ubrx200": "Reavon-UBR-X200",
    "reavon-ubr-x200": "Reavon-UBR-X200",
}

HARDWARE_PROFILES = {
    "UDP-203": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_STOCK_OPPO,
        "label": "OPPO UDP-203",
        "protocol_stance": PROTOCOL_STANCE_COMPATIBLE,
        "wake_behavior": "stock_oppo_power",
        "hardware_validation_required": True,
    },
    "UDP-205": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_STOCK_OPPO,
        "label": "OPPO UDP-205",
        "protocol_stance": PROTOCOL_STANCE_COMPATIBLE,
        "wake_behavior": "stock_oppo_power",
        "hardware_validation_required": True,
    },
    "M9702": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "Chinoppo M9702",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "M9200": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "Chinoppo M9200",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "M9201": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "Chinoppo M9201",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "M9203": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "Chinoppo M9203",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "M9205": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "Chinoppo M9205",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "M9205C": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "Chinoppo M9205C",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "CineUltra-V203": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "CineUltra V203",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "CineUltra-V204": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_CHINOPPO_CLONE,
        "label": "CineUltra V204",
        "protocol_stance": PROTOCOL_STANCE_CLONE_SAFE,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "IPUK-UHD8592": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_EXPERIMENTAL_CLONE,
        "label": "IPUK UHD8592 / similar",
        "protocol_stance": PROTOCOL_STANCE_EXPERIMENTAL,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "GIEC-BDP-G5300": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_EXPERIMENTAL_CLONE,
        "label": "GIEC BDP-G5300 / similar",
        "protocol_stance": PROTOCOL_STANCE_EXPERIMENTAL,
        "wake_behavior": "clone_eject_wake",
        "hardware_validation_required": True,
    },
    "Magnetar-UDP800": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR,
        "label": "Magnetar UDP800",
        "protocol_stance": PROTOCOL_STANCE_WARNING_ONLY,
        "wake_behavior": "warning_only_no_automatic_oppo_commands",
        "hardware_validation_required": True,
    },
    "Magnetar-UDP900": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR,
        "label": "Magnetar UDP900",
        "protocol_stance": PROTOCOL_STANCE_WARNING_ONLY,
        "wake_behavior": "warning_only_no_automatic_oppo_commands",
        "hardware_validation_required": True,
    },
    "Reavon-UBR-X100": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR,
        "label": "Reavon UBR-X100",
        "protocol_stance": PROTOCOL_STANCE_WARNING_ONLY,
        "wake_behavior": "warning_only_no_automatic_oppo_commands",
        "hardware_validation_required": True,
    },
    "Reavon-UBR-X110": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR,
        "label": "Reavon UBR-X110",
        "protocol_stance": PROTOCOL_STANCE_WARNING_ONLY,
        "wake_behavior": "warning_only_no_automatic_oppo_commands",
        "hardware_validation_required": True,
    },
    "Reavon-UBR-X200": {
        "role": HARDWARE_ROLE_PLAYER,
        "hardware_class": HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR,
        "label": "Reavon UBR-X200",
        "protocol_stance": PROTOCOL_STANCE_WARNING_ONLY,
        "wake_behavior": "warning_only_no_automatic_oppo_commands",
        "hardware_validation_required": True,
    },
}

for _key in TV_PROFILE_KEYS:
    HARDWARE_PROFILES[_key] = {
        "role": HARDWARE_ROLE_TV,
        "hardware_class": HARDWARE_CLASS_TV_PLATFORM,
        "label": _key.replace("_", " ").title(),
        "protocol_stance": "preserved_existing_backend",
        "hardware_validation_required": True,
    }

for _key in AVR_PROFILE_KEYS:
    HARDWARE_PROFILES[_key] = {
        "role": HARDWARE_ROLE_AVR,
        "hardware_class": HARDWARE_CLASS_AVR_FAMILY,
        "label": _key.replace("_", " ").title(),
        "protocol_stance": "planned_optional_disabled_by_default",
        "hardware_validation_required": True,
    }

ROLE_ORDER = (HARDWARE_ROLE_PLAYER, HARDWARE_ROLE_TV, HARDWARE_ROLE_AVR)


def normalize_profile_key(key: str) -> str:
    """Return a canonical profile key for known user/settings aliases."""
    if not isinstance(key, str):
        return ""
    stripped = key.strip()
    if stripped in HARDWARE_PROFILES:
        return stripped
    return PROFILE_ALIASES.get(stripped.lower(), stripped)


def list_roles() -> tuple[str, ...]:
    """Return hardware roles in stable UI/documentation order."""
    return ROLE_ORDER


def list_profiles(role: str | None = None) -> tuple[str, ...]:
    """Return canonical profile keys, optionally filtered by role."""
    keys = sorted(HARDWARE_PROFILES)
    if role is None:
        return tuple(keys)
    return tuple(key for key in keys if HARDWARE_PROFILES[key].get("role") == role)


def get_profile(key: str, default: dict[str, object] | None = None) -> dict[str, object]:
    """Return a copy of one profile without exposing mutable registry data."""
    key = normalize_profile_key(key)
    if key in HARDWARE_PROFILES:
        return dict(HARDWARE_PROFILES[key])
    return dict(default or {})


def profiles_by_role() -> dict[str, tuple[str, ...]]:
    """Return a role-to-profile-key mapping for diagnostics and tests."""
    return {role: list_profiles(role) for role in ROLE_ORDER}
