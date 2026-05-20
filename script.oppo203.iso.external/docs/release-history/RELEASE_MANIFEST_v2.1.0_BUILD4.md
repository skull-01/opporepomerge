# Release Manifest — v2.1.0 Build 4

```yaml
artifact_name: script.oppo203.iso.external-2.1.0-build4.zip
addon_version: 2.1.0.4
baseline_artifact: script.oppo203.iso.external-2.1.0-build3.zip
sha256: see companion script.oppo203.iso.external-2.1.0-build4.sha256
coverage_gate: fail_under = 97
measured_coverage: 97%
release_type: incremental_coverage_hardening_build
full_merge_started: false
real_hardware_validation: not_performed
```

## Required verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.1.0.4
```

## Package verification

After packaging, unpack `script.oppo203.iso.external-2.1.0-build4.zip` into a clean directory and rerun the same commands.
