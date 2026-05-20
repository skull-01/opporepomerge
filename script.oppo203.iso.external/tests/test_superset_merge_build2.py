"""v2.2.0 Build 2 - v0.9.14 hardware compatibility regression tests.

This merge slice deliberately ports/locks down remaining v0.9.14 hardware
assertions without starting the broad historical feature merge.
"""
from __future__ import annotations

import importlib
import os
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
    def get(self, key, default=None):
        return super().get(key, default)


class TestV0914HardwareMatrixPort(unittest.TestCase):
    def test_active_v2910_player_models_are_present_and_settings_enum_matches(self):
        import settings_reader as sr
        expected = {
            "UDP-203", "UDP-205", "M9200", "M9201", "M9203", "M9205", "M9205C", "M9702",
            "CineUltra-V203", "CineUltra-V204",
            "IPUK-UHD8592", "GIEC-BDP-G5300", "Magnetar-UDP800", "Magnetar-UDP900",
            "Reavon-UBR-X100", "Reavon-UBR-X110", "Reavon-UBR-X200",
        }
        self.assertEqual(set(sr.HARDWARE_COMPAT), expected)
        settings_xml = (ROOT / "resources" / "settings.xml").read_text(encoding="utf-8")
        import re
        match = re.search(r'id="oppo_hardware_model"[^>]*values="([^"]+)"', settings_xml)
        self.assertIsNotNone(match)
        enum_models = {sr.normalize_hardware_model(item) for item in match.group(1).split("|")}
        self.assertEqual(enum_models, expected)

    def test_m9203_and_m9205c_have_explicit_chinoppo_clone_profiles(self):
        import settings_reader as sr
        for model in ("M9203", "M9205C"):
            with self.subTest(model=model):
                profile = sr.hardware_profile(model)
                self.assertTrue(profile["protocol_compatible"])
                self.assertTrue(profile["is_clone"])
                self.assertFalse(profile["is_reavon"])
                self.assertFalse(profile["http_api_436"])
                self.assertEqual(profile["wake_command"], "#EJT")
                self.assertEqual(profile["src_supported"], {"#SRC 0", "#SRC 3", "#SRC 4"})
                self.assertIn("#SRC 1", profile["src_unsupported"])
                self.assertIn("#SRC 6", profile["src_unsupported"])

    def test_m9203_and_m9205c_presets_match_v0914_chinoppo_expectations(self):
        import settings_reader as sr
        for model in ("M9203", "M9205C"):
            with self.subTest(model=model):
                self.assertEqual(sr.compatibility_preset(model), {
                    "oppo_start_commands": "#EJT\n#PLA",
                    "oppo_start_mode": "tcp_commands",
                    "oppo_http_activate": "false",
                })
                self.assertEqual(sr.normalize_hardware_model(f"chinoppo_{model.lower()}"), model)

    def test_reavon_models_are_warning_only_with_no_command_mutation_preset(self):
        import settings_reader as sr
        for model in ("Reavon-UBR-X100", "Reavon-UBR-X110", "Reavon-UBR-X200"):
            with self.subTest(model=model):
                profile = sr.hardware_profile(model)
                self.assertFalse(profile["protocol_compatible"])
                self.assertTrue(profile["is_reavon"])
                self.assertIsNone(profile["wake_command"])
                self.assertEqual(sr.compatibility_preset(model), {"__reavon_warning__": True})
                self.assertTrue(sr.is_token_supported_by_hardware("#SRC 6", model))

    def test_stock_oppo_jailbreak_payload_does_not_stack_on_clones_or_reavon(self):
        import settings_reader as sr
        self.assertEqual(sr.compatibility_preset("UDP-203", jailbreak=True), {"oppo_http_payload_mode": "json_payload"})
        self.assertEqual(sr.compatibility_preset("UDP-205", jailbreak=True), {"oppo_http_payload_mode": "json_payload"})
        self.assertNotIn("oppo_http_payload_mode", sr.compatibility_preset("M9203", jailbreak=True))
        self.assertNotIn("oppo_http_payload_mode", sr.compatibility_preset("M9205C", jailbreak=True))
        self.assertEqual(sr.compatibility_preset("Reavon-UBR-X200", jailbreak=True), {"__reavon_warning__": True})


class TestV0914WarningHelperPort(unittest.TestCase):
    def setUp(self):
        sys.modules.pop("first_run_wizard", None)
        self.wizard = importlib.import_module("first_run_wizard")

    def test_reavon_warning_only_through_apply_helper_for_all_reavon_models(self):
        for model in ("Reavon-UBR-X100", "Reavon-UBR-X110", "Reavon-UBR-X200"):
            with self.subTest(model=model):
                settings = FakeSettings({"oppo_start_commands": "#PON\n#PLA", "oppo_http_activate": "true"})
                applied, warnings = self.wizard.apply_compatibility_preset(settings, model)
                self.assertEqual(applied, [])
                self.assertEqual(settings["oppo_start_commands"], "#PON\n#PLA")
                self.assertEqual(settings["oppo_http_activate"], "true")
                self.assertTrue(any("Reavon" in item for item in warnings))
                self.assertFalse(any("Quick Start" in item for item in warnings))

    def test_m9203_m9205c_apply_helper_logs_quick_start_warning_and_mutations(self):
        for model in ("M9203", "M9205C"):
            with self.subTest(model=model):
                settings = FakeSettings({
                    "oppo_start_commands": "#PON\n#PLA",
                    "oppo_start_mode": "http_api",
                    "oppo_http_activate": "true",
                })
                logs = []
                applied, warnings = self.wizard.apply_compatibility_preset(settings, model, _log=logs.append)
                self.assertEqual(settings["oppo_start_commands"], "#EJT\n#PLA")
                self.assertEqual(settings["oppo_start_mode"], "tcp_commands")
                self.assertEqual(settings["oppo_http_activate"], "false")
                self.assertEqual([item[0] for item in applied], ["oppo_start_commands", "oppo_start_mode", "oppo_http_activate"])
                self.assertTrue(any("Quick Start" in item for item in warnings))
                self.assertTrue(all("[v0.9.12-preset]" in item for item in logs))

    def test_autoscript_and_quick_start_helpers_match_v0914_warning_rules(self):
        self.assertIn("#SVM 2", self.wizard.autoscript_verbose_push_warning(True))
        self.assertIsNone(self.wizard.autoscript_verbose_push_warning(False))
        self.assertTrue(self.wizard.quick_start_required("M9203"))
        self.assertTrue(self.wizard.quick_start_required("M9205C"))
        self.assertFalse(self.wizard.quick_start_required("Reavon-UBR-X100"))


class TestBuild2AuditHardening(unittest.TestCase):
    def test_addon_xml_decl_and_version_are_exact(self):
        import xml.etree.ElementTree as ET
        text = (ROOT / "addon.xml").read_text(encoding="utf-8")
        self.assertTrue(text.startswith('<?xml version="1.0"'))
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.10")

    def test_release_audit_rejects_version_in_xml_declaration_only(self):
        import tools.audit_release as audit
        result_names = {item["name"]: item for item in audit.run_audit(ROOT, expected_version="2.9.10")}
        self.assertEqual(result_names["addon_xml_declaration"]["status"], "ok")
        self.assertEqual(result_names["addon_version"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
