"""Drift guard: the canonical playback-preset matrix JSON must match the add-on's live registries.

configurator/src/presets-db/playback-presets.json is the single cross-language source of truth for
the six-option playback-architecture matrix (3 routing modes x 2 monitor modes), shared with the
configurator (presetsdb.ts / mapping.ts). The add-on keeps running from its own tuples in
settings_reader.py, so this guard is what stops the JSON and the Python registries from diverging:
adding or removing a routing/monitor combo means the JSON and settings_reader must agree, or these
tests fail and name the mismatch. Pairs with the configurator-side guards (presetsdb.test.ts +
the completeness assertion in mapping.test.ts).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resources.lib.kodi import settings_reader as sr

DB = json.loads(
    (ROOT / "configurator/src/presets-db/playback-presets.json").read_text(encoding="utf-8")
)


def test_routing_modes_match_settings_reader():
    assert tuple(DB["routing_modes"]) == sr.PLAYBACK_ROUTING_MODES


def test_monitor_modes_match_settings_reader():
    assert tuple(DB["monitor_modes"]) == sr.PLAYBACK_MONITOR_MODES


def test_presets_match_settings_reader_in_order():
    assert tuple(DB["presets"]) == sr.PLAYBACK_ARCHITECTURE_PRESETS
    assert len(DB["presets"]) == 6


def test_preset_by_axes_matches_settings_reader():
    db_map = {(e["routing"], e["monitor"]): e["preset"] for e in DB["preset_by_axes"]}
    assert db_map == sr._PRESET_BY_AXES


def test_routing_aliases_match_settings_reader():
    db_aliases = {e["alias"]: e["routing"] for e in DB["routing_aliases"]}
    assert db_aliases == sr._ROUTING_ALIASES


def test_matrix_is_the_full_cross_product():
    pairs = {(e["routing"], e["monitor"]) for e in DB["preset_by_axes"]}
    expected = {(r, m) for r in DB["routing_modes"] for m in DB["monitor_modes"]}
    assert pairs == expected
    assert {e["preset"] for e in DB["preset_by_axes"]} == set(DB["presets"])


def test_preset_ids_follow_the_routing_monitor_convention():
    for entry in DB["preset_by_axes"]:
        assert entry["preset"] == f"{entry['routing']}_{entry['monitor']}"
