# CURRENT STATUS — v2.9.10 Build 10 TV Diagnostics and Dry-Run Validator

Current installable package: `script.oppo203.iso.external-2.9.10-build10.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-build10-artifacts-bundle.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-build10-dev-source.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Build 10`
Baseline: `script.oppo203.iso.external-2.9.10-build9b-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Build 10 summary

Build 10 adds the TV diagnostics and dry-run validator slice. It introduces `resources/lib/tv_diagnostics.py` for selected TV backend validation, network-free dry-run reports, explicit switch test action helpers, and sanitized diagnostic report export.

Dry-run reports do not contact TVs, ADB, Roku ECP, Sony Bravia APIs, SmartThings, or shell commands. The explicit switch test helpers are separate actions and return non-fatal sanitized results. Diagnostic reports redact SmartThings tokens, Sony PSKs, passwords, credentials, secrets, and command output fields. Reports always include `hardware_validation_claimed=false`.

No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, AVR sequencing, runtime ZIP policy, or hardware-control baseline behavior changed.

## Files changed or added

Added:

```text
resources/lib/tv_diagnostics.py
tests/test_v2910_build10_tv_diagnostics.py
release-evidence/v2.9.10-build10/MANIFEST.txt
BUILD_NOTES_v2.9.10_BUILD10.md
RELEASE_MANIFEST_v2.9.10_BUILD10.md
RELEASE_NOTES_v2.9.10_BUILD10.md
COVERAGE_REPORT_v2.9.10_BUILD10.md
TEST_AUDIT_REPORT_v2.9.10_BUILD10.md
HARDWARE_VALIDATION_v2.9.10_BUILD10.md
PRE_HARDWARE_AUDIT_REPORT_v2.9.10_BUILD10.md
HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD10.md
Combined_AI_Handoff_and_Historical_Build_Reconstruction_v94_v2.9.10_BUILD10.md
```

Updated:

```text
resources/lib/version.py
docs/sources.yaml
scripts/package_release.sh
addon.xml
README.md
reference.md
web-references.md
active current-build test expectations
```

## Verification evidence

Source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 10 tests: 8 passed
v2.9.10 targeted suite: 96 passed
pytest split/file-by-file run: 842 passed, 12 subtests passed
unittest split/file-by-file run: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 457/457
```

Post-unpack dev-source verification:

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
targeted Build 10 tests: 8 passed
v2.9.10 targeted suite: 96 passed
audit_release: PASS 457/457
```

Runtime ZIP audit:

```text
runtime files: 58
forbidden dev/evidence files: 0
zip integrity: passed
tv_diagnostics.py included: yes
```

## Historical reconstruction entry — v2.9.10 Build 10

```yaml
build_id: v2.9.10 Build 10
package: script.oppo203.iso.external-2.9.10-build10.zip
dev_source: script.oppo203.iso.external-2.9.10-build10-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build10-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build9b-dev-source.zip
scope: TV diagnostics and dry-run validator
planned_success_rate: 85 percent
actual_outcome: successful software build
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Reconstruction instructions

To reconstruct Build 10 from Build 9B:

1. Start from `script.oppo203.iso.external-2.9.10-build9b-dev-source.zip`.
2. Add `resources/lib/tv_diagnostics.py` with selected-backend validation, dry-run reporting, sanitized explicit switch test helpers, and report export helpers.
3. Ensure dry-run reporting never performs network, shell, ADB, Roku, Sony Bravia, or SmartThings calls.
4. Ensure reports redact SmartThings tokens, Sony PSKs, passwords, credentials, secrets, and command output.
5. Add `tests/test_v2910_build10_tv_diagnostics.py`.
6. Update version/build metadata to `v2.9.10 Build 10`, package suffix `build10`, generated docs metadata, README, reference, web references, addon metadata, evidence files, and support matrix.
7. Run source verification, package, run post-unpack verification, audit runtime ZIP cleanliness, and keep hardware validation unclaimed.

## Resume prompt for Build 11

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 10.

Use this baseline:
script.oppo203.iso.external-2.9.10-build10-dev-source.zip

Next build:
v2.9.10 Build 11 — AVR framework and settings skeleton.

Keep the build narrow. Add a generic AVR framework and settings skeleton without real brand command execution. AVR control must be disabled by default, AVR power-off must remain disabled by default, volume automation must remain disabled by default, and AVR failures must warn/continue. Add a controller factory or no-op path that returns no controller when AVR is disabled, reject incomplete AVR config safely, add AVR preset lookup metadata only, and do not hook AVR into playback sequencing yet. Preserve existing TV diagnostics/dry-run behavior, SmartThings experimental guardrails, command/custom TV presets, Roku ECP backend behavior, Android / Google TV ADB preset metadata, OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim.

Run source verification, package, run post-unpack dev-source verification, run runtime ZIP audit, update evidence, update the support matrix, and append the historical reconstruction entry.
```

---

# Previous handoff content preserved below

See `Combined_AI_Handoff_and_Historical_Build_Reconstruction_v93_v2.9.10_BUILD9B.md` for the complete previous historical archive through Build 9B.
