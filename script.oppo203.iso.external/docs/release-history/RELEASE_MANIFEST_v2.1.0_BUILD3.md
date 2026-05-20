# Release Manifest - v2.1.0 Build 3

artifact_name: script.oppo203.iso.external-2.1.0-build3.zip
checksum_name: script.oppo203.iso.external-2.1.0-build3.sha256
addon_version: 2.1.0.3
baseline_artifact: script.oppo203.iso.external-2.1.0-build2.zip
coverage_gate: fail_under = 96
measured_coverage: 96%
full_merge_started: false
real_hardware_validation: not performed

## Required verification

- python -m pytest -q
- python -m unittest discover -s tests
- python -m coverage run -m pytest -q
- python -m coverage report -m
- python tools/audit_release.py --expected-version 2.1.0.3
- post-unpack repeat of all commands above
