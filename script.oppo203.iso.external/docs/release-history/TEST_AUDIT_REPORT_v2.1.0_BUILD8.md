# Test and Audit Report — v2.1.0 Build 8

## Source verification

```text
python -m pytest -q
448 passed

python -m unittest discover -s tests
Ran 448 tests ... OK

python -m coverage run -m pytest -q
448 passed

python -m coverage report -m
TOTAL 99%
raw_combined_line_branch_coverage: 99.44%
line_coverage: 99.72%
branch_coverage: 98.66%

python tools/audit_release.py --expected-version 2.1.0.8
SUMMARY: PASS (60/60 checks passed)
```

## Post-unpack verification

Pending until the generated Build 8 zip is unpacked and verified.
