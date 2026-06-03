# Coverage Report — v2.9.16 Final

Source coverage result for the v2.9.16 release (`resources/lib`, with UI/glue modules measured):

```text
TOTAL 5899 statements, 16 missed, 1936 branches, 49 partial branches, 99% coverage
```

The enforced gate in `.coveragerc` and `pyproject.toml` is `fail_under = 99`. The serial `coverage run -m pytest` then `coverage report` gate passes; the v2.9.16 fixes add their pure helpers (`discovery._safe_port`, `autoscript_helper._safe_text`) under full property-test and fixture coverage. CI is the authoritative coverage runner.
