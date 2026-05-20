# Release Manifest — v2.5.3 Build 3

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.5.3
package: script.oppo203.iso.external-2.5.3-build3.zip
dev_source: script.oppo203.iso.external-2.5.3-build3-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.5.3-build3-artifacts-bundle.zip
checksum_file: script.oppo203.iso.external-2.5.3-build3.sha256
baseline: script.oppo203.iso.external-2.5.3-build2-dev-source.zip
release_type: version_identity_and_audit_reconciliation
hardware_validation: not_claimed
```

## Required verification

Run from source and from a clean unpack of the dev-source package:

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/installer.py resources/lib/wizard.py
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.5.3
```

Runtime package audit must confirm the installable ZIP excludes tests, tools, reports, handoff files, and build evidence.
