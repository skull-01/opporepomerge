# Release Manifest — v2.5.0 Build 3

- Add-on ID: `script.oppo203.iso.external`
- Add-on version: `2.5.0`
- Build ID: `v2.5.0 Build 3`
- Development series: `v2.5`
- Baseline: `v2.5.0 Build 2` / completed `v2.2.0` software-merge baseline
- Package filename: `script.oppo203.iso.external-2.5.0-build3.zip`

## Build intent

Wizard/user-experience message cleanup only. This build improves wording, guidance, and supportability of the active setup wizard without changing runtime behavior.

## Files intentionally revised

- `resources/lib/wizard.py`
  - Added `WIZARD_TEXT` and `_text()` helper.
  - Replaced inline wizard prompt strings with centralized, clearer copy.
  - Preserved dialog order, setting writes, and branch behavior.

- `tests/test_v250_build3_wizard_messages.py`
  - Added regression tests for clearer wizard copy.
  - Verified full wizard setting writes remain compatible.
  - Verified unreachable-player cancel behavior is preserved.

- `tools/audit_release.py`
  - Added Build 3 evidence files to the release audit requirements.

- Build evidence files added:
  - `BUILD_NOTES_v2.5.0_BUILD3.md`
  - `RELEASE_MANIFEST_v2.5.0_BUILD3.md`
  - `COVERAGE_REPORT_v2.5.0_BUILD3.md`
  - `TEST_AUDIT_REPORT_v2.5.0_BUILD3.md`

## Hardware validation

No hardware validation is claimed in this build. Real hardware validation remains pending and user-owned.
