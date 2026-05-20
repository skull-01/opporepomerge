# Build Notes — v2.1.0 Build 5

```yaml
artifact: script.oppo203.iso.external-2.1.0-build5.zip
addon_version: 2.1.0.5
baseline: script.oppo203.iso.external-2.1.0-build4.zip
build_role: gradual pre-merge coverage hardening
coverage_gate: 98%
measured_coverage: 98%
merge_status: full v1.1.9 + v0.9.14 superset merge not started
```

## Summary

Build 5 raises the enforced coverage gate from 97% to 98% as the next gradual step toward the pre-merge 99% target.

The build adds edge-path tests for OPPO protocol response parsing, multicast discovery cleanup, external-player cleanup and hold-mode behavior, installer error/dispatch branches, settings parsing, log rotation/format fallback, and playercorefactory merge deduplication.

## Scope control

No runtime feature expansion was performed. No full-merge work was started.

## Hardware status

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested for this build.
