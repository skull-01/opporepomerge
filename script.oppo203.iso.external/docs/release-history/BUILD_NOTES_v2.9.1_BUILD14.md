# Build Notes — v2.9.1 Build 14

```yaml
build_id: v2.9.1 Build 14
baseline: script.oppo203.iso.external-2.9.1-build13-dev-source.zip
scope: test naming/layout standardization transition
planned_success_rate: 86 percent
actual_outcome: successful
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Summary

Build 14 implements the cleanup-roadmap item for test naming/layout standardization. It does not mass-move historical tests. Instead, it introduces a transition-safe policy and local tooling:

- `tools/test_layout.py` classifies existing legacy flat tests, support paths, and future version/build test paths.
- `pytest.ini` declares `version(...)`, `build(...)`, and `legacy_layout` markers.
- `docs/test-layout.md` documents the future layout.
- `scripts/verify.sh` runs the layout check.

## Issues found and fixes

Inherited metadata regression tests still protected earlier build phrases. Build 14 preserved those phrases in `addon.xml`, including references to the v2.9 release lineage, command-map JSON path, audit manifest pattern, automation scripts, docs metadata/rendering tools, typed audit checks, and JSON reporter support.

No playback, OPPO command-map, XML routing, NAS, settings runtime, startup power, or hardware-control behavior changed.
