# Build Notes — GitHub Readiness G7 Safe Format and Lint Cleanup

**Date:** 2026-05-20
**Build:** GitHub Readiness G7 — Safe Format and Lint Cleanup
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g6-dev-source.zip`
**Add-on version:** `2.9.10`
**Protected release baseline:** `v2.9.10 Final`
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Scope

G7 performed a narrow, safe format-hygiene cleanup without broad code reformatting. The cleanup targeted archived GitHub-readiness Markdown files that contained trailing spaces. Runtime modules were not reformatted or refactored.

## Completed work

- Removed trailing whitespace from archived GitHub-readiness Markdown handoff/report files under `docs/github-readiness/`.
- Normalized those archived Markdown files to end with a single final newline.
- Added `tests/test_github_readiness_g7_safe_format_cleanup.py` to enforce non-runtime GitHub-readiness documentation hygiene.
- Updated `pyproject.toml` GitHub-readiness metadata from G6 to G7.
- Updated documentation to record the G7 cleanup scope.
- Restored executable bits on `scripts/verify.sh` and `scripts/package_release.sh` after unpacking revealed the scripts were non-executable in the working copy. This is a metadata-only repair needed for legacy release-automation tests.

## Files changed

- `docs/github-readiness/AI_HANDOFF_G1_REPOSITORY_HYGIENE.md`
- `docs/github-readiness/AI_HANDOFF_G2_PUBLIC_DOCS.md`
- `docs/github-readiness/AI_HANDOFF_G3_DEVELOPER_DOCS.md`
- `docs/github-readiness/BUILD_NOTES_G1_REPOSITORY_HYGIENE.md`
- `docs/github-readiness/BUILD_NOTES_G2_PUBLIC_DOCS.md`
- `docs/github-readiness/BUILD_NOTES_G3_DEVELOPER_DOCS.md`
- `docs/github-readiness/BUILD_NOTES_G4_GITHUB_TEMPLATES.md`
- `docs/github-readiness/COVERAGE_REPORT_G2.md`
- `docs/github-readiness/COVERAGE_REPORT_G3.md`
- `docs/github-readiness/COVERAGE_REPORT_G4.md`
- `docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G1.md`
- `docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G2.md`
- `docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G3.md`
- `docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G4.md`
- `docs/github-readiness/HARDWARE_VALIDATION_G1.md`
- `docs/github-readiness/HARDWARE_VALIDATION_G2.md`
- `docs/github-readiness/HARDWARE_VALIDATION_G3.md`
- `docs/github-readiness/HARDWARE_VALIDATION_G4.md`
- `docs/github-readiness/RELEASE_MANIFEST_G1.md`
- `docs/github-readiness/RELEASE_MANIFEST_G2.md`
- `docs/github-readiness/RELEASE_MANIFEST_G3.md`
- `docs/github-readiness/RELEASE_MANIFEST_G4.md`
- `docs/github-readiness/TEST_AUDIT_REPORT_G1.md`
- `docs/github-readiness/TEST_AUDIT_REPORT_G2.md`
- `docs/github-readiness/TEST_AUDIT_REPORT_G3.md`
- `docs/github-readiness/TEST_AUDIT_REPORT_G4.md`
- `docs/developer-guide/code-quality.md`
- `docs/github-readiness/README.md`
- `docs/README.md`
- `pyproject.toml`
- `tests/test_github_readiness_g7_safe_format_cleanup.py`
- `scripts/verify.sh (mode only: executable bit restored)`
- `scripts/package_release.sh (mode only: executable bit restored)`

## Validation summary

```text
py_compile: passed
render_docs --check: passed
sync_version --check --expected-version 2.9.10: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
G5/G6/G7 GitHub readiness tests: 16 passed
v2.9.10 final release tests: 3 passed
v2.9.10 tests: 189 passed
pytest split aggregate: 959 passed, 12 subtests passed
unittest discover -s tests: 571 tests OK
audit_release --expected-version 2.9.10: PASS 553/553
```

## Limitations

```text
Ruff, Black, and MyPy were not installed in this environment, so they were not run and are not claimed as passed.
A full unsplit pytest run was attempted but timed out before a final summary; the split pytest aggregate is recorded instead.
No new hard coverage percentage is claimed because G7 changed documentation, test hygiene checks, tooling metadata, and executable mode only; runtime modules were not changed.
```

## Outcome

Successful. G7 improves source hygiene and preserves runtime behavior. Hardware validation remains not performed / not claimed.
