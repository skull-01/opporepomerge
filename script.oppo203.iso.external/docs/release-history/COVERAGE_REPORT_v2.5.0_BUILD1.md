# Coverage Report — v2.5.0 Build 1

Command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
```

Result:

```text
539 passed, 12 subtests passed
TOTAL 2806 statements, 30 missed, 1000 branches, 20 partial branches, 99% coverage
```

Coverage gate status: passed. The v2.2.0 release gate of 99 percent is preserved.
