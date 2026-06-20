# Build Notes — Version 2.9 Release

```yaml
version: 2.9.0
package: script.oppo203.iso.external-2.9.0.zip
baseline: script.oppo203.iso.external-2.5.3-build6-dev-source.zip
build_type: release-identity rebuild / pre-hardware stable release package
runtime_behavior_changed: false
hardware_validation_claim: none
```

## Summary

Version 2.9.0 rebuilds the verified v2.5.3 Build 6 pre-hardware release-candidate baseline as a stable release identity. The rebuild is intentionally narrow: it updates release metadata, audit requirements, documentation, and package naming only.

## Preserved behavior

- v2.5.3 Build 1 precise 4K UHD disc-style service interception.
- v2.5.3 Build 2 conservative Option 4 XML routing.
- v2.5.3 Build 3 version identity reconciliation.
- v2.5.3 Build 4 playercorefactory.xml backup/idempotency/rollback hardening.
- v2.5.3 Build 5 hardware-validation readiness export.
- v2.5.3 Build 6 pre-hardware release-candidate freeze posture.

## Scope control

No OPPO command map, Chinoppo wake rewrite, Reavon warning-only behavior, service classifier, NAS playback adapter, XML routing semantics, wizard flow, or hardware-control behavior changed in this release rebuild.

## Hardware status

No real OPPO, Chinoppo/M9702, Kodi, NAS, TV, or ADB hardware validation was performed or claimed during this automated rebuild.
## Source verification results

```text
py_compile: passed
targeted v2.9.0 tests: 5 passed
pytest: 653 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 217/217 checks passed
```
## Post-unpack dev-source verification results

```text
py_compile: passed
targeted v2.9.0 tests: 5 passed
pytest: 653 passed, 12 subtests passed
unittest: 571 tests OK
coverage: TOTAL 99%
release audit: PASS 217/217 checks passed
runtime ZIP audit: passed; 45 runtime files; 0 forbidden evidence/test/tool files
```
