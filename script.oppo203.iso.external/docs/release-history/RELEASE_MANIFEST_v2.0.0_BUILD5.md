# Release Manifest — Version 2.0.0 Build 5

## Artifact identity

```text
addon_id: script.oppo203.iso.external
addon_version: 2.0.0.5
artifact_name: script.oppo203.iso.external-2.0.0-build5.zip
release_line: v2.0 MVP release-candidate hardening
base_build: Version 2.0.0 Build 4
```

## Build purpose

Build 5 is a reproducibility and release-audit hardening build. It preserves the MVP behavior from Build 4 and adds an auditable way to validate the package after unpacking.

## Included release evidence

| File | Purpose |
|---|---|
| `BUILD_NOTES_v2.0.0_BUILD5.md` | Build 5 change log and audit summary. |
| `RELEASE_MANIFEST_v2.0.0_BUILD5.md` | Artifact identity and verification instructions. |
| `HARDWARE_VALIDATION_v2.0.0_BUILD4.md` | User-provided/manual hardware-validation milestone retained from Build 4. |
| `MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md` | MVP compliance posture retained from Build 4. |
| `tools/audit_release.py` | Dependency-free release audit helper. |
| `.coveragerc` | Coverage configuration retained in the packaged artifact. |
| `README.md`, `reference.md`, `web-references.md` | Synchronized user-facing, technical, and source-reference documentation. |

## Verification commands

Run these from the unpacked `script.oppo203.iso.external/` folder:

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0.5
```

Expected result:

```text
344 tests passing
release audit passes
```

## MVP status

Build 5 remains scoped to the v2 MVP:

- External Player-first flow.
- M9702 / Chinoppo wake behavior.
- Optional TCL / Android TV switching through ADB.
- Basic OPPO TCP path.
- Fake OPPO loopback testing.
- Kodi stub foundation.
- Release-candidate style documentation and audit checks.

## Staged and deferred items

- Final 92% coverage gate: staged for post-MVP hardening.
- Full v1.3-style superset merge: deferred.
- Additional real-hardware regression testing: manual.
