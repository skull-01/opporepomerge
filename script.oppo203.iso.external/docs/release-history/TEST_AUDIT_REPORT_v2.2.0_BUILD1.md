# Test and Audit Report — v2.2.0 Build 1

## Source verification

```text
python -m pytest -q
461 passed

python -m unittest discover -s tests
Ran 461 tests ... OK

python -m coverage run -m pytest -q
461 passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.1
SUMMARY: PASS (64/64 checks passed)
```

## Scope

This was the first gradual v1.1.9 + v0.9.14 superset-merge slice. It restored the v0.9.14 compatibility helper API and service settings watcher only. No real hardware validation was performed.
