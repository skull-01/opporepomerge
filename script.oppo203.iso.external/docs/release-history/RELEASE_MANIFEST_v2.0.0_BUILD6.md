# Release Manifest — Version 2.0.0 Build 6

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.0.0.6
artifact_name: script.oppo203.iso.external-2.0.0-build6.zip
checksum_name: script.oppo203.iso.external-2.0.0-build6.sha256
base_artifact: script.oppo203.iso.external-2.0.0.zip
base_version: 2.0.0
release_line: v2.0 MVP build-id update
```

## Purpose

This manifest records the Build 6 package identity update. Build 6 exists to carry the requested build id `2.0.0.6` while preserving the previously verified v2.0.0 MVP behavior.

## Required verification commands

Run from the source tree and again after unpacking the generated zip:

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0.6
```

## Required package contents

| File | Purpose |
|---|---|
| `addon.xml` | Carries add-on version `2.0.0.6`. |
| `BUILD_NOTES_v2.0.0_BUILD6.md` | Build 6 notes and caveats. |
| `RELEASE_MANIFEST_v2.0.0_BUILD6.md` | Build 6 artifact identity and verification steps. |
| `README.md` | User-facing release/build ledger. |
| `reference.md` | Technical rationale and invariants. |
| `web-references.md` | Source/reference traceability. |
| `tools/audit_release.py` | Dependency-free release audit helper. |
| `RELEASE_NOTES_v2.0.0.md` | Preserved final v2.0.0 release notes. |
| `RELEASE_MANIFEST_v2.0.0.md` | Preserved final v2.0.0 manifest. |
| `MVP_COMPLIANCE_MATRIX_v2.0.0.md` | Preserved final MVP compliance evidence. |
| `HARDWARE_VALIDATION_v2.0.0.md` | Preserved hardware-validation status note. |

## Deferred work

- 92% coverage gate remains deferred.
- Full v1.1.9 + v0.9.14 strict superset merge remains deferred to a later v2.1-style milestone.
- No new hardware validation is claimed for Build 6.
