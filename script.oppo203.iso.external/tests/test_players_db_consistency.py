"""Drift guard: the canonical players DB (configurator players.json) must faithfully
reproduce the add-on's live player taxonomy.

players.json is the single source of truth for the OPPO/clone player catalog. The add-on
keeps running from its own registries (the TV DB follows the same split), so this guard is
what stops the JSON and the registries from diverging: adding or changing a model means the
JSON and the Python registries must agree, or these tests fail and name the mismatch.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resources.lib.kodi import settings_reader as sr
from resources.lib.oppo import hardware_capabilities as caps
from resources.lib.oppo import hardware_profiles as hp

_DOCS = json.loads((ROOT / "docs/configurator/players-db/players.json").read_text(encoding="utf-8"))
_SRC = json.loads(
    (ROOT / "configurator/src/players-db/players.json").read_text(encoding="utf-8")
)
DB = _DOCS
MODELS = DB["models"]


def test_bundled_and_docs_copies_are_identical():
    assert _SRC == _DOCS


def test_enum_order_matches_settings_reader_and_settings_xml():
    assert DB["enum_order"] == list(sr.ENUM_VALUES["oppo_hardware_model"])
    settings_xml = (ROOT / "resources/settings.xml").read_text(encoding="utf-8")
    values = (
        settings_xml.split('id="oppo_hardware_model"', 1)[1]
        .split('values="', 1)[1]
        .split('"', 1)[0]
        .split("|")
    )
    assert values == DB["enum_order"]


def test_models_cover_the_player_taxonomy_exactly():
    keys = [m["key"] for m in MODELS]
    assert keys == [sr.normalize_hardware_model(hw) for hw in DB["enum_order"]]
    assert set(keys) == set(hp.list_profiles("player"))
    assert set(keys) == set(sr.HARDWARE_COMPAT)
    assert len(keys) == len(set(keys))


def test_each_model_matches_profile_and_compat():
    for m in MODELS:
        key = m["key"]
        prof = hp.HARDWARE_PROFILES[key]
        assert prof["role"] == hp.HARDWARE_ROLE_PLAYER, key
        assert m["label"] == prof["label"], key
        assert m["hardware_class"] == prof["hardware_class"], key
        assert m["protocol_stance"] == prof["protocol_stance"], key
        assert m["wake_behavior"] == prof["wake_behavior"], key

        compat = sr.HARDWARE_COMPAT[key]
        assert m["wake_command"] == compat["wake_command"], key
        assert m["protocol_compatible"] == compat["protocol_compatible"], key
        assert m["is_clone"] == compat["is_clone"], key
        assert m["is_reavon"] == compat["is_reavon"], key
        assert m["is_successor"] == bool(compat.get("is_successor", False)), key
        assert m["http_api_436"] == compat["http_api_436"], key
        assert set(m["src_supported"]) == set(compat["src_supported"]), key
        assert set(m["src_unsupported"]) == set(compat["src_unsupported"]), key
        assert m["nas_playback_candidate"] == (key in caps.CHINOPPO_NAS_PLAYBACK_MODELS), key


def test_capability_tuples_derive_from_hardware_class():
    by_class: dict[str, set] = {}
    for m in MODELS:
        by_class.setdefault(m["hardware_class"], set()).add(m["key"])
    assert set(caps.STOCK_OPPO_MODELS) == by_class[hp.HARDWARE_CLASS_STOCK_OPPO]
    assert set(caps.CHINOPPO_STYLE_MODELS) == by_class[hp.HARDWARE_CLASS_CHINOPPO_CLONE]
    assert set(caps.EXPERIMENTAL_CLONE_MODELS) == by_class[hp.HARDWARE_CLASS_EXPERIMENTAL_CLONE]
    assert (
        set(caps.OPPO_LIKE_SUCCESSOR_WARNING_MODELS)
        == by_class[hp.HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR]
    )
    nas = {m["key"] for m in MODELS if m["nas_playback_candidate"]}
    assert set(caps.CHINOPPO_NAS_PLAYBACK_MODELS) == nas


def test_db_captures_every_player_alias_both_ways():
    keys = {m["key"] for m in MODELS}
    by_key = {m["key"]: set(m["aliases"]) for m in MODELS}
    # Forward: every alias the DB lists resolves back to its model key.
    for m in MODELS:
        for alias in m["aliases"]:
            assert (
                sr.normalize_hardware_model(alias) == m["key"]
                or hp.normalize_profile_key(alias) == m["key"]
            ), f"{alias} -> {m['key']}"
    # Reverse: every player-targeting alias in the registries is captured by the DB.
    for amap in (sr._HARDWARE_ALIASES, hp.PROFILE_ALIASES):
        for alias, target in amap.items():
            if target in keys:
                assert alias in by_key[target], f"{alias} -> {target} missing from players.json"


def test_families_cover_all_model_brands_and_other_aliases_resolve():
    family_ids = {f["id"] for f in DB["families"]}
    for m in MODELS:
        assert m["brand"] in family_ids, m["key"]
    valid_hw = {m["hw"] for m in MODELS}
    other = next(f for f in DB["families"] if f["id"] == "other")
    for ui_model in other["ui_models"]:
        assert ui_model["hw"] in valid_hw, ui_model
