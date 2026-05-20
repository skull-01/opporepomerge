# Build Notes — v2.5.0 Build 1

Version: 2.5.0
Baseline: v2.2.0 release package (`script.oppo203.iso.external-2.2.0.zip`)
Role: initial v2.5 development-series baseline.

## Planned build success rate

Estimated planned-build success rate: 95%
Confidence level: High
Reasoning for estimate: Build 1 is intentionally limited to version metadata, release documentation, v2.5 planning/tracking sections, audit awareness, packaging, and verification. No runtime behavior changes were planned.
Main success factors: v2.2.0 was already verified; scope is narrow; verification commands are known; no hardware-facing logic is changed.
Main risk factors: reconstruction or packaging mistakes; timeout behavior during test/coverage; tests that intentionally assert the current add-on version must be updated to 2.5.0.
Segmentation decision: proceed as one build.

## Summary

Build 1 starts the v2.5 development series from the completed v2.2.0 software-merge baseline. The purpose is to establish the new active cycle without introducing risky feature or runtime changes.

## Scope completed

- Bumped `addon.xml` version from `2.2.0` to `2.5.0`.
- Updated add-on metadata summary/description to identify the v2.5.0 Build 1 baseline.
- Added v2.5 roadmap documentation focused on stability-first enhancement, wizard/user experience refinement, and diagnostics/supportability.
- Added a hardware-validation findings tracker for user test results.
- Added v2.5 Build 1 release manifest, coverage report placeholder/final record, and test/audit report.
- Updated release audit required-file coverage so v2.5 Build 1 evidence is preserved.
- Updated current-version tests and audit calls to expect `2.5.0`.

## Runtime behavior

No runtime behavior was intentionally changed. Playback flow, OPPO command behavior, command-map invariants, Reavon warning-only behavior, Chinoppo wake rewrite, service watcher behavior, and wizard logic are preserved from v2.2.0.

## Hardware validation status

Real OPPO / Chinoppo / TCL / Android TV / ADB hardware validation was not performed by the AI. Hardware validation remains user-owned and should be recorded in `HARDWARE_VALIDATION_TRACKER_v2.5.0.md`.

## Verification commands

```bash
python -m pytest -q -p no:ddtrace
python -m unittest discover -s tests -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
python tools/audit_release.py --expected-version 2.5.0
```
