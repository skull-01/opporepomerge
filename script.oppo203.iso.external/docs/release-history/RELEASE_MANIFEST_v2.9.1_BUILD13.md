# Release Manifest — v2.9.1 Build 13

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 13
baseline: script.oppo203.iso.external-2.9.1-build12-dev-source.zip
package: script.oppo203.iso.external-2.9.1-build13.zip
scope: type hints and non-blocking mypy baseline
hardware_validation: not_performed_not_claimed
```

## Required verification

Run source and post-unpack verification separately:

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/version.py resources/lib/disc_classification.py resources/lib/command_map.py resources/lib/settings_schema.py tools/type_check.py
python3 tools/sync_version.py --root . --check --expected-version 2.9.1
python3 tools/type_check.py --root .
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --root . --expected-version 2.9.1
```
