# Release Manifest — GitHub Readiness G4

**Build:** GitHub Readiness G4 — GitHub Templates and Community Files
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip`
**Runtime ZIP:** `script.oppo203.iso.external-2.9.10-github-g4.zip`
**Dev source ZIP:** `script.oppo203.iso.external-2.9.10-github-g4-dev-source.zip`
**Artifact bundle:** `script.oppo203.iso.external-2.9.10-github-g4-artifacts-bundle.zip`
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Added

- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/documentation_fix.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/hardware_validation_report.yml`
- `.github/pull_request_template.md`

## Changed

- `docs/README.md`

## Preserved

- OPPO playback routing and command-map behavior.
- TV and AVR sequencing behavior.
- Service interception and playercorefactory behavior.
- NAS / AutoScript behavior.
- Runtime ZIP allowlist policy.
- v2.9.10 Final software-verified release posture.

## Package notes

The runtime ZIP remains runtime-only. GitHub templates and documentation are included in the dev-source package but not in the installable runtime ZIP.
