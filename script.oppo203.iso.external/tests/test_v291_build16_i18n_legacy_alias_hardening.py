"""v2.9.1 Build 16 - i18n extraction legacy alias hardening tests."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_make_pot_is_documented_legacy_alias_not_deleted():
    make_pot = _load("make_pot_build16", "tools/make_pot.py")
    assert make_pot.LEGACY_ALIAS_FOR == "tools/i18n_extract.py"
    assert make_pot.LEGACY_ALIAS_STATUS == "retained_legacy_compatibility_alias"
    assert "legacy compatibility alias" in make_pot.legacy_alias_notice()
    # Historical parser/renderer contract remains callable for old automation.
    assert make_pot._ids_in_source("x = L(31000)\ny = _('#31001')\n") == {31000, 31001}
    assert 'msgctxt "#31000"' in make_pot.render_pot([31000])


def test_i18n_extract_reports_build16_alias_policy():
    i18n = _load("i18n_extract_build16", "tools/i18n_extract.py")
    policy = i18n.legacy_alias_policy()
    assert policy["primary"] == "tools/i18n_extract.py"
    assert policy["legacy_alias"] == "tools/make_pot.py"
    assert policy["status"] == "retained_legacy_compatibility_alias"
    assert policy["removal_policy"] == "not removed in Build 16"
    ok, detail = i18n.check_extraction(ROOT, "legacy")
    assert ok is True
    assert "make_pot fallback preserved" in detail
    assert "legacy alias retained" in detail


def test_i18n_extract_cli_keeps_check_non_writing_with_alias_notice():
    pot = ROOT / "resources" / "language" / "strings.pot"
    before = pot.exists()
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "i18n_extract.py"),
            "--root",
            str(ROOT),
            "--backend",
            "legacy",
            "--check",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: i18n_extract" in result.stdout
    assert "legacy alias retained" in result.stdout
    assert pot.exists() == before


def test_verify_and_docs_mark_make_pot_legacy_alias():
    verify = (ROOT / "scripts" / "verify.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reference = (ROOT / "reference.md").read_text(encoding="utf-8")
    assert 'python3 tools/i18n_extract.py --root "$ROOT" --check' in verify
    assert "tools/make_pot.py" in verify
    assert "v2.9.10 Build 4" in readme
    assert "legacy compatibility alias" in readme
    assert "v2.9.10 Build 4" in reference
    assert "not removed in Build 16" in reference


def test_runtime_zip_still_excludes_i18n_development_tooling(tmp_path):
    package_tool = _load("package_installable_zip_build16", "tools/package_installable_zip.py")
    assert package_tool.is_runtime_member("tools/i18n_extract.py") is False
    assert package_tool.is_runtime_member("tools/make_pot.py") is False
    assert package_tool.is_runtime_member("babel.cfg") is False
    out = tmp_path / "runtime.zip"
    package_tool.create_installable_zip(ROOT, out)
    with zipfile.ZipFile(out) as zf:
        packaged = set(zf.namelist())
    assert "script.oppo203.iso.external/tools/i18n_extract.py" not in packaged
    assert "script.oppo203.iso.external/tools/make_pot.py" not in packaged
    assert "script.oppo203.iso.external/babel.cfg" not in packaged


def test_release_audit_discovers_build16_manifest_and_evidence():
    audit = _load("audit_release_build16", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.17")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build16/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD16.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD16.md" in names
    assert "file:tools/i18n_extract.py" in names
    assert "file:tools/make_pot.py" in names


def test_addon_metadata_and_version_source_identify_build16():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from resources.lib import version

    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert version.BUILD_ID == "v2.9.17 Final"
    assert version.BUILD_NUMBER == 26
    assert "Version 2.9.10 Build 2" in addon_text
    assert "legacy compatibility alias" in addon_text
    assert "Version 2.9.1 Build 15" in addon_text
