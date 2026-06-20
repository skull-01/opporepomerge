# Release Manifest — v2.9.1 Build 2

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
package: script.oppo203.iso.external-2.9.1-build2.zip
dev_source: script.oppo203.iso.external-2.9.1-build2-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.1-build2-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.1-build1-dev-source.zip
runtime_behavior_changed: false
hardware_validation_claimed: false
```

## Required verification

Run source and post-unpack verification separately:

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/disc_classification.py resources/lib/constants.py
python3 -m pytest -q tests/test_v291_build2_disc_classification.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.1
```
