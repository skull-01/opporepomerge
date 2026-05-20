"""v2.5.2 Build 2 - runtime ZIP cleanup and evidence handoff policy."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file


def _package_tool():
    spec = importlib.util.spec_from_file_location("package_installable_zip", ROOT / "tools" / "package_installable_zip.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build2_metadata_preserves_v252_runtime_baseline():
    addon = ET.parse(ROOT / "addon.xml").getroot()
    assert addon.attrib["version"] == "2.9.10"
    text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.5.2 Build 2" in text
    assert "optimized runtime installable package" in text


def test_runtime_member_filter_excludes_development_and_evidence_files():
    tool = _package_tool()
    excluded = [
        "BUILD_NOTES_v2.5.2_BUILD2.md",
        "COVERAGE_REPORT_v2.5.2_BUILD2.md",
        "HARDWARE_VALIDATION_TRACKER_v2.5.2.md",
        "MERGE_COMPLIANCE_MATRIX_v2.2.0_RELEASE.md",
        "MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md",
        "MVP_COMPLIANCE_MATRIX_v2.0.0.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.5.1.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD2.md",
        "RELEASE_NOTES_v2.5.2_BUILD2.md",
        "ROADMAP_v2.5.0.md",
        "SLICE1_NOTES.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD2.md",
        "README.md",
        "reference.md",
        "web-references.md",
        "tests/test_v252_build2_packaging_cleanup.py",
        "tools/audit_release.py",
        ".github/workflows/ci.yml",
        ".coveragerc",
        "pytest.ini",
        "conftest.py",
        "ruff.toml",
    ]
    for rel in excluded:
        assert tool.is_runtime_member(rel) is False, rel

    included = [
        "addon.xml",
        "default.py",
        "service.py",
        "resources/settings.xml",
        "resources/lib/settings_reader.py",
        "resources/language/resource.language.en_gb/strings.po",
    ]
    for rel in included:
        assert tool.is_runtime_member(rel) is True, rel


def test_created_installable_zip_is_runtime_focused(tmp_path):
    tool = _package_tool()
    out = tmp_path / "script.oppo203.iso.external-2.5.2-build2.zip"
    names = set(tool.create_installable_zip(ROOT, out))

    required = {
        "script.oppo203.iso.external/addon.xml",
        "script.oppo203.iso.external/default.py",
        "script.oppo203.iso.external/service.py",
        "script.oppo203.iso.external/resources/settings.xml",
        "script.oppo203.iso.external/resources/lib/settings_reader.py",
    }
    assert required.issubset(names)
    assert all(name.startswith("script.oppo203.iso.external/") for name in names)

    forbidden_fragments = (
        "/BUILD_NOTES_",
        "/COVERAGE_REPORT_",
        "/HARDWARE_VALIDATION",
        "/MERGE_COMPLIANCE_MATRIX_",
        "/MERGE_PARITY_AUDIT_",
        "/MVP_COMPLIANCE_MATRIX_",
        "/PRE_HARDWARE_AUDIT_REPORT_",
        "/RELEASE_MANIFEST_",
        "/RELEASE_NOTES_",
        "/ROADMAP_",
        "/SLICE",
        "/TEST_AUDIT_REPORT_",
        "/tests/",
        "/tools/",
        "/.github/",
        "/README.md",
        "/reference.md",
        "/web-references.md",
    )
    assert not any(any(fragment in name for fragment in forbidden_fragments) for name in names)

    with zipfile.ZipFile(out) as zf:
        zip_names = set(zf.namelist())
    assert zip_names == names


def test_build2_evidence_is_preserved_in_source_and_audit_not_installable_zip(tmp_path):
    for rel in [
        "BUILD_NOTES_v2.5.2_BUILD2.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD2.md",
        "RELEASE_NOTES_v2.5.2_BUILD2.md",
        "COVERAGE_REPORT_v2.5.2_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD2.md",
    ]:
        assert find_project_file(ROOT, rel).exists(), rel

    spec = importlib.util.spec_from_file_location("audit_release_v252_build2", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.10")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:BUILD_NOTES_v2.5.2_BUILD2.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.5.2_BUILD2.md" in names

    tool = _package_tool()
    out = tmp_path / "runtime.zip"
    tool.create_installable_zip(ROOT, out)
    with zipfile.ZipFile(out) as zf:
        packaged = "\n".join(zf.namelist())
    assert "BUILD_NOTES_v2.5.2_BUILD2.md" not in packaged
    assert "TEST_AUDIT_REPORT_v2.5.2_BUILD2.md" not in packaged
