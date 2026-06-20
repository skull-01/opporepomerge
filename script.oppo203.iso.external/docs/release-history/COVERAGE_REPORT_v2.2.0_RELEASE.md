# Coverage Report — v2.2.0 Release

Coverage gate: 99 percent, enforced in `.coveragerc`.

Expected command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
```

Expected displayed result: `TOTAL 99%`.

The `-p no:ddtrace` / `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` combination is a local verification-process hardening measure introduced after Build 9 timeout behavior.
