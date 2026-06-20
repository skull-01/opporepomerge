# Build Notes — v2.9.10 Build 12

## Scope

Build 12 adds guarded Denon/Marantz Telnet-style AVR command support behind the disabled-by-default Build 11 AVR framework.

Implemented:

- Added `resources/lib/avr_denon_marantz.py`.
- Added `PWON` power-on helper.
- Added `SI<input>` input-selection helper.
- Added `PW?` and `SI?` query helpers.
- Opens and closes a socket per command.
- Uses short timeouts.
- Returns non-fatal `AvrResult` objects for timeouts, network failures, invalid inputs, and unsupported actions.
- Keeps AVR disabled by default.
- Keeps AVR power-off disabled by default.
- Keeps volume automation disabled by default.
- Does not hook AVR into playback sequencing.

## Preserved behavior

No OPPO playback routing, service interception, `playercorefactory.xml`, NAS/AutoScript, OPPO command-map, startup auto-power, TV diagnostics, SmartThings, Roku ECP, Android TV ADB preset, command/custom TV preset, runtime ZIP, or hardware-validation behavior changed.

## Hardware status

No real Denon, Marantz, OPPO, Kodi, TV, NAS, or AVR hardware validation was performed or claimed.
