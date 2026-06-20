# Release Manifest — v2.9.10 Build 5

```yaml
build_id: v2.9.10 Build 5
artifact_name: script.oppo203.iso.external-2.9.10-build5.zip
dev_source: script.oppo203.iso.external-2.9.10-build5-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build5-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build4-dev-source.zip
hardware_validation: not_performed_not_claimed
```

## Required verification

Run source and post-unpack verification separately:

```bash
python3 -m py_compile service.py default.py resources/lib/*.py
python3 -m pytest -q tests/test_v2910_build5_tv_backend_registry.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.10
```

Runtime ZIP must remain allowlist-only and exclude tests, tools, scripts, docs, release evidence, handoff files, and Markdown evidence.
