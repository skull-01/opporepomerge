# Release Manifest — v2.9.1 Build 6

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 6
artifact_name: script.oppo203.iso.external-2.9.1-build6.zip
baseline: script.oppo203.iso.external-2.9.1-build5-dev-source.zip
scope: build/release automation scripts
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Expected outputs

- `script.oppo203.iso.external-2.9.1-build6.zip`
- `script.oppo203.iso.external-2.9.1-build6-dev-source.zip`
- `script.oppo203.iso.external-2.9.1-build6-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.1-build6.sha256`

## Automation added

- `scripts/verify.sh`
- `scripts/package_release.sh`

The scripts are local and portable shell wrappers around existing Python tooling. They do not require external services.
