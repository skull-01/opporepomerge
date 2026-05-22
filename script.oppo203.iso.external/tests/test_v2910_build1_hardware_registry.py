"""v2.9.10 Build 3 - unified hardware registry foundation."""
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


def test_hardware_profiles_define_three_roles_and_player_classes():
    profiles = _load("hardware_profiles_build1", "resources/lib/hardware_profiles.py")
    assert profiles.list_roles() == ("player", "tv", "avr")
    assert profiles.HARDWARE_CLASS_STOCK_OPPO == "stock_oppo"
    assert profiles.HARDWARE_CLASS_CHINOPPO_CLONE == "chinoppo_clone"
    assert profiles.HARDWARE_CLASS_EXPERIMENTAL_CLONE == "experimental_clone"
    assert profiles.HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR == "oppo_like_successor"
    assert "UDP-203" in profiles.list_profiles("player")
    assert "adb" in profiles.list_profiles("tv")
    assert "denon_marantz" in profiles.list_profiles("avr")


def test_hardware_capabilities_are_read_only_and_do_not_claim_validation():
    caps = _load("hardware_capabilities_build1", "resources/lib/hardware_capabilities.py")
    summary = caps.hardware_registry_summary()
    assert summary["runtime_behavior_changed"] is False
    assert summary["hardware_validation_claimed"] is False
    assert summary["player_count"] >= 12
    assert caps.is_stock_oppo("UDP-203") is True
    assert caps.is_clone_family("M9702") is True
    assert caps.is_warning_only_successor("Reavon-UBR-X100") is True
    assert caps.is_warning_only_successor("Magnetar-UDP800") is True


def test_build1_does_not_mutate_existing_oppo_command_map_or_settings_count():
    command_map = _load("command_map_build1", "resources/lib/command_map.py")
    settings_reader = _load("settings_reader_build1", "resources/lib/settings_reader.py")
    loaded = command_map.load_default_command_map()
    assert len(loaded) == 76
    assert not any(token in value for value in loaded.values() for token in ("#SIS", "#PGU", "#PGD"))
    settings_xml = (ROOT / "resources/settings.xml").read_text(encoding="utf-8")
    enum_values = settings_xml.split('id="oppo_hardware_model"', 1)[1].split('values="', 1)[1].split('"', 1)[0].split("|")
    assert len(enum_values) == len(settings_reader.HARDWARE_COMPAT)


def test_build1_version_docs_and_evidence_identity():
    version = _load("version_build1", "resources/lib/version.py")
    assert version.ADDON_VERSION == "2.9.12"
    assert version.BUILD_ID == "v2.9.12 Final"
    assert version.BUILD_NUMBER == 21
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert 'version="2.9.12"' in addon
    assert "Version 2.9.10 Build 2" in addon
    assert "Version 2.9.1 Build 16" in addon
    assert "OPPO clone taxonomy and aliases" in (ROOT / "README.md").read_text(encoding="utf-8")


def test_release_audit_discovers_build1_manifest_and_evidence():
    audit = _load("audit_release_build1", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.12")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.10-build1/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.10_BUILD1.md" in names
    assert "file:HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD1.md" in names


def test_runtime_zip_excludes_build1_development_evidence(tmp_path):
    package_tool = _load("package_installable_zip_build1", "tools/package_installable_zip.py")
    output = tmp_path / "runtime.zip"
    names = package_tool.create_installable_zip(ROOT, output)
    assert names
    assert all("hardware_profiles.py" in name or not name.endswith(".md") for name in names)
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


def test_build1_registry_helpers_cover_default_and_unknown_paths():
    profiles = _load("hardware_profiles_build1_extra", "resources/lib/hardware_profiles.py")
    caps = _load("hardware_capabilities_build1_extra", "resources/lib/hardware_capabilities.py")
    all_profiles = profiles.list_profiles()
    assert "UDP-203" in all_profiles
    assert profiles.get_profile("missing", {"role": "unknown"}) == {"role": "unknown"}
    assert "UDP-205" in caps.supported_profile_keys()
    assert caps.profile_class("missing") == ""


def test_build1_covers_command_map_validation_failure_paths(tmp_path):
    mod = _load("command_map_build1_extra", "resources/lib/command_map.py")
    valid = mod.load_default_command_map()
    bad_value = dict(valid)
    first = next(iter(bad_value))
    bad_value[first] = object()
    try:
        mod.CommandMap(bad_value)
    except TypeError as exc:
        assert "keys and values" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("non-string command map value accepted")
    array_path = tmp_path / "array.json"
    array_path.write_text("[]", encoding="utf-8")
    try:
        mod.load_command_map(array_path)
    except TypeError as exc:
        assert "must contain an object" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("non-object command map accepted")


def test_build1_covers_settings_schema_boundary_validation():
    schema_mod = _load("settings_schema_build1_extra", "resources/lib/settings_schema.py")
    assert schema_mod.parse_bool(True) is True
    assert schema_mod.parse_bool("", default=True) is True
    assert schema_mod.parse_float("-1", minimum=0.5) == 0.5
    assert schema_mod.parse_float("99", maximum=5.0) == 5.0
    schema = schema_mod.SettingsSchema([
        schema_mod.SettingSpec("i_low", "int", "0", minimum=1, maximum=10),
        schema_mod.SettingSpec("i_high", "int", "0", minimum=1, maximum=10),
        schema_mod.SettingSpec("f_low", "float", "0", minimum=1.5, maximum=5.5),
        schema_mod.SettingSpec("f_high", "float", "0", minimum=1.5, maximum=5.5),
        schema_mod.SettingSpec("b_bad", "bool", "false"),
    ])
    issues = schema.validate({"i_low": "0", "i_high": "11", "f_low": "1.0", "f_high": "6.0", "b_bad": "maybe"})
    codes = {(item.key, item.code) for item in issues}
    assert ("i_low", "below_minimum") in codes
    assert ("i_high", "above_maximum") in codes
    assert ("f_low", "below_minimum") in codes
    assert ("f_high", "above_maximum") in codes
    assert ("b_bad", "invalid_bool") in codes


def test_build1_covers_diagnostic_logging_stream_refresh(capsys):
    mod = _load("diagnostic_logging_build1_extra", "resources/lib/diagnostic_logging.py")
    logger = mod.fallback_logger()
    logger.handlers.clear()
    mod.fallback_logger().info("first stream")
    first = capsys.readouterr().out
    assert "first stream" in first
    mod.fallback_logger().info("second stream")
    second = capsys.readouterr().out
    assert "second stream" in second


def test_build1_covers_preset_manager_unparseable_versions():
    mod = _load("preset_manager_build1_extra", "resources/lib/preset_manager.py")
    assert mod.compare_versions("not-a-version", "1.0") is None
    class BadMatch:
        def group(self, index):
            return "1.bad"
    class BadRegex:
        def match(self, value):
            return BadMatch()
    old = mod._VERSION_RE
    mod._VERSION_RE = BadRegex()
    try:
        assert mod.compare_versions("anything", "1.0") is None
    finally:
        mod._VERSION_RE = old
