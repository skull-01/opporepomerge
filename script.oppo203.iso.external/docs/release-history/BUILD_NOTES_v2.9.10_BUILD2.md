# BUILD_NOTES_v2.9.10_BUILD2.md

## Build identity

```yaml
build_id: v2.9.10 Build 2
package: script.oppo203.iso.external-2.9.10-build2.zip
dev_source: script.oppo203.iso.external-2.9.10-build2-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build2-artifacts-bundle.zip
hardware_validation: not_performed_not_claimed
software_validation: automated_tests_only
runtime_behavior_changed: false
baseline: script.oppo203.iso.external-2.9.10-build1-dev-source.zip
```

## Purpose

Build 2 adds missing OPPO clone/successor player identifiers and safe aliases while preserving the Build 1 unified hardware registry foundation. It is intentionally limited to taxonomy and alias recognition.

## Files changed

- `resources/lib/hardware_profiles.py` — adds M9200, M9205, CineUltra V203/V204, Magnetar UDP900, and alias normalization helpers.
- `resources/lib/hardware_capabilities.py` — updates read-only capability sets and alias normalization.
- `resources/lib/settings_reader.py` — adds settings aliases, compatibility entries, and enum metadata for the new player identifiers.
- `resources/settings.xml` — exposes the new player identifiers in the OPPO hardware dropdown.
- `resources/lib/version.py` — v2.9.10 Build 2 identity.
- `addon.xml` — v2.9.10 Build 2 metadata while preserving Build 1 and v2.9.1 Build 16 lineage.
- `docs/sources.yaml`, `README.md`, `reference.md`, `web-references.md` — Build 2 documentation metadata and notes.
- `scripts/package_release.sh` — default build suffix updated to build2.
- `tests/test_v2910_build2_player_taxonomy.py` — Build 2 regression tests.
- `release-evidence/v2.9.10-build2/MANIFEST.txt` — Build 2 evidence manifest.

## Behavior changed

No runtime playback behavior changed. No OPPO command-map payload changed. No service interception, `playercorefactory.xml` routing, NAS adapter behavior, startup auto-power behavior, TV switching behavior, AVR sequencing, or hardware-control behavior changed.

## Behavior preserved

- 76-key command map.
- No `#SIS`, `#PGU`, or `#PGD` commands.
- Stock OPPO wake passthrough.
- Clone-safe wake rewrite for clone-family models.
- Reavon warning-only behavior.
- Magnetar UDP900 warning-only / unverified behavior.
- Existing TV switching non-fatal behavior.
- Runtime ZIP exclusion policy.
- 99% coverage gate.

## Known limitations

No real hardware validation was performed or claimed. New player identifiers are software taxonomy entries until a tester records real device results.

## Reconstruction instructions

Start from `script.oppo203.iso.external-2.9.10-build1-dev-source.zip`, add the Build 2 taxonomy/alias changes, update version/docs/package metadata to v2.9.10 Build 2, add Build 2 tests and evidence, then run source and post-unpack verification separately.
