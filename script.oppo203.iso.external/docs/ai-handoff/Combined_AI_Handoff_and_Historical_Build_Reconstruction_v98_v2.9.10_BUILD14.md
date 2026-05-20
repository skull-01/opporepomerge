# CURRENT STATUS — v2.9.10 Build 14 Onkyo / Integra / Pioneer eISCP AVR driver

Current installable package: `script.oppo203.iso.external-2.9.10-build14.zip`
Current dev-source package: `script.oppo203.iso.external-2.9.10-build14-dev-source.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build14-artifacts-bundle.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 14`
Baseline: `script.oppo203.iso.external-2.9.10-build13-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 14 summary

Build 14 adds guarded Onkyo / Integra / Pioneer eISCP AVR command support behind the disabled-by-default AVR framework. It uses TCP port 60128, ISCP frame magic, `!1PWR01` power-on payloads, and `!1SLIxx` input-select payloads. It opens and closes a socket per command, handles malformed response frames safely, returns non-fatal `AvrResult` objects, keeps Pioneer experimental/unverified, and does not hook AVR into playback sequencing.

## Files changed or added

- Added `resources/lib/avr_onkyo_eiscp.py`.
- Updated `resources/lib/avr_control.py`.
- Updated `resources/lib/avr_presets.py`.
- Updated `resources/lib/avr_types.py`.
- Added `tests/test_v2910_build14_onkyo_eiscp_avr.py`.
- Updated Build 14 metadata, docs, release evidence, and support matrix.

## Preserved behavior

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV diagnostics/dry-run behavior, SmartThings guardrails, Roku ECP behavior, Android/Google TV ADB preset metadata, runtime ZIP policy, or hardware-validation status changed.

## Verification plan used

Build 14 uses the shortened Balanced Gate strategy: source checks, targeted Build 14 tests, all v2.9.10 tests, focused AVR Build 11-14 regressions, source coverage only, release audit, post-unpack py_compile/targeted/audit, and runtime ZIP audit. Full legacy pytest, full unittest discovery, and full post-unpack coverage are deferred to Build 18.

## Historical reconstruction entry — v2.9.10 Build 14

```yaml
build_id: v2.9.10 Build 14
package: script.oppo203.iso.external-2.9.10-build14.zip
dev_source: script.oppo203.iso.external-2.9.10-build14-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build14-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build13-dev-source.zip
scope: Onkyo / Integra / Pioneer eISCP AVR driver
planned_success_rate: 78 percent
actual_outcome: successful software build
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Resume prompt for Build 15A

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 14.

Use this baseline:
script.oppo203.iso.external-2.9.10-build14-dev-source.zip

Next build:
v2.9.10 Build 15A — Sony AVR experimental driver skeleton.

Keep the build narrow because Sony AVR support is high risk. Add only the Sony Audio Control API experimental skeleton behind the existing AVR framework. Add Sony AVR preset metadata, explicit experimental acknowledgement gating, settings placeholders, validation helpers, sanitized diagnostics metadata, and tests. Do not perform live Sony API calls in Build 15A. The Sony AVR path must refuse to run unless experimental acknowledgement is enabled. Never log or export Sony PSKs, passwords, credentials, tokens, or secrets.

Preserve Onkyo/Integra/Pioneer Build 14 behavior, Yamaha Build 13 behavior, Denon/Marantz Build 12 behavior, TV diagnostics/dry-run behavior, SmartThings experimental guardrails, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Use the shortened Balanced Gate verification strategy:
1. Run source checks first: py_compile, render_docs --check, sync_version --check, test_layout.py --check, and i18n_extract.py --check.
2. Run targeted Build 15A tests.
3. Run all v2.9.10 tests.
4. Run focused AVR regression tests for Build 11–15A only.
5. Run source coverage only and preserve TOTAL 99%.
6. Run audit_release.
7. Package runtime ZIP, dev-source ZIP, artifact bundle, and SHA256.
8. Post-unpack dev-source verification should run py_compile, targeted Build 15A tests, and audit_release only unless a failure requires deeper verification.
9. Run runtime ZIP audit.
10. Do not claim post-unpack full coverage unless it was actually run.

Defer full legacy pytest, full unittest discovery, and full post-unpack coverage to Build 18 regression/audit packaging.

After completion, generate the next resume prompt using this same structure and verification wording.
```
