"""v2.5.0 Build 3 - wizard wording cleanup.

Build 3 intentionally changes only user-facing wizard copy.  These tests guard
that the new copy is clearer while dialog ordering and setting writes remain
compatible with the established v2.5.0 Build 2 wizard flow.
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


class FakeAddon:
    def __init__(self, initial=None):
        self.values = dict(initial or {})

    def getSetting(self, key):
        return self.values.get(key, "")

    def setSetting(self, key, value):
        self.values[key] = str(value)


class TestV250Build3WizardMessageCleanup(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("wizard", None)
        self.wizard = importlib.import_module("wizard")

    def test_wizard_text_constants_are_actionable_and_behavior_neutral(self):
        text = self.wizard.WIZARD_TEXT
        self.assertIn("Basic", text["welcome_body"])
        self.assertIn("Full", text["welcome_body"])
        self.assertIn("IP Control", text["prerequisites_body"])
        self.assertIn("Quick Start", text["prerequisites_body"])
        self.assertIn("Check the IP address", text["unreachable_body"])
        self.assertIn("recommended", text["architecture_body"].lower())
        self.assertEqual(self.wizard._text("quick_start_title"), "Quick Start confirmation")

    def test_full_wizard_uses_clearer_prompts_without_changing_writes(self):
        addon = FakeAddon({"oppo_ip": "192.0.2.20", "oppo_port": "23"})
        prompts = []
        ok_messages = []
        # prerequisites, jailbreak, autoscript shell, quick start, auto-power,
        # architecture auto-test, use external player
        responses = iter([True, True, False, True, False, False, True])
        inputs = iter(["192.0.2.20", "23"])

        def yn(title, message):
            prompts.append((title, message))
            return next(responses)

        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="full"), \
             mock.patch.object(self.wizard, "_probe", return_value=True), \
             mock.patch.object(self.wizard, "_sel", return_value=0), \
             mock.patch.object(self.wizard, "_yn", side_effect=yn), \
             mock.patch.object(self.wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda title, msg: ok_messages.append((title, msg))):
            self.assertTrue(self.wizard.run_wizard())

        titles = [title for title, _ in prompts]
        self.assertIn("Before setup", titles)
        self.assertIn("Stock OPPO jailbreak mode", titles)
        self.assertIn("AutoScript shell handler", titles)
        self.assertIn("Quick Start confirmation", titles)
        self.assertIn("Playback architecture", titles)
        self.assertEqual(addon.values["wizard_completed"], "true")
        self.assertEqual(addon.values["oppo_hardware_model"], "udp_203")
        self.assertEqual(addon.values["oppo_jailbreak_enabled"], "true")
        self.assertEqual(addon.values["oppo_autoscript_shell_handler"], "false")
        self.assertEqual(addon.values["playback_architecture"], "external_player")
        self.assertIn("rerun the wizard", ok_messages[-1][1])

    def test_unreachable_prompt_now_gives_recovery_guidance_and_preserves_cancel(self):
        addon = FakeAddon({"oppo_ip": "192.0.2.21", "oppo_port": "23"})
        prompts = []
        responses = iter([True, False])  # prerequisites yes; unreachable continue no
        inputs = iter(["192.0.2.21", "23"])

        def yn(title, message):
            prompts.append((title, message))
            return next(responses)

        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="basic"), \
             mock.patch.object(self.wizard, "_probe", return_value=False), \
             mock.patch.object(self.wizard, "_yn", side_effect=yn), \
             mock.patch.object(self.wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda *a, **k: None):
            self.assertFalse(self.wizard.run_wizard())

        unreachable = [p for p in prompts if p[0] == "Player not reachable"]
        self.assertEqual(len(unreachable), 1)
        self.assertIn("Check the IP address", unreachable[0][1])
        self.assertNotEqual(addon.values.get("wizard_completed"), "true")


if __name__ == "__main__":
    unittest.main()
