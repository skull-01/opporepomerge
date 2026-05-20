# v2.9.10 Build 16 — AVR wizard, diagnostics, and safety UI

v2.9.10 Build 16 adds AVR setup UI helpers, query-only AVR test actions, explicit user-action gates for power/input tests, sanitized AVR diagnostic export, and safety wording. AVR support remains disabled by default, AVR power-off and volume automation remain disabled by default, no AVR playback sequencing hook is added, diagnostics sanitize credentials and state hardware_validation_claimed=false, and hardware validation is not claimed.

| Area | Build 16 status | Hardware validation |
|---|---|---|
| OPPO/external-player routing | Preserved | Not claimed |
| TV diagnostics / SmartThings / Roku / ADB / command presets | Preserved | Not claimed |
| Denon/Marantz AVR | Build 12 software driver preserved | Not claimed |
| Yamaha AVR | Build 13 software driver preserved | Not claimed |
| Onkyo/Integra/Pioneer AVR | Build 14 software driver preserved; Pioneer experimental | Not claimed |
| Sony AVR | Build 15A/15B experimental guarded helper preserved | Not claimed |
| AVR wizard/diagnostics | Build 16 metadata/UI helpers and sanitized diagnostics | Not claimed |
| Playback sequencing | Not hooked in Build 16 | Not claimed |
