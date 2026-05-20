"""v2.5.0 Final - final packaging checks."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


class TestV250FinalPackaging(unittest.TestCase):
    def test_final_release_evidence_files_are_present_and_specific(self):
        required = [
            "BUILD_NOTES_v2.5.0_FINAL.md",
            "RELEASE_MANIFEST_v2.5.0_FINAL.md",
            "RELEASE_NOTES_v2.5.0.md",
            "HARDWARE_VALIDATION_v2.5.0_FINAL.md",
            "COVERAGE_REPORT_v2.5.0_FINAL.md",
            "TEST_AUDIT_REPORT_v2.5.0_FINAL.md",
        ]
        for rel in required:
            text = read_project_file(ROOT, rel)
            self.assertIn("v2.5.0", text)

    def test_addon_metadata_identifies_final_without_version_drift(self):
        root = ET.parse(ROOT / "addon.xml").getroot()
        self.assertEqual(root.attrib["version"], "2.9.10")
        xml_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
        self.assertIn("final", xml_text.lower())
        self.assertNotIn("Build 7: combined regression and packaging candidate", xml_text)

    def test_final_notes_explicitly_defer_hardware_validation(self):
        notes = read_project_file(ROOT, "BUILD_NOTES_v2.5.0_FINAL.md")
        hardware = read_project_file(ROOT, "HARDWARE_VALIDATION_v2.5.0_FINAL.md")
        self.assertIn("No runtime behavior changes", notes)
        self.assertIn("skipped", hardware.lower())
        self.assertIn("deferred", hardware.lower())
        self.assertNotIn("hardware validation passed", hardware.lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
