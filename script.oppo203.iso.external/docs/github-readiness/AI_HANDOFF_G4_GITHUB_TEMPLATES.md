# AI Handoff — GitHub Readiness Build G4

## Current status

- Current build: GitHub Readiness G4 — GitHub Templates and Community Files
- Baseline: `script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip`
- Runtime package: `script.oppo203.iso.external-2.9.10-github-g4.zip`
- Dev source: `script.oppo203.iso.external-2.9.10-github-g4-dev-source.zip`
- Runtime behavior changed: false
- Hardware validation: not_performed_not_claimed

## Scope completed

G4 added structured GitHub issue forms and a pull request template so future public GitHub collaboration has safe, consistent triage for bugs, feature requests, documentation fixes, and real hardware-validation evidence.

## Files added

- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/documentation_fix.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/hardware_validation_report.yml`
- `.github/pull_request_template.md`

## Files changed

- `docs/README.md`

## Validation performed

```text
YAML validation for .github/**/*.yml: passed
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
v2.9.10 final release tests: 3 passed
all v2.9.10 tests: 189 passed
unittest discovery: 571 tests OK
audit_release: PASS 553/553
runtime ZIP audit: 68 files, 0 forbidden directory policy violations, ZIP integrity passed
post-unpack targeted validation: passed
```

## Validation not performed / limitations

A complete broad split pytest aggregate was attempted but timed out in this environment before a complete summary could be captured. No new G4 coverage percentage is claimed because this was a documentation/community-template-only build.

## Packaging notes

- Runtime ZIP remains runtime-only.
- GitHub templates and docs are present in dev-source, not runtime ZIP.
- Hardware-validation wording remains conservative and evidence-based.

## Historical reconstruction entry

```yaml
build_id: GitHub Readiness G4
baseline: script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip
scope: GitHub templates and community files
planned_success_rate: 95 percent
actual_outcome: successful
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Resume prompt for next AI

```text
Proceed with GitHub Readiness Build G5 — Tooling Configuration.

Use this baseline:
script.oppo203.iso.external-2.9.10-github-g4-dev-source.zip

Rules:
- Do not change runtime behavior.
- Do not add product features.
- Do not claim hardware validation.
- Preserve v2.9.10 Final software-verified behavior.
- Add or update pyproject.toml and requirements-dev.txt for maintainability tooling.
- Configure lint/format/test tooling conservatively.
- Do not apply broad formatting changes in G5 unless explicitly scoped.
- Run practical validation gates.
- Produce build notes, release manifest, test audit, coverage note if applicable, hardware validation status, AI handoff Markdown, historical reconstruction entry, dev-source ZIP, runtime ZIP, and artifact bundle.
```
