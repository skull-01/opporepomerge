# BUILD_NOTES_v2.9.10_BUILD1.md

## Build identity

```yaml
build_id: v2.9.10 Build 1
package: script.oppo203.iso.external-2.9.10-build1.zip
dev_source: script.oppo203.iso.external-2.9.10-build1-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build1-artifacts-bundle.zip
hardware_validation: not_performed_not_claimed
software_validation: automated_tests_only
runtime_behavior_changed: false
baseline: script.oppo203.iso.external-2.9.1-build16-dev-source.zip
```

## Purpose

Build 1 starts the v2.9.10 Unified Hardware Ecosystem Expansion with a side-effect-free hardware registry foundation. It adds player, TV, and AVR role families plus profile-class constants that later builds can extend.

## Files changed

- `resources/lib/hardware_profiles.py` — new unified hardware profile registry.
- `resources/lib/hardware_capabilities.py` — read-only capability summary helpers.
- `resources/lib/version.py` — v2.9.10 Build 1 identity.
- `addon.xml` — v2.9.10 Build 1 metadata while preserving v2.9.1 Build 16 lineage.
- `docs/sources.yaml`, `README.md`, `reference.md`, `web-references.md` — generated documentation metadata.
- `scripts/package_release.sh` — default build suffix updated to build1.
- `tests/test_v2910_build1_hardware_registry.py` — Build 1 regression tests.
- `release-evidence/v2.9.10-build1/MANIFEST.txt` — Build 1 evidence manifest.

## Behavior changed

No runtime playback behavior changed. No OPPO command-map behavior, service interception, `playercorefactory.xml` routing, NAS adapter behavior, startup auto-power behavior, TV switching behavior, AVR sequencing, settings runtime behavior, or hardware-control behavior changed.

## Behavior preserved

- 76-key command map.
- No `#SIS`, `#PGU`, or `#PGD` commands.
- Stock OPPO wake passthrough.
- Clone-safe wake rewrite.
- Reavon warning-only behavior.
- Magnetar warning-only behavior unless hardware-proven.
- Existing TV switching non-fatal behavior.
- Runtime ZIP exclusion policy.
- 99% coverage gate.

## Known limitations

No real hardware validation was performed or claimed. The registry is a foundation only; later builds will expand taxonomy, TV presets, and AVR drivers.

## Reconstruction instructions

Start from `script.oppo203.iso.external-2.9.1-build16-dev-source.zip`, add the two registry modules, update version/docs/package metadata to v2.9.10 Build 1, add Build 1 tests and evidence, then run source and post-unpack verification separately.
