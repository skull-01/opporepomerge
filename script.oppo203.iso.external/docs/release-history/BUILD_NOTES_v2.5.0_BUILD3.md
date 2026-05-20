# Build Notes — v2.5.0 Build 3

## Purpose

v2.5.0 Build 3 is the wizard/user-experience message cleanup build in the v2.5 development series. It builds on v2.5.0 Build 2 and preserves the v2.2.0 merge-complete software baseline.

## Planned success rate

- Planned success rate: 90%
- Reason: the build intentionally changes user-facing wizard wording only and avoids playback, hardware-command, OPPO protocol, mount, service, and settings-behavior changes.

## Scope completed

- Added a centralized `WIZARD_TEXT` dictionary in `resources/lib/wizard.py` for active wizard copy.
- Reworded the active wizard welcome, prerequisite, unreachable-player, OPPO jailbreak, AutoScript, Chinoppo preset, Quick Start, startup power-on, Wake-on-LAN, architecture auto-test, playback architecture, and completion messages.
- Improved recovery guidance for unreachable player setup by telling users to check IP address, port, network connection, and IP Control.
- Clarified Quick Start and OPPO-compatible wake/power context.
- Clarified that External Player remains the safest/recommended default.
- Added regression tests proving the copy changed while preserving dialog flow and persisted setting behavior.

## Out of scope

No intentional changes were made to:

- playback flow
- wizard branching order
- persisted setting keys
- OPPO command maps
- TV switching behavior
- HTTP payload behavior
- hardware presets
- Reavon warning-only behavior
- Chinoppo wake rewrite behavior
- service interception behavior

## Verification summary

Build 3 verification evidence is captured in:

- `TEST_AUDIT_REPORT_v2.5.0_BUILD3.md`
- `COVERAGE_REPORT_v2.5.0_BUILD3.md`
- `RELEASE_MANIFEST_v2.5.0_BUILD3.md`

## Next recommended build

v2.5.0 Build 4 should focus on wizard recovery flow only: cancel, retry, partial setup, and rerun safety.
