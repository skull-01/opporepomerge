# Build Notes — v2.9.1 Build 8

## Scope

Build 8 implements settings exception narrowing, phase 1. It is intentionally limited to low-risk parsing paths in `resources/lib/settings_reader.py`.

## Changes

- Added `_setting_text()` to isolate legacy defensive handling for unusual objects whose `__str__` raises.
- Added `_settings_items()` to preserve save fallback behavior for malformed mapping-like settings objects.
- Replaced broad `except Exception` in low-risk numeric and XML parsing paths with narrower exception classes.
- Preserved existing fallback behavior for malformed numeric settings, corrupted `settings.xml`, and invalid firmware strings.

## Behavior preserved

No playback, OPPO command semantics, XML routing, NAS adapter behavior, startup auto-power behavior, packaging semantics, or hardware-control behavior changed.

## Hardware status

No hardware validation was performed or claimed.
