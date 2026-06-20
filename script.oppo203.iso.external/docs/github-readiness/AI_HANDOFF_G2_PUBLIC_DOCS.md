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
