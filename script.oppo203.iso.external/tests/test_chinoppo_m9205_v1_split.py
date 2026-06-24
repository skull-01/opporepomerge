"""Regression: Chinoppo M9205 V1 is a distinct hardware model from the plain M9205.

The configurator confirmed M9205 V1 and M9205 are distinct devices that share the
M9205 power-CEC clone control protocol (#PON wake). This pins the new ``chinoppo_m9205_v1``
enum value end-to-end on the add-on side (settings dropdown, alias normalization,
compatibility profile, registry profile, capability gates) and that it mirrors
M9205 without collapsing back into it.
"""

from pathlib import Path

from resources.lib import oppo_remote
from resources.lib.kodi import settings_reader
from resources.lib.oppo import hardware_capabilities as caps
from resources.lib.oppo import hardware_profiles as profiles

ROOT = Path(__file__).resolve().parents[1]


def test_enum_dropdown_exposes_distinct_v1_value():
    assert "chinoppo_m9205_v1" in settings_reader.ENUM_VALUES["oppo_hardware_model"]
    settings_xml = (ROOT / "resources/settings.xml").read_text(encoding="utf-8")
    values = (
        settings_xml.split('id="oppo_hardware_model"', 1)[1]
        .split('values="', 1)[1]
        .split('"', 1)[0]
        .split("|")
    )
    assert "chinoppo_m9205_v1" in values
    assert "chinoppo_m9205" in values
    assert values.index("chinoppo_m9205_v1") != values.index("chinoppo_m9205")


def test_v1_normalizes_to_its_own_canonical_key():
    assert settings_reader.normalize_hardware_model("chinoppo_m9205_v1") == "M9205-V1"
    assert profiles.normalize_profile_key("chinoppo_m9205_v1") == "M9205-V1"
    assert settings_reader.normalize_hardware_model("chinoppo_m9205") == "M9205"


def test_v1_compatibility_profile_mirrors_m9205():
    v1 = settings_reader.hardware_profile("M9205-V1")
    base = settings_reader.hardware_profile("M9205")
    # V1 fully mirrors base M9205, including its operator-validated #PON wake
    # (the whole M9205 family drives CEC via network power).
    assert v1 == base
    assert v1["wake_command"] == "#PON"
    assert v1["is_clone"] is True
    assert v1["http_api_436"] is False


def test_v1_registry_profile_is_a_chinoppo_clone():
    profile = profiles.get_profile("M9205-V1")
    assert profile["hardware_class"] == profiles.HARDWARE_CLASS_CHINOPPO_CLONE
    assert profile["wake_behavior"] == "clone_eject_wake"
    assert profile["label"] == "Chinoppo M9205 V1"
    assert "M9205-V1" in profiles.list_profiles("player")


def test_v1_capability_gates_match_clone_family():
    assert caps.supports_clone_safe_wake("M9205-V1") is True
    assert caps.allows_automatic_oppo_commands("M9205-V1") is True
    assert caps.is_chinoppo_style_clone("M9205-V1") is True
    assert oppo_remote.resolve_power_on_token("#PON", "chinoppo_m9205_v1") == "#PON"
    assert oppo_remote.resolve_power_on_token("#POW", "M9205-V1") == "#PON"
