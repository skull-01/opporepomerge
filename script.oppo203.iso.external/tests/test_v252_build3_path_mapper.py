"""v2.5.2 Build 3 - deterministic Kodi-to-player path mapping helper."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file


def test_smb_path_maps_to_player_mount_with_url_decoding():
    from resources.lib.path_mapper import PathMappingRule, map_kodi_path_to_player_path

    rules = [PathMappingRule("smb://truenas/media/", "/mnt/nas/media/")]
    assert map_kodi_path_to_player_path(
        "smb://truenas/media/Movies/My%20Movie/movie.iso",
        rules,
    ) == "/mnt/nas/media/Movies/My Movie/movie.iso"


def test_local_kodi_path_maps_to_same_player_tree_for_bdmv_folder():
    from resources.lib.path_mapper import PathMappingRule, map_kodi_path_to_player_path

    rules = [PathMappingRule("/mnt/media", "/mnt/nas/media")]
    assert map_kodi_path_to_player_path(
        "/mnt/media/Movies/Disc Backup/BDMV/index.bdmv",
        rules,
    ) == "/mnt/nas/media/Movies/Disc Backup/BDMV/index.bdmv"


def test_video_ts_folder_and_mkv_paths_preserve_suffixes():
    from resources.lib.path_mapper import PathMappingRule, map_kodi_path_to_player_path

    rules = [PathMappingRule("smb://truenas/media", "/mnt/nas/media")]
    assert map_kodi_path_to_player_path(
        "smb://truenas/media/DVDs/Title/VIDEO_TS/VIDEO_TS.IFO",
        rules,
    ) == "/mnt/nas/media/DVDs/Title/VIDEO_TS/VIDEO_TS.IFO"
    assert map_kodi_path_to_player_path(
        "smb://truenas/media/UHD/Test.mkv",
        rules,
    ) == "/mnt/nas/media/UHD/Test.mkv"


def test_prefix_boundary_prevents_media2_false_match():
    from resources.lib.path_mapper import PathMappingRule, map_kodi_path_to_player_path

    rules = [PathMappingRule("/mnt/media", "/mnt/nas/media")]
    assert map_kodi_path_to_player_path("/mnt/media2/Movie.iso", rules) is None


def test_first_matching_rule_wins_for_specific_over_broad_mappings():
    from resources.lib.path_mapper import PathMappingRule, explain_path_mapping

    rules = [
        PathMappingRule("smb://truenas/media/UHD/", "/mnt/nas/uhd/", label="uhd"),
        PathMappingRule("smb://truenas/media/", "/mnt/nas/media/", label="broad"),
    ]
    result = explain_path_mapping("smb://truenas/media/UHD/Movie.iso", rules)
    assert result["matched"] is True
    assert result["rule"]["label"] == "uhd"
    assert result["player_path"] == "/mnt/nas/uhd/Movie.iso"


def test_dry_run_reports_no_match_and_strict_mode_raises():
    from resources.lib.path_mapper import NoMatchingPathRule, PathMappingRule, explain_path_mapping, map_kodi_path_to_player_path

    rules = [PathMappingRule("smb://truenas/media/", "/mnt/nas/media/")]
    detail = explain_path_mapping("smb://other/media/Movie.iso", rules)
    assert detail["matched"] is False
    assert detail["reason"] == "no_matching_rule"
    assert detail["player_path"] is None
    with pytest.raises(NoMatchingPathRule):
        map_kodi_path_to_player_path("smb://other/media/Movie.iso", rules, strict=True)


def test_parse_mapping_rules_and_settings_adapter():
    from resources.lib.path_mapper import parse_mapping_rules, rules_from_settings
    from resources.lib.settings_reader import Settings

    rules = parse_mapping_rules(
        """
        # comments are ignored
        smb://truenas/media => /mnt/nas/media
        /mnt/local/media => /mnt/nas/media
        """
    )
    assert len(rules) == 2
    assert rules[0].kodi_prefix == "smb://truenas/media"

    settings = Settings({
        "nas_path_mapping_rules": "smb://truenas/media => /mnt/nas/media",
        "nas_kodi_path_prefix": "/mnt/local/media",
        "nas_player_path_prefix": "/mnt/nas/media",
    })
    setting_rules = rules_from_settings(settings)
    assert len(setting_rules) == 2
    assert setting_rules[-1].label == "settings_prefix"


def test_invalid_rules_are_rejected():
    from resources.lib.path_mapper import InvalidPathMappingRule, PathMappingRule, parse_mapping_rule

    with pytest.raises(InvalidPathMappingRule):
        PathMappingRule("", "/mnt/nas/media")
    with pytest.raises(InvalidPathMappingRule):
        parse_mapping_rule("smb://truenas/media /mnt/nas/media")


def test_build3_metadata_and_release_audit_evidence():
    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.5.2 Build 3" in addon_text
    assert "deterministic Kodi-to-player path mapping helper" in addon_text

    for rel in [
        "BUILD_NOTES_v2.5.2_BUILD3.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD3.md",
        "RELEASE_NOTES_v2.5.2_BUILD3.md",
        "COVERAGE_REPORT_v2.5.2_BUILD3.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD3.md",
    ]:
        assert find_project_file(ROOT, rel).exists(), rel

    spec = importlib.util.spec_from_file_location("audit_release_v252_build3", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.12")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:BUILD_NOTES_v2.5.2_BUILD3.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.5.2_BUILD3.md" in names


def test_runtime_zip_includes_helper_but_excludes_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location("package_installable_zip", ROOT / "tools" / "package_installable_zip.py")
    packager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packager)
    output = tmp_path / "runtime.zip"
    names = set(packager.create_installable_zip(ROOT, output))
    assert "script.oppo203.iso.external/resources/lib/path_mapper.py" in names
    assert "script.oppo203.iso.external/BUILD_NOTES_v2.5.2_BUILD3.md" not in names
    assert "script.oppo203.iso.external/tests/test_v252_build3_path_mapper.py" not in names
    with zipfile.ZipFile(output) as zf:
        assert set(zf.namelist()) == names


def test_path_mapper_defensive_and_normalization_branches():
    from resources.lib.path_mapper import (
        InvalidPathMappingRule,
        PathMappingRule,
        explain_path_mapping,
        map_kodi_path_to_player_path,
        normalize_kodi_path,
        normalize_player_path,
        parse_mapping_rule,
        rules_from_settings,
    )

    with pytest.raises(InvalidPathMappingRule):
        PathMappingRule("smb://truenas/media", "")
    with pytest.raises(InvalidPathMappingRule):
        parse_mapping_rule("# commented rule")

    dict_rule = {"kodi_prefix": "SMB://TRUENAS/media", "player_prefix": "/mnt/nas/media", "label": "dict"}
    detail = explain_path_mapping("smb://truenas/media/Movie.iso", [dict_rule])
    assert detail["matched"] is True
    assert detail["rule"]["label"] == "dict"

    with pytest.raises(InvalidPathMappingRule):
        explain_path_mapping("smb://truenas/media/Movie.iso", [object()])

    empty = explain_path_mapping("   ", [PathMappingRule("/mnt/media", "/mnt/nas/media")])
    assert empty["reason"] == "empty_kodi_path"
    assert empty["rule_count"] == 1

    assert normalize_kodi_path(None) == ""
    assert normalize_kodi_path("smb://truenas/media/Movie.iso?x=1#frag") == "smb://truenas/media/Movie.iso?x=1#frag"
    assert normalize_kodi_path("C:\\Media\\Movie.iso", decode_url=False) == "C:/Media/Movie.iso"
    assert normalize_player_path("/mnt/nas/media/") == "/mnt/nas/media/"

    # Exact prefix mapping returns the mount root without adding a trailing slash.
    assert map_kodi_path_to_player_path(
        "/mnt/media",
        [PathMappingRule("/mnt/media", "/mnt/nas/media")],
    ) == "/mnt/nas/media"

    # Case-sensitive mode intentionally does not match different URI casing.
    case_rule = PathMappingRule("smb://TRUENAS/media", "/mnt/nas/media", case_sensitive=True)
    assert map_kodi_path_to_player_path("smb://truenas/media/Movie.iso", [case_rule]) is None

    # Dict-like settings without a .get method are supported.
    setting_rules = rules_from_settings({
        "nas_path_mapping_rules": "",
        "nas_kodi_path_prefix": "smb://truenas/media",
        "nas_player_path_prefix": "/mnt/nas/media",
    })
    assert len(setting_rules) == 1
    assert setting_rules[0].label == "settings_prefix"

