# Release Manifest — Version 2.9.0

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.0
package: script.oppo203.iso.external-2.9.0.zip
dev_source: script.oppo203.iso.external-2.9.0-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.0-artifacts-bundle.zip
checksum_file: script.oppo203.iso.external-2.9.0.sha256
baseline: script.oppo203.iso.external-2.5.3-build6-dev-source.zip
runtime_zip_policy: runtime_only
hardware_validation: not_claimed
```

## Verification requirements

Run from source and again from a clean unpack of the dev-source package:

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/playercorefactory_merge.py resources/lib/hardware_validation_readiness.py
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.9.0
```

## Runtime ZIP exclusions

The installable runtime ZIP must not contain tests, tools, reports, handoff files, build notes, release manifests, coverage reports, audit reports, hardware-validation notes, or reconstruction evidence.
## Post-unpack dev-source verification results

```text
py_compile: passed
targeted v2.9.0 tests: 5 passed
pytest: 653 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 217/217 checks passed
runtime ZIP audit: passed; 45 runtime files; 0 forbidden evidence/test/tool files
```
