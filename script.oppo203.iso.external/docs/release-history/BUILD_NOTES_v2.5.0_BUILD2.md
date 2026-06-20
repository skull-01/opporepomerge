# Build Notes — v2.5.0 Build 2

## Purpose

v2.5.0 Build 2 is the first stability-guardrail build in the v2.5 development series. It builds on v2.5.0 Build 1 and preserves the v2.2.0 merge-complete software baseline.

## Planned success rate

85%.

The scope intentionally remained narrow because this build touches shared settings-reading code used by service, external-player, wizard, installer, and tests.

## Implemented changes

- Added conservative `Settings.get_int()` helper with safe fallback and optional clamping.
- Added conservative `Settings.get_float()` helper with safe fallback and optional clamping.
- Added `Settings.get_path()` helper for normalized path-like values without requiring the path to exist.
- Added `Settings.validate_required()` helper for detecting explicit blank/missing configuration values.
- Added `Settings.validation_summary()` helper for non-throwing partial-setup/configuration status.
- Hardened `read_settings()` so corrupt or partially written `settings.xml` recovers to defaults and records `_settings_read_error` instead of propagating parser failure.
- Added targeted regression tests in `tests/test_v250_build2_stability.py`.

## Runtime behavior impact

This build is conservative. It does not change playback flow, wizard flow, OPPO command behavior, TV switching, HTTP payload behavior, hardware presets, or service-interception architecture.

The only active runtime hardening is that corrupt or partial `settings.xml` now falls back to defaults with a diagnostic marker instead of forcing broad caller-level exception behavior.

## Verification summary

- Targeted pytest: 5 passed.
- Full pytest: 544 passed, 12 subtests passed.
- Unittest discovery: 544 tests OK.
- Coverage: TOTAL 99%.
- Release audit: PASS after Build 2 evidence files were added.

## Remaining work

Recommended next build: v2.5.0 Build 3 — wizard message cleanup, with behavior unchanged.
