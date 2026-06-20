# Version 2.0.0 Build 4 - MVP release-candidate hardening

Build 4 continues from Build 3 after the user-reported/manual hardware-validation milestone. For this build, the hardware result is recorded as an accepted project assumption: the latest build was tested against the real hardware path and no issues were found. This build does not claim that the automated environment reproduced that physical OPPO/M9702/TCL/Android TV test; it records the manual validation result and tightens release packaging around it.

## Goal

Prepare the v2 MVP line for a release-candidate style review by closing the packaging/documentation gap found after unpacking Build 3 and by making MVP compliance visible in the source tree.

## Changes

- Bumped `addon.xml` to `2.0.0.4`.
- Restored `.coveragerc` to the packaged source tree. Build 3 packaging omitted this hidden file, which caused a post-unpack test failure even though the source workspace had passed.
- Added `HARDWARE_VALIDATION_v2.0.0_BUILD4.md` to record the assumed manual hardware pass.
- Added `MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md` to show what is complete, what is staged, and what remains deferred.
- Added release-artifact tests so the build notes, hardware-validation note, MVP matrix, docs, and version bump are checked automatically.
- Updated `README.md`, `reference.md`, and `web-references.md`.

## Test and audit result

- Unit tests: `337 / 337 passing`.
- Python compile audit: passed.
- `addon.xml` parse: passed.
- `resources/settings.xml` parse: passed.
- Locale parity: 12 locale files with matching msgctxt sets.
- Settings label/help coverage: passed.
- Command map audit: 76 canonical keys; no `#SIS`, no `#PGU`, no `#PGD`.
- Hardware audit: `oppo_hardware_model` enum count matches `HARDWARE_COMPAT` count at 12.
- Package layout audit: clean root folder; `.coveragerc` included; no `__pycache__`, `.pyc`, `.coverage`, or `.pytest_cache`.

## Manual hardware validation status

Accepted as user-provided project input for this build:

```text
Latest build tested on real hardware.
No issues found.
```

This unblocks release-candidate style hardening, but does not remove the need to re-run manual validation after any future change that touches OPPO control, ADB/TV switching, settings, packaging, or Kodi runtime behavior.

## Known staged item

The final 92% coverage gate remains staged. `.coveragerc` is restored with the historical 85% target so CI/scaffolding remains honest, while the workflow still treats coverage as a report until the remaining Kodi-bound modules have enough stub-backed tests for a fair hard gate.
