# AI Handoff — GitHub Readiness Build G6 — CI Hardening

## Current status

- Current build: GitHub Readiness G6 — CI Hardening
- Baseline: `script.oppo203.iso.external-2.9.10-github-g5-dev-source.zip`
- Current runtime package: `script.oppo203.iso.external-2.9.10-github-g6.zip`
- Current dev source: `script.oppo203.iso.external-2.9.10-github-g6-dev-source.zip`
- Runtime behavior changed: false
- Hardware validation: not performed / not claimed

## Scope completed

G6 hardened the GitHub CI surface and dependency-update automation without changing runtime add-on behavior.

## Files changed

```text
.github/workflows/ci.yml
scripts/verify.sh
pyproject.toml
docs/README.md
docs/developer-guide/README.md
docs/developer-guide/testing.md
docs/developer-guide/code-quality.md
docs/github-readiness/README.md
```

## Files added

```text
.github/dependabot.yml
docs/developer-guide/ci.md
tests/test_github_readiness_g6_ci_hardening.py
BUILD_NOTES_G6_CI_HARDENING.md
RELEASE_MANIFEST_G6.md
TEST_AUDIT_REPORT_G6.md
COVERAGE_REPORT_G6.md
HARDWARE_VALIDATION_G6.md
AI_HANDOFF_G6_CI_HARDENING.md
Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G6.md
```

## Validation performed

```text
py_compile: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
G5/G6 GitHub readiness tests: 12 passed
final release tests: 3 passed
v2.9.10 tests: 189 passed
unittest discovery: 571 tests OK
audit_release: PASS 553/553
runtime ZIP audit: 68 files, 0 forbidden policy violations, ZIP integrity passed
post-unpack targeted validation: 15 passed
post-unpack audit_release: PASS 553/553
```

## Validation not performed / not claimed

- GitHub Actions itself was not executed because this environment is not GitHub.
- Ruff and Black were not run locally because they are not installed in the container.
- No new coverage percentage is claimed for G6.
- Full unsplit pytest timed out before a final summary.

## Known limitations

The GitHub Actions workflow should be run after the repository is pushed to GitHub. Any workflow syntax or runner-specific issue found there should be fixed in a narrow follow-up CI patch.

## Packaging notes

The runtime ZIP remains clean. Development-only paths such as `.github/`, `docs/`, `tests/`, `tools/`, `scripts/`, and `release-evidence/` are excluded from the installable ZIP.

## Historical reconstruction entry

```yaml
build_id: GitHub Readiness G6 — CI Hardening
baseline: script.oppo203.iso.external-2.9.10-github-g5-dev-source.zip
scope: GitHub Actions CI hardening, Dependabot configuration, CI documentation, and CI configuration tests
planned_success_rate: 85 percent
actual_outcome: successful
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Resume prompt for next AI

```text
Proceed with GitHub Readiness Build G7 — Safe Format and Lint Cleanup.

Use this baseline:
script.oppo203.iso.external-2.9.10-github-g6-dev-source.zip

Rules:
- Preserve v2.9.10 Final runtime behavior.
- Do not add features.
- Do not claim hardware validation.
- Treat G7 as safe formatting/import/lint cleanup only.
- Do not refactor protected playback, OPPO, TV, AVR, NAS, or service logic.
- Run available validation gates.
- Produce build notes, release manifest, test audit, coverage status, hardware-validation status, AI handoff Markdown, combined historical reconstruction handoff, runtime ZIP, dev-source ZIP, artifact bundle, and SHA256 files.
```
