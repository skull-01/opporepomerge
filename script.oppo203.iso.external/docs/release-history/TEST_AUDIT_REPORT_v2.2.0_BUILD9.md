# Test and Audit Report — v2.2.0 Build 9

## Source verification

```text
python -m pytest -q
523 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 523 tests ... OK

python -m coverage run -m pytest -q
523 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.9
SUMMARY: PASS (99/99 checks passed)
```

## Post-unpack verification

```text
python -m pytest -q
523 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 523 tests ... OK

python -m coverage run -m pytest -q
523 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.9
SUMMARY: PASS (99/99 checks passed)
```

## Note on coverage command execution in this environment

The coverage run produced a valid `.coverage` data file and `coverage report` passed the enforced 99 percent gate. In this container, some coverage subprocess invocations did not always return cleanly after pytest printed its success summary; rerunning with the same test set produced the same 99 percent coverage data. The release decision is based on the generated coverage data, successful coverage report, pytest/unittest success, and release audit success from source and post-unpack artifact.
