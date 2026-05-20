# Release Manifest — v2.1.0 Build 1

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.1.0.1
artifact_name: script.oppo203.iso.external-2.1.0-build1.zip
checksum_name: script.oppo203.iso.external-2.1.0-build1.sha256
baseline: script.oppo203.iso.external-2.0.0.zip
coverage_gate: 92 percent
real_hardware_validation: deferred until after full merge
```

## Required verification commands

```text
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.1.0.1
```

## Included evidence

- `BUILD_NOTES_v2.1.0_BUILD1.md`
- `RELEASE_MANIFEST_v2.1.0_BUILD1.md`
- `COVERAGE_REPORT_v2.1.0_BUILD1.md`
- Updated AI handoff: `Combined_DevLog_and_Addon_Research_v7_Handoff.md`
