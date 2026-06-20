# Release Manifest — v2.1.0 Build 7

```yaml
addon_version: 2.1.0.7
artifact_name: script.oppo203.iso.external-2.1.0-build7.zip
checksum_name: script.oppo203.iso.external-2.1.0-build7.sha256
baseline: script.oppo203.iso.external-2.1.0-build6.zip
coverage_gate: 99 percent
measured_total_coverage: 99 percent
raw_combined_line_branch_coverage: 99.06 percent
release_audit_expected_version: 2.1.0.7
full_superset_merge_started: false
real_hardware_tested: false
```

## Required verification

- `python -m pytest -q`
- `python -m unittest discover -s tests`
- `python -m coverage run -m pytest -q`
- `python -m coverage report -m`
- `python tools/audit_release.py --expected-version 2.1.0.7`
