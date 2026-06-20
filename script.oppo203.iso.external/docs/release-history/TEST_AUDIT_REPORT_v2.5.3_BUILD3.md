# Test and Audit Report — v2.5.3 Build 3

```yaml
build: v2.5.3 Build 3
source_py_compile: passed
source_targeted_build3_tests: 4 passed
source_pytest: 628 passed, 12 subtests passed
source_unittest: 571 tests OK
source_coverage: TOTAL 99%
source_audit: PASS 190/190
post_unpack_py_compile: passed
post_unpack_targeted_build3_tests: 4 passed
post_unpack_pytest: 628 passed, 12 subtests passed
post_unpack_unittest: 571 tests OK
post_unpack_coverage: TOTAL 99%
post_unpack_audit: PASS 190/190
runtime_package_audit: passed
```

## Source verification

```text
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/installer.py resources/lib/wizard.py
passed

python3 -m pytest -q tests/test_v253_build3_version_identity.py -p no:ddtrace
4 passed

python3 -m pytest -q -p no:ddtrace
628 passed, 12 subtests passed

python3 -m unittest discover -s tests -p 'test_*.py' -q
Ran 571 tests ... OK

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
628 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 99%

python3 tools/audit_release.py --expected-version 2.5.3
SUMMARY: PASS (190/190 checks passed)
```

## Post-unpack verification

```text
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/installer.py resources/lib/wizard.py
passed

python3 -m pytest -q tests/test_v253_build3_version_identity.py -p no:ddtrace
4 passed

python3 -m pytest -q -p no:ddtrace
628 passed, 12 subtests passed

python3 -m unittest discover -s tests -p 'test_*.py' -q
Ran 571 tests ... OK

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
628 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 99%

python3 tools/audit_release.py --expected-version 2.5.3
SUMMARY: PASS (190/190 checks passed)
```

## Runtime package audit

```text
Runtime ZIP contains Kodi runtime files only.
Excluded: tests, tools, reports, build notes, release manifests, handoff files, and development evidence.
ZIP integrity check passed.
```

## Planned success-rate comparison

```text
Planned success rate: 92%
Actual outcome: Successful; source verification, post-unpack verification, packaging, checksums, and handoff completed.
What improved the success rate: Build was limited to version identity, audit expectations, tests, and documentation.
What reduced the success rate: Two inherited tests still expected the old 2.5.2 identity and required reconciliation.
Future segmentation recommendation: continue using narrow stability-first builds.
```
