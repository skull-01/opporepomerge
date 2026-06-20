# CURRENT STATUS — v2.9.10 Build 9A SmartThings Experimental Settings and Acknowledgement Skeleton

Current installable package: `script.oppo203.iso.external-2.9.10-build9a.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build9a-artifacts-bundle.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-build9a-dev-source.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 9A`
Baseline: `script.oppo203.iso.external-2.9.10-build8-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 9A summary

Build 9A safely splits the below-75% SmartThings roadmap item into a metadata/settings skeleton only. It adds `smartthings` backend metadata, experimental preset metadata, acknowledgement settings, token/device/input placeholders, token-redaction helpers, and validation metadata. It does not perform live SmartThings API calls.

## Historical reconstruction entry — v2.9.10 Build 9A

```yaml
build_id: v2.9.10 Build 9A
package: script.oppo203.iso.external-2.9.10-build9a.zip
dev_source: script.oppo203.iso.external-2.9.10-build9a-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build9a-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build8-dev-source.zip
scope: SmartThings experimental settings and acknowledgement skeleton
planned_success_rate: 82 percent
actual_outcome: successful software build
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
live_smartthings_api_calls: disabled
```

## Resume prompt for next AI

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 9A.

Use this baseline:
script.oppo203.iso.external-2.9.10-build9a-dev-source.zip

Next build:
v2.9.10 Build 9B — SmartThings experimental request helper and fake API tests.

Keep the build narrow. Add the guarded SmartThings request helper and fake API tests only. Require explicit experimental acknowledgement, never log/export tokens, handle HTTP 401/403 safely, preserve non-fatal behavior, and keep hardware validation unclaimed. Preserve existing TV backend registry APIs, SmartThings 9A metadata/settings, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, AVR sequencing, runtime ZIP policy, and the 99% coverage gate.
```

---

# CURRENT STATUS — v2.9.10 Build 8 Command TV Preset Polish

Current installable package: `script.oppo203.iso.external-2.9.10-build8.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build8-artifacts-bundle.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-build8-dev-source.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 8`
Baseline: `script.oppo203.iso.external-2.9.10-build7-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 8 summary

v2.9.10 Build 8 polishes the software-only command/custom TV preset layer for LG, Samsung, Panasonic, Vizio, and generic custom-command users while preserving the Build 5 TV backend registry foundation, Build 6 Android / Google TV ADB preset metadata, Build 7 Roku TV ECP backend, and all protected OPPO external-player behavior.

Implemented:

- Added explicit command/custom preset IDs: `lg_webos_command`, `samsung_command`, `panasonic_custom_command`, `vizio_custom_command`, and `generic_custom_command`.
- Preserved existing LG and Samsung command compatibility presets.
- Added command preset metadata fields for editable command templates, `{tv_ip}` placeholder support, missing-command validation warnings, non-fatal playback-flow stance, and no native protocol expansion.
- Added command preset list and support-matrix helpers in `resources/lib/tv_presets.py`.
- Updated Build 8 metadata, docs, evidence, support matrix, and tests.

No OPPO playback routing, service interception, `playercorefactory.xml` behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, Roku ECP behavior, Android / Google TV ADB preset metadata, TV-switching non-fatal behavior, AVR sequencing, runtime ZIP policy, or hardware-validation posture changed.

## Files changed or added

- Updated `resources/lib/tv_presets.py`.
- Updated `resources/lib/version.py` to `BUILD_ID = "v2.9.10 Build 8"` and `BUILD_NUMBER = 8`.
- Updated `docs/sources.yaml` and rendered docs metadata.
- Updated `scripts/package_release.sh` default suffix to `build8`.
- Updated `addon.xml`, README, reference, and web references.
- Added `tests/test_v2910_build8_command_tv_presets.py`.
- Updated active current-build expectations in inherited tests.
- Added Build 8 evidence files:
  - `BUILD_NOTES_v2.9.10_BUILD8.md`
  - `RELEASE_MANIFEST_v2.9.10_BUILD8.md`
  - `RELEASE_NOTES_v2.9.10_BUILD8.md`
  - `COVERAGE_REPORT_v2.9.10_BUILD8.md`
  - `TEST_AUDIT_REPORT_v2.9.10_BUILD8.md`
  - `HARDWARE_VALIDATION_v2.9.10_BUILD8.md`
  - `PRE_HARDWARE_AUDIT_REPORT_v2.9.10_BUILD8.md`
  - `HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD8.md`
- Added `release-evidence/v2.9.10-build8/MANIFEST.txt`.

## Verification evidence

Source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 8 tests: 7 passed
pytest split run: 819 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 430/430
```

Post-unpack dev-source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 8 tests: 7 passed
pytest split run: 819 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 430/430
```

Runtime ZIP audit:

```text
runtime files: 56
forbidden tests/tools/scripts/docs/release-evidence/reports/handoff/evidence files: 0
zip integrity: passed
```

Note: the one-shot aggregate coverage command hit the local execution timeout, so coverage was completed through the established split/combined coverage workflow. All split test chunks passed.

## Historical reconstruction entry — v2.9.10 Build 8

```yaml
build_id: v2.9.10 Build 8
package: script.oppo203.iso.external-2.9.10-build8.zip
dev_source: script.oppo203.iso.external-2.9.10-build8-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build8-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build7-dev-source.zip
scope: Command TV preset polish
planned_success_rate: 86 percent
actual_outcome: successful software build
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Reconstruction instructions

To reconstruct Build 8 from Build 7:

1. Start from `script.oppo203.iso.external-2.9.10-build7-dev-source.zip`.
2. Update `resources/lib/tv_presets.py` with explicit Build 8 command/custom preset metadata for LG webOS command, Samsung command, Panasonic custom command, Vizio custom command, and generic custom command.
3. Preserve existing LG and Samsung command compatibility preset IDs.
4. Ensure command/custom presets remain editable, software-only, non-fatal in playback flow, and marked as not hardware validated.
5. Preserve `{tv_ip}` placeholder support and missing-command validation-warning metadata.
6. Do not add native LG, Samsung, Panasonic, Vizio, or other live protocol expansion in Build 8.
7. Update version/build metadata to Build 8 and package suffix defaults to `build8`.
8. Update docs metadata and run `python3 tools/render_docs.py --root . --write`.
9. Add Build 8 tests, release evidence, and release-evidence manifest.
10. Run source and post-unpack verification separately.
11. Package with the allowlist runtime ZIP policy; do not include tests, tools, scripts, docs, release evidence, reports, handoff files, or Markdown evidence in the installable ZIP.

## Remaining work

Next build should be split because the original SmartThings experimental backend estimate is below the 75% threshold.

Recommended next build: `v2.9.10 Build 9A — SmartThings experimental settings and acknowledgement skeleton`.

## Resume prompt for next AI

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 8.

Use this baseline:
script.oppo203.iso.external-2.9.10-build8-dev-source.zip

Next build:
v2.9.10 Build 9A — SmartThings experimental settings and acknowledgement skeleton.

Keep the build narrow because the full SmartThings backend is a below-75% risk item in the v2.9.10 roadmap. Add only experimental SmartThings preset/backend metadata, settings placeholders, explicit experimental acknowledgement gating, token-redaction helpers or validation metadata, documentation, support-matrix entries, and tests. Do not perform live SmartThings API calls in Build 9A. Preserve existing TV backend registry APIs, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, ADB command editability, non-fatal TV switching behavior, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, AVR sequencing, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Run source verification, package, run post-unpack dev-source verification, run runtime ZIP audit, update evidence, update the support matrix, and append the historical reconstruction entry.
```

---

# Previous handoff content preserved below

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
