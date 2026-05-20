# Build Notes — v2.1.0 Build 7

```yaml
addon_version: 2.1.0.7
artifact_name: script.oppo203.iso.external-2.1.0-build7.zip
baseline: script.oppo203.iso.external-2.1.0-build6.zip
build_type: coverage hardening
scope: raw coverage improvement after displayed 99 percent gate
full_superset_merge_started: false
real_hardware_tested: false
coverage_gate: 99 percent
measured_total_coverage: 99 percent
raw_combined_line_branch_coverage: 99.06 percent
```

Build 7 keeps the enforced 99% gate and improves raw combined line+branch coverage above 99% using small behavior-oriented tests. No runtime feature expansion or full merge work is included.

## Changes

- Bumped package identity from `2.1.0.6` to `2.1.0.7`.
- Added Build 7 branch tests for remaining meaningful defensive paths.
- Updated README.md, reference.md, web-references.md, audit tooling, and release evidence.
- Preserved Build 6's 99% enforced gate.

## Known caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
