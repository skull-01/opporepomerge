# Release Manifest — v2.9.1 Build 7

```yaml
addon_id: script.oppo203.iso.external
addon_version: 2.9.1
build_id: v2.9.1 Build 7
baseline: script.oppo203.iso.external-2.9.1-build6-dev-source.zip
scope: allowlist-based runtime packaging
hardware_validation: not_performed_not_claimed
```

## Expected artifacts

- `script.oppo203.iso.external-2.9.1-build7.zip`
- `script.oppo203.iso.external-2.9.1-build7-dev-source.zip`
- `script.oppo203.iso.external-2.9.1-build7-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.1-build7.sha256`

## Packaging policy

The installable runtime ZIP contains only `addon.xml`, `default.py`, `service.py`, optional root runtime assets, and `resources/**`. Tests, tools, scripts, release evidence, handoff files, reports, and documentation evidence remain in dev-source and artifact bundles only.
