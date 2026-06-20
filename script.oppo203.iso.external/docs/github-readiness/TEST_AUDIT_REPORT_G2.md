# Test Audit Report G2

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Completed validation

```text
py_compile service.py default.py tests/_support/project_files.py: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
tests/test_v2910_final_release.py: 3 passed
tests/test_v2910*.py: 189 passed
audit_release --expected-version 2.9.10: PASS 553/553
pytest split aggregate: 943 passed + 12 subtests
unittest discover -s tests: 571 tests OK
runtime ZIP audit: 68 files, 0 forbidden files, ZIP integrity OK
post-unpack dev-source v2.9.10 tests: 189 passed
post-unpack audit_release --expected-version 2.9.10: PASS 553/553
```

## Split pytest strategy

The full test suite was executed as split groups to avoid command timeout. The aggregate completed result is:

```text
383 passed in tests/test_all.py
143 passed + 12 subtests in coverage/superset group 1
60 passed in superset/v2.5.0 group
96 passed in v2.5.2/v2.5.3/v2.9.0/v2.9.10 group
110 passed in v2.9.10 AVR/registry group
50 passed in v2.9.10 TV/final/docs group
18 passed in v2.9.1 audit/logging/docs group
6 passed in v2.9.1 type-hint baseline group
7 passed in v2.9.1 layout group
7 passed in v2.9.1 i18n extraction group
28 passed in v2.9.1 startup/disc/command-map group
18 passed in v2.9.1 evidence/version/release automation group
17 passed in v2.9.1 packaging/settings group
```

## Validation limitations

- A full unsplit `pytest -q` run timed out before completion in this environment and is not claimed.
- A split parallel coverage run was attempted but timed out before completion, so G2 does not claim a new coverage gate result.
- No real hardware validation was performed.
