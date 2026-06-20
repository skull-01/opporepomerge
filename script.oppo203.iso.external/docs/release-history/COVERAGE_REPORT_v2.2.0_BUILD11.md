# Coverage Report — v2.2.0 Build 11

```yaml
version: 2.2.0.11
coverage_gate: 99 percent
coverage_command: python -m coverage run -m pytest -q -p no:ddtrace
displayed_total: 99 percent
raw_line_branch_coverage: 98.63373620599054 percent
line_coverage: 98.93086243763364 percent
branch_coverage: 97.8 percent
```

The 99 percent coverage gate remains enforced in `.coveragerc`. Build 11 uses the improved verification process introduced after Build 9: commands are run one at a time and the local `ddtrace` pytest plugin is disabled only during pytest/coverage execution to prevent container timeout behavior.

## Source result

```text
python -m coverage run -m pytest -q -p no:ddtrace
533 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%
```

## Scope note

Build 11 adds targeted wizard/UI compatibility-flag tests. It does not expand runtime feature scope beyond the narrow merge slice.
