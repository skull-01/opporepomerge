"""v2.9.10 Final - software-verified release packaging."""
from __future__ import annotations

from pathlib import Path

from resources.lib import avr_sequence, version
from resources.lib.settings_reader import Settings

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file


def _settings(**overrides):
    data = {
        "playback_architecture": "external_player",
        "avr_control_enabled": "false",
        "avr_backend": "denon_marantz",
        "avr_host": "192.168.1.81",
        "avr_player_input": "BD",
        "avr_power_on_enabled": "true",
        "avr_restore_enabled": "true",
        "avr_restore_input": "TV",
    }
    data.update(overrides)
    return Settings(data)


def test_final_active_identity_and_release_candidate_docs():
    assert version.ADDON_VERSION == "2.9.13"
    assert version.BUILD_ID == "v2.9.13 Final"
    assert version.BUILD_NUMBER == 22

    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert (
        "Version 2.9.13 Final: Testing-strategy refresh, ruff format, and faster parallel test tooling (software-verified; no runtime change)."
        in addon
    )
    assert "Version 2.9.10 Build 17 safely hooks optional TV and AVR" in addon
    assert "real hardware validation was not performed or claimed" in addon.lower()

    for rel in ("README.md", "reference.md", "web-references.md"):
        text = ((ROOT / rel) if (ROOT / rel).exists() else (ROOT / "docs" / "release-history" / rel)).read_text(encoding="utf-8")
        assert "Version 2.9.10 Final" in text
        assert "hardware validation" in text.lower()


def test_final_evidence_manifest_tracks_final_release_files():
    expected = {
        "BUILD_NOTES_v2.9.10_FINAL.md",
        "RELEASE_MANIFEST_v2.9.10.md",
        "RELEASE_NOTES_v2.9.10.md",
        "COVERAGE_REPORT_v2.9.10.md",
        "TEST_AUDIT_REPORT_v2.9.10.md",
        "HARDWARE_VALIDATION_v2.9.10.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.10.md",
        "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10.md",
    }
    manifest = ROOT / "release-evidence" / "v2.9.10-final" / "MANIFEST.txt"
    listed = {line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()}
    assert expected <= listed
    for rel in expected:
        text = ((ROOT / rel) if (ROOT / rel).exists() else (ROOT / "docs" / "release-history" / rel)).read_text(encoding="utf-8")
        assert ("v2.9.10 Final" in text) or ("v2.9.10 final" in text.lower())


def test_build18_preserves_build17_sequencing_contract_noop_and_restore_guards():
    disabled = avr_sequence.pre_playback_sequence(_settings())
    assert disabled.ok is True
    assert disabled.skipped is True
    assert "avr_control_disabled" in disabled.warnings

    ineligible = avr_sequence.pre_playback_sequence(
        _settings(avr_control_enabled="true", playback_architecture="service_interception")
    )
    assert ineligible.ok is True
    assert ineligible.skipped is True
    assert "avr_sequence_ineligible_external_player" in ineligible.warnings

    restore_disabled = avr_sequence.post_playback_sequence(
        _settings(avr_control_enabled="true", avr_restore_enabled="false")
    )
    assert restore_disabled.ok is True
    assert restore_disabled.skipped is True


def test_final_docs_sources_and_package_suffix_are_current():
    docs = (ROOT / "docs" / "sources.yaml").read_text(encoding="utf-8")
    assert "build_number: 22" in docs
    assert "build_id: v2.9.13 Final" in docs
    assert "package_suffix: final" in docs

    package_script = (ROOT / "scripts" / "package_release.sh").read_text(encoding="utf-8")
    assert "SUFFIX_PART" in package_script
    assert "build18" not in package_script
    assert "build17" not in package_script
