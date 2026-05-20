"""v2.2.0 Build 4 - service watcher persistence merge slice.

This slice keeps the v1.1.9 + v0.9.14 merge gradual by persisting
compatibility-preset changes made by the service settings watcher.  The
v0.9.14 watcher behavior should not be only in-memory: if a user changes the
hardware model in Kodi settings, the safe preset should be written back to the
addon-data settings file when possible.
"""
from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class FakeSettings(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self

    def get_bool(self, key, default=False):
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text == "":
            return bool(default)
        return text in ("1", "true", "yes", "on")


class TestSettingsReaderPersistence(unittest.TestCase):
    def test_save_settings_creates_file_and_skips_private_runtime_keys(self):
        import settings_reader as sr
        with tempfile.TemporaryDirectory() as tmp:
            settings = sr.Settings({
                "oppo_hardware_model": "M9702",
                "oppo_start_commands": "#EJT\n#PLA",
                "addon_data_dir": tmp,
                "_lib_path": "/tmp/ignored",
            })
            self.assertTrue(sr.save_settings(tmp, settings))
            root = ET.parse(Path(tmp) / "settings.xml").getroot()
            values = {node.attrib["id"]: node.attrib.get("value", "") for node in root.iter("setting")}
        self.assertEqual(values["oppo_hardware_model"], "M9702")
        self.assertEqual(values["oppo_start_commands"], "#EJT\n#PLA")
        self.assertNotIn("addon_data_dir", values)
        self.assertNotIn("_lib_path", values)

    def test_save_settings_preserves_existing_rows_and_updates_values(self):
        import settings_reader as sr
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.xml"
            path.write_text('<settings><setting id="oppo_start_mode" value="http_api"/></settings>', encoding="utf-8")
            settings = sr.Settings({"oppo_start_mode": "tcp_commands", "oppo_http_activate": "false"})
            self.assertTrue(sr.save_settings(tmp, settings))
            values = {node.attrib["id"]: node.attrib.get("value", "") for node in ET.parse(path).getroot().iter("setting")}
        self.assertEqual(values["oppo_start_mode"], "tcp_commands")
        self.assertEqual(values["oppo_http_activate"], "false")


class TestServiceWatcherPersistence(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("service", None)
        self.service = importlib.import_module("service")

    def test_model_change_persists_applied_clone_preset(self):
        with tempfile.TemporaryDirectory() as tmp:
            initial = FakeSettings({
                "addon_data_dir": tmp,
                "oppo_hardware_model": "UDP-203",
                "oppo_jailbreak_enabled": "false",
                "oppo_autoscript_shell_handler": "false",
                "oppo_start_commands": "#PON\n#PLA",
                "oppo_start_mode": "http_api",
                "oppo_http_activate": "true",
            })
            changed = FakeSettings(dict(initial, oppo_hardware_model="M9203"))
            calls = [initial, changed]
            logs = []
            with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
                 mock.patch.object(self.service, "log", side_effect=logs.append):
                monitor = self.service.Monitor()
                monitor.onSettingsChanged()
            values = {node.attrib["id"]: node.attrib.get("value", "") for node in ET.parse(Path(tmp) / "settings.xml").getroot().iter("setting")}
        self.assertEqual(values["oppo_start_commands"], "#EJT\n#PLA")
        self.assertEqual(values["oppo_start_mode"], "tcp_commands")
        self.assertEqual(values["oppo_http_activate"], "false")
        self.assertTrue(any("saved=True" in item for item in logs))

    def test_reavon_warning_only_change_does_not_persist_command_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            initial = FakeSettings({
                "addon_data_dir": tmp,
                "oppo_hardware_model": "UDP-203",
                "oppo_jailbreak_enabled": "false",
                "oppo_autoscript_shell_handler": "false",
                "oppo_start_commands": "#PON\n#PLA",
            })
            changed = FakeSettings(dict(initial, oppo_hardware_model="Reavon-UBR-X200"))
            calls = [initial, changed]
            logs = []
            with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
                 mock.patch.object(self.service, "log", side_effect=logs.append):
                monitor = self.service.Monitor()
                monitor.onSettingsChanged()
        self.assertFalse((Path(tmp) / "settings.xml").exists())
        joined = "\n".join(logs)
        self.assertIn("Reavon", joined)
        self.assertIn("saved=False", joined)


class TestBuild4ReleaseIdentity(unittest.TestCase):
    def test_addon_version_is_build4(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.10")


if __name__ == "__main__":
    unittest.main()
