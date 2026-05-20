# Release Manifest — v2.2.0 Build 9

```yaml
build: v2.2.0 Build 9
addon_version: 2.2.0.9
baseline_zip: script.oppo203.iso.external-2.2.0-build8.zip
package_zip: script.oppo203.iso.external-2.2.0-build9.zip
coverage_gate: 99 percent enforced
merge_scope: parity audit checkpoint only
```

## Required verification

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.9
```

## Build 9 evidence files

- `BUILD_NOTES_v2.2.0_BUILD9.md`
- `RELEASE_MANIFEST_v2.2.0_BUILD9.md`
- `COVERAGE_REPORT_v2.2.0_BUILD9.md`
- `TEST_AUDIT_REPORT_v2.2.0_BUILD9.md`
- `MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md`
