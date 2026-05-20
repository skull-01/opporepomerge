# BUILD_NOTES_v2.9.10_BUILD4.md

## Build identity

```yaml
build_id: v2.9.10 Build 4
package: script.oppo203.iso.external-2.9.10-build4.zip
dev_source: script.oppo203.iso.external-2.9.10-build4-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build4-artifacts-bundle.zip
hardware_validation: not_performed_not_claimed
software_validation: automated_tests_only
runtime_behavior_changed: false
baseline: script.oppo203.iso.external-2.9.10-build3-dev-source.zip
```

## Purpose

Build 4 updates player wizard/help/readiness wording for stock OPPO, Chinoppo-style clones, experimental clones, and OPPO-like successors. It documents that stock OPPO uses stock power behavior, clone-family players use clone-safe wake behavior and NAS/AutoScript readiness gates, and Reavon/Magnetar successors remain warning-only unless hardware-proven.

## Files changed

- `resources/lib/hardware_capabilities.py` — adds read-only player setup guidance and formatter helpers.
- `resources/lib/wizard.py` — surfaces player hardware class guidance after model selection without changing settings or playback flow.
- `resources/lib/hardware_validation_readiness.py` — includes player guidance, hardware-validation-required status, and NAS readiness guidance in exported reports.
- `resources/language/resource.language.*/strings.po` — updates the hardware model help text while preserving localization IDs.
- `resources/lib/version.py` — v2.9.10 Build 4 identity.
- `addon.xml` — v2.9.10 Build 4 metadata while preserving Build 3/2/1 lineage.
- `docs/sources.yaml`, `README.md`, `reference.md`, `web-references.md` — Build 4 documentation metadata and notes.
- `scripts/package_release.sh` — default build suffix updated to build4.
- `tests/test_v2910_build4_player_wizard_readiness.py` — Build 4 regression tests.
- `release-evidence/v2.9.10-build4/MANIFEST.txt` — Build 4 evidence manifest.

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

No real hardware validation was performed or claimed. Wording and readiness exports are software guidance only until a tester records real device results.

## Reconstruction instructions

Start from `script.oppo203.iso.external-2.9.10-build3-dev-source.zip`, add the Build 4 wording/readiness changes, update version/docs/package metadata to v2.9.10 Build 4, add Build 4 tests and evidence, then run source and post-unpack verification separately.


## Verification

```text
Source py_compile/render_docs/sync_version/test_layout/i18n_extract: passed
Source targeted Build 4 tests: 7 passed
Source targeted v2.9.10 Build 1-4 tests: 34 passed
Source pytest split run: 788 passed, 12 subtests passed
Source unittest discovery: 571 tests OK
Source coverage: TOTAL 99%
Source release audit: PASS 394/394
Runtime ZIP audit: passed; 53 runtime files; forbidden dev/evidence files: 0
Post-unpack targeted Build 4 tests: 7 passed
Post-unpack pytest split run: 788 passed, 12 subtests passed
Post-unpack unittest discovery: 571 tests OK
Post-unpack coverage: TOTAL 99%
Post-unpack release audit: PASS 394/394
```
