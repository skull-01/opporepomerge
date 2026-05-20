# Coverage Report — v2.5.3 Build 5

```yaml
coverage_gate: 99
source_result: TOTAL 99%
post_unpack_result: TOTAL 99%
new_runtime_module: resources/lib/hardware_validation_readiness.py
```

Build 5 adds tests for the hardware-validation readiness helper and export path so the 99% coverage gate remains preserved.

## Source coverage result

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
643 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 3429 statements, 35 missed, 1200 branches, 26 partial branches, 99% coverage
```

## Post-unpack coverage result

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
643 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 3429 statements, 35 missed, 1200 branches, 26 partial branches, 99% coverage
```
