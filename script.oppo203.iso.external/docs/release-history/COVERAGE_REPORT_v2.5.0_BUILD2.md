# Coverage Report — v2.5.0 Build 2

Command used:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 coverage erase
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 coverage run -m pytest -q -p no:ddtrace
coverage report
```

Result:

```text
544 passed, 12 subtests passed
TOTAL 99%
```
