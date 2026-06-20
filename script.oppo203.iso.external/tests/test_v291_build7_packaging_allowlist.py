"""v2.9.1 Build 16 - allowlist-based runtime packaging policy."""

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

# package_release.sh is POSIX shell tooling (bash/python3/sha256sum) run by CI on
# Linux; skip it on platforms that cannot run it rather than failing.
_POSIX_SHELL_TOOLING = os.name != "nt" and shutil.which("bash") is not None
_requires_posix_shell = pytest.mark.skipif(
    not _POSIX_SHELL_TOOLING,
    reason="POSIX release scripts (bash/python3/sha256sum) are unavailable on this platform",
)


def _load_package_tool():
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip_build8", ROOT / "tools" / "package_installable_zip.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "audit_release_build8", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def test_runtime_packaging_policy_is_allowlist_driven():
    tool = _load_package_tool()
    summary = tool.runtime_allowlist_summary()
    assert summary["root_files"] == ("addon.xml", "default.py", "service.py")
    assert summary["runtime_dirs"] == ("resources",)
    assert "tests" not in summary["runtime_dirs"]
    assert "tools" not in summary["runtime_dirs"]
    assert "scripts" not in summary["runtime_dirs"]
    assert "release-evidence" not in summary["runtime_dirs"]


def test_unknown_top_level_files_and_development_dirs_are_excluded_by_omission():
    tool = _load_package_tool()
    excluded = [
        "README.md",
        "reference.md",
        "web-references.md",
        "BUILD_NOTES_v2.9.1_BUILD7.md",
        "release-evidence/v2.9.1-build8/MANIFEST.txt",
        "tools/audit_release.py",
        "tools/package_installable_zip.py",
        "scripts/verify.sh",
        "scripts/package_release.sh",
        "tests/test_v291_build8_packaging_allowlist.py",
        ".github/workflows/ci.yml",
        ".coveragerc",
        "pytest.ini",
        "random-dev-note.txt",
    ]
    for rel in excluded:
        assert tool.is_runtime_member(rel) is False, rel


def test_runtime_allowlist_includes_only_root_runtime_files_and_resources():
    tool = _load_package_tool()
    included = [
        "addon.xml",
        "default.py",
        "service.py",
        "resources/settings.xml",
        "resources/data/oppo_command_map.json",
        "resources/lib/kodi/version.py",
        "resources/lib/kodi/disc_classification.py",
        "resources/language/resource.language.en_gb/strings.po",
    ]
    for rel in included:
        assert tool.is_runtime_member(rel) is True, rel
    assert tool.is_runtime_member("resources/lib/__pycache__/version.cpython-311.pyc") is False
    assert tool.is_runtime_member("resources/lib/version.pyc") is False


def test_created_runtime_zip_uses_allowlist_and_has_no_dev_artifacts(tmp_path):
    tool = _load_package_tool()
    out = tmp_path / "script.oppo203.iso.external-2.9.17.zip"
    names = set(tool.create_installable_zip(ROOT, out))
    assert "script.oppo203.iso.external/addon.xml" in names
    assert "script.oppo203.iso.external/default.py" in names
    assert "script.oppo203.iso.external/service.py" in names
    assert "script.oppo203.iso.external/resources/data/oppo_command_map.json" in names
    forbidden_fragments = (
        "/tests/",
        "/tools/",
        "/scripts/",
        "/release-evidence/",
        "/.github/",
        "/README.md",
        "/reference.md",
        "/web-references.md",
        "/BUILD_NOTES_",
        "/RELEASE_MANIFEST_",
        "/TEST_AUDIT_REPORT_",
        "/COVERAGE_REPORT_",
        "/HARDWARE_VALIDATION_",
        "/PRE_HARDWARE_AUDIT_REPORT_",
    )
    assert not any(any(fragment in name for fragment in forbidden_fragments) for name in names)
    with zipfile.ZipFile(out) as zf:
        assert set(zf.namelist()) == names


@_requires_posix_shell
def test_package_release_script_defaults_to_active_build(tmp_path):
    out = tmp_path / "dist"
    env = {k: v for k, v in os.environ.items() if k != "BUILD_SUFFIX"}
    env.update({"OUT_DIR": str(out), "VERSION": "2.9.17"})
    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "package_release.sh")],
        check=False,
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    runtime_zip = out / "script.oppo203.iso.external-2.9.17.zip"
    dev_zip = out / "script.oppo203.iso.external-2.9.17-dev-source.zip"
    checksum = out / "script.oppo203.iso.external-2.9.17.sha256"
    assert runtime_zip.exists()
    assert dev_zip.exists()
    assert checksum.exists()


def test_release_audit_requires_build8_manifest_and_evidence():
    audit = _load_audit()
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.17")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build8/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD7.md" in names
    assert "file:RELEASE_MANIFEST_v2.9.1_BUILD7.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD7.md" in names


def test_addon_metadata_and_version_source_identify_build8():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from resources.lib import version

    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert version.BUILD_ID == "v2.9.17 Final"
    assert version.BUILD_NUMBER == 26
    assert "Version 2.9.1 Build 11" in addon_text
    assert "allowlist-driven packaging policy" in addon_text
