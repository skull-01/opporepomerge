"""v2.5.0 Build 4 - wizard recovery flow regression tests.

Build 4 adds additive recovery metadata so cancelled, failed, or retried wizard
runs are supportable without changing playback, command, or hardware behavior.
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


class TestV250Build4WizardRecovery(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("wizard", None)
        self.wizard = importlib.import_module("wizard")

    def test_prerequisite_cancel_marks_recovery_without_claiming_completion(self):
        addon = FakeAddon({"wizard_completed": "false"})
        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="basic"), \
             mock.patch.object(self.wizard, "_yn", return_value=False), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda *a, **k: None):
            self.assertFalse(self.wizard.run_wizard())

        self.assertEqual(addon.values["wizard_completed"], "false")
        self.assertEqual(addon.values["wizard_in_progress"], "false")
        self.assertEqual(addon.values["wizard_last_exit"], "cancelled")
        self.assertEqual(addon.values["wizard_last_step"], "prerequisites")
        self.assertEqual(addon.values["wizard_recovery_available"], "true")

    def test_unreachable_cancel_preserves_prior_completed_rerun_state(self):
        addon = FakeAddon({"wizard_completed": "true", "oppo_ip": "192.0.2.44", "oppo_port": "23"})
        responses = iter([True, False])  # prerequisites yes, unreachable continue no
        inputs = iter(["192.0.2.44", "23"])
        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="basic"), \
             mock.patch.object(self.wizard, "_probe", return_value=False), \
             mock.patch.object(self.wizard, "_yn", side_effect=lambda *a, **k: next(responses)), \
             mock.patch.object(self.wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda *a, **k: None):
            self.assertFalse(self.wizard.run_wizard())

        self.assertEqual(addon.values["wizard_completed"], "true")
        self.assertEqual(addon.values["wizard_in_progress"], "false")
        self.assertEqual(addon.values["wizard_last_exit"], "cancelled")
        self.assertEqual(addon.values["wizard_last_step"], "network_unreachable")
        self.assertEqual(addon.values["wizard_recovery_available"], "true")

    def test_successful_retry_clears_partial_recovery_markers(self):
        addon = FakeAddon({
            "wizard_completed": "false",
            "wizard_in_progress": "true",
            "wizard_last_exit": "cancelled",
            "wizard_last_step": "network_unreachable",
            "wizard_recovery_available": "true",
            "oppo_ip": "192.0.2.45",
            "oppo_port": "23",
        })
        responses = iter([True, True, False])  # prerequisites, quick start, auto power
        inputs = iter(["192.0.2.45", "23"])
        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_choose_mode", return_value="basic"), \
             mock.patch.object(self.wizard, "_probe", return_value=True), \
             mock.patch.object(self.wizard, "_sel", return_value=0), \
             mock.patch.object(self.wizard, "_yn", side_effect=lambda *a, **k: next(responses)), \
             mock.patch.object(self.wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda *a, **k: None):
            self.assertTrue(self.wizard.run_wizard())

        self.assertEqual(addon.values["wizard_completed"], "true")
        self.assertEqual(addon.values["wizard_in_progress"], "false")
        self.assertEqual(addon.values["wizard_last_exit"], "completed")
        self.assertEqual(addon.values["wizard_last_step"], "completed")
        self.assertEqual(addon.values["wizard_recovery_available"], "false")
        self.assertEqual(addon.values["architecture_choice_made"], "true")

    def test_exception_marks_error_then_reraises_for_existing_error_handling(self):
        addon = FakeAddon({"wizard_completed": "false"})
        with mock.patch.object(self.wizard, "_addon", return_value=addon), \
             mock.patch.object(self.wizard, "_ok", side_effect=lambda *a, **k: None), \
             mock.patch.object(self.wizard, "_choose_mode", side_effect=RuntimeError("mode fail")):
            with self.assertRaises(RuntimeError):
                self.wizard.run_wizard()

        self.assertEqual(addon.values["wizard_completed"], "false")
        self.assertEqual(addon.values["wizard_in_progress"], "false")
        self.assertEqual(addon.values["wizard_last_exit"], "error")
        self.assertEqual(addon.values["wizard_last_step"], "mode")
        self.assertEqual(addon.values["wizard_recovery_available"], "true")

    def test_recovery_summary_reports_support_state(self):
        addon = FakeAddon({
            "wizard_completed": "false",
            "wizard_in_progress": "false",
            "wizard_last_exit": "cancelled",
            "wizard_last_step": "prerequisites",
            "wizard_recovery_available": "true",
        })
        self.assertEqual(self.wizard.wizard_recovery_summary(addon), {
            "completed": "false",
            "in_progress": "false",
            "last_exit": "cancelled",
            "last_step": "prerequisites",
            "recovery_available": "true",
        })


if __name__ == "__main__":
    unittest.main()
