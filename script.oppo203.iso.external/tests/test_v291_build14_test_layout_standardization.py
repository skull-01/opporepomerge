"""v2.9.1 Build 16 - test naming/layout standardization transition."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def _load_test_layout():
    spec = importlib.util.spec_from_file_location("test_layout_build14", ROOT / "tools" / "test_layout.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


def _load_package_tool():
    spec = importlib.util.spec_from_file_location("package_installable_zip_build14", ROOT / "tools" / "package_installable_zip.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


def _load_audit():
    spec = importlib.util.spec_from_file_location("audit_release_build14", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def test_test_layout_tool_accepts_legacy_flat_and_future_versioned_paths():
    tool = _load_test_layout()
    assert tool.classify_test_path("tests/test_v291_build14_test_layout_standardization.py") == "legacy-flat"
    assert tool.classify_test_path("tests/v2_9_1/build14/test_example.py") == "future"
    assert tool.classify_test_path("tests/_support/helpers.py") == "support"
    assert tool.classify_test_path("tests/random/nested_test.py") == "nonstandard"
    assert tool.is_future_layout("tests/v2_9_1/build14/test_example.py") is True
    assert tool.is_legacy_flat_layout("tests/test_all.py") is True


def test_pytest_ini_declares_future_marker_strategy():
    tool = _load_test_layout()
    markers = tool.pytest_ini_markers(ROOT)
    assert "version(version): mark tests that belong to a release/version line." in markers
    assert "build(number): mark tests that belong to a build-specific cleanup slice." in markers
    assert "legacy_layout: inherited flat-layout tests retained during the transition." in markers


def test_test_layout_cli_check_passes_for_transition_layout():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "test_layout.py"), "--root", str(ROOT), "--check"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: test_layout" in result.stdout
    assert "legacy flat layout retained" in result.stdout


def test_verify_script_runs_test_layout_check():
    text = (ROOT / "scripts" / "verify.sh").read_text(encoding="utf-8")
    assert 'python3 tools/test_layout.py --root "$ROOT" --check' in text
    assert "python3 tools/type_check.py" in text


def test_runtime_zip_excludes_test_layout_dev_tool_and_pytest_config():
    tool = _load_package_tool()
    assert tool.is_runtime_member("tools/test_layout.py") is False
    assert tool.is_runtime_member("pytest.ini") is False
    assert tool.is_runtime_member("tests/test_v291_build14_test_layout_standardization.py") is False


def test_release_audit_requires_build14_manifest_and_layout_evidence():
    audit = _load_audit()
    results = audit.run_audit(ROOT, expected_version="2.9.10")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build14/MANIFEST.txt" in names
    assert "file:tools/test_layout.py" in names
    assert "file:pytest.ini" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD14.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD14.md" in names


def test_addon_metadata_and_version_source_identify_build14():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from resources.lib import version

    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert version.BUILD_ID == "v2.9.10 Final"
    assert version.BUILD_NUMBER == 19
    assert "Version 2.9.10 Build 2" in addon_text
    assert "test naming/layout standardization" in addon_text
