"""v2.2.0 Build 10 - merge-compliance candidate checkpoint."""

from __future__ import annotations

import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file

LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class TestBuild10MergeComplianceCandidate(unittest.TestCase):
    def read(self, rel: str) -> str:
        return read_project_file(ROOT, rel)

    def test_addon_version_is_build10(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.13")

    def test_merge_compliance_matrix_exists_and_does_not_overclaim_completion(self):
        text = self.read("MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD10.md")
        self.assertIn("full_merge_status: in_progress_not_complete", text)
        self.assertIn("Merge-complete status: NOT COMPLETE", text)
        self.assertIn("Active wizard warning surfacing", text)
        self.assertIn("Partially complete", text)
        self.assertIn("Real hardware validation", text)
        self.assertIn("Needs hardware validation", text)
        self.assertIn("Remaining gaps before full merge completion", text)

    def test_build10_documents_improved_verification_process(self):
        for rel in (
            "BUILD_NOTES_v2.2.0_BUILD10.md",
            "TEST_AUDIT_REPORT_v2.2.0_BUILD10.md",
            "COVERAGE_REPORT_v2.2.0_BUILD10.md",
            "README.md",
            "reference.md",
        ):
            text = self.read(rel)
            self.assertIn("-p no:ddtrace", text)
        self.assertIn("one command at a time", self.read("TEST_AUDIT_REPORT_v2.2.0_BUILD10.md"))

    def test_docs_record_build10_merge_candidate_status(self):
        for rel in ("README.md", "reference.md", "web-references.md"):
            text = self.read(rel)
            self.assertIn("Version 2.2.0 Build 10", text)
            self.assertIn("merge", text.lower())
            self.assertIn("compliance", text.lower())

    def test_audit_requires_build10_evidence(self):
        path = ROOT / "tools" / "audit_release.py"
        spec = importlib.util.spec_from_file_location("audit_release_v220_build10", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(ROOT)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        for rel in (
            "BUILD_NOTES_v2.2.0_BUILD10.md",
            "RELEASE_MANIFEST_v2.2.0_BUILD10.md",
            "COVERAGE_REPORT_v2.2.0_BUILD10.md",
            "TEST_AUDIT_REPORT_v2.2.0_BUILD10.md",
            "MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD10.md",
        ):
            self.assertIn(f"file:{rel}", names)


if __name__ == "__main__":
    unittest.main()
