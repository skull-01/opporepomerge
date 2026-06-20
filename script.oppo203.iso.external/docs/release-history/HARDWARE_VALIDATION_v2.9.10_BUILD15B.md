# v2.9.10 Build 15B — Sony AVR experimental request helper and fake API tests

Project: script.oppo203.iso.external
Baseline: script.oppo203.iso.external-2.9.10-build15a-dev-source.zip
Hardware validation: not performed / not claimed
Runtime behavior changed: No OPPO playback/routing behavior changed
AVR playback sequencing hook: not added

Build 15B adds a guarded Sony Audio Control API JSON POST request helper behind the existing disabled-by-default AVR framework. The helper requires explicit experimental acknowledgement before any request is sent, is fakeable for tests, returns nonfatal AvrResult objects for API/network/JSON/error paths, and never exports Sony PSKs, passwords, credentials, tokens, or secrets.

Preserved behavior: OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, TV diagnostics/dry-run behavior, SmartThings experimental guardrails, Roku ECP, Android/Google TV presets, command/custom TV presets, Denon/Marantz, Yamaha, Onkyo/Integra/Pioneer AVR behavior, and no hardware-validation claim.

## Hardware validation

No real Sony AVR, OPPO, Chinoppo, Kodi, NAS, TV, Roku, SmartThings, or AVR hardware validation was performed or claimed.
