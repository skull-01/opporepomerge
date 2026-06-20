# RELEASE MANIFEST — v2.9.1 Build 15

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 15
package_name: script.oppo203.iso.external-2.9.1-build15.zip
dev_source_name: script.oppo203.iso.external-2.9.1-build15-dev-source.zip
artifact_bundle_name: script.oppo203.iso.external-2.9.1-build15-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.1-build14-dev-source.zip
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Required source verification

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/version.py resources/lib/disc_classification.py resources/lib/command_map.py resources/lib/settings_schema.py tools/i18n_extract.py tools/make_pot.py
python3 tools/render_docs.py --root . --check
python3 tools/sync_version.py --root . --check --expected-version 2.9.1
python3 tools/type_check.py --root .
python3 tools/test_layout.py --root . --check
python3 tools/i18n_extract.py --root . --check
python3 -m pytest -q tests/test_v291_build15_i18n_extraction_transition.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --root . --expected-version 2.9.1
```

## Runtime ZIP policy

The installable ZIP must include only runtime files. Build 15 development-only i18n files such as `tools/i18n_extract.py`, `tools/make_pot.py`, and `babel.cfg` must remain outside the installable ZIP.
