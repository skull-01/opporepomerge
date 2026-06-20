# Release Manifest — v2.9.10 Build 7

```yaml
build_id: v2.9.10 Build 7
artifact_name: script.oppo203.iso.external-2.9.10-build7.zip
dev_source_name: script.oppo203.iso.external-2.9.10-build7-dev-source.zip
artifact_bundle_name: script.oppo203.iso.external-2.9.10-build7-artifacts-bundle.zip
checksum_name: script.oppo203.iso.external-2.9.10-build7.sha256
baseline: script.oppo203.iso.external-2.9.10-build6-dev-source.zip
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Runtime package policy

The installable ZIP remains runtime-only. Tests, tools, scripts, docs, release evidence, reports, handoff files, and Markdown evidence are excluded from the installable ZIP.

## Runtime additions

- `resources/lib/roku_ecp_control.py`
- Roku ECP backend metadata in `resources/lib/tv_backends.py`
- Roku software presets in `resources/lib/tv_presets.py`
