"""Dolby Vision capability data for the OPPO / clone player taxonomy.

Data-only and side-effect free (like hardware_profiles.py). This is the add-on-side
source of truth for per-player Dolby Vision processing guidance, mirrored by the
``dolby_vision`` field on each model in the configurator's players-models.json and
pinned cross-area by tests/test_players_db_consistency.py.

Sourced from the 2026-06-04 OPPO/Chinoppo PlayBridge capability summary
(docs/configurator/players-db/PLAYBRIDGE_CAPABILITY_SUMMARY.md). These are
research-grade recommendations, NOT hardware-validated: nothing here changes
playback, OPPO command dispatch, TV switching, or claims a confirmed device result.
"""

from __future__ import annotations

try:
    from .hardware_profiles import normalize_profile_key
except ImportError:  # top-level/audit import compatibility
    from hardware_profiles import normalize_profile_key  # type: ignore

# Controlled vocabularies -- the normalized form of the capability summary's free-text
# stances, so the data can be guarded and consumed instead of parsed.
DV_CAPABLE_VALUES = ("yes", "unknown", "no")
DV_TV_LED_VALUES = (
    "official",
    "expected",
    "setup_sensitive",
    "needs_validation",
    "not_assessed",
)
DV_PLAYER_LED_VALUES = (
    "official",
    "recommended_for_sony_lldv",
    "available",
    "not_assessed",
)
DV_CONFIDENCE_VALUES = ("high", "medium", "low")

_DV_UNKNOWN = {
    "capable": "unknown",
    "tv_led": "not_assessed",
    "player_led": "not_assessed",
    "confidence": "low",
}


def _dv(capable: str, tv_led: str, player_led: str, confidence: str) -> dict[str, str]:
    return {
        "capable": capable,
        "tv_led": tv_led,
        "player_led": player_led,
        "confidence": confidence,
    }


DOLBY_VISION_PROFILES: dict[str, dict[str, str]] = {
    "UDP-203": _dv("yes", "official", "official", "high"),
    "UDP-205": _dv("yes", "official", "official", "high"),
    "M9201": _dv("yes", "expected", "recommended_for_sony_lldv", "medium"),
    "M9203": _dv("yes", "expected", "recommended_for_sony_lldv", "medium"),
    "M9205C": _dv("yes", "needs_validation", "recommended_for_sony_lldv", "medium"),
    "M9702": _dv("yes", "setup_sensitive", "available", "medium"),
    "IPUK-UHD8592": _dv("unknown", "not_assessed", "not_assessed", "low"),
    "GIEC-BDP-G5300": _dv("unknown", "not_assessed", "not_assessed", "low"),
    "Magnetar-UDP800": _dv("unknown", "not_assessed", "not_assessed", "low"),
    "Reavon-UBR-X100": _dv("unknown", "not_assessed", "not_assessed", "low"),
    "Reavon-UBR-X110": _dv("unknown", "not_assessed", "not_assessed", "low"),
    "Reavon-UBR-X200": _dv("unknown", "not_assessed", "not_assessed", "low"),
    "M9200": _dv("unknown", "needs_validation", "not_assessed", "low"),
    "M9205": _dv("yes", "expected", "recommended_for_sony_lldv", "medium"),
    "CineUltra-V203": _dv("yes", "expected", "available", "medium"),
    "CineUltra-V204": _dv("yes", "expected", "available", "medium"),
    "Magnetar-UDP900": _dv("unknown", "not_assessed", "not_assessed", "low"),
    "M9205-V1": _dv("yes", "expected", "recommended_for_sony_lldv", "low"),
    "M9205-V2": _dv("yes", "expected", "recommended_for_sony_lldv", "low"),
    "M9205-V3": _dv("yes", "expected", "recommended_for_sony_lldv", "low"),
    "M9205-V4": _dv("yes", "expected", "recommended_for_sony_lldv", "low"),
    "M9702-Plus": _dv("yes", "setup_sensitive", "available", "low"),
    "VenPro-V203": _dv("unknown", "needs_validation", "not_assessed", "low"),
}

# Display-/TV-type-driven processing rule (capability summary section 7, global_dv_rule).
# A list (not a tuple) for ``unknown_tv_test_order`` so it compares equal to the JSON mirror.
DOLBY_VISION_TV_RULE: dict[str, object] = {
    "full_dv_tv_default": "tv_led",
    "sony_or_lldv_tv_default": "player_led_or_auto",
    "unknown_tv_test_order": ["auto", "tv_led", "player_led"],
    "proof_source": "uhd_iso_or_bdmv",
    "avoid_as_proof": "mkv_dv",
}


def dolby_vision_profile(key: str) -> dict[str, str]:
    """Return a copy of the Dolby Vision profile for a player key/alias.

    Unknown keys degrade to a conservative ``unknown`` profile rather than raising.
    """
    canonical = normalize_profile_key(key)
    return dict(DOLBY_VISION_PROFILES.get(canonical, _DV_UNKNOWN))


def dv_processing_recommendation(tv_type: str) -> str:
    """Map a coarse TV type to a recommended DV processing mode (see DOLBY_VISION_TV_RULE).

    ``full_dv`` -> TV-led; ``sony_lldv`` -> Player-led/Auto; anything else -> Auto first.
    """
    if tv_type == "full_dv":
        return str(DOLBY_VISION_TV_RULE["full_dv_tv_default"])
    if tv_type == "sony_lldv":
        return str(DOLBY_VISION_TV_RULE["sony_or_lldv_tv_default"])
    return "auto"
