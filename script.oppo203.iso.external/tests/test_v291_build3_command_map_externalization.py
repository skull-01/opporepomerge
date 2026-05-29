from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resources.lib.constants import OPPO_COMMAND_MAP_SIZE
from resources.lib.settings_reader import DEFAULTS

from resources.lib import command_map


def test_default_command_map_json_file_exists_and_has_canonical_size():
    path = ROOT / "resources" / "data" / "oppo_command_map.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) == OPPO_COMMAND_MAP_SIZE
    assert data["bluray_input"] == "#SRC 0"
    assert data["page_up"] == "#PUP"
    assert data["page_down"] == "#PDN"


def test_validated_loader_rejects_forbidden_tokens_and_size_drift(tmp_path):
    valid = command_map.load_default_command_map()
    assert len(valid) == OPPO_COMMAND_MAP_SIZE

    too_small = dict(valid)
    too_small.pop(next(iter(too_small)))
    small_path = tmp_path / "small.json"
    small_path.write_text(json.dumps(too_small), encoding="utf-8")
    with pytest.raises(ValueError, match="must contain"):
        command_map.load_command_map(small_path)

    forbidden = dict(valid)
    forbidden["power_on"] = "#SIS"
    forbidden_path = tmp_path / "forbidden.json"
    forbidden_path.write_text(json.dumps(forbidden), encoding="utf-8")
    with pytest.raises(ValueError, match="Forbidden OPPO command tokens"):
        command_map.load_command_map(forbidden_path)


def test_settings_default_remains_backward_compatible_json():
    legacy_json = DEFAULTS["oppo_remote_command_map"]
    parsed = json.loads(legacy_json)
    assert parsed == command_map.load_default_command_map()
    assert len(parsed) == OPPO_COMMAND_MAP_SIZE


def test_oppo_remote_default_map_uses_externalized_loader():
    from resources.lib import oppo_remote

    assert oppo_remote.DEFAULT_COMMAND_MAP == command_map.load_default_command_map()
    assert oppo_remote.DEFAULT_COMMAND_MAP["power_on"] == "#PON"
    assert oppo_remote.DEFAULT_COMMAND_MAP["eject"] == "#EJT"


def test_user_command_map_override_still_merges_with_defaults():
    from resources.lib import oppo_remote

    class FakeSettings:
        def __init__(self, raw: str):
            self.raw = raw

        def get(self, key, default=None):
            if key == "oppo_remote_command_map":
                return self.raw
            return default

    merged = oppo_remote._command_map(FakeSettings('{"power_on":"#POW","custom":"#NOP","bad": 1}'))
    assert merged["power_on"] == "#POW"
    assert merged["custom"] == "#NOP"
    assert "bad" not in merged
    assert merged["play"] == "#PLA"


def test_addon_metadata_mentions_build3_externalized_command_map():
    text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.1 Build 3" in text
    assert "resources/data/oppo_command_map.json" in text
    assert "resources/lib/command_map.py" in text
