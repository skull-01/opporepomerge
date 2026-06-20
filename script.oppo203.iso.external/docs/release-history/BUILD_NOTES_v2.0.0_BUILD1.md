# Version 2.0.0 Build 1 Notes

## Baseline

- Source baseline: reconstructed v1.x bundle from the combined DevLog / Addon Research handoff.
- Baseline tests before edits: 305 / 305 passing.

## Changes

- Bumped add-on version to `2.0.0`.
- Added v2 MVP build documentation.
- Restored canonical 76-key OPPO command map.
- Added MVP hardware compatibility helpers and 12 canonical hardware compatibility entries.
- Added `oppo_hardware_model` setting.
- Added send-time `#PON` / `#POW` wake resolution for Chinoppo/M9702-style models.
- Removed old architecture-selection settings from the visible Kodi settings UI while keeping internal defaults for compatibility.
- Added regression tests for v2 build metadata, command-map invariants, hardware compatibility, wake rewrite, and settings UI scope.

## Deferred

- Slice 3 TCL/Android TV HDMI hardening.
- Fake OPPO server integration tests.
- Kodi API stubs and 92% coverage gate.
- Full v1.3-style superset merge.

## Final verification in this build session

- Test command: `python -m pytest -q`
- Test result: `311 passed in 0.55s`
- Compile audit: `python -m compileall -q .` passed.
- XML audit: `addon.xml` and `resources/settings.xml` parsed successfully.
- Strings audit: 12 locales, 148 `msgctxt` entries each, balanced `msgctxt` / `msgid` / `msgstr` counts.
- Settings string audit: every numeric settings `label` and `help` ID resolves to a locale string.
- Command-map audit: 76 keys; no `#SIS`, `#PGU`, or `#PGD` in the default command map.
- Hardware audit: `oppo_hardware_model` enum count matches `HARDWARE_COMPAT` count at 12 entries.
