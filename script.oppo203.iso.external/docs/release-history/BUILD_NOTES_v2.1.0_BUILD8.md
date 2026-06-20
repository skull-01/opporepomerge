# Build Notes — v2.1.0 Build 8

```yaml
addon_version: 2.1.0.8
artifact: script.oppo203.iso.external-2.1.0-build8.zip
baseline: script.oppo203.iso.external-2.1.0-build7.zip
scope: additional raw 99 percent coverage hardening
full_merge_started: false
real_hardware_tested: false
coverage_gate: 99
measured_coverage_display: 99%
raw_combined_line_branch_coverage: 99.44%
```

## Summary

Build 8 keeps the existing 99% coverage gate and improves the raw combined line+branch percentage from Build 7. The build adds behavior-oriented tests for remaining meaningful branches in external-player entrypoint handling, intercept filtering, logging rotation, OPPO control defensive helpers, TCP partial-buffer handling, playercorefactory merge edges, preset/settings parsing, and wizard full-mode WoL behavior.

No runtime feature expansion or full superset merge work was performed.

## Known caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
