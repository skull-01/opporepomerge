"""v2.9.1 Build 4 - dynamic audit evidence manifest discovery."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "audit_release_build4", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def test_manifest_discovery_finds_build4_release_evidence():
    audit = _load_audit()
    manifests = audit.discover_evidence_manifests(ROOT)
    manifest_rels = {path.relative_to(ROOT).as_posix() for path in manifests}
    assert "release-evidence/v2.9.1-build4/MANIFEST.txt" in manifest_rels

    discovered = set(audit.discover_manifest_evidence(ROOT))
    assert "release-evidence/v2.9.1-build4/MANIFEST.txt" in discovered
    for rel in (
        "BUILD_NOTES_v2.9.1_BUILD4.md",
        "RELEASE_MANIFEST_v2.9.1_BUILD4.md",
        "RELEASE_NOTES_v2.9.1_BUILD4.md",
        "COVERAGE_REPORT_v2.9.1_BUILD4.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD4.md",
        "HARDWARE_VALIDATION_v2.9.1_BUILD4.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD4.md",
    ):
        assert rel in discovered


def test_release_audit_uses_manifest_entries_and_legacy_fallback():
    audit = _load_audit()
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.17")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}

    # New dynamic-manifest evidence path for Build 4.
    assert "file:release-evidence/v2.9.1-build4/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD4.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD4.md" in names
    assert "file:PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD4.md" in names

    # Transition fallback: older inline legacy evidence remains checked.
    assert "file:BUILD_NOTES_v2.9.1_BUILD3.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD3.md" in names


def test_manifest_reader_rejects_unsafe_entries(tmp_path):
    audit = _load_audit()
    manifest = tmp_path / "MANIFEST.txt"
    manifest.write_text("../outside.md\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe evidence manifest entry"):
        audit.read_evidence_manifest(tmp_path, manifest)

    manifest.write_text("/absolute.md\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe evidence manifest entry"):
        audit.read_evidence_manifest(tmp_path, manifest)


def test_runtime_zip_policy_excludes_evidence_manifests():
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip", ROOT / "tools" / "package_installable_zip.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    assert tool.is_runtime_member("release-evidence/v2.9.1-build4/MANIFEST.txt") is False
    assert tool.is_runtime_member("BUILD_NOTES_v2.9.1_BUILD4.md") is False
    assert tool.is_runtime_member("tools/audit_release.py") is False
    assert tool.is_runtime_member("resources/lib/oppo/command_map.py") is True


def test_addon_metadata_mentions_build4_audit_manifest_transition():
    text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.1 Build 4" in text
    assert "release-evidence/*/MANIFEST.txt" in text
    assert "legacy hard-coded evidence list" in text
    assert "Version 2.9.1 Build 3 externalized validated OPPO command map" in text
