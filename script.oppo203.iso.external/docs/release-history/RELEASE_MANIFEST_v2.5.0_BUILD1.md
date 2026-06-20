# Release Manifest — v2.5.0 Build 1

artifact_name: script.oppo203.iso.external-2.5.0-build1.zip
addon_version: 2.5.0
baseline: script.oppo203.iso.external-2.2.0.zip
role: initial v2.5 development-series baseline
hardware_validation: pending user validation
source_tests: 539 passed, 12 subtests passed
unittest_discovery: 539 tests OK
coverage: TOTAL 99%
release_audit: PASS 122/122

## Included release evidence

- BUILD_NOTES_v2.5.0_BUILD1.md
- ROADMAP_v2.5.0.md
- HARDWARE_VALIDATION_TRACKER_v2.5.0.md
- RELEASE_MANIFEST_v2.5.0_BUILD1.md
- COVERAGE_REPORT_v2.5.0_BUILD1.md
- TEST_AUDIT_REPORT_v2.5.0_BUILD1.md

## Verification

```bash
python -m pytest -q -p no:ddtrace
python -m unittest discover -s tests -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
python tools/audit_release.py --expected-version 2.5.0
```
