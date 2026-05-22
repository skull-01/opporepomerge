"""v2.2.0 Build 6 - active wizard warning-surfacing integration.

This slice wires the Build 5 compatibility-warning surfacing helper into one
active v1.x wizard path without replacing the wizard or changing the existing
clone preset confirmation flow.
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class FakeAddon:
    def __init__(self, initial=None):
        self.values = dict(initial or {})

    def getSetting(self, key):
        return self.values.get(key, "")

    def setSetting(self, key, value):
        self.values[key] = str(value)


class TestActiveWizardWarningIntegration(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("wizard", None)
        self.wizard = importlib.import_module("wizard")

    def test_direct_active_wizard_helper_surfaces_reavon_warning_only(self):
        addon = FakeAddon({"oppo_jailbreak_enabled": "true"})
        ui_calls = []
        class UI:
            def ok(self, title, message):
                ui_calls.append((title, message))
        count = self.wizard._surface_hardware_compatibility_warnings(
            addon, "reavon_ubrx100", ui=UI()
        )
        self.assertEqual(count, 1)
        self.assertIn("Reavon", ui_calls[0][1])
        self.assertNotIn("oppo_start_commands", addon.values)
        self.assertNotIn("oppo_http_payload_mode", addon.values)

    def test_direct_active_wizard_helper_surfaces_autoscript_warning(self):
        addon = FakeAddon({"oppo_autoscript_shell_handler": "true"})
        messages = []
        class UI:
            def ok(self, title, message):
                messages.append(message)
        count = self.wizard._surface_hardware_compatibility_warnings(
            addon, "M9702", ui=UI()
        )
        self.assertGreaterEqual(count, 2)
        joined = "\n".join(messages)
        self.assertIn("Quick Start", joined)
        self.assertIn("AutoScript", joined)

    def test_run_wizard_surfaces_reavon_warning_in_active_hardware_path(self):
        addon = FakeAddon({
            "oppo_ip": "192.0.2.55",
            "oppo_port": "23",
            "oppo_jailbreak_enabled": "true",
        })
        ok_messages = []
        responses = iter([True, True, False])  # prerequisites, quick start, auto-power
        inputs = iter(["192.0.2.55", "23"])
        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="basic"), \
             mock.patch.object(self.wizard, "_probe", return_value=True), \
             mock.patch.object(self.wizard, "_sel", return_value=9), \
             mock.patch.object(self.wizard, "_yn", side_effect=lambda *a, **k: next(responses)), \
             mock.patch.object(self.wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda title, msg: ok_messages.append((title, msg))):
            self.assertTrue(self.wizard.run_wizard())
        self.assertEqual(addon.values["oppo_hardware_model"], "reavon_ubrx100")
        joined = "\n".join(message for _, message in ok_messages)
        self.assertIn("Reavon", joined)
        self.assertNotIn("oppo_start_commands", addon.values)

    def test_active_wizard_helper_import_failure_is_nonfatal(self):
        addon = FakeAddon()
        with mock.patch.dict(sys.modules, {"first_run_wizard": None}):
            self.assertEqual(
                self.wizard._surface_hardware_compatibility_warnings(addon, "M9702"),
                0,
            )


class TestBuild6ReleaseIdentity(unittest.TestCase):
    def test_addon_version_is_build6(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.11")


if __name__ == "__main__":
    unittest.main()
