"""v2.9.1 Build 16 - type hints and non-blocking mypy baseline tests."""

from __future__ import annotations

import importlib.util
import inspect
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for item in (str(ROOT), str(LIB)):
    if item not in sys.path:
        sys.path.insert(0, item)


def _load_type_check():
    spec = importlib.util.spec_from_file_location(
        "type_check_build13", ROOT / "tools" / "type_check.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


def _load_package_tool():
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip_build13", ROOT / "tools" / "package_installable_zip.py"
    )
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    return tool


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "audit_release_build13", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def test_type_check_script_is_non_blocking_when_mypy_is_missing_or_reports_findings():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "type_check.py"), "--root", str(ROOT)],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert any(
        token in result.stdout
        for token in ("SKIP: mypy is not installed", "OK: mypy", "WARN: mypy")
    )


def test_mypy_configuration_exists_and_targets_runtime_helpers():
    text = (ROOT / "mypy.ini").read_text(encoding="utf-8")
    # ENH-#51 aligns the mypy target with the rest of the toolchain (ruff py39,
    # requires-python >=3.9) and turns on the incremental strict gate.
    assert "python_version = 3.9" in text
    assert "ignore_missing_imports = True" in text
    assert "strict = True" in text
    assert "follow_imports = silent" in text
    assert "files =" in text
    assert "resources/lib/avr/avr_sequence.py" in text
    tool = _load_type_check()
    command = tool.build_mypy_command(ROOT)
    assert str(ROOT / "resources/lib") in command
    assert str(ROOT / "tools/package_installable_zip.py") in command


def test_strict_gate_command_uses_allowlist_not_full_tree():
    tool = _load_type_check()
    command = tool.build_gate_command(ROOT)
    assert "--config-file" in command
    assert str(ROOT / "mypy.ini") in command
    # The gate must rely on the mypy.ini ``files`` allowlist, never an explicit
    # resources/lib target, so not-yet-annotated modules are followed silently
    # (follow_imports = silent) instead of blocking the gate.
    assert str(ROOT / "resources/lib") not in command
    assert str(ROOT / "tools/package_installable_zip.py") not in command


def test_selected_public_helpers_have_type_annotations():
    from resources.lib import intercept

    for func in (
        intercept.classify,
        intercept.is_disc_image,
        intercept.is_excluded_loose_video,
        intercept.is_4k_disc_style_source,
        intercept.should_intercept_4k_disc_source,
        intercept.normalise_pattern,
        intercept.pattern_matches,
        intercept.should_intercept,
    ):
        sig = inspect.signature(func)
        assert sig.return_annotation is not inspect.Signature.empty, func.__name__
        assert any(
            param.annotation is not inspect.Parameter.empty for param in sig.parameters.values()
        ), func.__name__


def test_runtime_packaging_excludes_type_check_dev_files():
    tool = _load_package_tool()
    assert tool.is_runtime_member("tools/type_check.py") is False
    assert tool.is_runtime_member("mypy.ini") is False
    assert tool.is_runtime_member("tests/test_v291_build13_type_hint_baseline.py") is False


def test_release_audit_requires_build13_manifest_and_type_check_evidence():
    audit = _load_audit()
    results = audit.run_audit(ROOT, expected_version="2.9.16")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build13/MANIFEST.txt" in names
    assert "file:tools/type_check.py" in names
    assert "file:mypy.ini" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD13.md" in names


def test_addon_metadata_and_version_source_identify_build13():
    from resources.lib import version

    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert version.BUILD_ID == "v2.9.16 Final"
    assert version.BUILD_NUMBER == 25
    assert "Version 2.9.10 Build 2" in addon_text
    assert "type hints and non-blocking mypy baseline" in addon_text
