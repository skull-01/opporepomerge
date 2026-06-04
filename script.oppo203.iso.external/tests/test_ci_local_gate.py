"""Local-first CI/release tooling guards.

These tests pin the local gate script that replaced the cloud `ci.yml`
(see AGENTS.md "CI is local-only"). They inspect script text only; they do not
run the gate or touch runtime playback / TV / AVR / NAS / OPPO behavior.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _read_bytes(rel: str) -> bytes:
    return (ROOT / rel).read_bytes()


def test_ci_local_script_exists_and_is_lf() -> None:
    raw = _read_bytes("scripts/ci-local.sh")
    assert raw, "scripts/ci-local.sh is empty"
    assert b"\r\n" not in raw, "scripts/ci-local.sh must use LF endings (runs under bash/WSL)"
    assert raw.startswith(b"#!/usr/bin/env bash")


def test_gitattributes_pins_shell_scripts_to_lf() -> None:
    assert "*.sh text eol=lf" in _read(".gitattributes")


def test_ci_local_mirrors_the_cloud_gate_commands() -> None:
    # Parity guard: ci-local.sh must run the same gate that g6 pins for ci.yml,
    # so the local gate cannot silently drift from the (frozen) cloud spec.
    text = _read("scripts/ci-local.sh")
    required = [
        "ruff check .",
        "ruff format --check .",
        "tools/type_check.py --gate",
        "tools/render_docs.py --check",
        "tools/sync_version.py --check --expected-version",
        "tools/test_layout.py --check",
        "tools/i18n_extract.py --check",
        "py_compile service.py default.py",
        "-m pytest -q",
        "unittest discover -s tests -p 'test_*.py' -q",
        "-m coverage run -m pytest -q",
        "-m coverage report -m",
        "tools/audit_release.py --expected-version",
        "scripts/package_release.sh",
        "Forbidden runtime ZIP members",
        "-cilocal-dev-source.zip",
    ]
    for snippet in required:
        assert snippet in text, f"ci-local.sh missing gate step: {snippet!r}"


def test_ci_local_runs_full_gate_plus_compat_smoke_matrix() -> None:
    text = _read("scripts/ci-local.sh")
    assert 'PRIMARY_PY="3.12"' in text
    assert 'SMOKE_PYS=("3.9" "3.10")' in text
    # The gate must run against committed state via a clean-room clone.
    assert 'git -C "$SRC_ROOT" clone' in text


def test_ci_local_targeted_smoke_matches_compat_job() -> None:
    # The compat-smoke set must match ci.yml's compatibility-smoke job.
    text = _read("scripts/ci-local.sh")
    for name in (
        "tests/test_v2910_final_release.py",
        "tests/test_github_readiness_g5_tooling_config.py",
        "tests/test_github_readiness_g6_ci_hardening.py",
        "tests/test_github_readiness_g7_safe_format_cleanup.py",
        "tests/test_github_readiness_g8_final_packaging.py",
    ):
        assert name in text
