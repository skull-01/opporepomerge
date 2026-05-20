# Combined AI Handoff and Historical Build Reconstruction — GitHub Readiness G2

# AI Handoff G2 — Public Documentation Pack

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Current status

- Current build: GitHub Readiness G2 — Public Documentation Pack
- Baseline: `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
- Recommended next baseline: `script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip`
- Runtime behavior changed: `false`
- Hardware validation: `not_performed_not_claimed`

## Scope completed

- Added public GitHub documentation files.
- Reworked README top section for public users while preserving historical reconstruction content below it.
- Added user-guide documents for installation, configuration, and troubleshooting.
- Added GitHub publication notes.
- Replaced hardware-validation README with public validation-language guidance.
- Added test helper `tests/_support/project_files.py` and updated legacy documentation tests so they can read archived historical files after G1 root cleanup.

## Files added

```text
LICENSE
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
SUPPORT.md
CODE_OF_CONDUCT.md
docs/README.md
docs/user-guide/INSTALLATION.md
docs/user-guide/CONFIGURATION.md
docs/user-guide/TROUBLESHOOTING.md
docs/publication/GITHUB_PUBLICATION_NOTES.md
tests/_support/project_files.py
docs/github-readiness/BUILD_NOTES_G2_PUBLIC_DOCS.md
docs/github-readiness/RELEASE_MANIFEST_G2.md
docs/github-readiness/TEST_AUDIT_REPORT_G2.md
docs/github-readiness/COVERAGE_REPORT_G2.md
docs/github-readiness/HARDWARE_VALIDATION_G2.md
docs/github-readiness/AI_HANDOFF_G2_PUBLIC_DOCS.md
docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G2.md
```

## Files changed

```text
README.md
docs/hardware-validation/README.md
docs/github-readiness/README.md
tests/test_all.py
tests/test_superset_merge_build8.py
tests/test_superset_merge_build9.py
tests/test_superset_merge_build10.py
tests/test_superset_merge_build11.py
tests/test_superset_merge_build12.py
tests/test_v250_build7_packaging_candidate.py
tests/test_v250_final_packaging.py
tests/test_v252_build2_packaging_cleanup.py
tests/test_v252_build3_path_mapper.py
tests/test_v252_build4_nas_playback_adapter.py
tests/test_v253_build3_version_identity.py
tests/test_v253_build6_release_candidate.py
tests/test_v290_release.py
tests/test_v291_build1_startup_autopower_wizard_wording.py
tests/test_v291_build2_disc_classification.py
tests/test_v291_build12_docs_metadata_pipeline.py
tests/test_v2910_build7_roku_ecp_backend.py
tests/test_v2910_build8_command_tv_presets.py
tests/test_v2910_build9a_smartthings_skeleton.py
tests/test_v2910_build9b_smartthings_request_helper.py
tests/test_v2910_build10_tv_diagnostics.py
tests/test_v2910_build11_avr_framework.py
tests/test_v2910_build12_denon_marantz_avr.py
tests/test_v2910_build13_yamaha_yxc_avr.py
tests/test_v2910_build14_onkyo_eiscp_avr.py
tests/test_v2910_build15a_sony_avr_skeleton.py
tests/test_v2910_build15b_sony_avr_request_helper.py
tests/test_v2910_build16_avr_wizard_diagnostics.py
tests/test_v2910_build18_regression_audit_candidate.py
```

## Validation performed

```text
py_compile service.py default.py tests/_support/project_files.py: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
tests/test_v2910_final_release.py: 3 passed
tests/test_v2910*.py: 189 passed
audit_release --expected-version 2.9.10: PASS 553/553
pytest split aggregate: 943 passed + 12 subtests
unittest discover -s tests: 571 tests OK
runtime ZIP audit: 68 files, 0 forbidden files, ZIP integrity OK
post-unpack v2.9.10 tests: 189 passed
post-unpack audit: PASS 553/553
```

## Validation not performed / not claimed

- Full unsplit pytest is not claimed because it timed out in this environment.
- New hard coverage result is not claimed because the split coverage attempt timed out.
- Real hardware validation is not claimed.

## Packaging notes

- Runtime ZIP now has 68 files because `LICENSE` is included as an optional allowlisted runtime root file.
- Forbidden development material remains excluded from the runtime ZIP.
- Dev source and artifact bundle contain the GitHub documentation and G2 evidence.

## Historical reconstruction entry

```yaml
build_id: GitHub Readiness G2 — Public Documentation Pack
baseline: script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip
package: script.oppo203.iso.external-2.9.10-github-g2.zip
dev_source: script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-github-g2-artifacts-bundle.zip
scope: public GitHub documentation pack and archived-document test compatibility
planned_success_rate: 95 percent
actual_outcome: successful documentation build
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
runtime_zip_files: 68
runtime_zip_forbidden_files: 0
coverage_gate_rerun: not_completed_due_timeout
```

## Resume prompt for next AI

```text
Continue the Kodi add-on GitHub readiness work from Build G2.

Use this baseline:
script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip

Next build:
GitHub Readiness Build G3 — Developer Documentation Pack.

Rules:
- Preserve v2.9.10 Final runtime behavior.
- Do not add features.
- Do not claim hardware validation.
- Keep runtime ZIP clean.
- Add developer documentation for architecture, testing, packaging, release process, code quality, AI maintainer rules, and hardware-validation process.
- Preserve the G2 public documentation files.
- Produce build notes, manifest, test audit, coverage report if completed, hardware-validation status, AI handoff, historical reconstruction entry, and artifact bundle.
```

---

# Build Notes

# Build Notes G2 — Public Documentation Pack

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Summary

G2 adds the public-facing GitHub documentation layer for the add-on while preserving the G1 repository hygiene layout and v2.9.10 Final runtime behavior. The top of `README.md` is now a concise public project overview, while the historical README content remains below it for traceability and legacy regression tests.

The build also adds standard public project files for GitHub publication: license, changelog, contributing guide, security policy, support guide, and code of conduct. User-facing installation, configuration, troubleshooting, hardware-validation, and publication notes were added under `docs/`.

No runtime module behavior was changed. The only test changes are documentation-layout compatibility helpers so legacy tests can read historical build files from `docs/release-history/` after the G1 root cleanup.

## Key decisions

- The add-on metadata already declares MIT licensing, so G2 adds a matching MIT `LICENSE` file for publication consistency.
- The runtime package now includes `LICENSE` because the installable ZIP allowlist permits optional runtime license files.
- The runtime ZIP file count increased from 67 to 68 due to inclusion of `LICENSE`; forbidden development material remains excluded.
- Hardware validation remains explicitly not performed and not claimed.
- The README now separates public user guidance from historical build/reconstruction notes.

## Files added

```text
LICENSE
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
SUPPORT.md
CODE_OF_CONDUCT.md
docs/README.md
docs/user-guide/INSTALLATION.md
docs/user-guide/CONFIGURATION.md
docs/user-guide/TROUBLESHOOTING.md
docs/publication/GITHUB_PUBLICATION_NOTES.md
tests/_support/project_files.py
docs/github-readiness/BUILD_NOTES_G2_PUBLIC_DOCS.md
docs/github-readiness/RELEASE_MANIFEST_G2.md
docs/github-readiness/TEST_AUDIT_REPORT_G2.md
docs/github-readiness/COVERAGE_REPORT_G2.md
docs/github-readiness/HARDWARE_VALIDATION_G2.md
docs/github-readiness/AI_HANDOFF_G2_PUBLIC_DOCS.md
docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G2.md
```

## Files changed

```text
README.md
docs/hardware-validation/README.md
docs/github-readiness/README.md
tests/test_all.py
tests/test_superset_merge_build8.py
tests/test_superset_merge_build9.py
tests/test_superset_merge_build10.py
tests/test_superset_merge_build11.py
tests/test_superset_merge_build12.py
tests/test_v250_build7_packaging_candidate.py
tests/test_v250_final_packaging.py
tests/test_v252_build2_packaging_cleanup.py
tests/test_v252_build3_path_mapper.py
tests/test_v252_build4_nas_playback_adapter.py
tests/test_v253_build3_version_identity.py
tests/test_v253_build6_release_candidate.py
tests/test_v290_release.py
tests/test_v291_build1_startup_autopower_wizard_wording.py
tests/test_v291_build2_disc_classification.py
tests/test_v291_build12_docs_metadata_pipeline.py
tests/test_v2910_build7_roku_ecp_backend.py
tests/test_v2910_build8_command_tv_presets.py
tests/test_v2910_build9a_smartthings_skeleton.py
tests/test_v2910_build9b_smartthings_request_helper.py
tests/test_v2910_build10_tv_diagnostics.py
tests/test_v2910_build11_avr_framework.py
tests/test_v2910_build12_denon_marantz_avr.py
tests/test_v2910_build13_yamaha_yxc_avr.py
tests/test_v2910_build14_onkyo_eiscp_avr.py
tests/test_v2910_build15a_sony_avr_skeleton.py
tests/test_v2910_build15b_sony_avr_request_helper.py
tests/test_v2910_build16_avr_wizard_diagnostics.py
tests/test_v2910_build18_regression_audit_candidate.py
```

## Historical reconstruction entry

```yaml
build_id: GitHub Readiness G2 — Public Documentation Pack
baseline: script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip
package: script.oppo203.iso.external-2.9.10-github-g2.zip
dev_source: script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip
artifact_bundle: script.oppo203.iso.external-2.9.10-github-g2-artifacts-bundle.zip
scope: public GitHub documentation pack and archived-document test compatibility
planned_success_rate: 95 percent
actual_outcome: successful documentation build
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
runtime_zip_files: 68
runtime_zip_forbidden_files: 0
coverage_gate_rerun: not_completed_due_timeout
```

## Known limitations

- A full unsplit `pytest -q` run timed out in this environment, so the completed validation uses split pytest groups.
- A split parallel coverage attempt timed out before completion; G2 does not claim a new hard coverage result. The v2.9.10 Final inherited coverage evidence remains unchanged because runtime code was not changed.
- Real hardware validation was not performed.

---

# Release Manifest

# Release Manifest G2

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Source and artifact identity

```text
Runtime ZIP: script.oppo203.iso.external-2.9.10-github-g2.zip
Dev source ZIP: script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip
Artifact bundle: script.oppo203.iso.external-2.9.10-github-g2-artifacts-bundle.zip
SHA256 file: script.oppo203.iso.external-2.9.10-github-g2.sha256
Baseline: script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip
```

## Files added

```text
LICENSE
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
SUPPORT.md
CODE_OF_CONDUCT.md
docs/README.md
docs/user-guide/INSTALLATION.md
docs/user-guide/CONFIGURATION.md
docs/user-guide/TROUBLESHOOTING.md
docs/publication/GITHUB_PUBLICATION_NOTES.md
tests/_support/project_files.py
docs/github-readiness/BUILD_NOTES_G2_PUBLIC_DOCS.md
docs/github-readiness/RELEASE_MANIFEST_G2.md
docs/github-readiness/TEST_AUDIT_REPORT_G2.md
docs/github-readiness/COVERAGE_REPORT_G2.md
docs/github-readiness/HARDWARE_VALIDATION_G2.md
docs/github-readiness/AI_HANDOFF_G2_PUBLIC_DOCS.md
docs/github-readiness/Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G2.md
```

## Files changed

```text
README.md
docs/hardware-validation/README.md
docs/github-readiness/README.md
tests/test_all.py
tests/test_superset_merge_build8.py
tests/test_superset_merge_build9.py
tests/test_superset_merge_build10.py
tests/test_superset_merge_build11.py
tests/test_superset_merge_build12.py
tests/test_v250_build7_packaging_candidate.py
tests/test_v250_final_packaging.py
tests/test_v252_build2_packaging_cleanup.py
tests/test_v252_build3_path_mapper.py
tests/test_v252_build4_nas_playback_adapter.py
tests/test_v253_build3_version_identity.py
tests/test_v253_build6_release_candidate.py
tests/test_v290_release.py
tests/test_v291_build1_startup_autopower_wizard_wording.py
tests/test_v291_build2_disc_classification.py
tests/test_v291_build12_docs_metadata_pipeline.py
tests/test_v2910_build7_roku_ecp_backend.py
tests/test_v2910_build8_command_tv_presets.py
tests/test_v2910_build9a_smartthings_skeleton.py
tests/test_v2910_build9b_smartthings_request_helper.py
tests/test_v2910_build10_tv_diagnostics.py
tests/test_v2910_build11_avr_framework.py
tests/test_v2910_build12_denon_marantz_avr.py
tests/test_v2910_build13_yamaha_yxc_avr.py
tests/test_v2910_build14_onkyo_eiscp_avr.py
tests/test_v2910_build15a_sony_avr_skeleton.py
tests/test_v2910_build15b_sony_avr_request_helper.py
tests/test_v2910_build16_avr_wizard_diagnostics.py
tests/test_v2910_build18_regression_audit_candidate.py
```

## Runtime ZIP audit

```text
runtime files: 68
forbidden tests/tools/scripts/docs/release-evidence/reports/handoff/evidence files: 0
zip integrity: passed
LICENSE included: yes
```

## Packaging note

The runtime ZIP includes only allowlisted runtime files and the optional root `LICENSE` file. Public documentation and GitHub-readiness records are included in the dev-source package and artifact bundle, not in the installable runtime ZIP.

---

# Test Audit

# Test Audit Report G2

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Completed validation

```text
py_compile service.py default.py tests/_support/project_files.py: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
tests/test_v2910_final_release.py: 3 passed
tests/test_v2910*.py: 189 passed
audit_release --expected-version 2.9.10: PASS 553/553
pytest split aggregate: 943 passed + 12 subtests
unittest discover -s tests: 571 tests OK
runtime ZIP audit: 68 files, 0 forbidden files, ZIP integrity OK
post-unpack dev-source v2.9.10 tests: 189 passed
post-unpack audit_release --expected-version 2.9.10: PASS 553/553
```

## Split pytest strategy

The full test suite was executed as split groups to avoid command timeout. The aggregate completed result is:

```text
383 passed in tests/test_all.py
143 passed + 12 subtests in coverage/superset group 1
60 passed in superset/v2.5.0 group
96 passed in v2.5.2/v2.5.3/v2.9.0/v2.9.10 group
110 passed in v2.9.10 AVR/registry group
50 passed in v2.9.10 TV/final/docs group
18 passed in v2.9.1 audit/logging/docs group
6 passed in v2.9.1 type-hint baseline group
7 passed in v2.9.1 layout group
7 passed in v2.9.1 i18n extraction group
28 passed in v2.9.1 startup/disc/command-map group
18 passed in v2.9.1 evidence/version/release automation group
17 passed in v2.9.1 packaging/settings group
```

## Validation limitations

- A full unsplit `pytest -q` run timed out before completion in this environment and is not claimed.
- A split parallel coverage run was attempted but timed out before completion, so G2 does not claim a new coverage gate result.
- No real hardware validation was performed.

---

# Coverage Report

# Coverage Report G2

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Coverage status

G2 is a public documentation and test-layout compatibility build. It did not change runtime modules.

A coverage run based only on unittest discovery completed but produced 70% total coverage because unittest discovery does not exercise the complete pytest-based coverage suite. That result is not used as a release coverage gate.

A split parallel coverage attempt was started to reproduce the hard gate, but it timed out before completion in this environment. Therefore:

```text
G2 coverage gate rerun: not completed
New coverage claim: none
Inherited v2.9.10 Final coverage evidence: unchanged
Runtime behavior changed: false
```

Do not use G2 as a new coverage-gate proof. Use the completed split pytest, unittest, audit, runtime ZIP audit, and post-unpack verification listed in `TEST_AUDIT_REPORT_G2.md` for this documentation-only build.

---

# Hardware Validation

# Hardware Validation G2

**Build:** GitHub Readiness G2 — Public Documentation Pack
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
**Output line:** `script.oppo203.iso.external-2.9.10-github-g2`
**Runtime behavior changed:** `false`
**Hardware validation:** `not_performed_not_claimed`
**Generated:** 2026-05-20

## Hardware validation status

```text
not_performed_not_claimed
```

G2 made no runtime behavior changes and performed no real hardware testing.

Do not claim validation for OPPO, Chinoppo, Magnetar, Reavon, Kodi, NAS, TV, ADB, Roku, LG, Samsung, Sony, Panasonic, Vizio, AVR, or any other hardware path based on this build.

Allowed public wording remains:

```text
Software-verified release. Hardware validation not performed / not claimed.
```
