"""v2.9.0 release rebuild tests."""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file, read_project_file

LIB = ROOT / "resources" / "lib"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))


def _read(name: str) -> str:
    return read_project_file(ROOT, name)


def test_v290_addon_metadata_declares_release_without_runtime_behavior_change():
    addon = _read("addon.xml")
    assert 'version="2.9.13"' in addon
    assert "Version 2.9 release" in addon
    assert "v2.5.3 Build 6" in addon
    assert "No playback" in addon
    assert "Hardware validation is intentionally not claimed" in addon


def test_v290_release_evidence_files_record_no_hardware_claim():
    for name in (
        "BUILD_NOTES_v2.9.0_RELEASE.md",
        "RELEASE_MANIFEST_v2.9.0.md",
        "RELEASE_NOTES_v2.9.0.md",
        "COVERAGE_REPORT_v2.9.0.md",
        "TEST_AUDIT_REPORT_v2.9.0.md",
        "HARDWARE_VALIDATION_v2.9.0.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.0.md",
    ):
        assert find_project_file(ROOT, name).exists(), name
    assert "runtime_behavior_changed: false" in _read("BUILD_NOTES_v2.9.0_RELEASE.md")
    assert "hardware_claim: none" in _read("PRE_HARDWARE_AUDIT_REPORT_v2.9.0.md")
    assert "not performed" in _read("HARDWARE_VALIDATION_v2.9.0.md").lower()


def test_v290_docs_are_updated():
    assert "Version 2.9 Release" in _read("README.md")
    assert "v2.9.0 release technical note" in _read("reference.md")
    assert "v2.9.0 release reference note" in _read("web-references.md")


def test_v290_release_audit_requires_release_evidence():
    spec = importlib.util.spec_from_file_location(
        "audit_release", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.13")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    for required in (
        "file:BUILD_NOTES_v2.9.0_RELEASE.md",
        "file:RELEASE_MANIFEST_v2.9.0.md",
        "file:TEST_AUDIT_REPORT_v2.9.0.md",
        "file:HARDWARE_VALIDATION_v2.9.0.md",
        "file:PRE_HARDWARE_AUDIT_REPORT_v2.9.0.md",
    ):
        assert required in names


def test_v290_runtime_zip_excludes_release_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip", ROOT / "tools" / "package_installable_zip.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    out = tmp_path / "runtime.zip"
    names = tool.create_installable_zip(ROOT, out)
    forbidden_suffixes = (
        "BUILD_NOTES_v2.9.0_RELEASE.md",
        "RELEASE_MANIFEST_v2.9.0.md",
        "TEST_AUDIT_REPORT_v2.9.0.md",
        "HARDWARE_VALIDATION_v2.9.0.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.0.md",
        "tests/test_v290_release.py",
        "tools/audit_release.py",
    )
    for suffix in forbidden_suffixes:
        assert f"script.oppo203.iso.external/{suffix}" not in names
    with zipfile.ZipFile(out) as zf:
        addon_text = zf.read("script.oppo203.iso.external/addon.xml").decode("utf-8")
    assert 'version="2.9.13"' in addon_text
    assert "Version 2.9 release" in addon_text
