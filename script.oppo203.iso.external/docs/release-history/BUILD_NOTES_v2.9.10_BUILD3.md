# BUILD_NOTES_v2.9.10_BUILD3.md

## Build identity

```yaml
build_id: v2.9.10 Build 3
package: script.oppo203.iso.external-2.9.10-build3.zip
dev_source: script.oppo203.iso.external-2.9.10-build3-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build3-artifacts-bundle.zip
hardware_validation: not_performed_not_claimed
software_validation: automated_tests_only
runtime_behavior_changed: false
baseline: script.oppo203.iso.external-2.9.10-build2-dev-source.zip
```

## Purpose

Build 3 separates clone-safe behavior from warning-only successor behavior. It makes the stock OPPO, clone-family, experimental-clone, and OPPO-like successor gates explicit while preserving all playback/control behavior.

## Files changed

- `resources/lib/hardware_capabilities.py` — adds explicit stock, clone-family, NAS playback, and warning-only successor gates.
- `resources/lib/settings_reader.py` — keeps Magnetar UDP800/UDP900 warning-only, removes Magnetar from clone/NAS gates, and blocks successor NAS direct-playback assumptions.
- `resources/lib/hardware_validation_readiness.py` — adds player hardware class and command-map gate fields to readiness reports.
- `resources/lib/version.py` — v2.9.10 Build 3 identity.
- `addon.xml` — v2.9.10 Build 3 metadata while preserving Build 2 and Build 1 lineage.
- `docs/sources.yaml`, `README.md`, `reference.md`, `web-references.md` — Build 3 documentation metadata and notes.
- `scripts/package_release.sh` — default build suffix updated to build3.
- `tests/test_v2910_build3_capability_gates.py` — Build 3 regression tests.
- `release-evidence/v2.9.10-build3/MANIFEST.txt` — Build 3 evidence manifest.

## Behavior changed

No runtime playback behavior changed. No OPPO command-map payload changed. No service interception, `playercorefactory.xml` routing, NAS adapter behavior, startup auto-power behavior, TV switching behavior, AVR sequencing, or hardware-control behavior changed.

## Behavior preserved

- 76-key command map.
- No `#SIS`, `#PGU`, or `#PGD` commands.
- Stock OPPO wake passthrough.
- Clone-safe wake rewrite for clone-family models.
- Reavon warning-only behavior.
- Magnetar UDP800/UDP900 warning-only / unverified behavior.
- Existing TV switching non-fatal behavior.
- Runtime ZIP exclusion policy.
- 99% coverage gate.

## Known limitations

No real hardware validation was performed or claimed. Capability gates are software classifications only until a tester records real device results.

## Reconstruction instructions

Start from `script.oppo203.iso.external-2.9.10-build2-dev-source.zip`, add the Build 3 capability-gate changes, update version/docs/package metadata to v2.9.10 Build 3, add Build 3 tests and evidence, then run source and post-unpack verification separately.
