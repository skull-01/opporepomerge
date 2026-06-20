# Combined AI Handoff and Historical Build Reconstruction — GitHub Readiness G6

## Current status

G6 completed GitHub CI hardening for the Kodi OPPO 203 ISO External Player add-on.

- Add-on version: `2.9.10`
- Runtime build identity: `v2.9.10 Final`
- GitHub readiness build: `G6 — CI Hardening`
- Runtime behavior changed: false
- Hardware validation: not performed / not claimed

## Build G6 summary

G6 replaces the legacy CI workflow with a release-gate-oriented GitHub Actions workflow, adds Dependabot configuration, adds CI documentation, updates `scripts/verify.sh` to default to `2.9.10`, and adds tests that inspect CI/dependency configuration.

## Reconstruction instructions

Start from:

```text
script.oppo203.iso.external-2.9.10-github-g5-dev-source.zip
```

Apply these changes:

1. Replace `.github/workflows/ci.yml` with the G6 workflow containing `test`, `lint`, and `compatibility-smoke` jobs.
2. Add `.github/dependabot.yml` for GitHub Actions and pip development-dependency updates.
3. Update `scripts/verify.sh` so `EXPECTED_VERSION` defaults to `2.9.10`.
4. Update `[tool.github-readiness]` metadata in `pyproject.toml` to `G6 CI Hardening`.
5. Add `docs/developer-guide/ci.md`.
6. Update developer and GitHub-readiness documentation indexes.
7. Add `tests/test_github_readiness_g6_ci_hardening.py`.
8. Run the documented validation gates.
9. Package runtime/dev-source/artifact outputs.

## Validation evidence

```text
G5/G6 GitHub readiness tests: 12 passed
final release tests: 3 passed
v2.9.10 tests: 189 passed
unittest discovery: 571 tests OK
audit_release: PASS 553/553
runtime ZIP audit: passed
post-unpack targeted validation: passed
```

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

## Next build

```text
Proceed with GitHub Readiness Build G7 — Safe Format and Lint Cleanup.
```
