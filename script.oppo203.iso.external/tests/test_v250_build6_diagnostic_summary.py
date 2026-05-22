"""v2.5.0 Build 6 - lightweight diagnostic summary helper tests."""
from __future__ import annotations

import importlib
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class TestV250Build6DiagnosticSummary(unittest.TestCase):
    def setUp(self):
        for name in ("diagnostic_summary", "settings_reader"):
            sys.modules.pop(name, None)

    def test_build_summary_reports_version_and_configuration_without_full_paths(self):
        helper = importlib.import_module("diagnostic_summary")
        summary = helper.build_summary(
            {"python_path": "/missing/bin/python3", "oppo_ip": "192.168.1.50"},
            root_dir=ROOT,
            path_exists=lambda path: False,
        )
        self.assertEqual(summary["addon_version"], "2.9.13")
        self.assertFalse(summary["ok"])
        self.assertIn("python_path_not_found", summary["warnings"])
        self.assertEqual(summary["paths"]["python_path"]["name"], "python3")
        self.assertNotIn("value", summary["paths"]["python_path"])

    def test_build_summary_is_read_only_and_uses_tolerant_settings_reader(self):
        helper = importlib.import_module("diagnostic_summary")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.xml"
            path.write_text(
                textwrap.dedent(
                    """
                    <settings>
                      <setting id="python_path" value="/usr/bin/python3" />
                      <setting id="oppo_ip" value="" />
                    </settings>
                    """
                ).strip(),
                encoding="utf-8",
            )
            before = path.read_text(encoding="utf-8")
            summary = helper.build_summary(addon_data_dir=tmp, path_exists=lambda path: True)
            after = path.read_text(encoding="utf-8")
        self.assertEqual(before, after)
        self.assertFalse(summary["setup_complete"])
        self.assertIn("oppo_ip", summary["missing"])

    def test_format_summary_is_compact_and_support_friendly(self):
        helper = importlib.import_module("diagnostic_summary")
        text = helper.format_summary(
            {
                "addon_version": "2.5.3",
                "setup_complete": False,
                "ok": False,
                "missing": ["oppo_ip"],
                "warnings": ["python_path_not_found"],
                "configuration": {
                    "playback_architecture": "external_player",
                    "hardware_model": "udp_203",
                    "oppo_ip_configured": False,
                    "oppo_port": 23,
                },
            }
        )
        self.assertIn("OPPO203 Diagnostic Summary", text)
        self.assertIn("Setup complete: no", text)
        self.assertIn("Missing: oppo_ip", text)
        self.assertIn("Warnings: python_path_not_found", text)

    def test_addon_version_falls_back_to_unknown(self):
        helper = importlib.import_module("diagnostic_summary")
        self.assertEqual(helper.addon_version("/definitely/not/present"), "unknown")

    def test_build_summary_defaults_are_ok_when_no_source_is_supplied(self):
        helper = importlib.import_module("diagnostic_summary")
        summary = helper.build_summary(path_exists=lambda path: True)
        self.assertTrue(summary["setup_complete"])
        self.assertTrue(summary["ok"])
        self.assertEqual(summary["addon_version"], "unknown")

    def test_build_summary_accepts_settings_object_and_handles_path_check_errors(self):
        settings_reader = importlib.import_module("settings_reader")
        helper = importlib.import_module("diagnostic_summary")
        settings = settings_reader.Settings({"python_path": "/usr/bin/python3"})

        def boom(path):
            raise OSError("stat failed")

        summary = helper.build_summary(settings, path_exists=boom)
        self.assertIn("python_path_not_found", summary["warnings"])
        self.assertFalse(summary["paths"]["python_path"]["exists"])

    def test_format_summary_handles_invalid_input_and_no_missing_or_warning_lines(self):
        helper = importlib.import_module("diagnostic_summary")
        self.assertEqual(helper.format_summary(None), "OPPO203 diagnostic summary unavailable")
        text = helper.format_summary({"addon_version": "2.5.3", "setup_complete": True, "ok": True, "configuration": {}})
        self.assertNotIn("Missing:", text)
        self.assertNotIn("Warnings:", text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
