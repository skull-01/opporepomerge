"""v2.2.0 Build 9 - merge test-parity audit checkpoint."""
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


class TestBuild9MergeParityAudit(unittest.TestCase):
    def read(self, rel):
        return read_project_file(ROOT, rel)

    def test_addon_version_is_build9(self):
        self.assertEqual(ET.parse(ROOT / "addon.xml").getroot().attrib.get("version"), "2.9.13")

    def test_build9_parity_audit_records_protected_and_remaining_behavior(self):
        text = self.read("MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md")
        self.assertIn("full_merge_status: in_progress_not_complete", text)
        self.assertIn("Behavior already protected by tests", text)
        self.assertIn("Chinoppo/M9702", text)
        self.assertIn("Reavon warning-only behavior", text)
        self.assertIn("M9203/M9205C clone profiles", text)
        self.assertIn("Remaining merge areas", text)
        self.assertIn("service watcher edge cases", text)
        self.assertIn("Build 9 non-goals", text)

    def test_docs_record_build9_as_gradual_merge_slice(self):
        for rel in ("README.md", "reference.md", "web-references.md"):
            text = self.read(rel)
            self.assertIn("Version 2.2.0 Build 9", text)
            self.assertIn("test-parity audit", text)
            self.assertIn("full merge", text)

    def test_audit_requires_build9_evidence(self):
        path = ROOT / "tools" / "audit_release.py"
        spec = importlib.util.spec_from_file_location("audit_release_v220_build9", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(ROOT)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.2.0_BUILD9.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.2.0_BUILD9.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.2.0_BUILD9.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.2.0_BUILD9.md", names)
        self.assertIn("file:MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md", names)


if __name__ == "__main__":
    unittest.main()
