"""GitHub Readiness G7 safe format/lint cleanup checks.

These tests inspect non-runtime formatting hygiene only. They do not exercise or
change playback, OPPO control, TV control, AVR sequencing, NAS, or Kodi routing
behavior.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text_files_under(*parts: str) -> list[Path]:
    base = ROOT.joinpath(*parts)
    return sorted(
        path
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".yml", ".yaml", ".toml", ".py", ".sh"}
    )


def test_archived_github_readiness_docs_have_no_trailing_whitespace() -> None:
    """Keep archived handoff/reconstruction docs clean without touching runtime code."""
    offenders: list[str] = []
    for path in _text_files_under("docs", "github-readiness"):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip(" \t") != line:
                offenders.append(f"{path.relative_to(ROOT)}:{line_number}")
    assert offenders == []


def test_archived_github_readiness_docs_end_with_single_newline() -> None:
    offenders = []
    for path in _text_files_under("docs", "github-readiness"):
        data = path.read_bytes()
        if not data.endswith(b"\n") or data.endswith(b"\n\n"):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_g7_did_not_change_runtime_packaging_allowlist() -> None:
    from tools import package_installable_zip as package_tool

    assert package_tool.is_runtime_member("docs/github-readiness/README.md") is False
    assert (
        package_tool.is_runtime_member("tests/test_github_readiness_g7_safe_format_cleanup.py")
        is False
    )
    assert package_tool.is_runtime_member("pyproject.toml") is False
    assert package_tool.is_runtime_member("addon.xml") is True
    assert package_tool.is_runtime_member("default.py") is True
    assert package_tool.is_runtime_member("service.py") is True


def test_g7_archive_records_safe_cleanup_scope() -> None:
    archived = (ROOT / "docs" / "github-readiness" / "AI_HANDOFF_G7_SAFE_FORMAT_LINT.md").read_text(
        encoding="utf-8"
    )
    assert "G7" in archived
    assert "Safe Format" in archived or "safe format" in archived
    assert (
        "runtime_behavior_changed: false" in archived
        or "Runtime behavior changed: false" in archived
    )
    assert "not_performed_not_claimed" in archived or "not performed / not claimed" in archived
