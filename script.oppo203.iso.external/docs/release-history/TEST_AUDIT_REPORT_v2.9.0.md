# Test and Audit Report — Version 2.9.0

This report records the required verification sequence for the v2.9.0 release rebuild.

## Required commands

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/playercorefactory_merge.py resources/lib/hardware_validation_readiness.py
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.0
```

## Expected posture

- Source verification: required.
- Post-unpack dev-source verification: required.
- Runtime ZIP audit: required.
- Hardware validation: not performed and not claimed.
## Source verification results

```text
py_compile: passed
targeted v2.9.0 tests: 5 passed
pytest: 653 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 217/217 checks passed
```
## Post-unpack dev-source verification results

```text
py_compile: passed
targeted v2.9.0 tests: 5 passed
pytest: 653 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 217/217 checks passed
runtime ZIP audit: passed; 45 runtime files; 0 forbidden evidence/test/tool files
```
