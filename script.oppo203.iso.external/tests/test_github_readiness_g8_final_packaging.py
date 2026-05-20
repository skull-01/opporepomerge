"""GitHub Readiness G8 final packaging checks.

These tests inspect publication readiness and packaging boundaries only. They do
not exercise or change runtime playback, OPPO control, TV control, AVR
sequencing, NAS, or Kodi routing behavior.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_g8_publication_checklist_exists_and_preserves_truthful_claims() -> None:
    checklist = _read("docs/publication/GITHUB_PUBLICATION_CHECKLIST.md")
    assert "software-verified" in checklist
    assert "not performed / not claimed" in checklist
    assert "script.oppo203.iso.external-2.9.10-github-ready.zip" in checklist
    assert "v2.9.10-github-ready" in checklist


def test_g8_tooling_metadata_records_final_packaging_scope() -> None:
    pyproject = _read("pyproject.toml")
    assert 'build = "G8 GitHub Ready Final Packaging"' in pyproject
    assert 'runtime_behavior_changed = false' in pyproject
    assert 'hardware_validation = "not_performed_not_claimed"' in pyproject
    assert "finalizes the GitHub-ready source layout" in pyproject


def test_g8_gitHub_readiness_archive_has_prior_build_outputs() -> None:
    required = [
        "docs/github-readiness/AI_HANDOFF_G7_SAFE_FORMAT_LINT.md",
        "docs/github-readiness/BUILD_NOTES_G7_SAFE_FORMAT_LINT.md",
        "docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G7.md",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel


def test_g8_repository_root_excludes_prior_github_readiness_reports() -> None:
    forbidden_prefixes = (
        "AI_HANDOFF_G",
        "BUILD_NOTES_G",
        "COVERAGE_REPORT_G",
        "HARDWARE_VALIDATION_G",
        "RELEASE_MANIFEST_G",
        "TEST_AUDIT_REPORT_G",
        "Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G",
    )
    offenders = [path.name for path in ROOT.iterdir() if path.is_file() and path.name.startswith(forbidden_prefixes)]
    assert offenders == []


def test_g8_runtime_packaging_excludes_publication_and_readiness_docs() -> None:
    from tools import package_installable_zip as package_tool

    assert package_tool.is_runtime_member("docs/publication/GITHUB_PUBLICATION_CHECKLIST.md") is False
    assert package_tool.is_runtime_member("docs/github-readiness/README.md") is False
    assert package_tool.is_runtime_member("pyproject.toml") is False
    assert package_tool.is_runtime_member("requirements-dev.txt") is False
    assert package_tool.is_runtime_member("addon.xml") is True
    assert package_tool.is_runtime_member("default.py") is True
    assert package_tool.is_runtime_member("service.py") is True
