# Test/Audit Report — v2.5.2 Build 2

Build 2 adds packaging-cleanup tests and release-audit evidence for the runtime-focused installable ZIP policy.

## Commands and results

```text
python3 -m py_compile service.py default.py
result: passed

python3 -m pytest -q tests/test_v252_build2_packaging_cleanup.py -p no:ddtrace
result: 4 passed

python3 -m pytest -q -p no:ddtrace
result: 586 passed, 12 subtests passed

python3 -m unittest discover -s tests -p 'test_*.py' -q
result: Ran 571 tests / OK

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
result: TOTAL 99%

python3 tools/audit_release.py --expected-version 2.5.2
result: PASS 163/163 checks
```

## Post-unpack runtime package audit

The optimized installable ZIP was unpacked and checked for runtime integrity. `addon.xml` and `resources/settings.xml` parsed successfully, `service.py` and `default.py` compiled, required runtime files were present, and excluded development/evidence files were absent.
