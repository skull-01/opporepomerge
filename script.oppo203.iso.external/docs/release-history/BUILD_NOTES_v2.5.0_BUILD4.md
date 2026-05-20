# Build Notes — v2.5.0 Build 4

## Purpose

v2.5.0 Build 4 is the wizard recovery-flow build in the v2.5 development series. It builds on v2.5.0 Build 3 and preserves the completed v2.2.0 software-merge baseline.

## Planned success rate

- Planned success rate: 80%
- Reason: the build touches active wizard control flow, but the implementation is intentionally additive and limited to recovery metadata for cancel, retry, partial setup, and rerun support.

## Scope completed

- Added additive wizard recovery metadata keys:
  - `wizard_in_progress`
  - `wizard_last_exit`
  - `wizard_last_step`
  - `wizard_recovery_available`
- Added conservative helpers for wizard started, step, cancelled, error, and completed states.
- Added `wizard_recovery_summary()` for support/debug visibility of partial setup states.
- Preserved prior completed configuration when a user reruns the wizard and cancels before completion.
- Ensured first-run cancellation does not claim wizard completion.
- Ensured successful retry clears prior partial/cancelled recovery markers.
- Ensured unexpected wizard exceptions mark recovery metadata before re-raising to existing error handling.
- Added regression tests for cancel, retry, rerun, partial setup, and error recovery states.

## Out of scope

No intentional changes were made to:

- playback flow
- OPPO command behavior
- TV switching behavior
- HTTP payload behavior
- hardware presets
- Reavon warning-only behavior
- Chinoppo wake rewrite behavior
- service interception behavior
- wizard message text from Build 3, except where step tracking required metadata updates

## Verification summary

Build 4 verification evidence is captured in:

- `TEST_AUDIT_REPORT_v2.5.0_BUILD4.md`
- `COVERAGE_REPORT_v2.5.0_BUILD4.md`
- `RELEASE_MANIFEST_v2.5.0_BUILD4.md`

## Next recommended build

v2.5.0 Build 5 should focus on diagnostic logging standardization only: consistent prefixes and clearer support logging without changing playback or wizard behavior.
