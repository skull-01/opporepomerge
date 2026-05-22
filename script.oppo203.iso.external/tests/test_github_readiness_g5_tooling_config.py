"""GitHub Readiness G5 tooling configuration checks.

These tests intentionally inspect metadata/configuration only. They do not
exercise runtime playback, TV, AVR, NAS, or OPPO-control behavior.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_pyproject_declares_non_runtime_tooling_baseline() -> None:
    text = _read("pyproject.toml")
    assert "[project]" in text
    assert 'name = "script-oppo203-iso-external"' in text
    assert 'version = "2.9.11"' in text
    assert 'requires-python = ">=3.9"' in text
    assert "[tool.github-readiness]" in text
    assert 'runtime_behavior_changed = false' in text
    assert 'hardware_validation = "not_performed_not_claimed"' in text


def test_pyproject_carries_quality_tool_configuration() -> None:
    text = _read("pyproject.toml")
    assert "[tool.black]" in text
    assert "[tool.ruff]" in text
    assert "[tool.ruff.lint]" in text
    assert "[tool.coverage.run]" in text
    assert "[tool.coverage.report]" in text
    assert "[tool.mypy]" in text
    assert "line-length = 100" in text
    assert 'target-version = "py39"' in text
    assert "fail_under = 98" in text


def test_legacy_config_files_remain_for_existing_tools() -> None:
    for rel in ("pytest.ini", "ruff.toml", "mypy.ini", ".coveragerc"):
        assert (ROOT / rel).exists(), f"missing legacy-compatible config: {rel}"


def test_requirements_dev_lists_development_only_tools() -> None:
    text = _read("requirements-dev.txt")
    assert "Kodi runtime users do not need to install this file" in text
    for package in ("pytest", "coverage", "PyYAML", "ruff", "black", "mypy"):
        assert package in text
    assert "script.oppo" not in text


def test_runtime_packaging_excludes_dev_tooling_files() -> None:
    from tools import package_installable_zip as package_tool

    for rel in ("pyproject.toml", "requirements-dev.txt", "pytest.ini", "ruff.toml", "mypy.ini"):
        assert package_tool.is_runtime_member(rel) is False
