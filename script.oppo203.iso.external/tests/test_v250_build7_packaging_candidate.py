"""v2.5.0 Build 7 - combined regression and packaging-candidate checks."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


class TestV250Build7PackagingCandidate(unittest.TestCase):
    def test_build7_release_evidence_files_are_present_and_specific(self):
        required = [
            "BUILD_NOTES_v2.5.0_BUILD7.md",
            "RELEASE_MANIFEST_v2.5.0_BUILD7.md",
            "COVERAGE_REPORT_v2.5.0_BUILD7.md",
            "TEST_AUDIT_REPORT_v2.5.0_BUILD7.md",
        ]
        for rel in required:
            text = read_project_file(ROOT, rel)
            self.assertIn("Build 7", text)
            self.assertIn("v2.5.0", text)

    def test_addon_metadata_preserves_version_after_build7_candidate(self):
        root = ET.parse(ROOT / "addon.xml").getroot()
        self.assertEqual(root.attrib["version"], "2.9.12")
        xml_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
        self.assertTrue(
            ("Build 7" in xml_text and "combined regression" in xml_text)
            or ("final" in xml_text.lower() and "Hardware validation is intentionally deferred" in xml_text),
            "addon metadata must identify either the Build 7 candidate or the v2.5.0 final package",
        )

    def test_build7_keeps_candidate_scope_documented_as_no_runtime_behavior_change(self):
        notes = read_project_file(ROOT, "BUILD_NOTES_v2.5.0_BUILD7.md")
        self.assertIn("No runtime behavior changes", notes)
        self.assertIn("Real hardware validation remains pending", notes)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
