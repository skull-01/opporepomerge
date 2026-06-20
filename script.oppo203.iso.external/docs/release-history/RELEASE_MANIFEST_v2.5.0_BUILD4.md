# Release Manifest — v2.5.0 Build 4

- Add-on ID: `script.oppo203.iso.external`
- Add-on version: `2.5.0`
- Build ID: `v2.5.0 Build 4`
- Development series: `v2.5`
- Baseline: `v2.5.0 Build 3` / completed `v2.2.0` software-merge baseline
- Package filename: `script.oppo203.iso.external-2.5.0-build4.zip`

## Build intent

Wizard recovery flow only. This build makes cancelled, retried, partial, and rerun setup states safer to diagnose without changing playback, hardware command, or OPPO protocol behavior.

## Files intentionally revised

- `resources/lib/wizard.py`
  - Added additive recovery metadata helpers.
  - Added step tracking for active wizard phases.
  - Preserved prior completed state when a rerun is cancelled.
  - Marked first-run cancellation as incomplete.
  - Marked error state before re-raising unexpected exceptions.
  - Added `wizard_recovery_summary()` support helper.

- `tests/test_v250_build4_wizard_recovery.py`
  - Added regression tests for prerequisite cancellation.
  - Added regression tests for unreachable-player cancellation during rerun.
  - Added regression tests for successful retry clearing partial state.
  - Added regression tests for exception recovery metadata.
  - Added regression tests for recovery summary output.

- `tools/audit_release.py`
  - Added Build 4 evidence files to release audit requirements.

- Build evidence files added:
  - `BUILD_NOTES_v2.5.0_BUILD4.md`
  - `RELEASE_MANIFEST_v2.5.0_BUILD4.md`
  - `COVERAGE_REPORT_v2.5.0_BUILD4.md`
  - `TEST_AUDIT_REPORT_v2.5.0_BUILD4.md`

## Hardware validation

No hardware validation is claimed in this build. Real hardware validation remains pending and user-owned.
