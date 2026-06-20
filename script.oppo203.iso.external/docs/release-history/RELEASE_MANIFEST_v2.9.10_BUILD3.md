# RELEASE_MANIFEST_v2.9.10_BUILD3.md

```yaml
build_id: v2.9.10 Build 3
baseline: script.oppo203.iso.external-2.9.10-build2-dev-source.zip
package: script.oppo203.iso.external-2.9.10-build3.zip
dev_source: script.oppo203.iso.external-2.9.10-build3-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build3-artifacts-bundle.zip
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Scope

Clone / successor capability gates only. Reavon and Magnetar remain warning-only; stock OPPO and clone-family behavior remain protected.

## Required verification

Run source verification, package, run post-unpack dev-source verification, and audit the runtime ZIP for forbidden development/evidence files.
