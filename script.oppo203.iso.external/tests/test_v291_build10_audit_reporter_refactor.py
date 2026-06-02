"""v2.9.1 Build 16 - audit reporter refactor regression tests."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "audit_release_build11", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    return audit


def test_audit_check_value_object_and_legacy_dict_api_are_both_available():
    audit = _load_audit()
    check = audit.AuditCheck("sample", "ok", "detail")
    assert check.passed is True
    assert check.as_dict() == {"name": "sample", "status": "ok", "detail": "detail"}
    assert audit.AuditCheck.from_mapping(check.as_dict()) == check

    legacy = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.15")
    typed = audit.collect_audit_checks(
        audit.project_root(audit.Path(ROOT)), expected_version="2.9.15"
    )
    assert legacy
    assert typed
    assert all(isinstance(item, dict) for item in legacy)
    assert all(isinstance(item, audit.AuditCheck) for item in typed)
    assert [item.as_dict() for item in typed] == legacy


def test_text_reporter_preserves_historical_cli_format():
    audit = _load_audit()
    checks = [
        audit.AuditCheck("alpha", "ok", "passed"),
        audit.AuditCheck("beta", "fail", "broken"),
    ]
    rendered = audit.TextReporter().render(ROOT, checks)
    assert "OK: alpha - passed" in rendered
    assert "FAIL: beta - broken" in rendered
    assert "SUMMARY: FAIL (1/2 checks passed)" in rendered


def test_json_reporter_preserves_json_cli_schema():
    audit = _load_audit()
    checks = [audit.AuditCheck("alpha", "ok", "passed")]
    payload = json.loads(audit.JsonReporter().render(ROOT, checks))
    assert payload["root"] == str(ROOT)
    assert payload["ok"] is True
    assert payload["results"] == [{"name": "alpha", "status": "ok", "detail": "passed"}]


def test_audit_cli_text_output_still_works():
    # Real subprocess smoke kept for the CLI boundary: this verifies the actual
    # `python tools/audit_release.py` entrypoint (argv parsing + text reporter).
    text = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "audit_release.py"),
            "--root",
            str(ROOT),
            "--expected-version",
            "2.9.15",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert text.returncode == 0, text.stdout + text.stderr
    assert "OK: python_compile - compileall passed" in text.stdout
    assert "SUMMARY: PASS" in text.stdout


def test_audit_cli_json_output_still_works():
    # JSON path runs in-process via main() (no extra cold interpreter); the text
    # test above already covers the real subprocess CLI entrypoint.
    audit = _load_audit()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = audit.main(["--root", str(ROOT), "--expected-version", "2.9.15", "--json"])
    assert rc == 0
    payload = json.loads(buf.getvalue())
    assert payload["ok"] is True
    assert any(item["name"] == "version_consistency" for item in payload["results"])


def test_release_audit_requires_build11_manifest_and_evidence():
    audit = _load_audit()
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.15")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.1-build11/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.1_BUILD13.md" in names
    assert "file:RELEASE_MANIFEST_v2.9.1_BUILD13.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.9.1_BUILD13.md" in names


def test_addon_metadata_and_version_source_identify_build11():
    from resources.lib import version

    addon_text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert version.BUILD_ID == "v2.9.15 Final"
    assert version.BUILD_NUMBER == 24
    assert "Version 2.9.1 Build 11" in addon_text
    assert "typed audit checks" in addon_text
    assert "JSON reporter" in addon_text
