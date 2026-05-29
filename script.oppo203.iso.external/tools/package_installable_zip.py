#!/usr/bin/env python3
"""Create a runtime-focused installable ZIP for script.oppo203.iso.external.

The source tree intentionally keeps tests, audit tooling, release evidence, and
AI handoff material for development. Kodi users need only the runtime add-on
surface. This helper is allowlist-driven: a file is packaged only when it is one
of the known runtime root files, an optional runtime asset, or is under an
allowlisted runtime directory.
"""

from __future__ import annotations

import argparse
import zipfile
from collections.abc import Iterator
from pathlib import Path

ADDON_DIR_NAME = "script.oppo203.iso.external"

# Build 7 allowlist: only these root files and runtime directories are eligible
# for the installable Kodi package. Development folders such as tests/, tools/,
# scripts/, release-evidence/, and .github/ are excluded by omission.
RUNTIME_ALLOWLIST_ROOT_FILES = frozenset({"addon.xml", "default.py", "service.py"})
RUNTIME_ALLOWLIST_DIRS = frozenset({"resources"})
OPTIONAL_RUNTIME_ROOT_FILES = frozenset(
    {
        "icon.png",
        "fanart.jpg",
        "fanart.png",
        "LICENSE",
        "LICENSE.txt",
        "COPYING",
    }
)
GENERATED_CACHE_DIR_NAMES = frozenset({"__pycache__"})
GENERATED_CACHE_SUFFIXES = frozenset({".pyc", ".pyo"})
GENERATED_CACHE_FILE_NAMES = frozenset({".coverage"})

# Backward-compatible aliases for older tests/importers. These aliases remain
# allowlist terms; they are not denylist controls.
RUNTIME_ROOT_FILES = RUNTIME_ALLOWLIST_ROOT_FILES
RUNTIME_TOP_LEVEL_DIRS = RUNTIME_ALLOWLIST_DIRS


def project_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "addon.xml").exists() and (
            candidate / "resources" / "settings.xml"
        ).exists():
            return candidate
    raise RuntimeError("Could not find add-on root containing addon.xml and resources/settings.xml")


def _is_generated_or_cache(rel: Path) -> bool:
    return (
        any(part in GENERATED_CACHE_DIR_NAMES for part in rel.parts)
        or rel.suffix in GENERATED_CACHE_SUFFIXES
        or rel.name in GENERATED_CACHE_FILE_NAMES
    )


def _is_under_runtime_allowlist_dir(rel: Path) -> bool:
    return len(rel.parts) > 1 and rel.parts[0] in RUNTIME_ALLOWLIST_DIRS


def is_runtime_member(rel: Path | str) -> bool:
    """Return True if a source-tree relative path belongs in the installable ZIP.

    Build 7 intentionally uses allowlist semantics. Unknown top-level files and
    directories are rejected by default; they do not need to match a denylist.
    """
    rel = Path(rel)
    if not rel.parts or rel.is_absolute() or _is_generated_or_cache(rel):
        return False
    if len(rel.parts) == 1:
        return rel.name in RUNTIME_ALLOWLIST_ROOT_FILES or rel.name in OPTIONAL_RUNTIME_ROOT_FILES
    return _is_under_runtime_allowlist_dir(rel)


def iter_runtime_files(root: Path) -> Iterator[tuple[Path, Path]]:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root)
            if is_runtime_member(rel):
                yield path, rel


def runtime_allowlist_summary() -> dict[str, tuple[str, ...]]:
    """Return the active allowlist policy for tests and release audit evidence."""
    return {
        "root_files": tuple(sorted(RUNTIME_ALLOWLIST_ROOT_FILES)),
        "optional_root_files": tuple(sorted(OPTIONAL_RUNTIME_ROOT_FILES)),
        "runtime_dirs": tuple(sorted(RUNTIME_ALLOWLIST_DIRS)),
    }


def create_installable_zip(root: Path, output_zip: Path) -> list[str]:
    root = project_root(root)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path, rel in iter_runtime_files(root):
            arcname = f"{ADDON_DIR_NAME}/{rel.as_posix()}"
            zf.write(path, arcname)
            written.append(arcname)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a runtime-focused Kodi installable ZIP")
    parser.add_argument("--root", default=".", help="source tree root")
    parser.add_argument("--output", required=True, help="output ZIP path")
    args = parser.parse_args(argv)
    names = create_installable_zip(Path(args.root), Path(args.output))
    print(f"Created {args.output} with {len(names)} runtime files")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
