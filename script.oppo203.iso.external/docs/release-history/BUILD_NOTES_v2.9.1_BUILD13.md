# Build Notes — v2.9.1 Build 13

## Scope

Build 13 adds a non-blocking type-check baseline and selected type hints for public helper surfaces. It is intentionally advisory: mypy is not a required runtime dependency and missing mypy does not block release verification.

## Changes

- Added `tools/type_check.py`, a dependency-optional mypy wrapper.
- Added `mypy.ini` for a future type-check baseline.
- Added type hints to selected public helpers in `resources/lib/intercept.py` and `tools/package_installable_zip.py`.
- Updated `scripts/verify.sh` so type checking is reported in local verification without making release validation fail when mypy is unavailable.
- Added Build 13 tests and release evidence.

## Runtime behavior

No playback, OPPO control, XML routing, NAS adapter, startup power, settings semantics, or packaging behavior changed.

## Hardware validation

No hardware validation was performed or claimed.
