# Build Notes — v2.5.3 Build 6

```yaml
addon_version: 2.5.3
package: script.oppo203.iso.external-2.5.3-build6.zip
baseline: script.oppo203.iso.external-2.5.3-build5.zip
build_role: pre-hardware release-candidate packaging freeze
runtime_behavior_changed: false
hardware_validation_claimed: false
```

## Summary

Build 6 freezes the verified v2.5.3 software line as a pre-hardware release candidate. It is intentionally a packaging/evidence build. No playback path, OPPO command-map behavior, service interception behavior, Option 4 XML routing behavior, NAS playback adapter behavior, startup-power behavior, or hardware-control behavior changed.

## Preserved software baseline

- Build 1: precise Python classifier for tagged 4K/UHD/2160p disc-style service interception.
- Build 2: conservative Option 4 `playercorefactory.xml` rules and naming-convention warning.
- Build 3: `addon.xml` version identity reconciled to `2.5.3`.
- Build 4: `playercorefactory.xml` merge, backup, idempotency, and rollback hardening.
- Build 5: hardware-validation readiness checklist and diagnostic export.

## Build 6 changes

- Updated add-on metadata to identify Build 6 as the pre-hardware release-candidate packaging freeze.
- Added Build 6 release/evidence files.
- Added `PRE_HARDWARE_AUDIT_REPORT_v2.5.3_BUILD6.md`.
- Updated release audit requirements to require Build 6 evidence.
- Added Build 6 regression tests for freeze posture, evidence, audit, and runtime ZIP cleanliness.
- Updated README, reference, web-references, and AI handoff reconstruction.

## Hardware status

No real OPPO UDP-203/205, Chinoppo/M9702-family player, Kodi installation, NAS path mapping, TV/ADB switching, or external-player hardware path was tested in this build. Build 6 is software-verified and ready for user-owned hardware validation; it is not a hardware-validated final release.
