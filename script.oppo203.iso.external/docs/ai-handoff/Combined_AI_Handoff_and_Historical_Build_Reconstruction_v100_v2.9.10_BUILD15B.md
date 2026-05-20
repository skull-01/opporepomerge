# v2.9.10 Build 15B — Sony AVR experimental request helper and fake API tests

Project: script.oppo203.iso.external
Baseline: script.oppo203.iso.external-2.9.10-build15a-dev-source.zip
Hardware validation: not performed / not claimed
Runtime behavior changed: No OPPO playback/routing behavior changed
AVR playback sequencing hook: not added

Build 15B adds a guarded Sony Audio Control API JSON POST request helper behind the existing disabled-by-default AVR framework. The helper requires explicit experimental acknowledgement before any request is sent, is fakeable for tests, returns nonfatal AvrResult objects for API/network/JSON/error paths, and never exports Sony PSKs, passwords, credentials, tokens, or secrets.

Preserved behavior: OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, TV diagnostics/dry-run behavior, SmartThings experimental guardrails, Roku ECP, Android/Google TV presets, command/custom TV presets, Denon/Marantz, Yamaha, Onkyo/Integra/Pioneer AVR behavior, and no hardware-validation claim.

## Historical reconstruction entry — v2.9.10 Build 15B

```yaml
build_id: v2.9.10 Build 15B
package: script.oppo203.iso.external-2.9.10-build15b.zip
dev_source: script.oppo203.iso.external-2.9.10-build15b-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build15b-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build15a-dev-source.zip
scope: Sony AVR experimental request helper and fake API tests
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Verification summary

- py_compile/render_docs/sync_version/test_layout/i18n_extract: passed.
- Targeted Build 15B tests: 10 passed.
- All v2.9.10 tests: 154 passed.
- Focused AVR Build 11-15B tests: passed.
- Source coverage: TOTAL 99%.
- audit_release: passed.
- Post-unpack dev-source verification: py_compile, targeted Build 15B tests, audit_release.
- Runtime ZIP audit: forbidden dev/evidence files absent.

## Resume prompt for Build 16

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 15B.

Use this baseline:
script.oppo203.iso.external-2.9.10-build15b-dev-source.zip

Next build:
v2.9.10 Build 16 — AVR wizard, diagnostics, and safety UI.

Keep the build narrow. Add AVR setup UI, query-only test actions, diagnostic export, and safety wording. The wizard must support skipping AVR setup, selecting AVR family, entering AVR host/IP and port, entering OPPO/player AVR input, optional restore input, optional sound mode metadata, and Sony experimental acknowledgement. AVR support must remain disabled by default. Query-only test actions must not change AVR state. Power/input test actions must require explicit user action. Diagnostics must sanitize credentials and must state hardware_validation_claimed=false. Do not hook AVR into playback sequencing yet unless explicitly requested.

Preserve Sony Build 15A/15B experimental guardrails, Onkyo/Integra/Pioneer Build 14 behavior, Yamaha Build 13 behavior, Denon/Marantz Build 12 behavior, TV diagnostics/dry-run behavior, SmartThings experimental guardrails, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Use the shortened Balanced Gate verification strategy:
1. Run source checks first: py_compile, render_docs --check, sync_version --check, test_layout.py --check, and i18n_extract.py --check.
2. Run targeted Build 16 tests.
3. Run all v2.9.10 tests.
4. Run focused AVR wizard/diagnostics regression tests only.
5. Run source coverage only and preserve TOTAL 99%.
6. Run audit_release.
7. Package runtime ZIP, dev-source ZIP, artifact bundle, and SHA256.
8. Post-unpack dev-source verification should run py_compile, targeted Build 16 tests, and audit_release only unless a failure requires deeper verification.
9. Run runtime ZIP audit.
10. Do not claim post-unpack full coverage unless it was actually run.

Defer full legacy pytest, full unittest discovery, and full post-unpack coverage to Build 18 regression/audit packaging.

After completion, generate the next resume prompt using this same structure and verification wording.
```
