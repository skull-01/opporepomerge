# Combined AI Handoff and Historical Build Reconstruction — v103 v2.9.10 Build 18

## Current status

Completed v2.9.10 Build 18 — Regression, audit, and packaging candidate from the Build 17 baseline.

Build 18 is the Full Release Gate regression/audit candidate after Build 17 unified TV + AVR playback sequencing. It adds no new hardware features. It refreshes active build identity, evidence, support matrix, and packaging records while preserving Build 17 sequencing behavior and all protected OPPO/Kodi/NAS/TV/AVR behavior.

## Historical reconstruction entry — v2.9.10 Build 18

```yaml
build_id: v2.9.10 Build 18
package: script.oppo203.iso.external-2.9.10-build18.zip
dev_source: script.oppo203.iso.external-2.9.10-build18-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-build18-artifacts-bundle.zip
baseline: script.oppo203.iso.external-2.9.10-build17-dev-source.zip
scope: regression, audit, and packaging candidate
planned_success_rate: 86 percent
runtime_behavior_changed: false
hardware_validation: not_performed_not_claimed
```

## Files changed or added

- Updated `resources/lib/version.py` to `BUILD_ID = "v2.9.10 Build 18"` and `BUILD_NUMBER = 18`.
- Updated `docs/sources.yaml` and regenerated README/reference/web-reference metadata.
- Updated `scripts/package_release.sh` default package suffix to `build18`.
- Updated `addon.xml` active Build 18 summary/description while preserving historical Build 17 and earlier metadata.
- Added `tests/test_v2910_build18_regression_audit_candidate.py`.
- Updated active current-build expectations in inherited tests.
- Added Build 18 evidence files and `release-evidence/v2.9.10-build18/MANIFEST.txt`.

## Preserved behavior

- Build 17 unified TV + AVR sequencing behavior.
- AVR sequencing only for eligible OPPO/external-player handoff.
- AVR disabled no-op path.
- Nonfatal TV and AVR failures.
- Optional AVR restore only when enabled.
- Existing TV restore behavior.
- Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, and runtime ZIP policy.
- 99% coverage gate.
- Hardware validation not performed / not claimed.

## Verification summary

Full Release Gate verification results are recorded in the assistant completion report and Build 18 evidence files.

## Resume prompt for final release

```text
Continue the v2.9.10 Unified Hardware Ecosystem Expansion from v2.9.10 Build 18.

Use this baseline:
script.oppo203.iso.external-2.9.10-build18-dev-source.zip

Next build:
v2.9.10 Final — software-verified release packaging.

Keep the build narrow. This is final release packaging from the Build 18 regression/audit candidate. Do not add new hardware features. Preserve Build 18 Full Release Gate results, Build 17 unified TV + AVR playback sequencing behavior, AVR disabled no-op behavior, TV/AVR nonfatal failure behavior, optional AVR restore guard, existing TV restore, startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, runtime ZIP policy, the 99% coverage gate, and no hardware-validation claim unless real tester results are provided.

Create final release artifacts:
script.oppo203.iso.external-2.9.10.zip
script.oppo203.iso.external-2.9.10-dev-source.zip
script.oppo203.iso.external-2.9.10-artifacts-bundle.zip
script.oppo203.iso.external-2.9.10.sha256

Use the final packaging gate: source checks, final release metadata checks, full pytest, full unittest discovery, coverage TOTAL 99%, audit_release, post-unpack verification, runtime ZIP audit, final support matrix, final hardware-validation statement, and final combined handoff.
```
