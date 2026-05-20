# COVERAGE_REPORT_v2.9.10_BUILD2.md

```text
Coverage gate: fail_under = 99
Measured source TOTAL: 99%
```

Coverage was measured with branch coverage across `resources/lib` using split coverage runs to avoid local timeout behavior:

```bash
python3 -m coverage erase
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q tests/test_all.py -p no:ddtrace
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run --append -m pytest -q <chunk1> -p no:ddtrace
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run --append -m pytest -q <chunk2> -p no:ddtrace
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run --append -m pytest -q <chunk3> -p no:ddtrace
python3 -m coverage report -m
```

Build 2 preserves the 99% coverage gate.
