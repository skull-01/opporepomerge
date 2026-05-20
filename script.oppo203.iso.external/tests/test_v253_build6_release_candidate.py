"""v2.5.3 Build 6 - pre-hardware release-candidate freeze."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file
LIB = ROOT / "resources" / "lib"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))


def _read(name: str) -> str:
    return read_project_file(ROOT, name)


def test_build6_addon_metadata_declares_freeze_without_hardware_claim():
    addon = _read("addon.xml")
    assert 'version="2.9.10"' in addon
    assert "Version 2.5.3 Build 6" in addon
    assert "pre-hardware release-candidate packaging freeze" in addon
    assert "Hardware validation is intentionally not claimed" in addon


def test_build6_evidence_files_record_preserved_scope_and_no_hardware_claim():
    notes = _read("BUILD_NOTES_v2.5.3_BUILD6.md")
    manifest = _read("RELEASE_MANIFEST_v2.5.3_BUILD6.md")
    pre_hw = _read("PRE_HARDWARE_AUDIT_REPORT_v2.5.3_BUILD6.md")
    hw = _read("HARDWARE_VALIDATION_v2.5.3_BUILD6.md")
    assert "runtime_behavior_changed: false" in notes
    assert "pre_hardware_release_candidate_packaging_freeze" in manifest
    assert "hardware_claim: none" in pre_hw
    assert "Hardware validation is **not performed** and **not claimed**" in hw
    assert "Build 1: precise Python classifier" in notes
    assert "Build 5: hardware-validation readiness checklist" in notes


def test_build6_docs_are_updated_for_release_candidate_freeze():
    assert "Version 2.5.3 Build 6" in _read("README.md")
    assert "v2.5.3 Build 6 technical note" in _read("reference.md")
    assert "v2.5.3 Build 6 reference note" in _read("web-references.md")


def test_build6_release_audit_requires_build6_evidence():
    spec = importlib.util.spec_from_file_location("audit_release", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.10")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    for required in (
        "file:BUILD_NOTES_v2.5.3_BUILD6.md",
        "file:RELEASE_MANIFEST_v2.5.3_BUILD6.md",
        "file:TEST_AUDIT_REPORT_v2.5.3_BUILD6.md",
        "file:HARDWARE_VALIDATION_v2.5.3_BUILD6.md",
        "file:PRE_HARDWARE_AUDIT_REPORT_v2.5.3_BUILD6.md",
    ):
        assert required in names


def test_build6_runtime_zip_excludes_prehardware_and_build_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location("package_installable_zip", ROOT / "tools" / "package_installable_zip.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    out = tmp_path / "runtime.zip"
    names = tool.create_installable_zip(ROOT, out)
    forbidden_suffixes = (
        "BUILD_NOTES_v2.5.3_BUILD6.md",
        "RELEASE_MANIFEST_v2.5.3_BUILD6.md",
        "TEST_AUDIT_REPORT_v2.5.3_BUILD6.md",
        "HARDWARE_VALIDATION_v2.5.3_BUILD6.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.5.3_BUILD6.md",
        "tests/test_v253_build6_release_candidate.py",
        "tools/audit_release.py",
    )
    for suffix in forbidden_suffixes:
        assert f"script.oppo203.iso.external/{suffix}" not in names
    assert "script.oppo203.iso.external/resources/lib/hardware_validation_readiness.py" in names
    with zipfile.ZipFile(out) as zf:
        addon_text = zf.read("script.oppo203.iso.external/addon.xml").decode("utf-8")
    assert "Build 6" in addon_text
    assert 'version="2.9.10"' in addon_text
