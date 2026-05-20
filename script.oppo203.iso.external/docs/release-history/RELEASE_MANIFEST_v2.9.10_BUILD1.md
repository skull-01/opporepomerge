# RELEASE_MANIFEST_v2.9.10_BUILD1.md

```yaml
build_id: v2.9.10 Build 1
package: script.oppo203.iso.external-2.9.10-build1.zip
dev_source: script.oppo203.iso.external-2.9.10-build1-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build1-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.1-build16-dev-source.zip
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Required verification

```bash
python3 -m py_compile service.py default.py resources/lib/*.py
python3 -m pytest -q tests/test_v2910_build1_hardware_registry.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.10
```

Runtime ZIP must remain allowlist-only and must exclude tests, tools, scripts, docs, release evidence, handoff files, and Markdown evidence.
