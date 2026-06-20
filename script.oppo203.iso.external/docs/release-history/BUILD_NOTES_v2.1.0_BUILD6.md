# Build Notes — v2.1.0 Build 6

```yaml
addon_version: 2.1.0.6
artifact: script.oppo203.iso.external-2.1.0-build6.zip
baseline: script.oppo203.iso.external-2.1.0-build5.zip
build_role: final pre-merge coverage hardening step
coverage_gate: 99 percent
feature_scope: no runtime feature expansion; tests and audit/docs only except version metadata
full_merge_status: not started
real_hardware_test_status: not performed
```

## Summary

v2.1.0 Build 6 completes the gradual pre-merge coverage hardening track by raising the enforced `.coveragerc` gate from 98% to 99%.

The build adds targeted tests for meaningful remaining defensive paths:

- no-Kodi import fallbacks for Kodi-bound helper modules;
- AutoScript CIFS generation and wizard branches;
- OPPO response parsing, HTTP track parsing, discovery timeout cleanup, and file-list inference helpers;
- External Player manual-file wait loop behavior;
- OPPO TCP client timeout / OSError cleanup;
- stock OPPO remote power pass-through;
- playercorefactory merge branches and settings XML value fallback.

## Scope control

No full v1.1.9 + v0.9.14 superset merge work was started. No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
