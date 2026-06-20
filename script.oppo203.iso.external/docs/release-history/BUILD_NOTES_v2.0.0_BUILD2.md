# BUILD_NOTES_v2.0.0_BUILD2.md

## Target

Version 2.0.0 Build 2 — MVP compliance hardening for `script.oppo203.iso.external`.

## Baseline

Started from `script.oppo203.iso.external-2.0.0-build1.zip`.

## Main changes

- Bumped `addon.xml` version to `2.0.0.2`.
- Fixed stock OPPO `#POW` pass-through.
- Kept Chinoppo/M9702 `#PON` / `#POW` to `#EJT` rewrite.
- Added optional `tv_switching_enabled` setting.
- Made External Player TV switching deterministic, TV-first, and non-fatal.
- Added ADB runner injection for tests.
- Fixed clean TCP disconnect so it is not treated as playback stop.
- Added fake loopback OPPO TCP server tests.
- Added Slice 2 and Slice 3 notes.
- Updated README, reference, and web-references.

## Test result

`324 / 324 passing`

## Audit result

- Python compile audit: passed.
- `addon.xml`: parsed.
- `resources/settings.xml`: parsed.
- Locale/msgctxt parity: passed across 12 locales.
- Command map: 76 canonical keys; no `#SIS`, `#PGU`, or `#PGD`.
- Hardware enum vs `HARDWARE_COMPAT`: 12 / 12.
- Zip layout: package root contains `script.oppo203.iso.external/`.

## Known deferrals

- Kodi API stubs and 92% coverage gate.
- Physical OPPO validation.
- Physical TCL/Android TV + ADB validation.
- Full v1.3-style superset merge.
