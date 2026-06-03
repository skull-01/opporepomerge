"""v2.9.1 Build 16 - local build/release automation scripts."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The release scripts are POSIX shell tooling (bash + python3 + sha256sum) run by
# CI on Linux. They cannot run on Windows, so skip those cases there rather than
# failing. Pure-Python packaging policy is still covered by the other tests.
_POSIX_SHELL_TOOLING = os.name != "nt" and shutil.which("bash") is not None
_requires_posix_shell = pytest.mark.skipif(
    not _POSIX_SHELL_TOOLING,
    reason="POSIX release scripts (bash/python3/sha256sum) are unavailable on this platform",
)


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "audit_release_build6", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def _load_package_tool():
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip_build6", ROOT / "tools" / "package_installable_zip.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


@_requires_posix_shell
def test_build6_scripts_are_present_executable_and_parse():
    verify = ROOT / "scripts" / "verify.sh"
    package = ROOT / "scripts" / "package_release.sh"
    assert verify.exists()
    assert package.exists()
    assert verify.stat().st_mode & 0o111
    assert package.stat().st_mode & 0o111
    for script in (verify, package):
        result = subprocess.run(
            ["bash", "-n", str(script)], check=False, text=True, capture_output=True
        )
        assert result.returncode == 0, result.stderr


def test_verify_script_documents_required_release_verification_commands():
    text = (ROOT / "scripts" / "verify.sh").read_text(encoding="utf-8")
    assert "python3 -m py_compile service.py default.py" in text
    assert "tools/sync_version.py" in text
    assert "python3 -m pytest -q -p no:ddtrace" in text
    assert "python3 -m unittest discover -s tests -p 'test_*.py' -q" in text
    assert (
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace"
        in text
    )
    assert "tools/audit_release.py" in text


@_requires_posix_shell
def test_package_release_script_creates_runtime_zip_dev_source_and_checksum(tmp_path):
    out = tmp_path / "dist"
    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "package_release.sh")],
        check=False,
        cwd=str(ROOT),
        env={**os.environ, "OUT_DIR": str(out), "VERSION": "2.9.16", "BUILD_SUFFIX": "build6-test"},
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    runtime_zip = out / "script.oppo203.iso.external-2.9.16-build6-test.zip"
    dev_zip = out / "script.oppo203.iso.external-2.9.16-build6-test-dev-source.zip"
    checksum = out / "script.oppo203.iso.external-2.9.16-build6-test.sha256"
    assert runtime_zip.exists()
    assert dev_zip.exists()
    assert checksum.exists()
    with zipfile.ZipFile(runtime_zip) as zf:
        names = set(zf.namelist())
    assert "script.oppo203.iso.external/addon.xml" in names
    assert "script.oppo203.iso.external/service.py" in names
    assert "script.oppo203.iso.external/scripts/verify.sh" not in names
    assert "script.oppo203.iso.external/tools/audit_release.py" not in names
    assert not any("BUILD_NOTES_v2.9.1_BUILD6" in name for name in names)


def test_release_audit_requires_build6_manifest_and_evidence():
    audit = _load_audit()
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.16")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build6/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD6.md" in names
    assert "file:RELEASE_MANIFEST_v2.9.1_BUILD6.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD6.md" in names


def test_runtime_zip_policy_excludes_scripts_and_build6_evidence():
    tool = _load_package_tool()
    assert tool.is_runtime_member("scripts/verify.sh") is False
    assert tool.is_runtime_member("scripts/package_release.sh") is False
    assert tool.is_runtime_member("release-evidence/v2.9.1-build6/MANIFEST.txt") is False
    assert tool.is_runtime_member("BUILD_NOTES_v2.9.1_BUILD6.md") is False


def test_addon_metadata_and_version_source_identify_build6():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from resources.lib import version

    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert version.BUILD_ID == "v2.9.16 Final"
    assert version.BUILD_NUMBER == 25
    assert "Version 2.9.1 Build 11" in addon_text
    assert "scripts/verify.sh" in addon_text
    assert "scripts/package_release.sh" in addon_text
