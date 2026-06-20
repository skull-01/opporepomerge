"""v2.9.1 Build 5 - version single source of truth."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resources.lib import version


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "audit_release_build5", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def _load_sync_version():
    spec = importlib.util.spec_from_file_location(
        "sync_version_build5", ROOT / "tools" / "sync_version.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


def test_version_module_is_active_source_for_addon_identity():
    assert version.ADDON_ID == "script.oppo203.iso.external"
    assert version.ADDON_VERSION == "2.9.17"
    assert version.addon_version() == "2.9.17"
    assert version.BUILD_ID == "v2.9.17 Final"
    assert version.build_id() == "v2.9.17 Final"


def test_addon_xml_matches_version_source():
    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    addon_version = ET.parse(ROOT / "addon.xml").getroot().attrib["version"]
    assert addon_version == version.ADDON_VERSION
    assert 'version="2.9.17"' in addon_text
    assert "Version 2.9.1 Build 11" in addon_text


def test_sync_version_check_reports_consistency():
    tool = _load_sync_version()
    ok, detail = tool.check_version_consistency(ROOT, expected_version="2.9.17")
    assert ok is True
    assert "addon.xml and version.py agree on 2.9.17" in detail
    assert tool.version_source(ROOT) == "2.9.17"
    assert tool.addon_xml_version(ROOT) == "2.9.17"


def test_sync_version_cli_check_passes():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "sync_version.py"),
            "--root",
            str(ROOT),
            "--check",
            "--expected-version",
            "2.9.17",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: version_consistency" in result.stdout


def test_release_audit_checks_version_source_and_build5_evidence():
    audit = _load_audit()
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.17")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "version_source" in names
    assert "version_consistency" in names
    assert "file:release-evidence/v2.9.1-build5/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD5.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD5.md" in names


def test_runtime_zip_policy_excludes_version_tool_and_evidence_but_includes_runtime_version_module():
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip", ROOT / "tools" / "package_installable_zip.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    assert tool.is_runtime_member("resources/lib/version.py") is True
    assert tool.is_runtime_member("tools/sync_version.py") is False
    assert tool.is_runtime_member("release-evidence/v2.9.1-build5/MANIFEST.txt") is False
    assert tool.is_runtime_member("BUILD_NOTES_v2.9.1_BUILD5.md") is False


def test_sync_version_write_only_changes_addon_attribute_in_copy(tmp_path):
    tool = _load_sync_version()
    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")

    sandbox = tmp_path / "project"
    sandbox.mkdir()
    stale_text = re.sub(
        r'(<addon\b[^>]*\bversion=")([^"]+)(")', r"\g<1>0.0.0\g<3>", addon_text, count=1
    )
    (sandbox / "addon.xml").write_text(stale_text, encoding="utf-8")
    (sandbox / "resources" / "lib").mkdir(parents=True)
    (sandbox / "resources" / "lib" / "version.py").write_text(
        'ADDON_VERSION = "2.9.10"\n', encoding="utf-8"
    )

    written = tool.write_addon_xml_version(sandbox)
    assert written == "2.9.17"
    assert ET.parse(sandbox / "addon.xml").getroot().attrib["version"] == "2.9.17"
    assert (
        (sandbox / "addon.xml")
        .read_text(encoding="utf-8")
        .splitlines()[0]
        .startswith('<?xml version="1.0"')
    )
