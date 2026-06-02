"""v2.5.3 Build 4 - playercorefactory merge/backup/rollback hardening."""

from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

import playercorefactory_merge as pcf  # noqa: E402


class FakeFS:
    def __init__(self, files=None, *, corrupt_after_write=False, fail_write=False):
        self._store = dict(files or {})
        self._copies = []
        self.corrupt_after_write = corrupt_after_write
        self.fail_write = fail_write

    def exists(self, path):
        return path in self._store

    def read(self, path):
        return self._store[path]

    def write(self, path, text):
        if self.fail_write:
            self._store[path] = "<playercorefactory><partial>"
            raise OSError("simulated write failure")
        self._store[path] = "<playercorefactory><partial>" if self.corrupt_after_write else text

    def copy(self, src, dst):
        self._store[dst] = self._store[src]
        self._copies.append((src, dst))


def _rules(snippet):
    root = ET.fromstring(snippet)
    return root.find("rules").findall("rule")


def test_build4_snippet_rules_are_option4_tag_aware_and_disc_style_only():
    snippet = pcf.snippet_for("oppo203", player_path="/usr/bin/python3")
    rules = _rules(snippet)
    assert [rule.get("filetypes") for rule in rules] == ["iso", "bdmv", "mpls"]
    assert all(rule.get("filename") == pcf.XML_4K_TAG_FILENAME_PATTERN for rule in rules)
    emitted = {rule.get("filetypes") for rule in rules}
    for loose in pcf.XML_LOOSE_VIDEO_FILETYPES:
        assert loose not in emitted
    assert "m2ts" not in snippet.lower()
    assert "iso|bdmv|m2ts" not in snippet


def test_build4_merge_is_idempotent_for_player_and_all_option4_rules():
    fs = FakeFS()
    snippet = pcf.snippet_for("chinoppo", player_path="/x")
    pcf.merge("/userdata/playercorefactory.xml", snippet, fs=fs, now=lambda: 0)
    out = pcf.merge("/userdata/playercorefactory.xml", snippet, fs=fs, now=lambda: 1)
    assert out["added_players"] == 0
    merged = fs._store["/userdata/playercorefactory.xml"]
    root = ET.fromstring(merged)
    players = root.find("players").findall("player")
    rules = root.find("rules").findall("rule")
    assert [p.get("name") for p in players].count("OPPO_External_chinoppo") == 1
    names = [r.get("name") for r in rules if r.get("player") == "OPPO_External_chinoppo"]
    assert sorted(names) == sorted(
        [
            "OPPO_External_chinoppo_rule_iso",
            "OPPO_External_chinoppo_rule_bdmv",
            "OPPO_External_chinoppo_rule_mpls",
        ]
    )


def test_build4_merge_backs_up_existing_before_write():
    existing = "<playercorefactory><players/><rules action='prepend'/></playercorefactory>"
    fs = FakeFS({"/u/playercorefactory.xml": existing})
    out = pcf.merge(
        "/u/playercorefactory.xml",
        pcf.snippet_for("oppo203", player_path="/x"),
        fs=fs,
        now=lambda: 0,
    )
    assert out["backup"].endswith(".bak")
    assert fs._store[out["backup"]] == existing
    assert out["post_write_validated"] is True
    assert out["rolled_back"] is False


def test_build4_merge_rolls_back_if_write_fails_after_backup():
    existing = "<playercorefactory><players/><rules action='prepend'/></playercorefactory>"
    fs = FakeFS({"/u/playercorefactory.xml": existing}, fail_write=True)
    try:
        pcf.merge(
            "/u/playercorefactory.xml",
            pcf.snippet_for("oppo203", player_path="/x"),
            fs=fs,
            now=lambda: 0,
        )
    except OSError as exc:
        assert "simulated write failure" in str(exc)
    else:  # pragma: no cover - defensive failure assertion
        raise AssertionError("merge should fail")
    assert fs._store["/u/playercorefactory.xml"] == existing
    assert any(dst.endswith(".bak") for _, dst in fs._copies)


def test_build4_merge_rolls_back_if_post_write_validation_fails():
    existing = "<playercorefactory><players/><rules action='prepend'/></playercorefactory>"
    fs = FakeFS({"/u/playercorefactory.xml": existing}, corrupt_after_write=True)
    try:
        pcf.merge(
            "/u/playercorefactory.xml",
            pcf.snippet_for("oppo203", player_path="/x"),
            fs=fs,
            now=lambda: 0,
        )
    except ValueError as exc:
        assert "failed validation" in str(exc)
    else:  # pragma: no cover - defensive failure assertion
        raise AssertionError("merge should fail")
    assert fs._store["/u/playercorefactory.xml"] == existing


def test_build4_release_audit_requires_build4_evidence():
    spec = importlib.util.spec_from_file_location(
        "audit_release", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.15")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:BUILD_NOTES_v2.5.3_BUILD4.md" in names
    assert "file:RELEASE_MANIFEST_v2.5.3_BUILD4.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.5.3_BUILD4.md" in names
    assert "file:HARDWARE_VALIDATION_v2.5.3_BUILD4.md" in names


def test_runtime_zip_policy_still_excludes_build4_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip", ROOT / "tools" / "package_installable_zip.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    out = tmp_path / "runtime.zip"
    names = tool.create_installable_zip(ROOT, out)
    assert "script.oppo203.iso.external/addon.xml" in names
    assert "script.oppo203.iso.external/BUILD_NOTES_v2.5.3_BUILD4.md" not in names
    assert "script.oppo203.iso.external/TEST_AUDIT_REPORT_v2.5.3_BUILD4.md" not in names
    with zipfile.ZipFile(out) as zf:
        addon_text = zf.read("script.oppo203.iso.external/addon.xml").decode("utf-8")
    assert 'version="2.9.15"' in addon_text
    assert "Build 4" in addon_text
