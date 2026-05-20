# Release Manifest — v2.9.1 Build 3

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build: v2.9.1 Build 3
baseline: script.oppo203.iso.external-2.9.1-build2-dev-source.zip
package: script.oppo203.iso.external-2.9.1-build3.zip
dev_source: script.oppo203.iso.external-2.9.1-build3-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.1-build3-artifacts-bundle.zip
hardware_validation: not_performed_not_claimed
```

## Required verification

Run from source and again from a clean dev-source unpack:

```bash
python3 -m py_compile service.py default.py resources/lib/command_map.py resources/lib/settings_reader.py resources/lib/oppo_remote.py
python3 -m pytest -q tests/test_v291_build3_command_map_externalization.py -p no:ddtrace
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.1
```

## Runtime ZIP policy

The installable ZIP must remain runtime-only and must not include tests, tools, reports, handoff files, build notes, release manifests, coverage reports, test audit reports, pre-hardware audit reports, or development evidence.
