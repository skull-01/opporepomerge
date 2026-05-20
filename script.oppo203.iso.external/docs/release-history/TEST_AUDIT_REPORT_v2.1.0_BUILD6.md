# Test and Audit Report — v2.1.0 Build 6

## Source verification

```text
python -m pytest -q
431 passed

python -m unittest discover -s tests
Ran 431 tests ... OK

python -m coverage run -m pytest -q
431 passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.1.0.6
SUMMARY: PASS (52/52 checks passed)
```

## Post-unpack verification

```text
python -m pytest -q
431 passed

python -m unittest discover -s tests
Ran 431 tests ... OK

python -m coverage run -m pytest -q
431 passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.1.0.6
SUMMARY: PASS (52/52 checks passed)
```

## Notes

The unittest run emits existing ResourceWarning messages from legacy temporary-file fixtures, but the suite completes successfully. No real hardware testing is claimed.
