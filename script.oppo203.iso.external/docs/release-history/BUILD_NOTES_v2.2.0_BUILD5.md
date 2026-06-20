# Build Notes — v2.2.0 Build 5

```yaml
addon_version: 2.2.0.5
artifact: script.oppo203.iso.external-2.2.0-build5.zip
baseline: script.oppo203.iso.external-2.2.0-build4.zip
build_role: gradual v1.1.9 + v0.9.14 superset merge slice
scope: wizard/UI compatibility-warning surfacing helpers
coverage_gate: 99 percent enforced
```

## Summary

Build 5 adds a small, testable v0.9.14 wizard/UI compatibility-warning bridge without replacing the active v1.x wizard flow.

## Completed

- Added UI warning surfacing helper.
- Added choice validation helper.
- Added apply-and-surface compatibility bridge.
- Preserved Reavon warning-only behavior.
- Preserved Chinoppo/M9702 clone preset behavior.
- Preserved 99% coverage gate.

## Not done

- Full wizard rewrite was not started.
- Full v1.1.9 + v0.9.14 superset merge remains in progress.
- Real hardware validation was not performed.
