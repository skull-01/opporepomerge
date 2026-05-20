# CURRENT STATUS — v2.9.10 Build 17 Unified TV + AVR Playback Sequencing

Current installable package: `script.oppo203.iso.external-2.9.10-build17.zip`
Current dev-source package: `script.oppo203.iso.external-2.9.10-build17-dev-source.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build17-artifacts-bundle.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 17`
Baseline: `script.oppo203.iso.external-2.9.10-build16-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 17 summary

Build 17 safely hooks optional TV and AVR pre/post sequencing into the external-player flow. It adds a non-throwing AVR sequence helper and calls it from the external-player wrapper while preserving OPPO playback routing and existing TV restore behavior.

Implemented:

- Added `resources/lib/avr_sequence.py`.
- Updated `resources/lib/external_player.py` so startup order is TV switch-to-OPPO, optional AVR pre-playback sequencing, then OPPO/external-player start.
- Updated return order so OPPO stop commands run first, optional AVR restore runs only when enabled/configured, and existing TV switch-back continues to run.
- Updated AVR metadata to state `playback_sequencing_hooked=true` while keeping hardware validation unclaimed.
- Added Build 17 sequencing tests and updated current v2.9.10 active-build expectations.

Preserved: startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, Build 16 wizard/diagnostics safety behavior, Sony experimental guardrails, Denon/Marantz, Yamaha, Onkyo/Integra/Pioneer, Roku, SmartThings, Android/Google TV, command/custom TV preset behavior, runtime ZIP policy, 99% coverage gate, and no hardware-validation claim.

## Historical reconstruction entry — v2.9.10 Build 17

```yaml
build_id: v2.9.10 Build 17
package: script.oppo203.iso.external-2.9.10-build17.zip
dev_source: script.oppo203.iso.external-2.9.10-build17-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build17-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build16-dev-source.zip
scope: unified TV + AVR playback sequencing
planned_success_rate: 76 percent
actual_outcome: successful software build
hardware_validation: not_performed_not_claimed
post_unpack_full_coverage_claimed: false
```

## Resume prompt for Build 18

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 17.

Use this baseline:
script.oppo203.iso.external-2.9.10-build17-dev-source.zip

Next build:
v2.9.10 Build 18 — Regression, audit, and packaging candidate.

Use the Full Release Gate. Run full source verification, full legacy pytest, full unittest discovery, full coverage, audit_release, packaging, full post-unpack dev-source verification including coverage, runtime ZIP audit, and release-candidate evidence updates. Preserve Build 17 unified TV + AVR playback sequencing, AVR disabled no-op behavior, AVR/TV nonfatal failure behavior, optional AVR restore guard, existing TV restore, startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim unless real tester results are provided.
```

---

# Previous handoff content preserved below

# v2.9.10 Build 16 — AVR wizard, diagnostics, and safety UI

v2.9.10 Build 16 adds AVR setup UI helpers, query-only AVR test actions, explicit user-action gates for power/input tests, sanitized AVR diagnostic export, and safety wording. AVR support remains disabled by default, AVR power-off and volume automation remain disabled by default, no AVR playback sequencing hook is added, diagnostics sanitize credentials and state hardware_validation_claimed=false, and hardware validation is not claimed.

## Historical reconstruction entry — v2.9.10 Build 16

```yaml
build_id: v2.9.10 Build 16
package: script.oppo203.iso.external-2.9.10-build16.zip
dev_source: script.oppo203.iso.external-2.9.10-build16-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build16-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build15b-dev-source.zip
scope: AVR wizard, diagnostics, and safety UI
verification_strategy: Balanced Gate
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Files added

- `resources/lib/avr_diagnostics.py`
- `tests/test_v2910_build16_avr_wizard_diagnostics.py`
- `release-evidence/v2.9.10-build16/MANIFEST.txt`
- Build 16 release evidence files.

## Verification summary

```text
source checks: passed
targeted Build 16 tests: 15 passed
all v2.9.10 tests: 167 passed
focused AVR wizard/diagnostics regression tests: 15 passed
source coverage: TOTAL 99%
audit_release: PASS 525/525
```

## Resume prompt for Build 17

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 16.

Use this baseline:
script.oppo203.iso.external-2.9.10-build16-dev-source.zip

Next build:
v2.9.10 Build 17 — Unified TV + AVR playback sequencing.

Keep the build narrow. Hook optional TV and AVR pre/post sequencing into the external-player flow safely. AVR sequencing must run only for eligible OPPO/external-player handoff. AVR disabled path must be a no-op. AVR and TV failures must not block playback. Optional AVR restore must run only if enabled. Existing TV restore must continue to work. Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, and loose/raw file exclusion must remain unchanged.

Preserve AVR wizard/diagnostics Build 16 behavior, Sony Build 15A/15B experimental guardrails, Onkyo/Integra/Pioneer Build 14 behavior, Yamaha Build 13 behavior, Denon/Marantz Build 12 behavior, TV diagnostics/dry-run behavior, SmartThings experimental guardrails, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Use the shortened Balanced Gate verification strategy:
1. Run source checks first: py_compile, render_docs --check, sync_version --check, test_layout.py --check, and i18n_extract.py --check.
2. Run targeted Build 17 tests.
3. Run all v2.9.10 tests.
4. Run focused playback-sequencing regression tests only, including OPPO handoff eligibility, AVR disabled no-op, TV failure nonfatal, AVR failure nonfatal, and restore conditions.
5. Run source coverage only and preserve TOTAL 99%.
6. Run audit_release.
7. Package runtime ZIP, dev-source ZIP, artifact bundle, and SHA256.
8. Post-unpack dev-source verification should run py_compile, targeted Build 17 tests, and audit_release only unless a failure requires deeper verification.
9. Run runtime ZIP audit.
10. Do not claim post-unpack full coverage unless it was actually run.

Defer full legacy pytest, full unittest discovery, and full post-unpack coverage to Build 18 regression/audit packaging.

After completion, generate the next resume prompt using this same structure, but switch Build 18 to the Full Release Gate.

```
