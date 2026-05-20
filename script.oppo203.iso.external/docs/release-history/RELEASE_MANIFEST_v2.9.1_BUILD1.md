# Release Manifest — v2.9.1 Build 1

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
package: script.oppo203.iso.external-2.9.1-build1.zip
dev_source: script.oppo203.iso.external-2.9.1-build1-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.1-build1-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.0-dev-source.zip
release_type: small UX clarity build
hardware_validation: not_performed_not_claimed
```

## Purpose

This build packages a wording-only first-run wizard improvement for Kodi startup auto-power. It keeps the v2.9 runtime behavior and clarifies that automatic startup wake is optional.

## Required verification

Run from source and again after unpacking the dev-source ZIP:

```bash
python3 -m py_compile service.py default.py resources/lib/wizard.py
python3 -m pytest -q tests/test_v291_build1_startup_autopower_wizard_wording.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.1
```

## Runtime ZIP policy

The installable ZIP must contain runtime files only. Build notes, release evidence, tests, tools, coverage reports, and handoff files belong in the dev-source ZIP and artifact bundle.
