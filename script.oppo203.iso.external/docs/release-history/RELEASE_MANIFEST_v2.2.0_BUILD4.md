# Release Manifest — v2.2.0 Build 4

```yaml
addon_version: 2.2.0.4
artifact: script.oppo203.iso.external-2.2.0-build4.zip
checksum_file: script.oppo203.iso.external-2.2.0-build4.sha256
baseline: script.oppo203.iso.external-2.2.0-build3.zip
coverage_gate: 99
merge_status: gradual superset merge in progress
```

## Included build evidence

- `BUILD_NOTES_v2.2.0_BUILD4.md`
- `RELEASE_MANIFEST_v2.2.0_BUILD4.md`
- `COVERAGE_REPORT_v2.2.0_BUILD4.md`
- `TEST_AUDIT_REPORT_v2.2.0_BUILD4.md`

## Source files changed

- `addon.xml`
- `README.md`
- `reference.md`
- `web-references.md`
- `service.py`
- `resources/lib/settings_reader.py`
- `tools/audit_release.py`
- `tests/test_all.py`
- `tests/test_superset_merge_build2.py`
- `tests/test_superset_merge_build3.py`
- `tests/test_superset_merge_build4.py`

## Runtime scope

Build 4 is a narrow persistence hardening slice. It does not add large user-facing features and does not start the broad/full merge.
