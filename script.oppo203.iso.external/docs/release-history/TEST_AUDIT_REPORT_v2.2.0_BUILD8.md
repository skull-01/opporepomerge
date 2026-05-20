# Test and Audit Report — v2.2.0 Build 8

```yaml
addon_version: 2.2.0.8
baseline: script.oppo203.iso.external-2.2.0-build7.zip
source_verification: passed
post_unpack_verification: pending_until_package_verification
```

## Source verification commands and results

```bash
python -m pytest -q
```

```text
519 passed, 12 subtests passed
```

```bash
python -m unittest discover -s tests
```

```text
Ran 519 tests ... OK
```

```bash
python -m coverage run -m pytest -q
python -m coverage report -m
```

```text
519 passed, 12 subtests passed
TOTAL 99%
raw_combined_line_branch_coverage: 98.79743452699091%
```

```bash
python tools/audit_release.py --expected-version 2.2.0.8
```

```text
SUMMARY: PASS (94/94 checks passed)
```

## Notes

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
