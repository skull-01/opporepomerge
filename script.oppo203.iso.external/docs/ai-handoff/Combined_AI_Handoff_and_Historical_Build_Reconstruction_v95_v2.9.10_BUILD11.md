# CURRENT STATUS — v2.9.10 Build 11 AVR Framework and Settings Skeleton

Current installable package: `script.oppo203.iso.external-2.9.10-build11.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build11-artifacts-bundle.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-build11-dev-source.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 11`
Baseline: `script.oppo203.iso.external-2.9.10-build10-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 11 summary

Build 11 starts the AVR phase with a disabled-by-default framework and settings skeleton. It adds metadata-only AVR family presets, non-fatal AVR result/validation objects, safe settings defaults, and a controller factory that returns no controller while AVR control is disabled. It does not execute Denon/Marantz, Yamaha, Onkyo/Integra/Pioneer, or Sony AVR commands and does not hook AVR control into playback sequencing.

## Files changed or added

Added:

```text
resources/lib/avr_types.py
resources/lib/avr_presets.py
resources/lib/avr_control.py
tests/test_v2910_build11_avr_framework.py
release-evidence/v2.9.10-build11/MANIFEST.txt
BUILD_NOTES_v2.9.10_BUILD11.md
RELEASE_MANIFEST_v2.9.10_BUILD11.md
RELEASE_NOTES_v2.9.10_BUILD11.md
COVERAGE_REPORT_v2.9.10_BUILD11.md
TEST_AUDIT_REPORT_v2.9.10_BUILD11.md
HARDWARE_VALIDATION_v2.9.10_BUILD11.md
PRE_HARDWARE_AUDIT_REPORT_v2.9.10_BUILD11.md
HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD11.md
```

Updated:

```text
resources/lib/settings_reader.py
resources/lib/settings_schema.py
resources/lib/hardware_profiles.py
resources/settings.xml
resources/language/*/strings.po
resources/lib/version.py
docs/sources.yaml
scripts/package_release.sh
addon.xml
README.md
reference.md
web-references.md
active current-build test expectations
```

## Preserved behavior

```text
TV diagnostics / dry-run behavior
SmartThings experimental guardrails
command/custom TV presets
Roku ECP backend behavior
Android / Google TV ADB preset metadata
OPPO playback routing
service interception
playercorefactory.xml behavior
NAS / AutoScript behavior
OPPO command-map payloads
startup auto-power behavior
runtime ZIP policy
99% coverage gate
no hardware-validation claim
```

## Verification evidence

Source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 11 tests: 10 passed
pytest sharded total: 860 passed, 12 subtests passed
unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 466/466
```

Post-unpack dev-source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 11 tests: 10 passed
pytest sharded total: 860 passed, 12 subtests passed
unittest discovery: 571 tests OK
audit_release: PASS 466/466
```

Runtime ZIP audit:

```text
runtime files: 61
forbidden dev/evidence files: 0
zip integrity: passed
AVR framework runtime modules included: yes
```

## Historical reconstruction entry — v2.9.10 Build 11

```yaml
build_id: v2.9.10 Build 11
package: script.oppo203.iso.external-2.9.10-build11.zip
dev_source: script.oppo203.iso.external-2.9.10-build11-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build11-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build10-dev-source.zip
scope: AVR framework and settings skeleton
planned_success_rate: 88 percent
actual_outcome: successful
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
avr_driver_execution_added: false
playback_sequencing_hooked: false
```

## Reconstruction instructions

Start from `script.oppo203.iso.external-2.9.10-build10-dev-source.zip`. Add the three AVR skeleton modules, add AVR defaults/enums/settings XML/strings, add metadata-only AVR presets, update version/docs/evidence to Build 11, add `tests/test_v2910_build11_avr_framework.py`, update active current-build expectations, run the sharded verification workflow, and package with the allowlist runtime ZIP policy. Do not add AVR command execution or playback sequencing in Build 11.

## Resume prompt for Build 12

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 11.

Use this baseline:
script.oppo203.iso.external-2.9.10-build11-dev-source.zip

Next build:
v2.9.10 Build 12 — Denon / Marantz AVR driver.

Keep the build narrow. Add Denon/Marantz Telnet-style AVR command support only, behind the existing Build 11 AVR framework. Use PWON for power on, SI<input> for input selection, and query helpers such as PW? / SI? where supported. Open and close a socket per command, use short timeouts, return nonfatal AvrResult objects on timeout/network/error responses, keep AVR disabled by default, keep AVR power-off disabled by default, keep volume automation disabled by default, and do not hook AVR into playback sequencing yet unless explicitly requested. Preserve existing TV diagnostics/dry-run behavior, SmartThings experimental guardrails, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Use the Build 11 timeout-safe verification strategy: run source checks first, then targeted Build 12 tests, then deterministic sharded pytest/unittest/coverage chunks with per-chunk logs instead of one-shot aggregate commands. Run source verification, package, run post-unpack dev-source verification, run runtime ZIP audit, update evidence, update the support matrix, and append the historical reconstruction entry.
```
