# Release Manifest — v2.9.1 Build 4

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build: v2.9.1 Build 4
artifact_name: script.oppo203.iso.external-2.9.1-build4.zip
dev_source: script.oppo203.iso.external-2.9.1-build4-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.1-build4-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.1-build3-dev-source.zip
release_evidence_manifest: release-evidence/v2.9.1-build4/MANIFEST.txt
hardware_validation: not_performed_not_claimed
```

## Purpose

Build 4 adds dynamic release-evidence manifest discovery while preserving the legacy evidence-list fallback.

## Required verification

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/command_map.py tools/audit_release.py
python3 -m pytest -q tests/test_v291_build4_audit_evidence_manifest.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.1
```
