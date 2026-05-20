"""v2.2.0 Build 1 superset-merge tests.

This first merge slice restores v0.9.14 hardware-compatibility preset helpers
and the service settings watcher without starting the broad feature merge.
"""
from pathlib import Path
import importlib
import sys
import unittest
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


class TestFirstRunWizardCompatibilityHelpers(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("first_run_wizard", None)
        self.wizard = importlib.import_module("first_run_wizard")

    def test_clone_preset_mutates_only_recommended_keys_and_warns(self):
        settings = FakeSettings({
            "oppo_start_commands": "#PON\n#PLA",
            "oppo_start_mode": "http_api",
            "oppo_http_activate": "true",
        })
        logs = []
        applied, warnings = self.wizard.apply_compatibility_preset(
            settings, "M9702", _log=logs.append
        )

        self.assertEqual(settings["oppo_start_commands"], "#EJT\n#PLA")
        self.assertEqual(settings["oppo_start_mode"], "tcp_commands")
        self.assertEqual(settings["oppo_http_activate"], "false")
        self.assertEqual(len(applied), 3)
        self.assertTrue(any("Quick Start" in warning for warning in warnings))
        self.assertTrue(any("[v0.9.12-preset]" in line for line in logs))

    def test_stock_jailbreak_preset_uses_json_payload_mode(self):
        settings = FakeSettings({"oppo_http_payload_mode": "raw_path"})
        applied, warnings = self.wizard.apply_compatibility_preset(
            settings, "UDP-203", jailbreak=True
        )

        self.assertEqual(settings["oppo_http_payload_mode"], "json_payload")
        self.assertEqual(applied, [("oppo_http_payload_mode", "raw_path", "json_payload")])
        self.assertTrue(self.wizard.quick_start_required("UDP-203"))
        self.assertTrue(warnings)

    def test_reavon_is_warning_only_and_does_not_mutate_commands(self):
        settings = FakeSettings({"oppo_start_commands": "#PON\n#PLA"})
        applied, warnings = self.wizard.apply_compatibility_preset(
            settings, "Reavon-UBR-X100"
        )

        self.assertEqual(applied, [])
        self.assertEqual(settings["oppo_start_commands"], "#PON\n#PLA")
        self.assertTrue(any("Reavon" in warning for warning in warnings))
        self.assertFalse(self.wizard.quick_start_required("Reavon-UBR-X100"))

    def test_model_reapply_and_warning_logging_are_safe(self):
        settings = FakeSettings({"oppo_jailbreak_enabled": "false"})
        logs = []
        applied, warnings = self.wizard.reapply_preset_on_model_change(
            settings, "UDP-203", "M9205C", _log=logs.append
        )

        self.assertEqual(settings["oppo_start_commands"], "#EJT\n#PLA")
        self.assertEqual(len(applied), 3)
        self.assertTrue(warnings)
        self.assertIn("M9205C", "\n".join(logs))
        logged = self.wizard.log_compatibility_warnings(warnings, _log=logs.append)
        self.assertEqual(logged, len(warnings))
        self.assertEqual(self.wizard.log_compatibility_warnings(["x"], _log=lambda _: (_ for _ in ()).throw(RuntimeError("boom"))), 0)

    def test_autoscript_warning_and_same_model_noop(self):
        settings = FakeSettings({"oppo_jailbreak_enabled": "false"})
        self.assertIsNone(self.wizard.autoscript_verbose_push_warning(False))
        self.assertIn("#SVM 2", self.wizard.autoscript_verbose_push_warning(True))
        self.assertEqual(
            self.wizard.reapply_preset_on_model_change(settings, "UDP-203", "UDP-203"),
            ([], []),
        )

    def test_settings_defaults_and_ui_rows_exist(self):
        import settings_reader as sr
        settings_xml = (ROOT / "resources" / "settings.xml").read_text(encoding="utf-8")
        strings_po = (ROOT / "resources" / "language" / "resource.language.en_gb" / "strings.po").read_text(encoding="utf-8")

        self.assertEqual(sr.DEFAULTS["oppo_jailbreak_enabled"], "false")
        self.assertEqual(sr.DEFAULTS["oppo_autoscript_shell_handler"], "false")
        self.assertIn('id="oppo_jailbreak_enabled"', settings_xml)
        self.assertIn('id="oppo_autoscript_shell_handler"', settings_xml)
        for msg_id in ("#30160", "#30161", "#30162", "#30163"):
            self.assertIn(f'msgctxt "{msg_id}"', strings_po)


class TestServiceCompatibilityWatcher(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("service", None)
        self.service = importlib.import_module("service")

    def test_monitor_records_initial_model_and_reapplies_on_model_change(self):
        first = FakeSettings({"oppo_hardware_model": "UDP-203", "oppo_jailbreak_enabled": "false"})
        second = FakeSettings({"oppo_hardware_model": "M9702", "oppo_jailbreak_enabled": "false"})
        calls = [first, second]
        logs = []

        with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
             mock.patch.object(self.service, "log", side_effect=logs.append):
            monitor = self.service.Monitor()
            self.assertEqual(monitor._last_model, "UDP-203")
            monitor.onSettingsChanged()

        self.assertEqual(monitor._last_model, "M9702")
        self.assertEqual(second["oppo_start_commands"], "#EJT\n#PLA")
        self.assertTrue(any("model-change" in item for item in logs))
        self.assertTrue(any("[v0.9.14-warning]" in item for item in logs))

    def test_monitor_noops_when_relevant_settings_do_not_change(self):
        first = FakeSettings({"oppo_hardware_model": "UDP-203", "oppo_jailbreak_enabled": "false"})
        second = FakeSettings({"oppo_hardware_model": "UDP-203", "oppo_jailbreak_enabled": "false"})
        calls = [first, second]
        logs = []

        with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
             mock.patch.object(self.service, "log", side_effect=logs.append):
            monitor = self.service.Monitor()
            monitor.onSettingsChanged()

        self.assertEqual(logs, [])
        self.assertNotIn("oppo_start_commands", second)

    def test_monitor_jailbreak_change_applies_stock_json_payload(self):
        first = FakeSettings({"oppo_hardware_model": "UDP-203", "oppo_jailbreak_enabled": "false"})
        second = FakeSettings({"oppo_hardware_model": "UDP-203", "oppo_jailbreak_enabled": "true", "oppo_http_payload_mode": "raw_path"})
        calls = [first, second]

        with mock.patch.object(self.service, "_read_settings", side_effect=lambda: calls.pop(0)), \
             mock.patch.object(self.service, "log"):
            monitor = self.service.Monitor()
            monitor.onSettingsChanged()

        self.assertTrue(monitor._last_jailbreak)
        self.assertEqual(second["oppo_http_payload_mode"], "json_payload")


if __name__ == "__main__":
    unittest.main()

class TestFirstRunWizardDefensiveBranches(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("first_run_wizard", None)
        self.wizard = importlib.import_module("first_run_wizard")

    def test_private_setting_helpers_and_bool_edges(self):
        class RaisesGet:
            def get(self, *args):
                raise RuntimeError("get fail")
        class DataOnly:
            def __init__(self):
                self.data = {}
            def __setitem__(self, key, value):
                raise RuntimeError("set fail")
        class CannotSet:
            def __setitem__(self, key, value):
                raise RuntimeError("set fail")
        class BadStr:
            def __str__(self):
                raise RuntimeError("str fail")

        self.assertEqual(self.wizard._setting_get(RaisesGet(), "x", "d"), "d")
        data_only = DataOnly()
        self.assertTrue(self.wizard._setting_set(data_only, "x", "y"))
        self.assertEqual(data_only.data["x"], "y")
        self.assertFalse(self.wizard._setting_set(CannotSet(), "x", "y"))
        self.assertTrue(self.wizard._bool(None, default=True))
        self.assertTrue(self.wizard._bool(True))
        self.assertTrue(self.wizard._bool(BadStr(), default=True))
        self.assertTrue(self.wizard._bool("", default=True))
        self.assertFalse(self.wizard._bool("off"))

    def test_import_failure_fallbacks_are_safe(self):
        with mock.patch.dict(sys.modules, {"settings_reader": None}):
            self.assertEqual(self.wizard.apply_compatibility_preset({}, "M9702"), ([], []))
            self.assertTrue(self.wizard.quick_start_required("M9702"))
            self.assertIn("port-23", self.wizard.autoscript_verbose_push_warning(True))

    def test_apply_handles_profile_set_and_log_failures(self):
        import types
        fake = types.ModuleType("settings_reader")
        fake.REAVON_WARNING_TEXT = "reavon"
        fake.QUICK_START_PREREQUISITE_TEXT = "quick"
        fake.compatibility_preset = lambda model, jailbreak=False: {"a": "b", "c": "d"}
        fake.hardware_profile = lambda model: (_ for _ in ()).throw(RuntimeError("profile fail"))

        class RejectSettings(dict):
            def __setitem__(self, key, value):
                if key == "c":
                    raise RuntimeError("reject")
                return super().__setitem__(key, value)

        with mock.patch.dict(sys.modules, {"settings_reader": fake}):
            settings = RejectSettings()
            applied, warnings = self.wizard.apply_compatibility_preset(
                settings, "X", _log=lambda _: (_ for _ in ()).throw(RuntimeError("log fail"))
            )

        self.assertEqual(settings["a"], "b")
        self.assertEqual(applied, [("a", None, "b")])
        self.assertEqual(warnings, [])

    def test_reapply_and_warning_log_noop_and_log_exception(self):
        logs = []
        self.assertEqual(self.wizard.log_compatibility_warnings([], _log=logs.append), 0)
        self.assertEqual(self.wizard.log_compatibility_warnings(["x"], _log=None), 0)
        settings = FakeSettings({"oppo_jailbreak_enabled": "false"})
        applied, warnings = self.wizard.reapply_preset_on_model_change(
            settings, "UDP-203", "M9702", _log=lambda _: (_ for _ in ()).throw(RuntimeError("log fail"))
        )
        self.assertEqual(len(applied), 3)
        self.assertTrue(warnings)
