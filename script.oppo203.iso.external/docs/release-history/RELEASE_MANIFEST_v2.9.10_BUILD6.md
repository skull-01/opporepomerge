# Release Manifest — v2.9.10 Build 6

```yaml
build_id: v2.9.10 Build 6
artifact_name: script.oppo203.iso.external-2.9.10-build6.zip
dev_source: script.oppo203.iso.external-2.9.10-build6-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build6-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build5-dev-source.zip
hardware_validation: not_performed_not_claimed
```

## Required verification

Run source and post-unpack verification separately:

```bash
python3 -m py_compile service.py default.py resources/lib/*.py
python3 tools/render_docs.py --root . --check
python3 tools/sync_version.py --root . --check
python3 tools/test_layout.py --root . --check
python3 tools/i18n_extract.py --root . --check
python3 -m pytest -q tests/test_v2910_build6_android_tv_presets.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.10
```

Runtime ZIP must remain allowlist-only and exclude tests, tools, scripts, docs, release evidence, handoff files, and Markdown evidence.
