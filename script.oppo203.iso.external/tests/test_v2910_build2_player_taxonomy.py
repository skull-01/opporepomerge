"""v2.9.10 Build 3 - OPPO clone taxonomy and aliases."""

import importlib.util
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _players_db_model_count():
    db = json.loads(
        (ROOT / "docs/configurator/players-db/players-models.json").read_text(encoding="utf-8")
    )
    return len(db["models"])


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build2_registry_contains_new_clone_and_successor_models():
    profiles = _load("hardware_profiles_build2", "resources/lib/oppo/hardware_profiles.py")
    players = set(profiles.list_profiles("player"))
    for key in ("M9200", "M9205", "CineUltra-V203", "CineUltra-V204", "Magnetar-UDP900"):
        assert key in players
    assert profiles.get_profile("M9200")["hardware_class"] == profiles.HARDWARE_CLASS_CHINOPPO_CLONE
    assert profiles.get_profile("CineUltra-V204")["wake_behavior"] == "clone_eject_wake"
    magnetar = profiles.get_profile("Magnetar-UDP900")
    assert magnetar["hardware_class"] == profiles.HARDWARE_CLASS_OPPO_LIKE_SUCCESSOR
    assert magnetar["protocol_stance"] == profiles.PROTOCOL_STANCE_WARNING_ONLY


def test_build2_aliases_normalize_to_canonical_models():
    profiles = _load("hardware_profiles_build2_aliases", "resources/lib/oppo/hardware_profiles.py")
    settings_reader = _load(
        "settings_reader_build2_aliases", "resources/lib/kodi/settings_reader.py"
    )
    aliases = {
        "m9702_v1": "M9702",
        "m9702-v2": "M9702",
        "chinoppo_m9702_v3": "M9702",
        "m9200": "M9200",
        "chinoppo_m9205": "M9205",
        "cineultra-v203": "CineUltra-V203",
        "v204": "CineUltra-V204",
        "magnetar_udp900": "Magnetar-UDP900",
        "udp900": "Magnetar-UDP900",
    }
    for alias, canonical in aliases.items():
        assert profiles.normalize_profile_key(alias) == canonical
        assert settings_reader.normalize_hardware_model(alias) == canonical


def test_build2_settings_dropdown_and_compatibility_matrix_match():
    settings_reader = _load("settings_reader_build2", "resources/lib/kodi/settings_reader.py")
    settings_xml = (ROOT / "resources/settings.xml").read_text(encoding="utf-8")
    values = (
        settings_xml.split('id="oppo_hardware_model"', 1)[1]
        .split('values="', 1)[1]
        .split('"', 1)[0]
        .split("|")
    )
    normalized = {settings_reader.normalize_hardware_model(value) for value in values}
    assert normalized == set(settings_reader.HARDWARE_COMPAT)
    # Canonical count lives in players-models.json; the consistency guard keeps the two in lockstep.
    assert len(settings_reader.HARDWARE_COMPAT) == _players_db_model_count()


def test_build2_clone_models_use_eject_wake_and_stock_oppo_stays_passthrough():
    settings_reader = _load("settings_reader_build2_clone", "resources/lib/kodi/settings_reader.py")
    from resources.lib import oppo_remote as remote

    for model in ("M9200", "CineUltra-V203", "CineUltra-V204"):
        profile = settings_reader.hardware_profile(model)
        assert profile["is_clone"] is True
        assert profile["wake_command"] == "#EJT"
        assert remote.resolve_power_on_token("#PON", model) == "#EJT"
        assert remote.resolve_power_on_token("#POW", model) == "#EJT"
    # Base M9205 is a clone but operator-validated to drive CEC via stock power:
    # it wakes with #PON, so the wake rewrite resolves to #PON (a #POW press also
    # maps to the #PON wake). The M9205-V1..V4 / M9205C splits stay #EJT.
    m9205 = settings_reader.hardware_profile("M9205")
    assert m9205["is_clone"] is True
    assert m9205["wake_command"] == "#PON"
    assert remote.resolve_power_on_token("#PON", "M9205") == "#PON"
    assert remote.resolve_power_on_token("#POW", "M9205") == "#PON"
    assert remote.resolve_power_on_token("#PON", "UDP-203") == "#PON"
    assert remote.resolve_power_on_token("#POW", "UDP-205") == "#POW"


def test_build2_successors_do_not_receive_clone_wake_behavior():
    settings_reader = _load(
        "settings_reader_build2_successor", "resources/lib/kodi/settings_reader.py"
    )
    caps = _load(
        "hardware_capabilities_build2_successor", "resources/lib/oppo/hardware_capabilities.py"
    )
    from resources.lib import oppo_remote as remote

    profile = settings_reader.hardware_profile("magnetar_udp900")
    assert profile["protocol_compatible"] is False
    assert profile["is_clone"] is False
    assert profile["wake_command"] is None
    assert caps.is_warning_only_successor("Magnetar-UDP900") is True
    assert remote.resolve_power_on_token("#PON", "magnetar_udp900") == "#PON"
    assert remote.resolve_power_on_token("#POW", "magnetar_udp900") == "#POW"
    assert settings_reader.compatibility_preset("Reavon-UBR-X100") == {"__reavon_warning__": True}


def test_build2_command_map_remains_unchanged_and_forbidden_tokens_absent():
    command_map = _load("command_map_build2", "resources/lib/oppo/command_map.py")
    loaded = command_map.load_default_command_map()
    assert len(loaded) == 76
    values = "\n".join(loaded.values())
    assert "#SIS" not in values
    assert "#PGU" not in values
    assert "#PGD" not in values


def test_build2_version_docs_and_audit_evidence_identity():
    version = _load("version_build2", "resources/lib/kodi/version.py")
    assert version.BUILD_ID == "v2.9.17 Final"
    assert version.BUILD_NUMBER == 26
    addon = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.9.10 Build 2" in addon
    assert "Version 2.9.10 Build 2" in addon
    assert "Version 2.9.10 Build 1" in addon
    audit = _load("audit_release_build2", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.17")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.10-build2/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.10_BUILD2.md" in names
    assert "file:HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD2.md" in names


def test_runtime_zip_excludes_build2_development_evidence(tmp_path):
    package_tool = _load("package_installable_zip_build2", "tools/package_installable_zip.py")
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
