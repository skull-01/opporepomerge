"""Regression: the five OPPO-clone variants added from the PlayBridge capability summary.

M9205 V2/V3/V4 mirror the M9205 eject-to-wake clone profile; M9702 Plus mirrors M9702;
VenPro V203 is a new ``venpro``-family optical clone mirroring CineUltra. Each pins its new
``oppo_hardware_model`` enum value end-to-end on the add-on side (settings dropdown, alias
normalization, compatibility profile, registry profile, capability gates) and that it
mirrors its base device without collapsing into it -- the same contract the M9205-V1 split
pinned (tests/test_chinoppo_m9205_v1_split.py).
"""

from pathlib import Path

import pytest

from resources.lib import oppo_remote
from resources.lib.kodi import settings_reader
from resources.lib.oppo import hardware_capabilities as caps
from resources.lib.oppo import hardware_profiles as profiles

ROOT = Path(__file__).resolve().parents[1]

# (enum_value, canonical_key, base_key, label)
VARIANTS = [
    ("chinoppo_m9205_v2", "M9205-V2", "M9205", "Chinoppo M9205 V2"),
    ("chinoppo_m9205_v3", "M9205-V3", "M9205", "Chinoppo M9205 V3"),
    ("chinoppo_m9205_v4", "M9205-V4", "M9205", "Chinoppo M9205 V4"),
    ("chinoppo_m9702_plus", "M9702-Plus", "M9702", "Chinoppo M9702 Plus"),
    ("venpro_v203", "VenPro-V203", "CineUltra-V203", "VenPro V203"),
]


@pytest.mark.parametrize("enum_value, key, base, label", VARIANTS)
def test_enum_dropdown_exposes_distinct_value(enum_value, key, base, label):
    assert enum_value in settings_reader.ENUM_VALUES["oppo_hardware_model"]
    settings_xml = (ROOT / "resources/settings.xml").read_text(encoding="utf-8")
    values = (
        settings_xml.split('id="oppo_hardware_model"', 1)[1]
        .split('values="', 1)[1]
        .split('"', 1)[0]
        .split("|")
    )
    assert enum_value in values


@pytest.mark.parametrize("enum_value, key, base, label", VARIANTS)
def test_variant_normalizes_to_its_own_canonical_key(enum_value, key, base, label):
    assert settings_reader.normalize_hardware_model(enum_value) == key
    assert profiles.normalize_profile_key(enum_value) == key
    # The variant is distinct from its base device.
    assert key != base


@pytest.mark.parametrize("enum_value, key, base, label", VARIANTS)
def test_variant_compat_mirrors_base(enum_value, key, base, label):
    variant = settings_reader.HARDWARE_COMPAT[key]
    base_profile = settings_reader.HARDWARE_COMPAT[base]
    # The variant mirrors its base clone's structure. wake_command is compared
    # separately: base M9205 is operator-validated to #PON while its V2/V3/V4
    # splits stay conservative #EJT, so the two diverge only on that field.
    for field in (
        "is_clone",
        "is_reavon",
        "http_api_436",
        "protocol_compatible",
        "src_supported",
        "src_unsupported",
    ):
        assert variant[field] == base_profile[field]
    profile = settings_reader.hardware_profile(key)
    assert profile["wake_command"] == "#EJT"
    assert profile["is_clone"] is True
    assert profile["http_api_436"] is False


@pytest.mark.parametrize("enum_value, key, base, label", VARIANTS)
def test_variant_registry_profile_is_a_chinoppo_clone(enum_value, key, base, label):
    profile = profiles.get_profile(key)
    assert profile["hardware_class"] == profiles.HARDWARE_CLASS_CHINOPPO_CLONE
    assert profile["wake_behavior"] == "clone_eject_wake"
    assert profile["label"] == label
    assert key in profiles.list_profiles("player")


@pytest.mark.parametrize("enum_value, key, base, label", VARIANTS)
def test_variant_capability_gates_match_clone_family(enum_value, key, base, label):
    assert caps.supports_clone_safe_wake(key) is True
    assert caps.allows_automatic_oppo_commands(key) is True
    assert caps.is_chinoppo_style_clone(key) is True
    assert oppo_remote.resolve_power_on_token("#PON", enum_value) == "#EJT"
    assert oppo_remote.resolve_power_on_token("#POW", key) == "#EJT"
