# Release Manifest — v2.1.0 Build 6

```yaml
addon_version: 2.1.0.6
artifact: script.oppo203.iso.external-2.1.0-build6.zip
checksum_file: script.oppo203.iso.external-2.1.0-build6.sha256
baseline: script.oppo203.iso.external-2.1.0-build5.zip
coverage_gate: 99 percent
measured_coverage: 99 percent display / 98.77 percent raw combined line+branch coverage
full_merge_started: false
real_hardware_tested: false
```

## Required verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.1.0.6
```
