# Build Notes — v2.2.0 Build 7

```yaml
addon_version: 2.2.0.7
package: script.oppo203.iso.external-2.2.0-build7.zip
baseline: script.oppo203.iso.external-2.2.0-build6.zip
merge_scope: service watcher persistence edge-case hardening
coverage_gate: 99 percent
```

## Summary

Build 7 keeps the v1.1.9 + v0.9.14 superset merge gradual by hardening service watcher persistence edge cases.

## Stability notes

- Empty add-on-data directories no longer write `settings.xml` beside the current working directory.
- Service watcher save failures are logged and do not block settings changes.
- In-memory clone preset behavior remains available when persistence is unavailable.
- Stock OPPO jailbreak JSON payload persistence is verified.
- Reavon remains warning-only.
- No real hardware was tested.
