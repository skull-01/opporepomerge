# Build Notes — v2.2.0 Build 6

```yaml
addon_version: 2.2.0.6
package: script.oppo203.iso.external-2.2.0-build6.zip
baseline: script.oppo203.iso.external-2.2.0-build5.zip
merge_scope: active wizard compatibility-warning integration
coverage_gate: 99 percent
```

## Summary

Build 6 wires the v0.9.14 compatibility-warning surfacing helpers into one active v1.x wizard hardware-selection path. It intentionally avoids replacing the wizard flow or auto-applying presets.

## Stability notes

- Reavon remains warning-only.
- Reavon command maps are not mutated.
- Chinoppo/M9702 preset behavior remains controlled by the existing confirmation flow.
- Import failures in the compatibility warning helper are non-fatal.
- No real hardware was tested.
