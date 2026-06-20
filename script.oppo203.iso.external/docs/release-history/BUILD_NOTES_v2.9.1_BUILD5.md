# Build Notes — v2.9.1 Build 5

```yaml
build: v2.9.1 Build 5
baseline: script.oppo203.iso.external-2.9.1-build4-dev-source.zip
scope: version single source of truth
planned_success_rate: 82%
hardware_validation: not_performed_not_claimed
runtime_behavior_change: false
```

## Summary

Build 5 introduces `resources/lib/version.py` as the Python source of truth for add-on release identity and `tools/sync_version.py` as a local helper to check or write `addon.xml` from that source.

The release audit now imports the version source and verifies that `addon.xml`, `resources/lib/version.py`, and the optional `--expected-version` argument agree. This prevents the version drift that previously required manual test/audit reconciliation.

## Runtime behavior

No playback, OPPO command-map, service interception, XML routing, NAS playback, startup auto-power, or hardware-control behavior changed.

## Files changed or added

- `resources/lib/version.py`
- `tools/sync_version.py`
- `tools/audit_release.py`
- `release-evidence/v2.9.1-build5/MANIFEST.txt`
- `tests/test_v291_build5_version_source.py`
- `addon.xml`
- `README.md`
- `reference.md`
- `web-references.md`
- Build 5 release evidence files

## Hardware validation

Hardware validation was not performed and is not claimed.
