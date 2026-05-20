# Release Manifest — v2.9.1 Build 5

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build: v2.9.1 Build 5
artifact_name: script.oppo203.iso.external-2.9.1-build5.zip
dev_source: script.oppo203.iso.external-2.9.1-build5-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.1-build5-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.1-build4-dev-source.zip
release_evidence_manifest: release-evidence/v2.9.1-build5/MANIFEST.txt
hardware_validation: not_performed_not_claimed
```

## Purpose

Build 5 adds a single version source and tooling/audit checks to prevent future add-on version drift.

## Required verification

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/version.py tools/audit_release.py tools/sync_version.py
python3 -m pytest -q tests/test_v291_build5_version_source.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.1
python3 tools/sync_version.py --check --expected-version 2.9.1
```
