# Coverage Report — v2.5.0 Final

Final source-tree verification result:

```text
pytest: 571 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 152/152
```

Final post-unpack verification result:

```text
pytest: 571 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 152/152
```

Coverage command used:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest -q -p no:ddtrace
python -m coverage report -m
```

This file is final evidence for the v2.5.0 final packaging audit.
