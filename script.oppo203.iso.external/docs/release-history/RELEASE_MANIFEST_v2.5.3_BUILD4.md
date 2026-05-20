# Release Manifest — v2.5.3 Build 4

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.5.3
package: script.oppo203.iso.external-2.5.3-build4.zip
dev_source: script.oppo203.iso.external-2.5.3-build4-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.5.3-build4-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.5.3-build3-dev-source.zip
release_type: XML merge safety hardening build
hardware_validation: not_claimed
```

## Required verification

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/playercorefactory_merge.py
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.5.3
```

The same verification must pass from a clean post-unpack dev-source tree.

## Runtime package rule

The installable ZIP must remain runtime-focused and exclude tests, tools, build notes, release manifests, coverage reports, test/audit reports, hardware-validation notes, handoff files, and historical reconstruction evidence.
