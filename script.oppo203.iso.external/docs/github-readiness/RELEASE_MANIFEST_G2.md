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
