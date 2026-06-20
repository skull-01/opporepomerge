# v2.9.10 Build 13 — Yamaha MusicCast / YXC AVR driver

Build 13 adds guarded Yamaha MusicCast/YXC HTTP command support behind the disabled-by-default AVR framework from Build 11 and while preserving the Build 12 Denon/Marantz driver.

Implemented:

- Added `resources/lib/avr_yamaha.py`.
- Added HTTP GET helpers for `/YamahaExtendedControl/v1/main/setPower?power=on`, `/YamahaExtendedControl/v1/main/setInput?input=<input>`, and `/YamahaExtendedControl/v1/main/getStatus`.
- Parses JSON `response_code` values.
- Returns non-fatal `AvrResult` objects for non-zero response codes, invalid JSON, timeout, network failure, invalid input, and unsupported actions.
- Keeps AVR disabled by default.
- Keeps AVR power-off disabled by default.
- Keeps volume automation disabled by default.
- Does not hook AVR into playback sequencing.

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV diagnostics, SmartThings guardrails, Roku ECP behavior, Android/Google TV ADB preset metadata, runtime ZIP policy, or hardware-validation status changed.
