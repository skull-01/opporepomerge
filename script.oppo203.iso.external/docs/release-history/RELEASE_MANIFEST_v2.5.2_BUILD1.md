# Release Manifest — v2.5.2 Build 1

```yaml
package: script.oppo203.iso.external-2.5.2-build1.zip
addon_version: 2.5.2
baseline: v2.5.1 Build 1 startup-power release package
build_role: OPPO/Chinoppo NAS playback capability gates and firmware rules
hardware_validation_status: user NAS-mounted playback capability confirmed; per-model validation still pending
runtime_playback_trigger_change: none
coverage_gate: 99 percent enforced
source_verification: 582 passed, 12 subtests passed; unittest OK; coverage TOTAL 99%; audit PASS 158/158
```

## Required verification commands

```bash
python3 -m py_compile service.py default.py
python3 -m pytest -q tests/test_v252_build1_nas_capability.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.5.2
```

## Package boundary

This is Build 1 of the v2.5.2 NAS playback enhancement line. It prepares model/firmware gates only and intentionally defers path mapping, AutoScript profile changes, wizard setup, and playback trigger work to later builds.
