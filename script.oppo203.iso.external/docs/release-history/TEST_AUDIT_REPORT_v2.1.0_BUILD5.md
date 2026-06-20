# Test and Audit Report — v2.1.0 Build 5

## Source verification

```text
python -m pytest -q
413 passed

python -m unittest discover -s tests
Ran 413 tests ... OK

python -m coverage run -m pytest -q
413 passed

python -m coverage report -m
TOTAL 98%

python tools/audit_release.py --expected-version 2.1.0.5
SUMMARY: PASS (48/48 checks passed)
```

## Post-unpack verification

```text
python -m pytest -q
413 passed

python -m unittest discover -s tests
Ran 413 tests ... OK

python -m coverage run -m pytest -q
413 passed

python -m coverage report -m
TOTAL 98%

python tools/audit_release.py --expected-version 2.1.0.5
SUMMARY: PASS (48/48 checks passed)
```

## Caveat

No real hardware validation was performed.
