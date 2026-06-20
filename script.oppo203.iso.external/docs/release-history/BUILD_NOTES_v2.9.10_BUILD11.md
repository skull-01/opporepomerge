# v2.9.10 Build 11 — AVR framework and settings skeleton

## Result

Build 11 adds a generic AVR framework and settings skeleton while keeping AVR control disabled by default. It does not implement brand command execution and does not hook AVR control into playback sequencing.

## Implemented

- Added `resources/lib/avr_types.py` for non-fatal AVR result and validation containers.
- Added `resources/lib/avr_presets.py` for metadata-only AVR family preset lookup.
- Added `resources/lib/avr_control.py` for disabled-by-default validation and controller factory behavior.
- Added AVR settings placeholders for enabled state, backend, host, port, player input, restore input, optional power flags, and sound mode metadata.
- Added Build 11 regression tests.

## Safety stance

- `avr_control_enabled=false` by default.
- `avr_power_off_enabled=false` by default.
- `avr_volume_automation_enabled=false` by default.
- No Denon/Marantz, Yamaha, Onkyo/Integra/Pioneer, or Sony AVR command execution is implemented.
- No AVR playback sequencing hook is implemented.
- Hardware validation is not performed or claimed.
