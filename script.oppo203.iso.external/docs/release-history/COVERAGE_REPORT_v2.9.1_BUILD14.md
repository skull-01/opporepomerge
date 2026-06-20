# Coverage Report — v2.9.1 Build 14

Required gate: TOTAL 99%.

## Source coverage

Coverage was collected in split batches to avoid local timeout behavior:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage erase
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run --parallel-mode -m pytest -q tests/test_all.py -p no:ddtrace
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run --parallel-mode -m pytest -q <legacy/current test chunks> -p no:ddtrace
python3 -m coverage combine
python3 -m coverage report -m
```

Observed source result:

```text
TOTAL 3681 statements, 38 missed, 1270 branches, 34 partial branches, 99% coverage
```

Post-unpack coverage must be repeated from the unpacked dev-source package and must also report TOTAL 99%.
