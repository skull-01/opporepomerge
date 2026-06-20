# Build Notes — v2.2.0 Build 9

```yaml
build: v2.2.0 Build 9
addon_version: 2.2.0.9
baseline: script.oppo203.iso.external-2.2.0-build8.zip
scope: gradual v1.1.9 + v0.9.14 superset-merge parity audit slice
coverage_gate: 99 percent enforced
full_merge_status: in_progress_not_complete
```

## Summary

Build 9 keeps the merge gradual and stability-focused.  It does not broaden runtime feature scope.  It converts the Build 8 checkpoint into a more explicit test-parity audit slice so the next AI can distinguish behavior already protected by tests from remaining merge work.

## Changes

- Added `MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md`.
- Added Build 9 evidence files and audit requirements.
- Added tests that verify the Build 9 parity audit records completed coverage, remaining gaps, non-goals, and the self-contained handoff requirement.
- Bumped add-on identity to `2.2.0.9`.
- Preserved the 99% coverage gate.
- Did not mutate Reavon command maps.
- Did not start a broad/full merge.

## Known caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
