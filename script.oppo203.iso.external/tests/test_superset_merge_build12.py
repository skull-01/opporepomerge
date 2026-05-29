"""v2.2.0 Release 2.2.0 - final software merge-compliance review.

This build is a release-candidate stabilization checkpoint.  It may identify a
software merge-complete candidate state, but it must not overclaim real hardware
validation or final release status.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file, read_project_file

LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class TestBuild12MergeComplianceReview(unittest.TestCase):
    def read(self, rel: str) -> str:
        return read_project_file(ROOT, rel)

    def test_addon_version_is_build12(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.13")

    def test_build12_evidence_files_exist(self):
        for rel in (
            "BUILD_NOTES_v2.2.0_RELEASE.md",
            "RELEASE_MANIFEST_v2.2.0_RELEASE.md",
            "COVERAGE_REPORT_v2.2.0_RELEASE.md",
            "TEST_AUDIT_REPORT_v2.2.0_RELEASE.md",
            "MERGE_COMPLIANCE_MATRIX_v2.2.0_RELEASE.md",
        ):
            self.assertTrue(find_project_file(ROOT, rel).exists(), rel)

    def test_merge_matrix_marks_software_candidate_but_not_final_release(self):
        text = self.read("MERGE_COMPLIANCE_MATRIX_v2.2.0_RELEASE.md")
        self.assertIn("software_merge_status: complete_no_known_software_gaps", text)
        self.assertIn(
            "release_status: not_final_pending_real_hardware_validation_and_final_release_packaging",
            text,
        )
        self.assertIn("software merge-complete candidate", text)
        self.assertIn("not a hardware-validated final release", text)
        self.assertIn("Real hardware validation", text)
        self.assertIn("Pending external validation", text)

    def test_merge_matrix_covers_required_superset_invariants(self):
        text = self.read("MERGE_COMPLIANCE_MATRIX_v2.2.0_RELEASE.md")
        for phrase in (
            "12-SKU hardware compatibility table",
            "Chinoppo / M9201 / M9203 / M9205C / M9702 wake rewrite",
            "Stock OPPO pass-through behavior",
            "Reavon warning-only behavior",
            "No Reavon command-map mutation",
            "Quick Start warning behavior",
            "AutoScript verbose-push warning behavior",
            "Jailbreak JSON payload mode",
            "service.Monitor.onSettingsChanged() compatibility watcher",
            "Wizard/UI warning surfacing",
            "Fake OPPO server tests",
            "Clean TCP disconnect is not playback stopped",
            "Canonical 76-key command map",
            "99 percent coverage gate",
            "Self-contained AI handoff reconstruction",
        ):
            self.assertIn(phrase, text)

    def test_build12_docs_record_no_new_external_sources(self):
        self.assertIn(
            "No new external web sources were used for Release 2.2.0",
            self.read("web-references.md"),
        )
        self.assertIn("Version 2.2.0 Release 2.2.0", self.read("README.md"))
        self.assertIn(
            "Release 2.2.0 is a final software merge-compliance review", self.read("reference.md")
        )

    def test_build12_audit_requires_evidence(self):
        path = ROOT / "tools" / "audit_release.py"
        spec = importlib.util.spec_from_file_location("audit_release_build12", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(ROOT)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        for rel in (
            "BUILD_NOTES_v2.2.0_RELEASE.md",
            "RELEASE_MANIFEST_v2.2.0_RELEASE.md",
            "COVERAGE_REPORT_v2.2.0_RELEASE.md",
            "TEST_AUDIT_REPORT_v2.2.0_RELEASE.md",
            "MERGE_COMPLIANCE_MATRIX_v2.2.0_RELEASE.md",
        ):
            self.assertIn(f"file:{rel}", names)


if __name__ == "__main__":
    unittest.main()
