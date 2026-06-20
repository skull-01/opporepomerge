# v2.9.10 Build 14 — Onkyo / Integra / Pioneer eISCP AVR driver

Build 14 adds guarded Onkyo/Integra/Pioneer eISCP command support behind the disabled-by-default AVR framework while preserving Build 12 Denon/Marantz and Build 13 Yamaha drivers.

Implemented:

- Added `resources/lib/avr_onkyo_eiscp.py`.
- Added valid eISCP frame construction using `ISCP` magic, 16-byte header, version 1, and ASCII payloads.
- Added `!1PWR01` power-on payload helper.
- Added `!1SLIxx` input-selection payload helper with two-hex-character validation.
- Opens and closes a socket per command.
- Uses TCP port `60128` by default.
- Returns non-fatal `AvrResult` objects for timeout, network failure, invalid input, driver error, and malformed response frames.
- Keeps Integra on the same family driver.
- Keeps Pioneer marked experimental/unverified.
- Keeps AVR disabled by default, power-off disabled by default, and volume automation disabled by default.
- Does not hook AVR into playback sequencing.

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV diagnostics, SmartThings guardrails, Roku ECP behavior, Android/Google TV ADB preset metadata, runtime ZIP policy, or hardware-validation status changed.
