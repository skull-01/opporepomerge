# Test and Audit Report — v2.2.0 Build 5

## Source verification

```text
python -m pytest -q
496 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 496 tests ... OK

python -m coverage run -m pytest -q
496 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.5
SUMMARY: PASS (81/81 checks passed)
```

## Notes

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.

The full v1.1.9 + v0.9.14 superset merge remains in progress.
