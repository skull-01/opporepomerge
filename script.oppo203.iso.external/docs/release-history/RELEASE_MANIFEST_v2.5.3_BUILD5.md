# Release Manifest — v2.5.3 Build 5

```yaml
addon_version: 2.5.3
package: script.oppo203.iso.external-2.5.3-build5.zip
checksum_file: script.oppo203.iso.external-2.5.3-build5.sha256
baseline: script.oppo203.iso.external-2.5.3-build4.zip
build_role: hardware-validation readiness and diagnostic export
hardware_validation_claimed: false
```

## Included evidence

- `BUILD_NOTES_v2.5.3_BUILD5.md`
- `RELEASE_MANIFEST_v2.5.3_BUILD5.md`
- `RELEASE_NOTES_v2.5.3_BUILD5.md`
- `COVERAGE_REPORT_v2.5.3_BUILD5.md`
- `TEST_AUDIT_REPORT_v2.5.3_BUILD5.md`
- `HARDWARE_VALIDATION_v2.5.3_BUILD5.md`
- `HARDWARE_VALIDATION_READINESS_v2.5.3_BUILD5.md`

## Required verification

```bash
python3 -m py_compile service.py default.py resources/lib/intercept.py resources/lib/hardware_validation_readiness.py
python3 -m pytest -q -p no:ddtrace
python3 -m unittest discover -s tests -p 'test_*.py' -q
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m coverage run -m pytest -q -p no:ddtrace
python3 -m coverage report -m
python3 tools/audit_release.py --expected-version 2.5.3
```

The same checks must pass from the post-unpack dev-source package.
