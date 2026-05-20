# Release Manifest — v2.1.0 Build 2

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.1.0.2
artifact_name: script.oppo203.iso.external-2.1.0-build2.zip
checksum_name: script.oppo203.iso.external-2.1.0-build2.sha256
baseline_artifact: script.oppo203.iso.external-2.1.0-build1.zip
coverage_gate: 94
measured_coverage: 94%
expected_test_count_before_packaging: 392
real_hardware_validation: not claimed
```

## Required verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.1.0.2
```
