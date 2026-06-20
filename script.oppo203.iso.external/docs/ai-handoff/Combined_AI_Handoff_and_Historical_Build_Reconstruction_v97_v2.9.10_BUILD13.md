# CURRENT STATUS — v2.9.10 Build 13 Yamaha MusicCast / YXC AVR Driver

Current installable package: `script.oppo203.iso.external-2.9.10-build13.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-build13-dev-source.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build13-artifacts-bundle.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 13`
Baseline: `script.oppo203.iso.external-2.9.10-build12-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 13 summary

v2.9.10 Build 13 adds guarded Yamaha MusicCast/YXC HTTP command support behind the disabled-by-default AVR framework. It preserves the Build 12 Denon/Marantz driver and leaves all remaining AVR families metadata-only.

Implemented:

- Added `resources/lib/avr_yamaha.py`.
- Added Yamaha HTTP GET helpers for:
  - `/YamahaExtendedControl/v1/main/setPower?power=on`
  - `/YamahaExtendedControl/v1/main/setInput?input=<input>`
  - `/YamahaExtendedControl/v1/main/getStatus`
- Parses JSON `response_code`.
- Returns non-fatal `AvrResult` objects on non-zero response codes, invalid JSON, timeout, network failure, invalid input, and unsupported action paths.
- Keeps AVR disabled by default.
- Keeps AVR power-off disabled by default.
- Keeps volume automation disabled by default.
- Does not hook AVR into playback sequencing.
- Does not claim hardware validation.

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV diagnostics/dry-run behavior, SmartThings experimental guardrails, Roku ECP backend behavior, Android / Google TV ADB preset metadata, runtime ZIP policy, or 99% coverage gate changed.

## Files changed or added

Added:

```text
resources/lib/avr_yamaha.py
tests/test_v2910_build13_yamaha_yxc_avr.py
release-evidence/v2.9.10-build13/MANIFEST.txt
BUILD_NOTES_v2.9.10_BUILD13.md
RELEASE_MANIFEST_v2.9.10_BUILD13.md
RELEASE_NOTES_v2.9.10_BUILD13.md
COVERAGE_REPORT_v2.9.10_BUILD13.md
TEST_AUDIT_REPORT_v2.9.10_BUILD13.md
HARDWARE_VALIDATION_v2.9.10_BUILD13.md
PRE_HARDWARE_AUDIT_REPORT_v2.9.10_BUILD13.md
HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD13.md
Combined_AI_Handoff_and_Historical_Build_Reconstruction_v97_v2.9.10_BUILD13.md
```

Updated:

```text
resources/lib/avr_control.py
resources/lib/avr_presets.py
resources/lib/avr_types.py
resources/lib/version.py
addon.xml
docs/sources.yaml
scripts/package_release.sh
README.md
reference.md
web-references.md
active current-build test expectations
```

## Verification workflow

Use the Build 11 timeout-safe verification strategy:

```text
1. Source checks first.
2. Targeted Build 13 tests.
3. test_all.py shard.
4. Grouped v2.9.10 tests.
5. Grouped v2.9.1 tests.
6. Grouped legacy tests.
7. unittest discovery.
8. coverage shards + coverage combine.
9. audit_release.
```

## Historical reconstruction entry — v2.9.10 Build 13

```yaml
build_id: v2.9.10 Build 13
package: script.oppo203.iso.external-2.9.10-build13.zip
dev_source: script.oppo203.iso.external-2.9.10-build13-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build13-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build12-dev-source.zip
scope: Yamaha MusicCast / YXC AVR driver
planned_success_rate: 83 percent
actual_outcome: successful software build
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
playback_sequencing_hooked: false
```

## Resume prompt for next AI

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 13.

Use this baseline:
script.oppo203.iso.external-2.9.10-build13-dev-source.zip

Next build:
v2.9.10 Build 14 — Onkyo / Integra / Pioneer eISCP AVR driver.

Keep the build narrow. Add Onkyo/Integra/Pioneer eISCP command support only, behind the existing AVR framework. Use TCP port 60128, frame magic ISCP, power-on payload !1PWR01, and input-select payloads !1SLIxx. Build valid eISCP frames, handle malformed response frames safely, keep Integra on the same family driver, keep Pioneer experimental unless verified, return nonfatal AvrResult objects on timeout/network/error/malformed response paths, keep AVR disabled by default, keep AVR power-off disabled by default, keep volume automation disabled by default, and do not hook AVR into playback sequencing yet unless explicitly requested. Preserve Yamaha Build 13 behavior, Denon/Marantz Build 12 behavior, TV diagnostics/dry-run behavior, SmartThings experimental guardrails, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Use the Build 11 timeout-safe verification strategy: run source checks first, then targeted Build 14 tests, then deterministic sharded pytest/unittest/coverage chunks with per-chunk logs instead of one-shot aggregate commands. Run source verification, package, run post-unpack dev-source verification, run runtime ZIP audit, update evidence, update the support matrix, and append the historical reconstruction entry. Keep the resume prompt format consistent between runs.
```
