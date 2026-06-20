# v2.5.0 Build 7 — Combined Regression and Packaging Candidate

## Purpose

Build 7 is the combined regression and packaging candidate for the v2.5.0 development series after Builds 1 through 6.

This build intentionally does not introduce new runtime behavior. Its purpose is to package the accumulated v2.5 stability, wizard/user-experience, and diagnostics work into a candidate artifact and verify that the combined source tree remains stable.

## Planned success rate

- Planned success rate: 85%
- Rationale: Build 7 is primarily packaging, release evidence, audit, and regression verification. No new playback, wizard branch, OPPO command, TV switching, HTTP payload, hardware preset, or service-interception behavior is intended.

## Scope

- Preserve the v2.5.0 Build 6 source behavior.
- Add Build 7 release-evidence files.
- Add a lightweight packaging-candidate regression test for release evidence and addon metadata.
- Update release audit expectations to include Build 7 evidence.
- Package the candidate zip.
- Run source-tree and post-unpack verification.
- Update the handoff and audited release/feature tracking table.

## Behavior changes

No runtime behavior changes were intentionally introduced. None intended.

## Explicitly preserved behavior

- playback flow
- wizard branch order
- OPPO command behavior
- TV switching behavior
- HTTP payload behavior
- hardware presets
- Reavon warning-only behavior
- Chinoppo wake rewrite behavior
- service interception behavior
- persisted setting semantics
- Build 6 diagnostic summary helper behavior

## Verification summary

Final verification results are recorded in `TEST_AUDIT_REPORT_v2.5.0_BUILD7.md` and `COVERAGE_REPORT_v2.5.0_BUILD7.md`.

## Hardware validation

Real hardware validation remains pending and user-owned.
