# Build Notes — v2.2.0 Build 8

```yaml
addon_version: 2.2.0.8
artifact: script.oppo203.iso.external-2.2.0-build8.zip
baseline: script.oppo203.iso.external-2.2.0-build7.zip
build_type: gradual_superset_merge_checkpoint
coverage_gate: 99 percent enforced
```

## Summary

Build 8 continues the careful v1.1.9 + v0.9.14 superset merge with a merge-parity audit checkpoint. It also changes the AI-handoff requirement going forward: the latest handoff Markdown must contain a copy/paste resume prompt at the top and a reconstruction bundle for the latest source tree so a future AI can resume from the Markdown alone.

## What changed

- Bumped add-on version to `2.2.0.8`.
- Added `MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md`.
- Added tests that verify the Build 8 merge-parity audit and latest-handoff reconstruction requirement are recorded.
- Updated release audit required evidence for Build 8.
- Updated README, reference, and web-references.

## What did not change

- No broad/full merge was started.
- No Reavon command maps were added.
- No real hardware testing was claimed.
- The 99 percent coverage gate remains enforced.
