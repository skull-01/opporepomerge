"""Helpers for locating archived project documentation in tests.

GitHub Readiness G1 moved historical build reports out of the repository root
and into docs/release-history/ and docs/ai-handoff/. Older regression tests
still verify the content, so they resolve files through this helper instead of
requiring root-level historical clutter.
"""
from __future__ import annotations

from pathlib import Path


def candidate_project_paths(root: str | Path, name: str | Path) -> list[Path]:
    root_path = Path(root)
    rel = Path(name)
    return [
        root_path / rel,
        root_path / "docs" / "release-history" / rel,
        root_path / "docs" / "ai-handoff" / rel,
        root_path / "docs" / "github-readiness" / rel,
        root_path / "release-evidence" / "v2.9.10-final" / rel,
    ]


def find_project_file(root: str | Path, name: str | Path) -> Path:
    for candidate in candidate_project_paths(root, name):
        if candidate.exists():
            return candidate
    checked = ", ".join(str(item) for item in candidate_project_paths(root, name))
    raise FileNotFoundError(f"could not locate {name!s}; checked: {checked}")


def read_project_file(root: str | Path, name: str | Path) -> str:
    return find_project_file(root, name).read_text(encoding="utf-8")
