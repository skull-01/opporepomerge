# Build Notes — v2.9.1 Build 16

## Scope

Build 16 implements i18n extraction legacy alias hardening. It keeps `tools/make_pot.py` for compatibility, marks it as a legacy alias, and makes `tools/i18n_extract.py` the preferred facade for new automation.

## Changes

- Added explicit legacy alias metadata and notice to `tools/make_pot.py`.
- Added `legacy_alias_policy()` to `tools/i18n_extract.py`.
- Updated verification/documentation/evidence metadata to Build 16.
- Added Build 16 regression tests.

## Preserved behavior

No playback, OPPO command semantics, service interception, XML routing, NAS adapter behavior, startup auto-power behavior, settings runtime behavior, packaging semantics, or hardware-control behavior changed.

## Hardware validation

Not performed and not claimed.
