# Coverage Report — v2.9.1 Build 3

Coverage gate remains `fail_under = 99`.

## Source coverage

```text
TOTAL 3505 statements, 33 missed, 1208 branches, 26 partial branches, 99% coverage
```

## Post-unpack coverage

```text
TOTAL 3505 statements, 33 missed, 1208 branches, 26 partial branches, 99% coverage
```

Coverage was collected in two pytest chunks to avoid local container timeout behavior while preserving the same source tree and coverage database:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage erase
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q tests/test_all.py -p no:ddtrace
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -a -m pytest -q <remaining test files> -p no:ddtrace
python3 -m coverage report -m
```
