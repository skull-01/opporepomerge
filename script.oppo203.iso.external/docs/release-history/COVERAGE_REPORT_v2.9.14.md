# Coverage Report — v2.9.14 Final

Source coverage result for the v2.9.14 release (`resources/lib`, with UI/glue modules measured):

```text
TOTAL 5500 statements, 16 missed, 1792 branches, 47 partial branches, 99% coverage
```

The enforced gate in `.coveragerc` and `pyproject.toml` is `fail_under = 99`. The 99% floor was restored after the v2.9.13 line (UI/glue modules are now exercised by the suite and back in measurement; only a handful of on-device package-import shims remain uncovered via `# pragma: no cover`). The serial `coverage run -m pytest` then `coverage report` gate passes. CI is the authoritative coverage runner.
