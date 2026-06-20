# CURRENT STATUS — v2.9.10 Build 7 Roku TV ECP Backend

Current installable package: `script.oppo203.iso.external-2.9.10-build7.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build7-artifacts-bundle.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-build7-dev-source.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 7`
Baseline: `script.oppo203.iso.external-2.9.10-build6-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 7 summary

v2.9.10 Build 7 adds a local Roku TV ECP backend and Roku software preset metadata while preserving the existing OPPO external-player flow and the non-fatal TV switching design.

Implemented:

- Added `resources/lib/roku_ecp_control.py`.
- Added `roku_ecp` to the TV backend registry.
- Added local HTTP POST to `/keypress/<key>` with default port `8060`.
- Added strict allowlisted Roku input keys before URL construction to prevent path/query injection.
- Added editable Roku TV software presets: `roku_tv`, `tcl_roku_tv`, `hisense_roku_tv`, and `generic_roku_tv`.
- Added settings defaults for `roku_ecp_port`, `roku_oppo_key`, and `roku_kodi_key`.
- Updated Build 7 docs, evidence, support matrix, version metadata, and tests.

No OPPO playback routing, service interception, `playercorefactory.xml` behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, Android / Google TV ADB preset metadata, AVR sequencing, runtime ZIP policy, or hardware-validation posture changed.

## Files changed or added

- Added `resources/lib/roku_ecp_control.py`.
- Updated `resources/lib/tv_backends.py`.
- Updated `resources/lib/tv_control.py`.
- Updated `resources/lib/tv_presets.py`.
- Updated `resources/lib/settings_reader.py`.
- Updated `resources/settings.xml` and language `strings.po` files for Roku settings labels/help.
- Updated `resources/lib/version.py` to `BUILD_ID = "v2.9.10 Build 7"` and `BUILD_NUMBER = 7`.
- Updated `docs/sources.yaml` and rendered docs metadata.
- Updated `scripts/package_release.sh` default suffix to `build7`.
- Updated `addon.xml`, README, reference, and web references.
- Added `tests/test_v2910_build7_roku_ecp_backend.py`.
- Updated active current-build expectations in inherited tests.
- Added Build 7 evidence files and `release-evidence/v2.9.10-build7/MANIFEST.txt`.

## Verification evidence

Source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 7 tests: 10 passed
pytest split run: 812 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 421/421
```

Post-unpack verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 7 tests: 10 passed
pytest split run: 812 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 421/421
```

Runtime ZIP audit:

```text
runtime files: 56
forbidden tests/tools/scripts/docs/release-evidence/reports/handoff/evidence files: 0
zip integrity: passed
```

## Historical reconstruction entry — v2.9.10 Build 7

```yaml
build_id: v2.9.10 Build 7
package: script.oppo203.iso.external-2.9.10-build7.zip
dev_source: script.oppo203.iso.external-2.9.10-build7-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build7-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build6-dev-source.zip
scope: Roku TV ECP backend
planned_success_rate: 78 percent
actual_outcome: successful software build
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Reconstruction instructions

To reconstruct Build 7 from Build 6:

1. Start from `script.oppo203.iso.external-2.9.10-build6-dev-source.zip`.
2. Add `resources/lib/roku_ecp_control.py` with default port `8060`, local HTTP POST to `/keypress/<key>`, strict key allowlisting, and safe error handling.
3. Add `roku_ecp` metadata to `resources/lib/tv_backends.py` with target settings `roku_oppo_key` and `roku_kodi_key`.
4. Update `resources/lib/tv_control.py` to dispatch `roku_ecp` through the new helper while preserving non-fatal handling in `external_player.py`.
5. Add Roku TV software presets in `resources/lib/tv_presets.py`.
6. Add settings defaults and UI entries for Roku ECP port and input keys.
7. Update version/build metadata to Build 7 and package suffix defaults to `build7`.
8. Update docs metadata and run `python3 tools/render_docs.py --root . --write`.
9. Add Build 7 tests, release evidence, and release-evidence manifest.
10. Run source and post-unpack verification separately.
11. Package with the allowlist runtime ZIP policy; do not include tests, tools, scripts, docs, release evidence, reports, handoff files, or Markdown evidence in the installable ZIP.

## Resume prompt for next AI

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 7.

Use this baseline:
script.oppo203.iso.external-2.9.10-build7-dev-source.zip

Next build:
v2.9.10 Build 8 — Command TV preset polish.

Keep the build narrow. Improve LG, Samsung, Panasonic, Vizio, and generic command/custom TV presets without adding risky native protocol expansion. Preserve existing TV backend registry APIs, Roku ECP backend behavior, Android / Google TV ADB preset metadata, ADB command editability, non-fatal TV switching behavior, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, AVR sequencing, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Run source verification, package, run post-unpack dev-source verification, run runtime ZIP audit, update evidence, update the support matrix, and append the historical reconstruction entry.
```
