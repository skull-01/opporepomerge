# Release Manifest — v2.9.1 Build 8

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 8
baseline: script.oppo203.iso.external-2.9.1-build7-dev-source.zip
scope: settings exception narrowing phase 1
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Required verification

Run source and post-unpack verification separately:

```bash
python3 -m py_compile service.py default.py resources/lib/settings_reader.py
python3 -m pytest -q tests/test_v291_build8_settings_exception_narrowing.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/sync_version.py --check --expected-version 2.9.1
python3 tools/audit_release.py --expected-version 2.9.1
```
