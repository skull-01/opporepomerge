# Hardware Support Matrix

This matrix separates software support from real hardware validation.

| Area | Software support | Real hardware validation | Notes |
|---|---:|---:|---|
| Kodi add-on installation | Yes | Pending | Must be tested on real Kodi systems. |
| OPPO UDP-203 / UDP-205 compatible handoff | Yes | Pending | Requires real player testing. |
| Chinoppo / M9205 V1 serial-capable path | Yes | Pending | Only serial-capable hardware should be claimed after tests. |
| Magnetar / Reavon style external-player paths | Software-described | Pending | Must be validated per model. |
| NAS / AutoScript workflow | Yes | Pending | Network environment matters. |
| `playercorefactory.xml` merge | Yes | Pending | Must be tested with real user customization cases. |
| TV control — Android TV / ADB style | Yes | Pending | Backend-specific behavior. |
| TV control — Roku ECP | Yes | Pending | Requires real Roku-compatible device. |
| TV control — command presets | Yes | Pending | Requires target TV/device test. |
| TV control — SmartThings helper | Helper exists | Pending | Do not log tokens. |
| AVR sequencing — Denon/Marantz | Yes | Pending | Failure must not block playback. |
| AVR sequencing — Yamaha YXC | Yes | Pending | Failure must not block playback. |
| AVR sequencing — Onkyo eISCP | Yes | Pending | Failure must not block playback. |
| AVR sequencing — Sony helper/skeleton | Helper/skeleton | Pending | Do not log PSKs. |

## Claim rule

A row may move from `Pending` to `Validated` only after a real hardware report is recorded with model, firmware, connection method, media type, result, and logs/notes.
