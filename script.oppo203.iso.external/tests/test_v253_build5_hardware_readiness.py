"""v2.5.3 Build 5 - hardware-validation readiness and diagnostic export."""
from __future__ import annotations

from datetime import datetime
import importlib
import importlib.util
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))


def test_build5_readiness_report_is_non_claiming_and_contains_tester_checklist():
    helper = importlib.import_module("resources.lib.hardware_validation_readiness")
    report = helper.build_readiness_report(
        {
            "oppo_hardware_model": "udp_203",
            "oppo_jailbreak_enabled": "true",
            "oppo_firmware_version": "20X-65-0131",
            "oppo_ip": "192.168.1.50",
            "python_path": "/usr/bin/python3",
        },
        root_dir=ROOT,
        path_exists=lambda path: True,
    )
    assert report["hardware_validation_claimed"] is False
    assert report["safe_to_claim_hardware_pass"] is False
    assert report["ok_for_hardware_test"] is True
    assert report["nas_playback_capability"]["family"] == "oppo20x_jailbroken"
    checklist_ids = {item["id"] for item in report["checklist"]}
    assert "confirm_4k_disc_style_interception" in checklist_ids
    assert "confirm_loose_video_stays_kodi" in checklist_ids
    assert "confirm_option4_xml_mode" in checklist_ids
    assert "observed_handoff_result" in report["required_tester_results"]


def test_build5_reavon_readiness_report_keeps_warning_only_blocker():
    helper = importlib.import_module("resources.lib.hardware_validation_readiness")
    report = helper.build_readiness_report(
        {"oppo_hardware_model": "reavon_ubrx200", "oppo_ip": "192.168.1.50"},
        root_dir=ROOT,
        path_exists=lambda path: True,
    )
    assert report["ok_for_hardware_test"] is False
    assert "reavon_warning_only_not_supported_for_oppo_chinoppo_nas_playback" in report["blockers"]
    text = helper.format_readiness_report(report)
    assert "Hardware validation claimed: no" in text
    assert "Safe to claim hardware pass: no" in text
    assert "Loose-video negative tests" in text


def test_build5_export_readiness_report_writes_text_only(tmp_path):
    helper = importlib.import_module("resources.lib.hardware_validation_readiness")
    report = helper.build_readiness_report({"oppo_hardware_model": "chinoppo_m9702", "nas_playback_confirmed": "true"}, path_exists=lambda path: True)
    path = helper.export_readiness_report(tmp_path, report, now=lambda: datetime(2026, 5, 18, 12, 30, 0))
    output = Path(path)
    assert output.name == "hardware-validation-readiness-20260518-123000.txt"
    text = output.read_text(encoding="utf-8")
    assert "OPPO203 Hardware Validation Readiness Report" in text
    assert "device_model" in text
    assert "Hardware validation claimed: no" in text


def test_build5_installer_exposes_export_action_with_kodi_stubs(tmp_path, monkeypatch):
    stubs = ROOT / "tests" / "_stubs"
    monkeypatch.syspath_prepend(str(stubs))
    monkeypatch.syspath_prepend(str(ROOT))
    monkeypatch.syspath_prepend(str(LIB))
    from tests._support.lib_buckets import with_canonical
    for name in with_canonical(("xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs", "resources.lib.installer", "installer")):
        sys.modules.pop(name, None)
    import xbmcaddon  # type: ignore
    import xbmcvfs  # type: ignore

    xbmcaddon.reset(
        settings={"oppo_hardware_model": "chinoppo_m9702", "nas_playback_confirmed": "true"},
        info={"path": str(ROOT), "id": "script.oppo203.iso.external"},
    )
    xbmcvfs.translatePath = lambda path: str(tmp_path / path.replace("special://", ""))  # type: ignore[attr-defined]
    installer = importlib.import_module("resources.lib.installer")
    exported = installer.export_hardware_validation_readiness()
    assert exported is not None
    assert Path(exported).exists()
    assert "hardware-validation-readiness" in Path(exported).name


def test_build5_release_audit_requires_build5_evidence():
    spec = importlib.util.spec_from_file_location("audit_release", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.13")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:BUILD_NOTES_v2.5.3_BUILD5.md" in names
    assert "file:HARDWARE_VALIDATION_READINESS_v2.5.3_BUILD5.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.5.3_BUILD5.md" in names


def test_runtime_zip_includes_readiness_helper_but_excludes_build5_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location("package_installable_zip", ROOT / "tools" / "package_installable_zip.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    out = tmp_path / "runtime.zip"
    names = tool.create_installable_zip(ROOT, out)
    assert "script.oppo203.iso.external/resources/lib/oppo/hardware_validation_readiness.py" in names
    assert "script.oppo203.iso.external/BUILD_NOTES_v2.5.3_BUILD5.md" not in names
    assert "script.oppo203.iso.external/HARDWARE_VALIDATION_READINESS_v2.5.3_BUILD5.md" not in names
    with zipfile.ZipFile(out) as zf:
        addon_text = zf.read("script.oppo203.iso.external/addon.xml").decode("utf-8")
    assert 'version="2.9.13"' in addon_text
    assert "Build 5" in addon_text


def test_build5_readiness_helper_covers_settings_instance_empty_and_invalid_export(tmp_path):
    helper = importlib.import_module("resources.lib.hardware_validation_readiness")
    from resources.lib.settings_reader import Settings

    settings = Settings({"oppo_hardware_model": "chinoppo_m9702", "nas_playback_confirmed": "true"})
    report = helper.build_readiness_report(settings, path_exists=lambda path: True)
    assert report["nas_playback_capability"]["family"] == "chinoppo_family"

    default_report = helper.build_readiness_report(path_exists=lambda path: True)
    assert default_report["summary"]["configuration"]["hardware_model"] == "udp_203"

    assert helper.format_readiness_report(None) == "OPPO203 hardware-validation readiness report unavailable"
    try:
        helper.export_readiness_report("")
    except ValueError as exc:
        assert "addon_data_dir is required" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("empty addon_data_dir should fail")

    path = helper.export_readiness_report(tmp_path, now=lambda: datetime(2026, 5, 18, 13, 0, 0))
    assert Path(path).exists()


def test_build5_installer_export_failure_is_non_fatal(monkeypatch):
    stubs = ROOT / "tests" / "_stubs"
    monkeypatch.syspath_prepend(str(stubs))
    monkeypatch.syspath_prepend(str(ROOT))
    monkeypatch.syspath_prepend(str(LIB))
    from tests._support.lib_buckets import with_canonical
    for name in with_canonical(("xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs", "resources.lib.installer", "installer")):
        sys.modules.pop(name, None)
    import xbmcaddon  # type: ignore
    xbmcaddon.reset(info={"path": str(ROOT), "id": "script.oppo203.iso.external"})
    installer = importlib.import_module("resources.lib.installer")
    monkeypatch.setattr(installer, "_paths", lambda: (_ for _ in ()).throw(RuntimeError("no addon data")))
    assert installer.export_hardware_validation_readiness() is None
