# CURRENT STATUS — v2.9.10 Build 6 Android / Google TV Preset Pack

Current installable package: `script.oppo203.iso.external-2.9.10-build6.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build6-artifacts-bundle.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-build6-dev-source.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 6`
Baseline: `script.oppo203.iso.external-2.9.10-build5-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 6 summary

v2.9.10 Build 6 adds the Android / Google TV preset pack on top of the Build 5 TV backend registry and preset foundation.

Implemented:

- Added editable ADB software preset metadata for `tcl_android_tv`, `sony_android_tv`, `hisense_android_tv`, `philips_android_tv`, `xiaomi_android_tv`, `sharp_android_tv`, `skyworth_android_tv`, `haier_android_tv`, and `generic_android_tv`.
- Kept all Android / Google TV presets on the preserved `adb` backend.
- Kept ADB command fields editable through `oppo_input_adb_shell` and `kodi_input_adb_shell`.
- Added registry metadata proving that no universal ADB HDMI command is claimed.
- Updated Build 6 metadata, docs, evidence, support matrix, and tests.

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV switching execution semantics, AVR sequencing, or hardware-control behavior changed.

## Files changed or added

- Updated `resources/lib/tv_presets.py`.
- Updated `resources/lib/version.py` to `BUILD_ID = "v2.9.10 Build 6"` and `BUILD_NUMBER = 6`.
- Updated `docs/sources.yaml` for Build 6 generated documentation metadata.
- Updated `scripts/package_release.sh` default build suffix to `build6`.
- Updated `addon.xml`, README, reference, and web references.
- Updated active current-build expectations in inherited v2.9.1/v2.9.10 tests.
- Added `tests/test_v2910_build6_android_tv_presets.py`.
- Added Build 6 evidence files:
  - `BUILD_NOTES_v2.9.10_BUILD6.md`
  - `RELEASE_MANIFEST_v2.9.10_BUILD6.md`
  - `RELEASE_NOTES_v2.9.10_BUILD6.md`
  - `COVERAGE_REPORT_v2.9.10_BUILD6.md`
  - `TEST_AUDIT_REPORT_v2.9.10_BUILD6.md`
  - `HARDWARE_VALIDATION_v2.9.10_BUILD6.md`
  - `PRE_HARDWARE_AUDIT_REPORT_v2.9.10_BUILD6.md`
  - `HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD6.md`
- Added `release-evidence/v2.9.10-build6/MANIFEST.txt`.

## Verification evidence

Source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
type_check.py: passed / non-blocking skip when mypy unavailable
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 6 tests: 7 passed
pytest split run: 802 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 412/412
```

Post-unpack dev-source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 6 tests: 7 passed
pytest split run: 802 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 412/412
```

Runtime ZIP audit:

```text
runtime files: 55
forbidden tests/tools/scripts/docs/release-evidence/reports/handoff/evidence files: 0
zip integrity: passed
```

## Historical reconstruction entry — v2.9.10 Build 6

```yaml
build_id: v2.9.10 Build 6
package: script.oppo203.iso.external-2.9.10-build6.zip
dev_source: script.oppo203.iso.external-2.9.10-build6-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build6-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build5-dev-source.zip
scope: Android / Google TV preset pack
planned_success_rate: 82 percent
actual_outcome: successful
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Reconstruction instructions

To reconstruct Build 6 from Build 5:

1. Start from `script.oppo203.iso.external-2.9.10-build5-dev-source.zip`.
2. Update `resources/lib/tv_presets.py` to add the nine Android / Google TV ADB software presets listed above.
3. Keep all Android / Google TV presets editable, software-only, hardware-validation-required, and `adb`-backend based.
4. Keep `oppo_input_adb_shell` and `kodi_input_adb_shell` as the editable command fields; do not auto-apply a universal HDMI command.
5. Update version/build metadata to Build 6 and package suffix defaults to `build6`.
6. Update docs metadata and run `python3 tools/render_docs.py --root . --write`.
7. Add Build 6 tests, release evidence, and release-evidence manifest.
8. Run source and post-unpack verification separately.
9. Package with the allowlist runtime ZIP policy; do not include tests, tools, scripts, docs, release evidence, reports, handoff files, or Markdown evidence in the installable ZIP.

## Remaining work

Next build: `v2.9.10 Build 7 — Roku TV ECP backend`.

## Resume prompt for next AI

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 6.

Use this baseline:
script.oppo203.iso.external-2.9.10-build6-dev-source.zip

Next build:
v2.9.10 Build 7 — Roku TV ECP backend.

Keep the build narrow. Add local Roku ECP HTTP input-switching backend support with default port 8060, HTTP POST to /keypress/<key>, strict key allowlisting to prevent URL path injection, software-only Roku TV presets, and non-fatal failure handling. Preserve existing TV backend registry APIs, existing Android / Google TV ADB preset metadata, existing ADB command editability, existing non-fatal TV switching behavior, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, AVR sequencing, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Run source verification, package, run post-unpack dev-source verification, run runtime ZIP audit, update evidence, update the support matrix, and append the historical reconstruction entry.
```

## Protected behavior for Build 7

The next AI must preserve:

```text
- Existing TV backend registry APIs.
- Existing Android / Google TV ADB preset metadata.
- Existing ADB command editability.
- Existing non-fatal TV switching behavior.
- OPPO playback routing.
- Service interception.
- playercorefactory.xml behavior.
- NAS / AutoScript behavior.
- OPPO command-map payloads.
- Startup auto-power behavior.
- AVR sequencing.
- Runtime ZIP policy.
- 99% coverage gate.
- No hardware-validation claim.
```

---

# Previous handoff content preserved below

See `Combined_AI_Handoff_and_Historical_Build_Reconstruction_v88_v2.9.10_BUILD5.md` for the full historical reconstruction through Build 5.
