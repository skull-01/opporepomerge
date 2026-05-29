#!/usr/bin/env python3
"""Type-check wrapper for the OPPO ISO External add-on.

Build 13 introduced a portable baseline for mypy without making mypy a hard
runtime or release dependency. By default this tool reports whether mypy is
available and returns success even when mypy is missing or reports issues
(a non-blocking baseline over ``resources/lib``). Use ``--strict-exit`` only in
local development when you intentionally want those baseline findings to fail
the command.

ENH-#51 adds ``--gate``: a blocking strict gate that type-checks only the
curated ``files`` allowlist in ``mypy.ini`` (``follow_imports = silent`` keeps
not-yet-annotated modules from blocking) and returns mypy's real exit code. CI
runs ``--gate`` so strict-clean modules cannot regress, while the default
non-blocking baseline is preserved for release safety.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

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


def build_gate_command(root: Path) -> list[str]:
    """Build the strict-gate mypy command.

    No explicit targets are passed, so mypy checks exactly the ``files``
    allowlist declared in ``mypy.ini``.
    """
    config = root / "mypy.ini"
    command = [sys.executable, "-m", "mypy"]
    if config.exists():
        command.extend(["--config-file", str(config)])
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
    result = subprocess.run(
        command,
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout.strip()
    if output:
        print(output)
    if result.returncode == 0:
        print("OK: mypy completed without findings")
        return 0
    print(
        f"WARN: mypy reported findings with exit code {result.returncode}; non-blocking baseline keeps release verification green"
    )
    return result.returncode if strict_exit else 0


def run_gate(root: Path) -> int:
    """Run the blocking strict gate over the ``mypy.ini`` files allowlist.

    Returns mypy's exit code. A missing mypy fails the gate (returns 1) so CI
    cannot pass silently when the type checker is unavailable.
    """
    root = project_root(root)
    if not mypy_available():
        print("FAIL: mypy is not installed; the strict gate cannot run")
        return 1
    command = build_gate_command(root)
    result = subprocess.run(
        command,
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = result.stdout.strip()
    if output:
        print(output)
    if result.returncode == 0:
        print("OK: mypy strict gate passed for the allowlisted modules")
        return 0
    print(f"FAIL: mypy strict gate reported findings with exit code {result.returncode}")
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run mypy baseline and strict-gate checks")
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument(
        "--strict-exit",
        action="store_true",
        help="return mypy/missing-mypy status instead of always passing",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="run the blocking strict gate over the mypy.ini files allowlist",
    )
    args = parser.parse_args(argv)
    if args.gate:
        return run_gate(Path(args.root))
    return run_type_check(Path(args.root), strict_exit=args.strict_exit)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
