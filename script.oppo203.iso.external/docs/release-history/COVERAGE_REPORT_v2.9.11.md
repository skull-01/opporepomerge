# Coverage Report — v2.9.11 Final

Source coverage result after the repository-wide formatting pass:

```text
TOTAL ~5518 statements, ~61 missed, 1766 branches, ~47 partial branches, 98% coverage
```

The repository-wide `black` reformat split long calls and expressions onto
additional lines, exposing defensive lines and partial branches the suite does
not exercise. Net branch coverage settled at ~98%, so the enforced gate in
`.coveragerc` and `pyproject.toml` was set to `fail_under = 98`. CI is the
authoritative coverage runner.
