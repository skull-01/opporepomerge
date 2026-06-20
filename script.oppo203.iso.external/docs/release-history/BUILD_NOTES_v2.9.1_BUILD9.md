# Build Notes — v2.9.1 Build 9

## Scope

Build 9 adds a lightweight dependency-free settings schema and typed validation layer. It continues recommendation #6 after Build 8 narrowed low-risk exception handlers.

## Changes

- Added `resources/lib/settings_schema.py`.
- Exposed `SETTINGS_SCHEMA`, `Settings.schema_issues()`, and `Settings.typed_values()` from `resources/lib/settings_reader.py`.
- Updated `validation_summary()` to include schema issue metadata while preserving legacy summary keys.
- Added Build 9 regression tests for invalid integers/floats/booleans/enums and typed coercion.

## Runtime behavior

No playback behavior, OPPO command semantics, XML routing, NAS playback, startup auto-power behavior, or hardware-control behavior changed. The schema is advisory and non-mutating. Existing getter fallbacks remain active.

## Hardware validation

Not performed and not claimed.
