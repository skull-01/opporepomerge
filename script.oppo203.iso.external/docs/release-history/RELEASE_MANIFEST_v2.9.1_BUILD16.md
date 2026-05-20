# Release Manifest — v2.9.1 Build 16

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 16
package: script.oppo203.iso.external-2.9.1-build16.zip
dev_source: script.oppo203.iso.external-2.9.1-build16-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.1-build16-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.1-build15-dev-source.zip
scope: i18n extraction legacy alias hardening
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Required verification

Run source and post-unpack verification separately: py_compile, render_docs --check, sync_version --check, type_check.py, test_layout.py --check, i18n_extract.py --check, targeted Build 16 tests, pytest split run, unittest discovery, coverage, and audit_release.

The installable ZIP must remain runtime-only and must not include tests, tools, scripts, docs, release evidence, reports, handoff files, or development extraction tooling.
