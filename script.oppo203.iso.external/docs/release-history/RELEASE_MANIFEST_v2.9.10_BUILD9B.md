# Release Manifest — v2.9.10 Build 9B

## Artifact identity

- Runtime package: `script.oppo203.iso.external-2.9.10-build9b.zip`
- Dev-source package: `script.oppo203.iso.external-2.9.10-build9b-dev-source.zip`
- Artifact bundle: `script.oppo203.iso.external-2.9.10-build9b-artifacts-bundle.zip`
- Checksum file: `script.oppo203.iso.external-2.9.10-build9b.sha256`

## Changed runtime/source files

- `resources/lib/smartthings_control.py`
- `resources/lib/tv_control.py`
- `resources/lib/tv_backends.py`
- `resources/lib/tv_presets.py`
- `resources/lib/settings_reader.py`
- `resources/lib/version.py`
- `addon.xml`
- `docs/sources.yaml`
- `scripts/package_release.sh`
- `README.md`
- `reference.md`
- `web-references.md`

## Added tests

- `tests/test_v2910_build9b_smartthings_request_helper.py`

## Runtime ZIP policy

The installable runtime ZIP remains allowlist-only. Tests, tools, scripts, docs, release evidence, reports, handoff files, coverage data, and Markdown evidence must not be included.
