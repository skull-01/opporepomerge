# Build Notes — v2.9.1 Build 4

```yaml
build: v2.9.1 Build 4
baseline: script.oppo203.iso.external-2.9.1-build3-dev-source.zip
scope: dynamic audit evidence manifest discovery with legacy fallback
planned_success_rate: 78%
hardware_validation: not_performed_not_claimed
runtime_behavior_change: false
```

## Summary

Build 4 introduces manifest-based release evidence discovery to reduce future growth in `tools/audit_release.py`. The audit now discovers `release-evidence/*/MANIFEST.txt`, requires the manifest file itself, and requires every safe root-relative file listed in each manifest.

The existing legacy hard-coded evidence list remains active as a transition fallback so historical tests and older evidence checks remain stable. Build 4 proves the new manifest path without removing legacy behavior.

## Runtime behavior

No playback, OPPO command-map, service interception, XML routing, NAS playback, startup auto-power, or hardware-control behavior changed.

## Files changed or added

- `tools/audit_release.py`
- `release-evidence/v2.9.1-build4/MANIFEST.txt`
- `tests/test_v291_build4_audit_evidence_manifest.py`
- `addon.xml`
- `README.md`
- `reference.md`
- `web-references.md`
- Build 4 release evidence files

## Hardware validation

Hardware validation was not performed and is not claimed.
