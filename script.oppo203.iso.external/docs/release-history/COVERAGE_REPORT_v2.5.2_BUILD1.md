# Coverage Report — v2.5.2 Build 1

Coverage was measured with branch coverage enabled for `resources/lib` using the optimized local command:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
```

Observed result:

```text
582 passed, 12 subtests passed
TOTAL 3066 statements, 28 missed, 1068 branches, 21 partial branches, 99% coverage
```

The project coverage gate remains enforced at:

```ini
fail_under = 99
```

Build 1 added capability-gating helpers and targeted tests while keeping the required 99 percent coverage gate satisfied.
