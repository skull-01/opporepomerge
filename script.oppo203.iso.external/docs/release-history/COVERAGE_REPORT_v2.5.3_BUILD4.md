# Coverage Report — v2.5.3 Build 4

```yaml
coverage_gate: 99 percent
source_result: TOTAL 99%
post_unpack_result: TOTAL 99%
source_pytest: 635 passed, 12 subtests passed
post_unpack_pytest: 635 passed, 12 subtests passed
```

Build 4 preserved the established 99% coverage gate while adding playercorefactory merge safety tests.

## Source coverage result

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
635 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 99%
```

## Post-unpack coverage result

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
635 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 99%
```
