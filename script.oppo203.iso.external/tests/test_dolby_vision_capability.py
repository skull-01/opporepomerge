"""Dolby Vision capability registry (resources/lib/oppo/dolby_vision.py).

Every player has a vocab-checked DV profile, the M9205 family inherits an expected TV-led
stance (never "cannot do TV-led"), the global TV rule is well-formed, and the accessors
degrade safely. Data-only -- no hardware validation is claimed; the rows mirror the
research-grade PlayBridge capability summary.
"""

from resources.lib.oppo import dolby_vision as dv
from resources.lib.oppo import hardware_profiles as hp


def test_every_player_profile_has_a_dolby_vision_entry():
    players = set(hp.list_profiles("player"))
    assert players  # sanity: the player taxonomy is non-empty
    assert set(dv.DOLBY_VISION_PROFILES) == players


def test_profile_values_use_the_controlled_vocabulary():
    for key, profile in dv.DOLBY_VISION_PROFILES.items():
        assert profile["capable"] in dv.DV_CAPABLE_VALUES, key
        assert profile["tv_led"] in dv.DV_TV_LED_VALUES, key
        assert profile["player_led"] in dv.DV_PLAYER_LED_VALUES, key
        assert profile["confidence"] in dv.DV_CONFIDENCE_VALUES, key


def test_stock_oppo_is_official_and_high_confidence():
    for key in ("UDP-203", "UDP-205"):
        profile = dv.dolby_vision_profile(key)
        assert profile["capable"] == "yes"
        assert profile["tv_led"] == "official"
        assert profile["confidence"] == "high"


def test_m9205_family_keeps_expected_tv_led_with_lower_variant_confidence():
    base = dv.dolby_vision_profile("M9205")
    assert base["tv_led"] == "expected"
    assert base["confidence"] == "medium"
    for variant in ("M9205-V1", "M9205-V2", "M9205-V3", "M9205-V4"):
        profile = dv.dolby_vision_profile(variant)
        assert profile["tv_led"] == "expected"  # never "cannot do TV-led" for the M9205 family
        assert profile["confidence"] == "low"  # variant-specific validation still pending


def test_profile_resolves_through_aliases_and_degrades_on_unknown():
    assert dv.dolby_vision_profile("chinoppo_m9205_v4") == dv.dolby_vision_profile("M9205-V4")
    unknown = dv.dolby_vision_profile("not-a-real-player")
    assert unknown["capable"] == "unknown"
    assert unknown["confidence"] == "low"
    # The returned dict is a copy: mutating it must not corrupt the registry.
    unknown["capable"] = "mutated"
    assert dv.dolby_vision_profile("not-a-real-player")["capable"] == "unknown"


def test_global_tv_rule_shape_and_processing_recommendation():
    rule = dv.DOLBY_VISION_TV_RULE
    assert rule["full_dv_tv_default"] == "tv_led"
    assert rule["sony_or_lldv_tv_default"] == "player_led_or_auto"
    assert rule["unknown_tv_test_order"] == ["auto", "tv_led", "player_led"]
    assert rule["proof_source"] == "uhd_iso_or_bdmv"
    assert rule["avoid_as_proof"] == "mkv_dv"
    assert dv.dv_processing_recommendation("full_dv") == "tv_led"
    assert dv.dv_processing_recommendation("sony_lldv") == "player_led_or_auto"
    assert dv.dv_processing_recommendation("tcl_unknown") == "auto"
