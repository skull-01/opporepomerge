# Build Notes — v2.1.0 Build 4

```yaml
artifact: script.oppo203.iso.external-2.1.0-build4.zip
addon_version: 2.1.0.4
baseline: script.oppo203.iso.external-2.1.0-build3.zip
scope: gradual pre-merge coverage hardening
coverage_gate: fail_under = 97
measured_coverage: 97%
full_merge_started: false
real_hardware_tested: false
```

## Summary

Build 4 continues the gradual 99% pre-merge hardening track. It raises the enforced total `resources/lib` coverage gate from 96% to 97% while keeping the change set limited to tests, release documentation, audit evidence, and version identity.

## Coverage work

Added targeted tests for meaningful defensive paths in installer dialogs, discovery previews, TCL preset application, experimental file-list diagnostic display limits, OPPO HTTP track helpers, file-list parser edges, verbose-push timeout behavior, preflight failure handling, OPPO TCP-client timeout/cleanup branches, and preset-manager custom preset loading.

## Scope guard

The full v1.1.9 + v0.9.14 merge was not started. No real hardware validation was performed.
