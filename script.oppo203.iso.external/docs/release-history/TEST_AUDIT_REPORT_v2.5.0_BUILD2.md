# Test Audit Report — v2.5.0 Build 2

## Targeted stability tests

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p no:ddtrace tests/test_v250_build2_stability.py
5 passed
```

## Full pytest

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p no:ddtrace
544 passed, 12 subtests passed
```

## Unittest discovery

```text
python -m unittest discover -s tests -q
Ran 544 tests
OK
```

## Release audit

```text
python tools/audit_release.py --expected-version 2.5.0
SUMMARY: PASS
```
