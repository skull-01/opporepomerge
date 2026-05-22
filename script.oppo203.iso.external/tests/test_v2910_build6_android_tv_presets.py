"""v2.9.10 Build 16 - Android / Google TV ADB preset pack."""
from pathlib import Path
import importlib.util
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build7_adds_required_android_google_tv_adb_presets_only_as_software_metadata():
    presets = _load("tv_presets_build7", "resources/lib/tv_presets.py")
    expected = (
        "tcl_android_tv",
        "sony_android_tv",
        "hisense_android_tv",
        "philips_android_tv",
        "xiaomi_android_tv",
        "sharp_android_tv",
        "skyworth_android_tv",
        "haier_android_tv",
        "generic_android_tv",
    )
    assert presets.list_android_google_tv_presets() == expected
    summary = presets.preset_registry_summary()
    assert summary["android_google_tv_preset_count"] == 9
    assert summary["android_google_tv_preset_ids"] == expected
    assert summary["validation_warnings"] == ()
    assert summary["software_preset_only"] is True
    assert summary["hardware_validation_claimed"] is False
    assert summary["universal_hdmi_command_claimed"] is False

    for preset_id in expected:
        preset = presets.get_preset(preset_id)
        assert preset["backend"] == "adb"
        assert preset["editable"] is True
        assert preset["software_preset_only"] is True
        assert preset["hardware_validation_required"] is True
        assert preset["hardware_validation_claimed"] is False
        assert preset["command_fields"] == ("oppo_input_adb_shell", "kodi_input_adb_shell")
        assert preset["adb_command_scope"] == "model_specific_editable"
        assert preset["universal_hdmi_command_claimed"] is False


def test_build7_preserves_existing_tv_backend_apis_and_editable_adb_behavior():
    backends = _load("tv_backends_build7", "resources/lib/tv_backends.py")
    presets = _load("tv_presets_build7_backend", "resources/lib/tv_presets.py")
    assert backends.list_backends() == ("adb", "sony_bravia", "lg_command", "samsung_command", "custom_command", "roku_ecp", "smartthings")
    assert backends.registry_summary()["runtime_behavior_changed"] is False
    adb_presets = presets.presets_for_backend("adb")
    assert "adb_existing" in adb_presets
    assert "tcl_android_tv" in adb_presets
    assert "generic_android_tv" in adb_presets
    assert "generic_custom_command" in presets.presets_for_backend("custom_command")


def test_build7_settings_keep_backend_enum_and_store_preset_metadata_without_apply_behavior():
    sr = _load("settings_reader_build7", "resources/lib/settings_reader.py")
    assert sr.DEFAULTS["tv_backend"] == "adb"
    assert sr.DEFAULTS["selected_tv_preset_id"] == ""
    assert sr.ENUM_VALUES["tv_backend"] == ["adb", "sony_bravia", "lg_command", "samsung_command", "custom_command", "roku_ecp", "smartthings"]
    cfg = sr.Settings({"selected_tv_preset_id": "sony_android_tv", "tv_backend": "adb"})
    assert cfg.get("selected_tv_preset_id") == "sony_android_tv"
    assert cfg.get("oppo_input_adb_shell") == sr.DEFAULTS["oppo_input_adb_shell"]
    assert cfg.get("kodi_input_adb_shell") == sr.DEFAULTS["kodi_input_adb_shell"]


def test_build7_docs_warn_presets_are_not_universal_hardware_claims():
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reference = (ROOT / "reference.md").read_text(encoding="utf-8")
    web_refs = (ROOT / "web-references.md").read_text(encoding="utf-8")
    for text in (addon, readme, reference, web_refs):
        assert "Version 2.9.10 Build 11" in text
        assert "Android / Google TV preset pack" in text
        assert "No universal ADB HDMI command is claimed" in text
        assert "Hardware validation is not claimed" in text


def test_build7_release_audit_requires_build7_evidence():
    audit = _load("audit_release_build7", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.13")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.10-build7/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.10_BUILD7.md" in names
    assert "file:RELEASE_MANIFEST_v2.9.10_BUILD7.md" in names
    assert "file:HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD7.md" in names


def test_runtime_zip_includes_build7_presets_but_excludes_development_evidence(tmp_path):
    package_tool = _load("package_installable_zip_build7", "tools/package_installable_zip.py")
    output = tmp_path / "runtime.zip"
    names = package_tool.create_installable_zip(ROOT, output)
    assert "script.oppo203.iso.external/resources/lib/tv_presets.py" in names
    with zipfile.ZipFile(output) as zf:
        assert zf.testzip() is None
        bad = [
            name for name in zf.namelist()
            if any(token in name for token in ("tests/", "tools/", "scripts/", "release-evidence/", "BUILD_NOTES", "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX"))
        ]
    assert bad == []


def test_build7_android_preset_edge_paths_for_coverage(monkeypatch):
    presets = _load("tv_presets_build7_edges", "resources/lib/tv_presets.py")
    monkeypatch.setitem(presets.TV_PRESETS, "bad_android", {"backend": "custom_command", "editable": True})
    monkeypatch.setattr(presets, "ANDROID_GOOGLE_TV_PRESET_IDS", presets.ANDROID_GOOGLE_TV_PRESET_IDS + ("bad_android",))
    warnings = presets.validate_preset_registry()
    assert "preset:bad_android:android_google_tv_not_adb:custom_command" in warnings
    monkeypatch.setitem(presets.TV_PRESETS, "bad_claim", {"backend": "adb", "editable": True, "universal_hdmi_command_claimed": True})
    warnings = presets.validate_preset_registry()
    assert "preset:bad_claim:universal_hdmi_command_claimed" in warnings
