# COVERAGE REPORT — v2.9.1 Build 15

## Source coverage

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage erase
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q tests/test_all.py -p no:ddtrace
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -a -m pytest -q <remaining test_*.py split groups> -p no:ddtrace
python3 -m coverage report -m
```

Result:

```text
tests/test_all.py: 383 passed
remaining tests split groups: 364 passed, 12 subtests passed
TOTAL 99%
```

## Post-unpack coverage

The packaged Build 15 dev-source ZIP was unpacked and verified with the same split coverage workflow.

Result:

```text
tests/test_all.py: 383 passed
remaining tests split groups: 364 passed, 12 subtests passed
TOTAL 99%
```

The single-process coverage command reached the local container timeout near the end, so Build 15 used the established split coverage workflow already used in prior handoff builds.
