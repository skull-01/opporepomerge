# Test and Audit Report — v2.2.0 Build 11

## Source verification

```text
python -m pytest -q -p no:ddtrace
533 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 533 tests ... OK

python -m coverage run -m pytest -q -p no:ddtrace
533 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.11
SUMMARY: PASS (109/109 checks passed)
```

## Post-unpack verification

```text
python -m pytest -q -p no:ddtrace
533 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 533 tests ... OK

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q
533 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.11
SUMMARY: PASS (109/109 checks passed)
```

## Build-process improvement retained

Verification commands were run one at a time. Source pytest-style commands used `-p no:ddtrace`. For the post-unpack coverage run, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` was used because this container still displayed local plugin shutdown/timeout behavior after the coverage summary with plugin autoloading enabled. The test and coverage result itself remained valid and completed successfully with plugin autoload disabled.
