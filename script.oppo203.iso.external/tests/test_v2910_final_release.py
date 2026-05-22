"""Current final-release identity and evidence (v2.9.13 Final)."""
from __future__ import annotations

from pathlib import Path

from resources.lib import version

ROOT = Path(__file__).resolve().parents[1]
RELEASE_HISTORY = ROOT / "docs" / "release-history"


def _release_doc(name: str) -> str:
    """Read a release artifact from the GitHub-ready archive location.

    GitHub Readiness Build G1 moved historical Markdown artifacts out of the
    repository root while preserving their contents under docs/release-history.
    This helper keeps the final-release tests aligned to the public source
    layout instead of reintroducing root clutter.
    """
    return (RELEASE_HISTORY / name).read_text(encoding="utf-8")


def test_final_release_identity_and_artifact_names():
    assert version.ADDON_VERSION == "2.9.13"
    assert version.BUILD_ID == "v2.9.13 Final"
    assert version.BUILD_NUMBER == 22

    docs = (ROOT / "docs" / "sources.yaml").read_text(encoding="utf-8")
    assert "build_id: v2.9.13 Final" in docs
    assert "package_suffix: final" in docs

    manifest = _release_doc("RELEASE_MANIFEST_v2.9.13.md")
    assert "script.oppo203.iso.external-2.9.13.zip" in manifest
    assert "script.oppo203.iso.external-2.9.13-dev-source.zip" in manifest
    assert "script.oppo203.iso.external-2.9.13-artifacts-bundle.zip" in manifest
    assert "script.oppo203.iso.external-2.9.13.sha256" in manifest


def test_final_release_wording_separates_software_from_hardware_validation():
    hardware = _release_doc("HARDWARE_VALIDATION_v2.9.13.md")
    notes = _release_doc("RELEASE_NOTES_v2.9.13.md")
    matrix = _release_doc("HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.13.md")
    for text in (hardware, notes, matrix):
        assert "software-verified" in text.lower()
        assert "not performed" in text.lower()
        assert "not claimed" in text.lower()


def test_final_release_manifest_is_discovered_by_audit():
    manifest = ROOT / "release-evidence" / "v2.9.13-final" / "MANIFEST.txt"
    listed = set(manifest.read_text(encoding="utf-8").splitlines())
    assert "BUILD_NOTES_v2.9.13_FINAL.md" in listed
    assert "RELEASE_MANIFEST_v2.9.13.md" in listed
    assert "HARDWARE_VALIDATION_v2.9.13.md" in listed
