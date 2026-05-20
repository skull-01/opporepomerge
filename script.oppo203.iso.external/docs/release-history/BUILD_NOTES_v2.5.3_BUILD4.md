# Build Notes — v2.5.3 Build 4

```yaml
addon_version: 2.5.3
build: v2.5.3 Build 4
baseline: script.oppo203.iso.external-2.5.3-build3.zip / dev-source
scope: playercorefactory.xml merge, backup, idempotency, and rollback hardening
runtime_behavior_change: true_limited_to_xml_helper_safety
hardware_validation: not_performed
```

## Summary

Build 4 hardens the playercorefactory merge helper after Build 2 introduced conservative Option 4 installer XML rules and Build 3 reconciled version identity.

## Changes

- Aligned `resources/lib/playercorefactory_merge.py` with the Option 4 rule model.
- Generated helper snippets now emit three tag-aware rules only: `iso`, `bdmv`, and `mpls`.
- The helper no longer emits broad legacy `iso|bdmv|m2ts` routing.
- Merge behavior remains idempotent and deduplicates player/rule entries by name.
- Existing `playercorefactory.xml` files are backed up before writes.
- Write failure and post-write XML validation failure now trigger best-effort rollback to the backed-up/original file.
- Added regression tests for Option 4 helper rules, backup, idempotency, write-failure rollback, validation-failure rollback, audit evidence, and runtime ZIP cleanliness.

## Preserved behavior

- Build 1 precise Python service interception remains unchanged.
- Build 2 installer/wizard naming discipline warning remains unchanged.
- Build 3 `addon.xml` version identity remains `2.5.3`.
- Loose/raw video formats remain excluded from XML routing.
- Runtime ZIP remains runtime-only.

## Hardware status

No OPPO, Chinoppo/M9702, Kodi installation, NAS, TV switching, or ADB hardware validation was performed. Hardware validation remains user-owned.
