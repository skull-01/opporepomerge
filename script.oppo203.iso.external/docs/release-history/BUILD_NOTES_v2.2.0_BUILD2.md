# Build Notes — v2.2.0 Build 2

addon_version: 2.2.0.2
artifact_name: script.oppo203.iso.external-2.2.0-build2.zip

Build 2 continues the careful v1.1.9 + v0.9.14 superset merge with a narrow hardware-compatibility test-port and audit-hardening slice.

## Changes

- Corrected addon.xml XML declaration to version="1.0".
- Set parsed addon version attribute to 2.2.0.2.
- Hardened release audit so expected version is parsed from the addon XML attribute, not found by substring.
- Removed duplicate JSON output in audit JSON mode.
- Added v0.9.14 hardware regression tests for M9203, M9205C, Reavon variants, jailbreak JSON payload behavior, Quick Start warning behavior, and AutoScript verbose-push warning behavior.

## Scope control

The full historical feature merge was not started in this build.
