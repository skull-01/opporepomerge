"""v2.2.0 Build 8 - merge parity audit and handoff reconstruction rule.

This slice does not broaden runtime behavior.  It creates a merge-parity audit
checkpoint and makes the latest handoff self-contained for future AI agents.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class TestBuild8MergeParityAudit(unittest.TestCase):
    def read(self, rel):
        return read_project_file(ROOT, rel)

    def test_addon_version_is_build8(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.11")

    def test_merge_parity_audit_records_completed_and_remaining_work(self):
        text = self.read("MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md")
        self.assertIn("full_merge_status: in_progress_not_complete", text)
        self.assertIn("Chinoppo/M9702 wake rewrite", text)
        self.assertIn("Reavon warning-only behavior", text)
        self.assertIn("Full v1.1.9 + v0.9.14 wizard union", text)
        self.assertIn("Not complete", text)
        self.assertIn("Audit remaining v0.9.14 tests", text)

    def test_docs_record_self_contained_handoff_reconstruction_rule(self):
        for rel in ("README.md", "reference.md", "web-references.md"):
            text = self.read(rel)
            self.assertIn("Version 2.2.0 Build 8", text)
            self.assertIn("resume prompt", text)
            self.assertIn("reconstruction bundle", text)

    def test_audit_requires_build8_evidence_and_parity_audit(self):
        path = ROOT / "tools" / "audit_release.py"
        spec = importlib.util.spec_from_file_location("audit_release_v220_build8", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(ROOT)), expected_version="2.9.11")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.2.0_BUILD8.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.2.0_BUILD8.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.2.0_BUILD8.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.2.0_BUILD8.md", names)
        self.assertIn("file:MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md", names)


if __name__ == "__main__":
    unittest.main()
