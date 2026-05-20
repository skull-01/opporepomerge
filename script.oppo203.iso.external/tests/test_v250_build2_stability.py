import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
import sys
for path in (str(LIB), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import settings_reader as sr


class TestV250Build2StabilityGuardrails(unittest.TestCase):
    def test_numeric_getters_are_bounded_and_non_throwing(self):
        settings = sr.Settings({
            "bad_int": "not-an-int",
            "small_int": "-5",
            "large_float": "999.5",
            "blank_float": "",
        })
        self.assertEqual(settings.get_int("bad_int", 7), 7)
        self.assertEqual(settings.get_int("small_int", 7, minimum=1), 1)
        self.assertEqual(settings.get_float("large_float", 1.0, maximum=10.0), 10.0)
        self.assertEqual(settings.get_float("blank_float", 2.5), 2.5)

    def test_path_getter_expands_user_and_handles_blank(self):
        settings = sr.Settings({"p": "~/folder/../movie.iso", "blank": "   "})
        self.assertTrue(settings.get_path("p").endswith("movie.iso"))
        self.assertEqual(settings.get_path("blank"), "")

    def test_required_validation_treats_explicit_blank_as_missing(self):
        settings = sr.Settings({"python_path": "", "oppo_ip": "192.0.2.10"})
        self.assertIn("python_path", settings.validate_required(["python_path", "oppo_ip"]))
        self.assertNotIn("oppo_ip", settings.validate_required(["python_path", "oppo_ip"]))

    def test_validation_summary_reports_invalid_enums_without_throwing(self):
        settings = sr.Settings({
            "oppo_start_mode": "bad-mode",
            "playback_architecture": "bad-arch",
            "oppo_port": "70000",
        })
        summary = settings.validation_summary()
        self.assertFalse(summary["ok"])
        self.assertIn("invalid_oppo_start_mode", summary["warnings"])
        self.assertIn("invalid_playback_architecture", summary["warnings"])
        self.assertEqual(summary["oppo_port"], 65535)

    def test_corrupt_settings_file_recovers_to_defaults_with_marker(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, "settings.xml").write_text("<settings><setting", encoding="utf-8")
            settings = sr.read_settings(td)
        self.assertEqual(settings.get("python_path"), sr.DEFAULTS["python_path"])
        self.assertTrue(settings.get("_settings_read_error"))
        self.assertIn("settings_read_error", settings.validation_summary()["warnings"])


if __name__ == "__main__":
    unittest.main()
