# Build Notes — v2.5.3 Build 5

```yaml
addon_version: 2.5.3
build: v2.5.3 Build 5
artifact: script.oppo203.iso.external-2.5.3-build5.zip
baseline: script.oppo203.iso.external-2.5.3-build4.zip
scope: hardware-validation readiness checklist and diagnostic export
runtime_behavior_change: diagnostic_export_only
hardware_validation_claimed: false
```

## Summary

Build 5 adds a non-invasive hardware-validation readiness helper and export path. It prepares a consistent tester checklist and diagnostic report for real OPPO/Chinoppo/Kodi/NAS/TV/ADB validation while preserving all playback behavior from Builds 1–4.

## Changes

- Added `resources/lib/hardware_validation_readiness.py`.
- Added a Kodi installer menu action to export a hardware-validation readiness report.
- The report includes setup summary, NAS/AutoScript capability gate, Option 4 XML positive/negative test reminders, required tester-result fields, warnings, and blockers.
- Added Build 5 tests for non-claiming report behavior, Reavon warning-only blocker handling, report export, installer action exposure, audit evidence, and runtime ZIP policy.
- Updated README, reference, web-references, release evidence, and handoff reconstruction.

## Safety boundaries

- No OPPO/Chinoppo/TCL/ADB hardware is contacted by the readiness helper.
- No playback handoff behavior changes.
- No settings mutation except writing the exported text report when the user runs the export action.
- No hardware validation pass is claimed.

## Hardware status

Hardware validation remains pending and user-owned. Build 5 only makes tester evidence collection more repeatable.
