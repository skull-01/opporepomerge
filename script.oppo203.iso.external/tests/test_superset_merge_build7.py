"""v2.2.0 Build 7 - service watcher persistence edge-case lock-down.

This slice keeps the v1.1.9 + v0.9.14 merge gradual by adding tests around
service watcher persistence edge cases.  It does not broaden the merge scope;
it proves that failure paths are safe and that warning-only hardware remains
warning-only even when settings are changed outside the wizard.
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


class TestServiceWatcherPersistenceEdgeCases(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("service", None)
        self.service = importlib.import_module("service")

    def test_save_failure_is_logged_and_state_still_advances(self):
        """A failed settings.xml write must not loop or block Kodi settings UI."""
        first = FakeSettings({
            "addon_data_dir": "/tmp/not-written",
            "oppo_hardware_model": "UDP-203",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "false",
            "oppo_start_commands": "#PON\n#PLA",
            "oppo_start_mode": "http_api",
            "oppo_http_activate": "true",
        })
        second = FakeSettings(dict(first, oppo_hardware_model="M9702"))
        calls = [first, second, second]
        logs = []
        with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
             mock.patch.object(self.service, "log", side_effect=logs.append), \
             mock.patch("settings_reader.save_settings", side_effect=RuntimeError("disk locked")):
            monitor = self.service.Monitor()
            monitor.onSettingsChanged()
            monitor.onSettingsChanged()
        joined = "\n".join(logs)
        self.assertIn("save failed", joined)
        self.assertIn("saved=False", joined)
        self.assertEqual(second["oppo_start_commands"], "#EJT\n#PLA")
        # The second call sees no further change because last-state advanced.
        self.assertEqual(sum("model-change:" in item for item in logs), 1)

    def test_no_addon_data_dir_keeps_preset_in_memory_without_persisting(self):
        first = FakeSettings({
            "oppo_hardware_model": "UDP-203",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "false",
        })
        second = FakeSettings(dict(first, oppo_hardware_model="M9205C"))
        calls = [first, second]
        logs = []
        with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
             mock.patch.object(self.service, "log", side_effect=logs.append):
            monitor = self.service.Monitor()
            monitor.onSettingsChanged()
        self.assertEqual(second["oppo_start_commands"], "#EJT\n#PLA")
        self.assertTrue(any("saved=False" in item for item in logs))

    def test_jailbreak_toggle_persists_stock_json_payload_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = FakeSettings({
                "addon_data_dir": tmp,
                "oppo_hardware_model": "UDP-203",
                "oppo_jailbreak_enabled": "false",
                "oppo_autoscript_shell_handler": "false",
                "oppo_http_payload_mode": "raw_path",
            })
            second = FakeSettings(dict(first, oppo_jailbreak_enabled="true"))
            calls = [first, second]
            logs = []
            with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
                 mock.patch.object(self.service, "log", side_effect=logs.append):
                monitor = self.service.Monitor()
                monitor.onSettingsChanged()
            values = {node.attrib["id"]: node.attrib.get("value", "") for node in ET.parse(Path(tmp) / "settings.xml").getroot().iter("setting")}
        self.assertEqual(values["oppo_http_payload_mode"], "json_payload")
        self.assertTrue(any("saved=True" in item for item in logs))

    def test_settings_reader_save_settings_returns_false_for_blank_directory(self):
        import settings_reader as sr
        # Empty addon-data directory should fail safely rather than writing beside cwd.
        self.assertFalse(sr.save_settings("", sr.Settings({"oppo_hardware_model": "M9702"})))


class TestBuild7ReleaseIdentity(unittest.TestCase):
    def test_addon_version_is_build7(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.13")


if __name__ == "__main__":
    unittest.main()
