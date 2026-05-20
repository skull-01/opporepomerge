# Test and Audit Report — v2.5.3 Build 6

```yaml
build: v2.5.3 Build 6
verification_style: one_command_at_a_time
coverage_timeout_mitigation: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 and -p no:ddtrace
source_pytest: 648 passed, 12 subtests passed
source_unittest: 571 tests OK
source_coverage: TOTAL 99%
source_audit: PASS 210/210
post_unpack_pytest: 648 passed, 12 subtests passed
post_unpack_unittest: 571 tests OK
post_unpack_coverage: TOTAL 99%
post_unpack_audit: PASS 210/210
```

## Source verification commands and results

```text
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/playercorefactory_merge.py resources/lib/hardware_validation_readiness.py
passed

python3 -m pytest -q -p no:ddtrace
648 passed, 12 subtests passed

python3 -m unittest discover -s tests -p 'test_*.py' -q
Ran 571 tests ... OK

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
648 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 99%

python3 tools/audit_release.py --expected-version 2.5.3
SUMMARY: PASS (210/210 checks passed)
```

## Post-unpack verification commands and results

```text
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/playercorefactory_merge.py resources/lib/hardware_validation_readiness.py
passed

python3 -m pytest -q tests/test_v253_build6_release_candidate.py -p no:ddtrace
5 passed

python3 -m pytest -q -p no:ddtrace
648 passed, 12 subtests passed

python3 -m unittest discover -s tests -p 'test_*.py' -q
Ran 571 tests ... OK

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
648 passed, 12 subtests passed

python3 -m coverage report -m
TOTAL 99%

python3 tools/audit_release.py --expected-version 2.5.3
SUMMARY: PASS (210/210 checks passed)
```

## Hardware status

No real OPPO, Chinoppo/M9702, Kodi, NAS, TV, or ADB hardware validation was performed or claimed.
