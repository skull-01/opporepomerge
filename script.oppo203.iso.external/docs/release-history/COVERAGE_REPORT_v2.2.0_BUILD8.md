# Coverage Report — v2.2.0 Build 8

```yaml
addon_version: 2.2.0.8
coverage_gate: 99 percent enforced
coverage_display: 99 percent
raw_combined_line_branch_coverage: 98.79743452699091 percent
```

The Build 8 runtime slice is documentation/audit/checkpoint focused, so measured runtime-library coverage remains effectively the same as Build 7 while the 99 percent gate is preserved.

## Source coverage command

```bash
python -m coverage run -m pytest -q
python -m coverage report -m
```

## Source coverage result

```text
519 passed, 12 subtests passed
TOTAL 99%
```
