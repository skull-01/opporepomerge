"""v2.9.1 Build 2 - centralized disc classification and shared constants."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file, read_project_file
LIB = ROOT / "resources" / "lib"
STUBS = ROOT / "tests" / "_stubs"
for path in (str(STUBS), str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)

import disc_classification as dc  # noqa: E402
import intercept  # noqa: E402
import installer  # noqa: E402
import playercorefactory_merge as pcf  # noqa: E402
import constants  # noqa: E402


def _read(name: str) -> str:
    return read_project_file(ROOT, name)


def test_shared_classifier_matches_required_uhd_disc_policy():
    accepted = [
        "Movie (2024) 4K UHD.iso",
        "Movie (2024) 2160p/BDMV/index.bdmv",
        "Movie (2024) UHD/BDMV/MovieObject.bdmv",
        "Movie (2024) 4K/BDMV/PLAYLIST/00800.mpls",
    ]
    rejected = [
        "Movie.iso",
        "Movie 4K UHD.mkv",
        "Movie 2160p.m2ts",
        "Movie UHD.ts",
        "Movie 4K/VIDEO_TS/VIDEO_TS.IFO",
        "",
        None,
    ]
    for path in accepted:
        assert dc.should_intercept_4k_disc_source(path) is True
        assert intercept.should_intercept_4k_disc_source(path) is True
    for path in rejected:
        assert dc.should_intercept_4k_disc_source(path) is False
        assert intercept.should_intercept_4k_disc_source(path) is False


def test_shared_constants_preserve_option4_xml_outputs():
    assert constants.OPPO_COMMAND_MAP_SIZE == 76
    assert constants.MIN_COVERAGE_PERCENT == 98
    assert dc.XML_4K_TAG_FILENAME_PATTERN == r".*(4K|4k|UHD|uhd|2160p|2160P).*"
    assert dc.XML_DISC_FILETYPES == ("iso", "bdmv", "mpls")
    assert dc.XML_LOOSE_VIDEO_FILETYPES[:5] == ("mkv", "mp4", "m4v", "mov", "mpg")
    assert installer.XML_4K_TAG_FILENAME_PATTERN == dc.XML_4K_TAG_FILENAME_PATTERN
    assert pcf.XML_4K_TAG_FILENAME_PATTERN == dc.XML_4K_TAG_FILENAME_PATTERN
    assert installer.XML_DISC_FILETYPES == dc.XML_DISC_FILETYPES
    assert pcf.XML_DISC_FILETYPES == dc.XML_DISC_FILETYPES
    assert installer.XML_LOOSE_VIDEO_FILETYPES == dc.XML_LOOSE_VIDEO_FILETYPES
    assert pcf.XML_LOOSE_VIDEO_FILETYPES == dc.XML_LOOSE_VIDEO_FILETYPES


def test_generated_installer_and_merge_xml_remain_option4_safe():
    rule_xml = installer.build_rule_xml()
    for filetype in ("iso", "bdmv", "mpls"):
        assert f'filetypes="{filetype}"' in rule_xml
    assert dc.XML_4K_TAG_FILENAME_PATTERN in rule_xml
    for loose in dc.XML_LOOSE_VIDEO_FILETYPES:
        assert f'filetypes="{loose}"' not in rule_xml

    snippet = pcf.snippet_for("oppo203", player_path="/usr/bin/python3")
    for filetype in dc.XML_DISC_FILETYPES:
        assert f'filetypes="{filetype}"' in snippet
    assert dc.XML_4K_TAG_FILENAME_PATTERN in snippet
    for loose in dc.XML_LOOSE_VIDEO_FILETYPES:
        assert f'filetypes="{loose}"' not in snippet


def test_v291_build2_metadata_and_evidence_are_present():
    for name in (
        "BUILD_NOTES_v2.9.1_BUILD2.md",
        "RELEASE_MANIFEST_v2.9.1_BUILD2.md",
        "RELEASE_NOTES_v2.9.1_BUILD2.md",
        "COVERAGE_REPORT_v2.9.1_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD2.md",
        "HARDWARE_VALIDATION_v2.9.1_BUILD2.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD2.md",
    ):
        assert find_project_file(ROOT, name).exists(), name
    addon = _read("addon.xml")
    assert 'version="2.9.11"' in addon
    assert "Version 2.9.1 Build 2" in addon
    assert "centralized disc classification" in addon
    assert "No playback" in addon


def test_v291_build2_release_audit_requires_build2_evidence():
    spec = importlib.util.spec_from_file_location("audit_release", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.11")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    for required in (
        "file:BUILD_NOTES_v2.9.1_BUILD2.md",
        "file:RELEASE_MANIFEST_v2.9.1_BUILD2.md",
        "file:TEST_AUDIT_REPORT_v2.9.1_BUILD2.md",
        "file:HARDWARE_VALIDATION_v2.9.1_BUILD2.md",
        "file:PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD2.md",
    ):
        assert required in names


def test_v291_build2_runtime_zip_policy_includes_runtime_helpers_and_excludes_evidence():
    spec = importlib.util.spec_from_file_location("package_installable_zip", ROOT / "tools" / "package_installable_zip.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    for suffix in (
        "BUILD_NOTES_v2.9.1_BUILD2.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD2.md",
        "tests/test_v291_build2_disc_classification.py",
        "tools/audit_release.py",
    ):
        assert tool.is_runtime_member(suffix) is False
    assert tool.is_runtime_member("resources/lib/disc_classification.py") is True
    assert tool.is_runtime_member("resources/lib/constants.py") is True
    assert tool.is_runtime_member("addon.xml") is True


def test_shared_classifier_edge_helpers_cover_legacy_branches():
    assert dc.norm_path(None) == ""
    assert dc.norm_path(r"C:\\Movies\\Movie 4K.iso") == "C://Movies//Movie 4K.iso"
    assert dc.is_bdmv_navigation_path("Movie UHD/BDMV/SomeTitle.bdmv") is True
    assert dc.is_4k_disc_style_source("") is False
    assert dc.xml_4k_tag_filename_pattern() == dc.XML_4K_TAG_FILENAME_PATTERN
    assert dc.xml_disc_filetypes() == dc.XML_DISC_FILETYPES
    assert dc.xml_loose_video_filetypes() == dc.XML_LOOSE_VIDEO_FILETYPES


def test_intercept_legacy_wrapper_api_still_delegates_to_shared_classifier():
    assert intercept._path_has_uhd_disc_tag("movie 2160p.iso") is True
    assert intercept._extension("movie.ISO") == ".iso"
    assert intercept._is_bdmv_navigation_path("Movie 4K/BDMV/index.bdmv") is True
    assert intercept.is_excluded_loose_video("movie UHD.mp4") is True
    assert intercept.is_4k_disc_style_source("Movie UHD.iso") is True


class _WriteOnlyRollbackFS:
    def __init__(self):
        self.files = {"/tmp/playercorefactory.xml": "   "}
        self.write_calls = 0

    def exists(self, path):
        return path in self.files

    def read(self, path):
        return self.files.get(path, "")

    def write(self, path, text):
        self.write_calls += 1
        self.files[path] = text
        if self.write_calls == 1:
            raise OSError("write failed")

    def copy(self, src, dst):
        raise AssertionError("no backup expected for whitespace-only existing XML")


def test_build2_covers_playercorefactory_rollback_without_backup_branch():
    fs = _WriteOnlyRollbackFS()
    snippet = pcf.snippet_for("oppo203", player_path="/usr/bin/python3")
    try:
        pcf.merge("/tmp/playercorefactory.xml", snippet, fs=fs, now=lambda: 0)
    except OSError as exc:
        assert "write failed" in str(exc)
    else:  # pragma: no cover - defensive test guard
        raise AssertionError("merge should re-raise write failure")
    assert fs.files["/tmp/playercorefactory.xml"] == "   "
    assert fs.write_calls == 2
