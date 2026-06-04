"""Local-first release tooling guards.

These tests pin the local release scripts that replaced the cloud release jobs
(.github/workflows/package.yml + configurator-ci.yml). They inspect script text
only; they do not run a build, a publish, or any device I/O.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_addon_release_script_titles_final_and_yields_latest_to_configurator() -> None:
    text = _read("scripts/release-addon-local.ps1")
    # Builds the runtime installable ZIP via the Python packager under WSL.
    assert "tools/package_installable_zip.py" in text
    # Titled "v<version> Final", and explicitly NOT Latest (the configurator holds Latest).
    assert "v$Version Final" in text
    assert "--latest=false" in text
    # Default notes file follows the docs/release-history convention.
    assert "RELEASE_NOTES_v" in text
    for token in ("release", "create"):
        assert token in text


def test_configurator_release_script_builds_installers_and_publishes_latest() -> None:
    text = _read("scripts/release-configurator-local.ps1")
    assert "npm run dist" in text
    assert "configurator-v$Version" in text
    assert "--latest" in text
    assert "Kodi Oppo External Player Configurator v$Version" in text
    assert "SHA256SUMS" in text


def test_release_scripts_support_dry_run() -> None:
    for rel in ("scripts/release-addon-local.ps1", "scripts/release-configurator-local.ps1"):
        text = _read(rel)
        assert "[switch]$DryRun" in text
        assert "dry-run" in text.lower()
