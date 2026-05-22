"""v2.2.0 Build 3 - v0.9.14 service/wizard warning logging slice.

This merge slice keeps the superset merge gradual by extending the restored
compatibility watcher to log AutoScript verbose-push warnings and by adding a
side-effect-free warning collector for wizard/service reuse.
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from unittest import mock

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
        if value is None:
            return bool(default)
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text == "":
            return bool(default)
        return text in ("1", "true", "yes", "on")


class TestV0914WarningCollector(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("first_run_wizard", None)
        self.wizard = importlib.import_module("first_run_wizard")

    def test_collects_quick_start_and_autoscript_warnings_from_settings(self):
        settings = FakeSettings({
            "oppo_hardware_model": "M9702",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "true",
        })
        warnings = self.wizard.collect_compatibility_warnings(settings)
        text = "\n".join(warnings)
        self.assertIn("Quick Start", text)
        self.assertIn("#SVM 2", text)
        self.assertEqual(len(warnings), len(set(warnings)))

    def test_collects_reavon_without_quick_start_and_keeps_autoscript_warning(self):
        warnings = self.wizard.collect_compatibility_warnings(
            model="Reavon-UBR-X200", uses_autoscript_shell=True
        )
        text = "\n".join(warnings)
        self.assertIn("Reavon", text)
        self.assertIn("#SVM 2", text)
        self.assertNotIn("Quick Start mode is required", text)

    def test_collector_is_safe_when_settings_reader_import_fails(self):
        with mock.patch.dict(sys.modules, {"settings_reader": None}):
            warnings = self.wizard.collect_compatibility_warnings(
                model="M9702", uses_autoscript_shell=True
            )
        self.assertEqual(len(warnings), 1)
        self.assertIn("port-23", warnings[0])


class TestServiceV0914WarningWatcher(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("service", None)
        self.service = importlib.import_module("service")

    def test_monitor_tracks_initial_autoscript_flag(self):
        settings = FakeSettings({
            "oppo_hardware_model": "UDP-203",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "true",
        })
        with mock.patch.object(self.service, "_read_settings", return_value=settings):
            monitor = self.service.Monitor()
        self.assertTrue(monitor._last_autoscript_shell)

    def test_monitor_logs_autoscript_warning_when_only_autoscript_setting_changes(self):
        first = FakeSettings({
            "oppo_hardware_model": "UDP-203",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "false",
        })
        second = FakeSettings({
            "oppo_hardware_model": "UDP-203",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "true",
        })
        calls = [first, second]
        logs = []
        with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
             mock.patch.object(self.service, "log", side_effect=logs.append):
            monitor = self.service.Monitor()
            monitor.onSettingsChanged()
        self.assertTrue(monitor._last_autoscript_shell)
        joined = "\n".join(logs)
        self.assertIn("#SVM 2", joined)
        self.assertIn("autoscript_shell=True", joined)

    def test_monitor_logs_combined_reavon_and_autoscript_warnings(self):
        first = FakeSettings({
            "oppo_hardware_model": "UDP-203",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "false",
        })
        second = FakeSettings({
            "oppo_hardware_model": "Reavon-UBR-X110",
            "oppo_jailbreak_enabled": "false",
            "oppo_autoscript_shell_handler": "true",
        })
        calls = [first, second]
        logs = []
        with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
             mock.patch.object(self.service, "log", side_effect=logs.append):
            monitor = self.service.Monitor()
            monitor.onSettingsChanged()
        joined = "\n".join(logs)
        self.assertIn("Reavon", joined)
        self.assertIn("#SVM 2", joined)
        self.assertNotIn("Quick Start mode is required", joined)
        self.assertEqual(second.get("oppo_start_commands"), None)


class TestBuild3ReleaseIdentity(unittest.TestCase):
    def test_addon_version_is_build3(self):
        import xml.etree.ElementTree as ET
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.11")


if __name__ == "__main__":
    unittest.main()
