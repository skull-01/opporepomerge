# Coverage Report — v2.5.2 Build 2

Coverage gate remains 99 percent.

Command used:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage erase
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
```

Observed result:

```text
586 passed, 12 subtests passed
TOTAL 3066 statements, 28 missed, 1068 branches, 21 partial branches, 99% coverage
```

Build 2 added packaging-cleanup tests only and did not change runtime behavior.
