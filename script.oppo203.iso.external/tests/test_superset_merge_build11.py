"""v2.2.0 Build 11 - active wizard/UI compatibility flag reconciliation.

This slice further reduces the remaining v0.9.14/v1.1.9 wizard gap by
capturing jailbreak and AutoScript-shell compatibility flags in the active
v1.x full wizard path and by applying the safe stock-OPPO JSON payload preset
without replacing the stable wizard flow.
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file
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


class TestActiveWizardCompatibilityFlags(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("wizard", None)
        self.wizard = importlib.import_module("wizard")

    def test_full_wizard_asks_and_stores_stock_jailbreak_and_autoscript_flags(self):
        addon = FakeAddon({"oppo_ip": "192.0.2.10", "oppo_port": "23"})
        ok_messages = []
        # prerequisites, jailbreak, autoscript shell, quick start, auto-power,
        # architecture auto-test, use external player
        responses = iter([True, True, True, True, False, False, True])
        inputs = iter(["192.0.2.10", "23"])
        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="full"), \
             mock.patch.object(self.wizard, "_probe", return_value=True), \
             mock.patch.object(self.wizard, "_sel", return_value=0), \
             mock.patch.object(self.wizard, "_yn", side_effect=lambda *a, **k: next(responses)), \
             mock.patch.object(self.wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda title, msg: ok_messages.append((title, msg))):
            self.assertTrue(self.wizard.run_wizard())
        self.assertEqual(addon.values["oppo_hardware_model"], "udp_203")
        self.assertEqual(addon.values["oppo_jailbreak_enabled"], "true")
        self.assertEqual(addon.values["oppo_autoscript_shell_handler"], "true")
        self.assertEqual(addon.values["oppo_http_payload_mode"], "json_payload")
        joined = "\n".join(message for _, message in ok_messages)
        self.assertIn("Quick Start", joined)
        self.assertIn("AutoScript", joined)

    def test_basic_wizard_does_not_prompt_for_new_compatibility_flags(self):
        addon = FakeAddon({"oppo_jailbreak_enabled": "true"})
        prompts = []
        class UI:
            def ok(self, title, message):
                prompts.append((title, message))
        flags = self.wizard._ask_compatibility_flags(addon, "udp_203", is_full=False)
        self.assertEqual(flags["jailbreak"], True)
        self.assertEqual(flags["uses_autoscript_shell"], False)
        self.assertNotIn("oppo_autoscript_shell_handler", addon.values)
        # Existing settings can still be applied/surfaced explicitly.
        result = self.wizard._apply_and_surface_hardware_compatibility(addon, "udp_203", ui=UI())
        self.assertEqual(addon.values["oppo_http_payload_mode"], "json_payload")
        self.assertGreaterEqual(result["surfaced"], 1)

    def test_full_wizard_reavon_flags_surface_warnings_without_command_mutation(self):
        addon = FakeAddon({"oppo_ip": "192.0.2.11", "oppo_port": "23"})
        ok_messages = []
        # prerequisites, autoscript shell, quick start, auto-power,
        # architecture auto-test, use external player. Reavon is not stock, so
        # no jailbreak prompt is asked.
        responses = iter([True, True, True, False, False, True])
        inputs = iter(["192.0.2.11", "23"])
        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="full"), \
             mock.patch.object(self.wizard, "_probe", return_value=True), \
             mock.patch.object(self.wizard, "_sel", return_value=9), \
             mock.patch.object(self.wizard, "_yn", side_effect=lambda *a, **k: next(responses)), \
             mock.patch.object(self.wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda title, msg: ok_messages.append((title, msg))):
            self.assertTrue(self.wizard.run_wizard())
        self.assertEqual(addon.values["oppo_hardware_model"], "reavon_ubrx100")
        self.assertEqual(addon.values["oppo_autoscript_shell_handler"], "true")
        self.assertNotIn("oppo_start_commands", addon.values)
        self.assertNotIn("oppo_http_payload_mode", addon.values)
        joined = "\n".join(message for _, message in ok_messages)
        self.assertIn("Reavon", joined)
        self.assertIn("AutoScript", joined)


class TestBuild11ReleaseIdentity(unittest.TestCase):
    def test_addon_version_is_build11(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.12")

    def test_build11_evidence_files_exist(self):
        for rel in (
            "BUILD_NOTES_v2.2.0_BUILD11.md",
            "RELEASE_MANIFEST_v2.2.0_BUILD11.md",
            "COVERAGE_REPORT_v2.2.0_BUILD11.md",
            "TEST_AUDIT_REPORT_v2.2.0_BUILD11.md",
            "MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD11.md",
        ):
            self.assertTrue(find_project_file(ROOT, rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
