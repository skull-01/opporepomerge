#!/usr/bin/env python3
"""Non-blocking type-check wrapper for the OPPO ISO External add-on.

Build 13 introduces a portable baseline for mypy without making mypy a hard
runtime or release dependency. By default this tool reports whether mypy is
available and returns success even when mypy is missing or reports issues. Use
``--strict-exit`` only in local development when you intentionally want mypy
findings to fail the command.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
from typing import Sequence

DEFAULT_TARGETS = ("resources/lib", "tools/package_installable_zip.py")


def project_root(start: Path | None = None) -> Path:
    """Return the add-on project root containing addon.xml."""
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "addon.xml").exists() and (candidate / "resources" / "lib").exists():
            return candidate
    raise RuntimeError("Could not find add-on root containing addon.xml and resources/lib")


def mypy_available() -> bool:
    """Return True when the optional mypy package is importable."""
    return importlib.util.find_spec("mypy") is not None


def build_mypy_command(root: Path, targets: Sequence[str] = DEFAULT_TARGETS) -> list[str]:
    """Build the local mypy command for the configured project targets."""
    config = root / "mypy.ini"
    command = [sys.executable, "-m", "mypy"]
    if config.exists():
        command.extend(["--config-file", str(config)])
    command.extend(str(root / target) for target in targets)
    return command


def run_type_check(root: Path, *, strict_exit: bool = False) -> int:
    """Run optional mypy and return the release-safe exit code.

    The default mode is non-blocking: missing mypy or mypy findings produce a
    SKIP/WARN message and return 0. ``strict_exit=True`` returns mypy's status.
    """
    root = project_root(root)
    if not mypy_available():
        print("SKIP: mypy is not installed; non-blocking type-check baseline is configured")
        return 1 if strict_exit else 0
    command = build_mypy_command(root)
    result = subprocess.run(command, cwd=str(root), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    output = result.stdout.strip()
    if output:
        print(output)
    if result.returncode == 0:
        print("OK: mypy completed without findings")
        return 0
    print(f"WARN: mypy reported findings with exit code {result.returncode}; non-blocking baseline keeps release verification green")
    return result.returncode if strict_exit else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run non-blocking mypy baseline checks")
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument("--strict-exit", action="store_true", help="return mypy/missing-mypy status instead of always passing")
    args = parser.parse_args(argv)
    return run_type_check(Path(args.root), strict_exit=args.strict_exit)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
