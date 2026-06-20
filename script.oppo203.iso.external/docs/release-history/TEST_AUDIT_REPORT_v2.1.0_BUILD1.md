# Test and Audit Report — v2.1.0 Build 1

## Baseline

Baseline artifact: `script.oppo203.iso.external-2.0.0.zip`

Baseline verification before coverage-gate work:

```text
python -m pytest -q
354 passed

python -m unittest discover -s tests
Ran 354 tests ... OK

python tools/audit_release.py --expected-version 2.0.0
SUMMARY: PASS (31/31 checks passed)
```

Initial coverage measurement from the v2.0.0 baseline showed `51%` total measured coverage for `resources/lib`, so the 92 percent gate required real test/stub hardening rather than a configuration-only change.

## Source verification after v2.1.0 Build 1 changes

```text
python -m pytest -q
381 passed

python -m unittest discover -s tests
Ran 381 tests ... OK

python -m coverage erase
python -m coverage run -m pytest -q
381 passed

python -m coverage report -m
TOTAL 2516 statements, 163 missed, 894 branches, 114 partial branches, 92% coverage

python tools/audit_release.py --expected-version 2.1.0.1
SUMMARY: PASS (36/36 checks passed)
```

## Notes

- `.coveragerc` now enforces `fail_under = 92`.
- `tests/test_coverage_hardening.py` adds targeted coverage around existing behavior.
- `resources/lib/installer.py` now imports `xbmc` because coverage hardening exposed a real fallback-path bug.
- No physical OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
