# Release Manifest — v2.9.1 Build 12

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 12
artifact_name: script.oppo203.iso.external-2.9.1-build12.zip
baseline: script.oppo203.iso.external-2.9.1-build11-dev-source.zip
scope: docs metadata/rendering pipeline
hardware_validation: not_performed_not_claimed
```

## Required verification

Run source and post-unpack verification:

```bash
python3 -m py_compile service.py default.py resources/lib/version.py tools/render_docs.py
python3 tools/render_docs.py --root . --check
python3 -m pytest -q tests/test_v291_build12_docs_metadata_pipeline.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/sync_version.py --root . --check --expected-version 2.9.1
python3 tools/audit_release.py --expected-version 2.9.1
```
