"""v2.9.10 Build 3 - clone / successor capability gates."""

import importlib.util
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build3_required_capability_sets_are_explicit_and_disjoint():
    caps = _load("hardware_capabilities_build3_sets", "resources/lib/oppo/hardware_capabilities.py")
    assert set(caps.STOCK_OPPO_MODELS) == {"UDP-203", "UDP-205"}
    assert set(caps.CHINOPPO_NAS_PLAYBACK_MODELS) == {
        "M9702",
        "M9200",
        "M9201",
        "M9203",
        "M9205",
        "M9205-V1",
        "M9205C",
        "CineUltra-V203",
        "CineUltra-V204",
        "IPUK-UHD8592",
        "GIEC-BDP-G5300",
    }
    assert set(caps.OPPO_LIKE_SUCCESSOR_WARNING_MODELS) == {
        "Reavon-UBR-X100",
        "Reavon-UBR-X110",
        "Reavon-UBR-X200",
        "Magnetar-UDP800",
        "Magnetar-UDP900",
    }
    assert not (
        set(caps.CHINOPPO_NAS_PLAYBACK_MODELS) & set(caps.OPPO_LIKE_SUCCESSOR_WARNING_MODELS)
    )


def test_build3_clone_safe_wake_is_allowed_only_for_clone_family():
    caps = _load("hardware_capabilities_build3_wake", "resources/lib/oppo/hardware_capabilities.py")
    for model in ("M9702", "M9200", "M9205", "CineUltra-V203", "IPUK-UHD8592", "GIEC-BDP-G5300"):
        assert caps.supports_clone_safe_wake(model) is True
        gate = caps.nas_direct_playback_gate(model)
        assert gate["clone_safe_wake_allowed"] is True
        assert gate["automatic_oppo_command_map_allowed"] is True
        assert gate["requires_autoscript_or_equivalent"] is True
    for model in ("UDP-203", "UDP-205", "Reavon-UBR-X100", "Magnetar-UDP800", "Magnetar-UDP900"):
        assert caps.supports_clone_safe_wake(model) is False


def test_build3_stock_oppo_and_clones_allow_existing_command_map_successors_do_not():
    caps = _load(
        "hardware_capabilities_build3_command_gate", "resources/lib/oppo/hardware_capabilities.py"
    )
    for model in ("UDP-203", "UDP-205", "M9702", "M9201", "CineUltra-V204"):
        assert caps.allows_automatic_oppo_commands(model) is True
    for model in (
        "Reavon-UBR-X100",
        "Reavon-UBR-X110",
        "Reavon-UBR-X200",
        "Magnetar-UDP800",
        "Magnetar-UDP900",
    ):
        assert caps.is_warning_only_successor(model) is True
        assert caps.allows_automatic_oppo_commands(model) is False
        gate = caps.nas_direct_playback_gate(model)
        assert gate["warning_only_successor"] is True
        assert gate["nas_direct_playback_supported_by_family"] is False


def test_build3_settings_reader_treats_magnetar_as_warning_only_successor():
    settings_reader = _load(
        "settings_reader_build3_successor", "resources/lib/kodi/settings_reader.py"
    )
    from resources.lib import oppo_remote as remote

    for model in ("Magnetar-UDP800", "Magnetar-UDP900"):
        profile = settings_reader.hardware_profile(model)
        assert profile["protocol_compatible"] is False
        assert profile["is_clone"] is False
        assert profile["is_successor"] is True
        assert profile["wake_command"] is None
        assert remote.resolve_power_on_token("#PON", model) == "#PON"
        assert remote.resolve_power_on_token("#POW", model) == "#POW"
        assert settings_reader.compatibility_preset(model) == {"__successor_warning__": True}


def test_build3_nas_playback_gate_blocks_warning_only_successors():
    settings_reader = _load("settings_reader_build3_nas", "resources/lib/kodi/settings_reader.py")
    for model in ("Reavon-UBR-X100", "Magnetar-UDP800", "Magnetar-UDP900"):
        cap = settings_reader.nas_playback_capability(model)
        assert cap["family"] in ("unsupported_reavon", "unsupported_oppo_like_successor")
        assert cap["supported"] is False
        assert cap["requires_autoscript"] is False
        assert cap["blockers"]
    clone_cap = settings_reader.nas_playback_capability("M9205", confirmed=False)
    assert clone_cap["family"] == "chinoppo_family"
    assert clone_cap["requires_autoscript"] is True
    assert clone_cap["requires_capability_confirmation"] is True
    assert "chinoppo_firmware_binary_capability_must_be_confirmed" in clone_cap["warnings"]


def test_build3_readiness_report_exposes_player_gate_without_claiming_validation():
    readiness = _load("readiness_build3", "resources/lib/oppo/hardware_validation_readiness.py")
    report = readiness.build_readiness_report({"oppo_hardware_model": "magnetar_udp900"})
    assert report["hardware_validation_claimed"] is False
    assert report["player_hardware"]["model"] == "Magnetar-UDP900"
    assert report["player_hardware"]["warning_only_successor"] is True
    assert report["player_hardware"]["automatic_oppo_command_map_allowed"] is False
    rendered = readiness.format_readiness_report(report)
    assert "Player hardware class gate" in rendered
    assert "Warning-only successor: yes" in rendered


def test_build3_version_docs_and_audit_evidence_identity():
    version = _load("version_build3", "resources/lib/kodi/version.py")
    assert version.BUILD_ID == "v2.9.16 Final"
    assert version.BUILD_NUMBER == 25
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 3" in addon
    assert "Version 2.9.10 Build 2" in addon
    audit = _load("audit_release_build3", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.16")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.10-build3/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.10_BUILD3.md" in names
    assert "file:HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD3.md" in names


def test_runtime_zip_excludes_build3_development_evidence(tmp_path):
    package_tool = _load("package_installable_zip_build3", "tools/package_installable_zip.py")
    output = tmp_path / "runtime.zip"
    names = package_tool.create_installable_zip(ROOT, output)
    assert names
    forbidden = (
        "tests/",
        "tools/",
        "scripts/",
        "release-evidence/",
        "BUILD_NOTES",
        "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX",
    )
    with zipfile.ZipFile(output) as zf:
        assert zf.testzip() is None
        bad = [name for name in zf.namelist() if any(token in name for token in forbidden)]
    assert bad == []
