"""v2.9.10 Build 16 - TV backend registry and preset foundation."""
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


def test_build5_tv_backend_registry_preserves_existing_backend_ids():
    backends = _load("tv_backends_build5", "resources/lib/tv_backends.py")
    assert backends.list_backends() == ("adb", "sony_bravia", "lg_command", "samsung_command", "custom_command", "roku_ecp", "smartthings")
    summary = backends.registry_summary()
    assert summary["backend_count"] == 7
    assert summary["runtime_behavior_changed"] is False
    assert summary["hardware_validation_claimed"] is False
    assert backends.normalize_backend_id("sony_bravia_ip") == "sony_bravia"
    assert backends.is_supported_backend("generic_custom_command") is True
    assert backends.is_supported_backend("unknown_backend") is False
    assert backends.backend_target_setting("adb", "oppo") == "oppo_input_adb_shell"
    assert backends.backend_target_setting("sony_bravia", "kodi") == "sony_kodi_hdmi_port"


def test_build5_tv_preset_registry_is_software_only_and_uses_preserved_backends():
    presets = _load("tv_presets_build5", "resources/lib/tv_presets.py")
    preset_ids = presets.list_presets()
    assert "adb_existing" in preset_ids
    assert "sony_bravia_ip" in preset_ids
    assert "lg_command_existing" in preset_ids
    assert "samsung_command_existing" in preset_ids
    assert "generic_custom_command" in preset_ids
    summary = presets.preset_registry_summary()
    assert summary["preset_count"] >= 5
    assert summary["validation_warnings"] == ()
    assert summary["software_preset_only"] is True
    assert summary["hardware_validation_claimed"] is False
    assert presets.get_preset("adb_existing")["backend"] == "adb"
    assert presets.get_preset("sony_bravia_ip")["backend"] == "sony_bravia"
    assert "generic_custom_command" in presets.presets_for_backend("custom_command")


def test_build5_tv_control_keeps_public_api_and_dispatches_through_registry(monkeypatch):
    sys.path.insert(0, str(LIB))
    try:
        tv_control = importlib.import_module("tv_control")
        calls = []
        monkeypatch.setattr(tv_control, "adb_switch_input", lambda settings, command: calls.append((settings.get("tv_backend"), command)) or "adb-ok")
        settings = {"tv_backend": "android_tv_adb", "oppo_input_adb_shell": "to-oppo", "kodi_input_adb_shell": "to-kodi"}
        assert tv_control.selected_backend_id(settings) == "adb"
        assert tv_control.switch_to_oppo(settings) == "adb-ok"
        assert calls == [("android_tv_adb", "to-oppo")]
        try:
            tv_control.switch_to_kodi({"tv_backend": "not_a_backend"})
        except tv_control.TVControlError as exc:
            assert "Unsupported TV backend" in str(exc)
        else:  # pragma: no cover - defensive assertion branch
            raise AssertionError("unsupported backend should raise TVControlError")
    finally:
        try:
            sys.path.remove(str(LIB))
        except ValueError:
            pass


def test_build5_settings_default_records_selected_tv_preset_without_changing_backend_enum():
    sr = _load("settings_reader_build5_tv", "resources/lib/settings_reader.py")
    assert sr.DEFAULTS["tv_backend"] == "adb"
    assert sr.DEFAULTS["selected_tv_preset_id"] == ""
    assert sr.ENUM_VALUES["tv_backend"] == ["adb", "sony_bravia", "lg_command", "samsung_command", "custom_command", "roku_ecp", "smartthings"]
    cfg = sr.Settings({"tv_backend": "sony_bravia"})
    assert cfg.get("selected_tv_preset_id") == ""
    assert cfg.get("tv_backend") == "sony_bravia"


def test_build5_version_docs_and_audit_evidence_identity():
    version = _load("version_build5", "resources/lib/version.py")
    assert version.BUILD_ID == "v2.9.10 Final"
    assert version.BUILD_NUMBER == 19
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 11" in addon
    assert "switch_to_oppo(settings)" in addon
    assert "Version 2.9.10 Build 4" in addon
    audit = _load("audit_release_build5", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.10")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.10-build7/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.10_BUILD7.md" in names
    assert "file:HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD7.md" in names


def test_runtime_zip_excludes_build5_development_evidence(tmp_path):
    package_tool = _load("package_installable_zip_build5", "tools/package_installable_zip.py")
    output = tmp_path / "runtime.zip"
    names = package_tool.create_installable_zip(ROOT, output)
    assert "script.oppo203.iso.external/resources/lib/tv_backends.py" in names
    assert "script.oppo203.iso.external/resources/lib/tv_presets.py" in names
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


def test_build5_registry_edge_paths_for_coverage(monkeypatch):
    backends = _load("tv_backends_build5_edges", "resources/lib/tv_backends.py")
    presets = _load("tv_presets_build5_edges", "resources/lib/tv_presets.py")
    assert backends.normalize_backend_id(None) == "adb"
    assert backends.get_backend("missing", {"fallback": True}) == {"fallback": True}
    monkeypatch.setitem(backends.TV_BACKENDS, "bad_targets", {"target_settings": "not-a-dict"})
    assert backends.backend_target_setting("bad_targets", "oppo") == ""
    assert presets.get_preset(None, {"fallback": "preset"}) == {"fallback": "preset"}
    monkeypatch.setitem(presets.TV_PRESETS, "bad_backend", {"backend": "missing", "editable": False})
    warnings = presets.validate_preset_registry()
    assert "preset:bad_backend:unsupported_backend:missing" in warnings
    assert "preset:bad_backend:not_editable" in warnings
