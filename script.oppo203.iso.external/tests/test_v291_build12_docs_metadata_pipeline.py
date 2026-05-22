"""v2.9.1 Build 16 - docs metadata/rendering pipeline tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_render_docs():
    spec = importlib.util.spec_from_file_location("render_docs_build13", ROOT / "tools" / "render_docs.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


def _load_audit():
    spec = importlib.util.spec_from_file_location("audit_release_build13", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def test_docs_sources_yaml_is_dependency_free_metadata_source():
    tool = _load_render_docs()
    data = tool.load_sources(ROOT / "docs" / "sources.yaml")
    assert data["release"]["build_id"] == "v2.9.12 Final"
    assert data["release"]["build_number"] == 21
    assert data["release"]["runtime_behavior_changed"] is False
    assert data["release"]["hardware_validation_claimed"] is False
    assert "runtime-only installable ZIP policy" in data["protected_behavior"]
    assert "README.md" in data["managed_documents"]


def test_rendered_metadata_blocks_are_present_and_current():
    tool = _load_render_docs()
    data = tool.load_sources(ROOT / "docs" / "sources.yaml")
    for rel in tool.MANAGED_FILES:
        block = tool.render_block(data, rel)
        text = read_project_file(ROOT, rel)
        assert tool.BEGIN in text
        assert tool.END in text
        assert block in text
        assert "v2.9.12 Final" in block
        assert "Hardware validation claimed: `false`" in block


def test_render_docs_cli_check_passes_without_rewriting():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "render_docs.py"), "--root", str(ROOT), "--check"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: README.md: generated metadata block is current" in result.stdout
    assert "OK: reference.md: generated metadata block is current" in result.stdout
    assert "OK: web-references.md: generated metadata block is current" in result.stdout


def test_release_audit_requires_build13_manifest_docs_metadata_and_evidence():
    audit = _load_audit()
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.12")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build13/MANIFEST.txt" in names
    assert "file:docs/sources.yaml" in names
    assert "file:tools/render_docs.py" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD13.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD13.md" in names


def test_runtime_zip_policy_excludes_docs_and_render_tool():
    spec = importlib.util.spec_from_file_location("package_installable_zip_build13", ROOT / "tools" / "package_installable_zip.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    assert tool.is_runtime_member("docs/sources.yaml") is False
    assert tool.is_runtime_member("tools/render_docs.py") is False
    assert tool.is_runtime_member("README.md") is False


def test_addon_metadata_and_version_source_identify_build13():
    from resources.lib import version

    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert version.BUILD_ID == "v2.9.12 Final"
    assert version.BUILD_NUMBER == 21
    assert "Version 2.9.10 Build 2" in addon_text
    assert "docs/sources.yaml" in addon_text
    assert "tools/render_docs.py" in addon_text
