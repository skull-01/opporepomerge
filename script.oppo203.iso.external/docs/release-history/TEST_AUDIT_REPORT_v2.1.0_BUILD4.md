# Test and Audit Report — v2.1.0 Build 4

## Source verification

```text
python -m pytest -q
409 passed

python -m unittest discover -s tests
Ran 409 tests ... OK

python -m coverage run -m pytest -q
409 passed

python -m coverage report -m
TOTAL 97%

python tools/audit_release.py --expected-version 2.1.0.4
SUMMARY: PASS (48/48 checks passed)
```

## Post-unpack verification from `script.oppo203.iso.external-2.1.0-build4.zip`

```text
python -m pytest -q
409 passed

python -m unittest discover -s tests
Ran 409 tests ... OK

python -m coverage run -m pytest -q
409 passed

python -m coverage report -m
TOTAL 97%

python tools/audit_release.py --expected-version 2.1.0.4
SUMMARY: PASS (48/48 checks passed)
```

## Scope notes

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested. The full v1.1.9 + v0.9.14 merge was not started.

The unittest run emits existing `ResourceWarning` messages from temporary fixture writes, but the suite completes successfully.
