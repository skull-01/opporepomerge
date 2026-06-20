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
