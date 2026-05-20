# RELEASE MANIFEST — script.oppo203.iso.external v2.0.0 Final

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.0.0
release_line: v2.0 MVP
source_baseline: verified Build 6 line
artifact_name: script.oppo203.iso.external-2.0.0.zip
checksum_name: script.oppo203.iso.external-2.0.0.sha256
release_status: final MVP package
real_hardware_validation: deferred until after full merge
```

## Required verification

Source tree verification:

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0
```

Post-unpack package verification:

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0
```

## Release evidence files

- `RELEASE_NOTES_v2.0.0.md`
- `RELEASE_MANIFEST_v2.0.0.md`
- `MVP_COMPLIANCE_MATRIX_v2.0.0.md`
- `HARDWARE_VALIDATION_v2.0.0.md`
- `BUILD_NOTES_v2.0.0_BUILD6.md`
- `RELEASE_MANIFEST_v2.0.0_BUILD6.md`

## Scope notes

This is the final MVP package. It does not claim the 92% coverage gate, real hardware validation, or the full v1.1.9 + v0.9.14 superset merge.
