# Coverage Report — v2.9.1 Build 4

Coverage was measured with branch coverage enabled over `resources/lib` using split coverage runs to avoid local timeout behavior:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage erase
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q tests/test_all.py -p no:ddtrace
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run --append -m pytest -q <non-test_all test files> -p no:ddtrace
python3 -m coverage report -m
```

Observed result:

```text
TOTAL 3505 statements, 33 missed, 1208 branches, 26 partial branches, 99% coverage
```

The required 99% coverage gate remains satisfied.
