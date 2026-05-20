#!/usr/bin/env python3
"""Test-layout policy helper for the v2.9.1 cleanup roadmap.

Build 14 intentionally avoids a risky mass move of historical tests.  Instead,
it defines the forward-looking version/build directory shape and a marker policy
while accepting the inherited flat ``tests/test_*.py`` layout during transition.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Iterable

FUTURE_TEST_RE = re.compile(r"^tests/v\d+_\d+_\d+/build\d+/test_[^/]+\.py$")
LEGACY_FLAT_RE = re.compile(r"^tests/test_[^/]+\.py$")
SUPPORT_RE = re.compile(r"^tests/(?:_stubs|_support)(?:/.*)?$")
PYTEST_MARKERS = (
    "version(version): mark tests that belong to a release/version line.",
    "build(number): mark tests that belong to a build-specific cleanup slice.",
    "legacy_layout: inherited flat-layout tests retained during the transition.",
)


def project_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "addon.xml").exists() and (candidate / "tests").exists():
            return candidate
    raise RuntimeError("Could not find add-on root containing addon.xml and tests/")


def as_posix_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def is_future_layout(rel: str | Path) -> bool:
    return bool(FUTURE_TEST_RE.match(Path(rel).as_posix()))


def is_legacy_flat_layout(rel: str | Path) -> bool:
    return bool(LEGACY_FLAT_RE.match(Path(rel).as_posix()))


def is_support_path(rel: str | Path) -> bool:
    return bool(SUPPORT_RE.match(Path(rel).as_posix()))


def iter_test_files(root: Path) -> Iterable[Path]:
    tests = root / "tests"
    if not tests.exists():
        return []
    return sorted(path for path in tests.rglob("test_*.py") if path.is_file())


def classify_test_path(rel: str | Path) -> str:
    text = Path(rel).as_posix()
    if is_future_layout(text):
        return "future"
    if is_legacy_flat_layout(text):
        return "legacy-flat"
    if is_support_path(text):
        return "support"
    return "nonstandard"


def pytest_ini_markers(root: Path) -> list[str]:
    path = root / "pytest.ini"
    if not path.exists():
        return []
    markers: list[str] = []
    in_markers = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped == "markers =":
            in_markers = True
            continue
        if in_markers and raw.startswith("    ") and stripped:
            markers.append(stripped)
            continue
        if in_markers and stripped and not raw.startswith("    "):
            break
    return markers


def layout_report(root: Path) -> dict[str, object]:
    files = [as_posix_rel(root, path) for path in iter_test_files(root)]
    counts = {"future": 0, "legacy-flat": 0, "support": 0, "nonstandard": 0}
    nonstandard: list[str] = []
    for rel in files:
        kind = classify_test_path(rel)
        counts[kind] += 1
        if kind == "nonstandard":
            nonstandard.append(rel)
    return {
        "test_files": len(files),
        "counts": counts,
        "nonstandard": nonstandard,
        "markers": pytest_ini_markers(root),
        "future_pattern": FUTURE_TEST_RE.pattern,
        "transition_allows_legacy_flat": True,
    }


def check_layout(root: Path) -> tuple[bool, list[str]]:
    report = layout_report(root)
    messages: list[str] = []
    nonstandard = report["nonstandard"]
    if nonstandard:
        messages.append("nonstandard test paths: " + ", ".join(nonstandard[:20]))
    markers = set(report["markers"])
    missing = [marker for marker in PYTEST_MARKERS if marker not in markers]
    if missing:
        messages.append("missing pytest markers: " + ", ".join(missing))
    return not messages, messages or [
        f"layout policy ok: {report['test_files']} test files; "
        f"legacy flat layout retained; future pattern {report['future_pattern']}"
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check transitional test-layout policy")
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", action="store_true", help="check layout policy; default behavior")
    args = parser.parse_args(argv)
    root = project_root(Path(args.root))
    ok, messages = check_layout(root)
    for detail in messages:
        print(("OK" if ok else "FAIL") + f": test_layout - {detail}")
    return 0 if ok else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
