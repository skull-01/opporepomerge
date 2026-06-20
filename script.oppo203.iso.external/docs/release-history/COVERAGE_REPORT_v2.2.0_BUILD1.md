# Coverage Report — v2.2.0 Build 1

```text
python -m coverage run -m pytest -q
461 passed

python -m coverage report -m
TOTAL 99%
```

```yaml
coverage_gate: 99
measured_display_coverage: 99%
raw_combined_line_branch_coverage: 99.43422913719944%
covered_lines: 2604
num_statements: 2611
covered_branches: 911
num_branches: 924
```

The first merge slice added `resources/lib/first_run_wizard.py` and kept it covered by behavior-oriented tests so the 99% pre-merge gate remains intact.
