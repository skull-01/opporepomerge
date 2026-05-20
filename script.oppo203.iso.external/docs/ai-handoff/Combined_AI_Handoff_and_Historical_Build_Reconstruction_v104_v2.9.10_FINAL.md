# CURRENT STATUS — v2.9.10 Final Software-Verified Release Packaging

Current installable package: `script.oppo203.iso.external-2.9.10.zip`
Current artifact bundle: `script.oppo203.iso.external-2.9.10-artifacts-bundle.zip`
Current dev source: `script.oppo203.iso.external-2.9.10-dev-source.zip`
Current add-on version: `2.9.10`
Current build identity: `v2.9.10 Final`
Baseline: `script.oppo203.iso.external-2.9.10-build18-dev-source.zip`
Hardware validation status: not performed and not claimed.

## Final release summary

v2.9.10 Final is the software-verified release packaging build after v2.9.10 Build 18 regression/audit candidate. It adds no new hardware features and preserves the Build 17 unified TV + AVR playback sequencing behavior and the Build 18 Full Release Gate posture.

This is a software-verified release. Real hardware validation was not performed or claimed for OPPO/Chinoppo/Magnetar/Reavon/Kodi/NAS/TV/ADB/Roku/LG/Samsung/Sony/Panasonic/Vizio/AVR paths unless separately recorded from real tester results.

## Preserved behavior

- AVR sequencing runs only for eligible OPPO/external-player handoff.
- AVR disabled path is a no-op.
- AVR and TV failures do not block playback.
- Optional AVR restore runs only if enabled.
- Existing TV restore continues to work.
- Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, and loose/raw file exclusion remain unchanged.
- OPPO playback routing, OPPO command-map payloads, runtime ZIP policy, and 99% coverage gate remain preserved.

## Files changed or added

- Updated `resources/lib/version.py` to `BUILD_ID = "v2.9.10 Final"` and `BUILD_NUMBER = 19`.
- Updated `docs/sources.yaml` to final release metadata.
- Updated `scripts/package_release.sh` so final default artifacts omit a build suffix.
- Updated `addon.xml`, README, reference, and web references for final software-verified release wording.
- Added final release tests in `tests/test_v2910_final_release.py`.
- Updated current-line active identity expectations to v2.9.10 Final.
- Added final evidence files:
  - `BUILD_NOTES_v2.9.10_FINAL.md`
  - `RELEASE_MANIFEST_v2.9.10.md`
  - `RELEASE_NOTES_v2.9.10.md`
  - `COVERAGE_REPORT_v2.9.10.md`
  - `TEST_AUDIT_REPORT_v2.9.10.md`
  - `HARDWARE_VALIDATION_v2.9.10.md`
  - `PRE_HARDWARE_AUDIT_REPORT_v2.9.10.md`
  - `HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10.md`
- Added `release-evidence/v2.9.10-final/MANIFEST.txt`.

## Source verification

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
final targeted tests: 7 passed
all v2.9.10 tests: 189 passed
focused playback sequencing regression tests: 17 passed
full pytest single-process: local timeout before summary
full pytest split run: 943 passed, 12 subtests passed
full unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 553/553
```

## Post-unpack dev-source verification

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
final targeted tests: 7 passed
all v2.9.10 tests: 189 passed
focused playback sequencing regression tests: 17 passed
full pytest split run: 943 passed, 12 subtests passed
full unittest discovery: 571 tests OK
coverage: TOTAL 99%
audit_release: PASS 553/553
```

## Runtime ZIP audit

```text
runtime files: 67
forbidden tests/tools/scripts/docs/release-evidence/reports/handoff/evidence files: 0
zip integrity: passed
```

## Historical reconstruction entry — v2.9.10 Final

```yaml
build_id: v2.9.10 Final
package: script.oppo203.iso.external-2.9.10.zip
dev_source: script.oppo203.iso.external-2.9.10-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build18-dev-source.zip
scope: final software-verified release packaging
planned_success_rate: 90 percent
actual_outcome: successful
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Reconstruction instructions

To reconstruct v2.9.10 Final from Build 18:

1. Start from `script.oppo203.iso.external-2.9.10-build18-dev-source.zip`.
2. Update active version metadata to `v2.9.10 Final` with `BUILD_NUMBER = 19`.
3. Update docs metadata, addon metadata, README, reference, and web references with software-verified final release wording.
4. Update `scripts/package_release.sh` so default final package names are `script.oppo203.iso.external-2.9.10.zip`, `script.oppo203.iso.external-2.9.10-dev-source.zip`, and `script.oppo203.iso.external-2.9.10.sha256`.
5. Add final evidence files and `release-evidence/v2.9.10-final/MANIFEST.txt`.
6. Add final release tests and update current active identity expectations.
7. Run the Final Release Gate from source and from a clean dev-source unpack.
8. Package the runtime ZIP with the allowlist policy.
9. Create the final artifact bundle and SHA256 checksum.
10. Do not claim hardware validation unless separate real tester results are supplied.

## Suggested next prompt — hardware validation phase

```text
Continue from v2.9.10 Final software-verified release.

Use this baseline:
script.oppo203.iso.external-2.9.10-dev-source.zip

Next phase:
User-owned real hardware validation and issue triage.

Do not add features unless hardware testing reveals a specific issue. Use the final runtime ZIP for install testing:
script.oppo203.iso.external-2.9.10.zip

Record real tester results separately for OPPO/Chinoppo/Magnetar/Reavon/Kodi/NAS/TV/ADB/Roku/LG/Samsung/Sony/Panasonic/Vizio/AVR paths. Do not change the hardware-validation status from not performed / not claimed unless real tester evidence is provided.

If a hardware issue is found, create a narrow v2.9.10 post-final patch build that changes only the minimum required files, preserves runtime ZIP policy, preserves the 99% coverage gate, and clearly documents the tester evidence and fix scope.
```
