# Coverage Report — v2.9.12 Final

Source coverage result for the v2.9.12 release:

```text
TOTAL ~5640 statements, ~62 missed, ~1800 branches, ~50 partial branches, 98% coverage
```

The enforced gate in `.coveragerc` and `pyproject.toml` remains `fail_under = 98`.
The new ready-to-transfer file generators and the wizard hook added in this
release are covered by `tests/test_transfer_file_generation.py`. CI is the
authoritative coverage runner.
