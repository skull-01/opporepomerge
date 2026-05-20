"""v2.5.3 Build 3 - version identity and audit reconciliation."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file


def test_addon_xml_version_matches_v253_package_line():
    root = ET.parse(ROOT / "addon.xml").getroot()
    assert root.attrib["version"] == "2.9.10"
    text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.5.3 Build 3" in text
    assert "Version 2.5.3 Build 2" in text
    assert "Version 2.5.2 Build 2 optimized runtime installable package policy remains preserved" in text


def test_release_audit_requires_v253_and_build3_evidence():
    spec = importlib.util.spec_from_file_location("audit_release", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.10")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "addon_version" in names
    assert "file:BUILD_NOTES_v2.5.3_BUILD3.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.5.3_BUILD3.md" in names
    assert "file:HARDWARE_VALIDATION_v2.5.3_BUILD3.md" in names


def test_build3_documents_no_runtime_behavior_change():
    notes = read_project_file(ROOT, "BUILD_NOTES_v2.5.3_BUILD3.md")
    assert "runtime_behavior_change: false" in notes
    assert "Build 1 precise Python service interception" in notes
    assert "Build 2 conservative Option 4" in notes
    assert "Hardware validation remains user-owned" in notes


def test_runtime_zip_policy_still_excludes_build3_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location("package_installable_zip", ROOT / "tools" / "package_installable_zip.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    out = tmp_path / "runtime.zip"
    names = tool.create_installable_zip(ROOT, out)
    assert "script.oppo203.iso.external/addon.xml" in names
    assert "script.oppo203.iso.external/BUILD_NOTES_v2.5.3_BUILD3.md" not in names
    assert "script.oppo203.iso.external/TEST_AUDIT_REPORT_v2.5.3_BUILD3.md" not in names
    with zipfile.ZipFile(out) as zf:
        addon_text = zf.read("script.oppo203.iso.external/addon.xml").decode("utf-8")
    assert 'version="2.9.10"' in addon_text
