"""v2.2.0 Build 5 - wizard/UI compatibility-warning surfacing slice.

This slice keeps the v1.1.9 + v0.9.14 merge gradual by restoring the
v0.9.14 behavior that compatibility warnings can be surfaced through a wizard
UI while also being written to support logs.  The active v1.x wizard is not
replaced in this build.
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class DictSettings(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self


class RecordingUI:
    def __init__(self, answer=None):
        self.calls = []
        self.answer = answer

    def ok(self, title, message):
        self.calls.append(("ok", title, message))

    def notify(self, message):
        self.calls.append(("notify", message))

    def show_text(self, message):
        self.calls.append(("show_text", message))

    def ask_choice(self, prompt, choices, default):
        self.calls.append(("ask_choice", prompt, tuple(choices), default))
        return self.answer


class NotifyOnlyUI:
    def __init__(self):
        self.calls = []

    def notify(self, message):
        self.calls.append(("notify", message))


class OneArgumentOkUI:
    def __init__(self):
        self.calls = []

    def ok(self, message):
        self.calls.append(("ok", message))


class FailingUI:
    def ok(self, title, message):
        raise RuntimeError("ui down")

    def notify(self, message):
        raise RuntimeError("notify down")

    def show_text(self, message):
        raise RuntimeError("text down")

    def ask_choice(self, prompt, choices, default):
        raise RuntimeError("choice down")


class TestWizardWarningSurfacing(unittest.TestCase):
    def setUp(self):
        self.wizard = importlib.import_module("first_run_wizard")

    def test_surface_warnings_prefers_ok_and_logs_marker(self):
        ui = RecordingUI()
        logs = []
        count = self.wizard.surface_compatibility_warnings(
            ui, ["Quick Start", "AutoScript"], _log=logs.append
        )
        self.assertEqual(count, 2)
        self.assertEqual([call[0] for call in ui.calls], ["ok", "ok"])
        self.assertTrue(all("[v0.9.14-warning]" in item for item in logs))

    def test_surface_warnings_falls_back_to_notify_and_one_argument_ok(self):
        notify = NotifyOnlyUI()
        self.assertEqual(self.wizard.surface_compatibility_warnings(notify, ["warn"]), 1)
        self.assertEqual(notify.calls, [("notify", "warn")])
        one_arg = OneArgumentOkUI()
        self.assertEqual(self.wizard.surface_compatibility_warnings(one_arg, ["warn2"]), 1)
        self.assertEqual(one_arg.calls, [("ok", "warn2")])

    def test_surface_warnings_swallow_ui_and_log_failures(self):
        self.assertEqual(
            self.wizard.surface_compatibility_warnings(
                FailingUI(), ["warn", None, {"x": 1}], _log=lambda _: (_ for _ in ()).throw(RuntimeError("log down"))
            ),
            0,
        )

    def test_ask_choice_validates_ui_answer(self):
        valid = RecordingUI(answer="M9702")
        self.assertEqual(self.wizard.ask_choice(valid, "Hardware", ["UDP-203", "M9702"], "UDP-203"), "M9702")
        invalid = RecordingUI(answer="Bad")
        self.assertEqual(self.wizard.ask_choice(invalid, "Hardware", ["UDP-203", "M9702"], "UDP-203"), "UDP-203")
        self.assertEqual(self.wizard.ask_choice(None, "Hardware", ["UDP-203"], "UDP-203"), "UDP-203")
        self.assertIsNone(self.wizard.ask_choice(FailingUI(), "Hardware", [], None))
        self.assertEqual(self.wizard.ask_choice(FailingUI(), "Hardware", ["UDP-203"], "Bad"), "UDP-203")

    def test_apply_and_surface_clone_preset_with_autoscript_warning(self):
        settings = DictSettings({"oppo_start_commands": "#PON\n#PLA"})
        ui = RecordingUI()
        logs = []
        result = self.wizard.apply_and_surface_compatibility(
            settings, "M9702", uses_autoscript_shell=True, ui=ui, _log=logs.append
        )
        self.assertEqual(settings["oppo_start_commands"], "#EJT\n#PLA")
        self.assertEqual(settings["oppo_start_mode"], "tcp_commands")
        self.assertEqual(settings["oppo_http_activate"], "false")
        self.assertTrue(result["applied"])
        self.assertGreaterEqual(result["surfaced"], 2)
        joined = "\n".join(result["warnings"])
        self.assertIn("Quick Start", joined)
        self.assertIn("AutoScript", joined)
        self.assertTrue(any("v0.9.12-preset" in item for item in logs))

    def test_apply_and_surface_reavon_remains_warning_only(self):
        settings = DictSettings({"oppo_start_commands": "#PON\n#PLA"})
        ui = RecordingUI()
        result = self.wizard.apply_and_surface_compatibility(
            settings, "Reavon-UBR-X100", jailbreak=True, uses_autoscript_shell=False, ui=ui
        )
        self.assertEqual(result["applied"], [])
        self.assertEqual(settings["oppo_start_commands"], "#PON\n#PLA")
        self.assertEqual(result["surfaced"], 1)
        self.assertIn("Reavon", result["warnings"][0])


class TestBuild5ReleaseIdentity(unittest.TestCase):
    def test_addon_version_is_build5(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.10")


if __name__ == "__main__":
    unittest.main()
