# Test Audit Report — v2.5.0 Build 6

## Targeted pytest

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_v250_build6_diagnostic_summary.py -p no:ddtrace
7 passed
```

## Full pytest

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p no:ddtrace
565 passed, 12 subtests passed
```

## Unittest discovery

```text
python -m unittest discover -s tests -q
Ran 565 tests
OK
```

## Coverage

```text
TOTAL 99%
```

## Release audit

```text
python tools/audit_release.py --root . --expected-version 2.5.0
SUMMARY: PASS (142/142 checks passed)
```

## Scope verified

Build 6 adds only a lightweight, read-only diagnostic summary helper and tests. No playback, wizard branch order, OPPO command, TV switching, HTTP payload, hardware preset, or service interception behavior was intentionally changed.
