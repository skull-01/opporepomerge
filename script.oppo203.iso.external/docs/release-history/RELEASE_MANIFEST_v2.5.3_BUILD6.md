# Release Manifest — v2.5.3 Build 6

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.5.3
package: script.oppo203.iso.external-2.5.3-build6.zip
dev_source: script.oppo203.iso.external-2.5.3-build6-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.5.3-build6-artifacts-bundle.zip
checksum_file: script.oppo203.iso.external-2.5.3-build6.sha256
baseline: script.oppo203.iso.external-2.5.3-build5.zip
release_role: pre_hardware_release_candidate_packaging_freeze
hardware_validation: not_claimed
```

## Required verification

Run from source and again from a clean unpack of the dev-source package:

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/playercorefactory_merge.py resources/lib/hardware_validation_readiness.py
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.5.3
```

## Runtime ZIP rule

The installable ZIP must remain runtime-only and must exclude tests, tools, handoff Markdown, build notes, release manifests, coverage reports, test audit reports, hardware-validation notes, pre-hardware audit reports, and reconstruction evidence.
