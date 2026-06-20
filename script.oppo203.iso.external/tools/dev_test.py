#!/usr/bin/env python3
"""Fast local test loop — run only the tests affected by your code changes.

Wraps ``pytest --testmon``. The testmon plugin records which tests exercise
which code and, on the next run, selects only the tests impacted by the files
you changed since the last run ("if we didn't touch it, we don't re-test it").

This is a developer convenience for tight iteration. It is **not** a substitute
for the authoritative gate: the full suite plus the 99% coverage floor
(``scripts/verify.sh`` and CI) remain the backstop before a PR leaves draft.

The first invocation builds the impact map (``.testmondata``, git-ignored) by
running the whole suite once; later invocations run only affected tests.
``--full`` drops the map and rebuilds it.

Usage (run with the project venv interpreter):

    .venv\\Scripts\\python.exe tools/dev_test.py            # only affected tests
    .venv\\Scripts\\python.exe tools/dev_test.py --full     # rebuild the map
    .venv\\Scripts\\python.exe tools/dev_test.py -k yamaha  # extra args -> pytest

Note: do not combine with ``-n`` (xdist) or ``-p no:cacheprovider`` — testmon
runs serially and reads the cacheprovider ``lf`` option.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

TESTMON_DATA = ".testmondata"
WINDOWS_BASETEMP = "build/_pt"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def build_command(python: str, passthrough: list[str], *, on_windows: bool) -> list[str]:
    """Assemble the pytest invocation that activates testmon.

    Keeps the cacheprovider plugin enabled (testmon reads its ``lf`` option) and,
    on Windows, pins ``--basetemp`` to a repo-local scratch dir.
    """
    cmd = [python, "-m", "pytest", "--testmon", *passthrough]
    if on_windows:
        cmd += ["--basetemp", WINDOWS_BASETEMP]
    return cmd


def testmon_env(base_env: dict[str, str], *, on_windows: bool, scratch_dir: Path) -> dict[str, str]:
    """Environment for the run; routes the temp dir outside the repo on Windows.

    Keeps the pytest temp tree out of the worktree so the release audit walker
    cannot trip over OS-locked tmp dirs (see AGENTS.md / handoff gotchas).
    """
    env = dict(base_env)
    if on_windows:
        env["TEMP"] = str(scratch_dir)
        env["TMP"] = str(scratch_dir)
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run only the tests affected by your changes (pytest --testmon)."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="drop the cached impact map and run the whole suite to rebuild it",
    )
    args, passthrough = parser.parse_known_args(argv)

    root = repo_root()
    if args.full:
        for stale in root.glob(TESTMON_DATA + "*"):
            stale.unlink()

    on_windows = os.name == "nt"
    scratch_dir = Path.home() / ".pytest-tmp"
    if on_windows:
        scratch_dir.mkdir(exist_ok=True)

    cmd = build_command(sys.executable, passthrough, on_windows=on_windows)
    env = testmon_env(os.environ, on_windows=on_windows, scratch_dir=scratch_dir)
    return subprocess.call(cmd, cwd=str(root), env=env)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
