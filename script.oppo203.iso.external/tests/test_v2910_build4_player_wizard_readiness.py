"""v2.9.10 Build 4 - player wizard wording and readiness updates."""
from pathlib import Path
import importlib
import importlib.util
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build4_player_guidance_distinguishes_stock_clone_magnetar_and_reavon():
    caps = _load("hardware_capabilities_build4_guidance", "resources/lib/hardware_capabilities.py")
    stock = caps.player_setup_guidance("UDP-203")
    clone = caps.player_setup_guidance("cineultra_v204")
    magnetar = caps.player_setup_guidance("Magnetar-UDP900")
    reavon = caps.player_setup_guidance("Reavon-UBR-X200")
    assert "stock OPPO UDP-203/UDP-205" in stock["summary"]
    assert "stock OPPO #PON/#POW power behavior" in stock["summary"]
    assert "OPPO/Chinoppo-style clone" in clone["summary"]
    assert "clone-safe wake commands can be used" in clone["summary"]
    assert "NAS path locally through AutoScript or equivalent clone firmware support" in clone["summary"]
    assert "Magnetar UDP800/UDP900" in magnetar["summary"]
    assert "Automatic OPPO command-map behavior is disabled" in magnetar["summary"]
    assert "Reavon UBR-X100/X110/X200 remain warning-only" in reavon["summary"]
    assert "Do not assume stock OPPO command compatibility" in reavon["summary"]
    assert clone["hardware_validation_claimed"] is False
    assert magnetar["warning_only_successor"] is True


def test_build4_formatted_guidance_is_read_only_and_mentions_validation_status():
    caps = _load("hardware_capabilities_build4_format", "resources/lib/hardware_capabilities.py")
    text = caps.format_player_setup_guidance("m9205")
    assert "Player hardware guidance" not in text  # title is model class, not the dialog title
    assert "OPPO/Chinoppo-style clone" in text
    assert "Hardware validation claimed: no" in text
    assert "NAS/direct playback is a readiness gate" in text
    command_map = _load("command_map_build4", "resources/lib/command_map.py").load_default_command_map()
    assert len(command_map) == 76
    assert not any(token in value for value in command_map.values() for token in ("#SIS", "#PGU", "#PGD"))


def test_build4_wizard_surfaces_player_class_guidance_without_mutating_settings(monkeypatch):
    sys.path.insert(0, str(LIB))
    try:
        wizard = importlib.import_module("wizard")
        messages = []
        monkeypatch.setattr(wizard, "_ok", lambda title, message: messages.append((title, message)))
        assert wizard._surface_player_hardware_guidance(None, "magnetar_udp900") is True
        assert messages[0][0] == "Player hardware class guidance"
        assert "Magnetar UDP800/UDP900" in messages[0][1]
        assert "Automatic OPPO command-map behavior: disabled" in messages[0][1]
        assert "Hardware validation claimed: no" in messages[0][1]
        assert wizard.player_hardware_guidance_text("reavon_ubrx100").count("warning-only") >= 1
    finally:
        try:
            sys.path.remove(str(LIB))
        except ValueError:
            pass


def test_build4_readiness_report_includes_player_guidance_and_validation_status():
    readiness = _load("readiness_build4", "resources/lib/hardware_validation_readiness.py")
    clone = readiness.build_readiness_report({"oppo_hardware_model": "m9200"})
    assert clone["hardware_validation_claimed"] is False
    assert clone["player_hardware"]["hardware_validation_required"] is True
    assert clone["player_setup_guidance"]["nas_mount_question_status"] == "documented_readiness_gate"
    assert "OPPO/Chinoppo-style clone" in clone["player_setup_guidance"]["summary"]
    rendered = readiness.format_readiness_report(clone)
    assert "Player setup guidance" in rendered
    assert "NAS/direct playback is a readiness gate" in rendered
    assert "Hardware validation claimed: no" in rendered


def test_build4_settings_help_text_explains_player_classes():
    settings = (ROOT / "resources/settings.xml").read_text(encoding="utf-8")
    strings = (ROOT / "resources/language/resource.language.en_gb/strings.po").read_text(encoding="utf-8")
    assert "oppo_hardware_model" in settings
    assert "stock OPPO uses stock power behavior" in strings
    assert "Chinoppo-style clones use clone-safe wake behavior" in strings
    assert "Reavon/Magnetar successors remain warning-only" in strings


def test_build4_version_docs_and_audit_evidence_identity():
    version = _load("version_build4", "resources/lib/version.py")
    assert version.BUILD_ID == "v2.9.11 Final"
    assert version.BUILD_NUMBER == 20
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 4" in addon
    assert "Version 2.9.10 Build 3" in addon
    audit = _load("audit_release_build4", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.11")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.10-build4/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.10_BUILD4.md" in names
    assert "file:HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD4.md" in names


def test_runtime_zip_excludes_build4_development_evidence(tmp_path):
    package_tool = _load("package_installable_zip_build4", "tools/package_installable_zip.py")
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
