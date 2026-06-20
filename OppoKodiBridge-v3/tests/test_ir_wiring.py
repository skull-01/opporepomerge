"""Regression guard for the from_addon wiring bug: the three IR settings must round-trip
settings -> Config -> runtime_config.json -> Config, end to end. No Kodi, no hardware."""
import dataclasses
import json
import os
import sys
import tempfile
import types

from resources.lib.config import Config


def _fake_xbmcaddon(settings):
    mod = types.ModuleType("xbmcaddon")

    class Addon:
        def getSettingString(self, key):
            return settings.get(key, "")

        def getSettingBool(self, key):
            return bool(settings.get(key, False))

        def getSettingInt(self, key):
            return int(settings.get(key, 0))

    mod.Addon = Addon
    return mod


def test_from_addon_reads_ir_settings(monkeypatch):
    settings = {
        "oppo_ip": "192.168.10.10",
        "broadlink_ip": "192.168.1.50",
        "ir_code_oppo": "JgBYAAAB",
        "ir_code_kodi": "JgBYAAAC",
    }
    monkeypatch.setitem(sys.modules, "xbmcaddon", _fake_xbmcaddon(settings))
    from resources.lib import config as config_mod

    cfg = config_mod.from_addon()
    assert cfg.broadlink_ip == "192.168.1.50"
    assert cfg.ir_code_oppo == "JgBYAAAB"
    assert cfg.ir_code_kodi == "JgBYAAAC"


def test_ir_settings_survive_json_file_roundtrip():
    # exercises the REAL boundary service_v3 uses: dataclasses.asdict -> json.dump (file) ->
    # json.load -> Config.from_dict, where the original bug silently dropped the IR fields.
    cfg = Config(
        oppo_ip="192.168.10.10",
        broadlink_ip="192.168.1.50",
        ir_code_oppo="JgBYAAAB,JgBYAAAC",   # comma-delimited nav sequence
        ir_code_kodi="JgBYAAAD",
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "runtime_config.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(dataclasses.asdict(cfg), fh)
        with open(path, "r", encoding="utf-8") as fh:
            restored = Config.from_dict(json.load(fh))
    assert restored.broadlink_ip == "192.168.1.50"
    assert restored.ir_code_oppo == "JgBYAAAB,JgBYAAAC"
    assert restored.ir_code_kodi == "JgBYAAAD"
