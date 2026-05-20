# Release Manifest — v2.9.1 Build 14

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 14
package: script.oppo203.iso.external-2.9.1-build14.zip
dev_source: script.oppo203.iso.external-2.9.1-build14-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.1-build14-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.1-build13-dev-source.zip
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Required verification

Run source verification and post-unpack verification separately:

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/version.py resources/lib/disc_classification.py resources/lib/command_map.py resources/lib/settings_schema.py tools/test_layout.py tools/package_installable_zip.py tools/audit_release.py
python3 tools/render_docs.py --root . --check
python3 tools/sync_version.py --root . --check --expected-version 2.9.1
python3 tools/type_check.py --root .
python3 tools/test_layout.py --root . --check
python3 -m pytest -q tests/test_v291_build14_test_layout_standardization.py -p no:ddtrace
python3 -m pytest -q tests/test_all.py -p no:ddtrace
python3 -m pytest -q <remaining split test chunks> -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run --parallel-mode -m pytest -q <split test chunks> -p no:ddtrace
python3 -m coverage combine
python3 -m coverage report -m
python3 tools/audit_release.py --root . --expected-version 2.9.1
```

The installable runtime ZIP must remain allowlist-driven and exclude tests, tools, scripts, docs, release evidence, handoff files, and reports.
