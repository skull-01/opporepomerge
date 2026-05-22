# Coverage Report — v2.9.13 Final

Source coverage result for the v2.9.13 release (logic modules; UI/glue omitted per `docs/testing-strategy.md`):

```text
TOTAL ~4628 statements, ~34 missed, ~1530 branches, ~46 partial branches, 99% coverage
```

The enforced gate in `.coveragerc` and `pyproject.toml` is `fail_under = 50`. UI/glue
modules (`wizard.py`, `first_run_wizard.py`, `wizard_polish.py`, `installer.py`) are
omitted from measurement so the gate reflects coverage of logic modules. CI is the
authoritative coverage runner.
