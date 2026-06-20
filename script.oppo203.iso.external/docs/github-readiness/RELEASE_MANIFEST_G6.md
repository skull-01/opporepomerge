# Release Manifest — GitHub Readiness Build G6

## Build

- Build ID: GitHub Readiness G6 — CI Hardening
- Baseline: `script.oppo203.iso.external-2.9.10-github-g5-dev-source.zip`
- Add-on version: `2.9.10`
- Build identity in runtime code: `v2.9.10 Final`
- Runtime behavior changed: false
- Hardware validation: not performed / not claimed

## Output artifacts

- `script.oppo203.iso.external-2.9.10-github-g6.zip`
- `script.oppo203.iso.external-2.9.10-github-g6-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-github-g6-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10-github-g6.sha256`
- `script.oppo203.iso.external-2.9.10-github-g6-artifacts-bundle.sha256`

## Source changes

### Changed

- `.github/workflows/ci.yml`
- `scripts/verify.sh`
- `pyproject.toml`
- `docs/README.md`
- `docs/developer-guide/README.md`
- `docs/developer-guide/testing.md`
- `docs/developer-guide/code-quality.md`
- `docs/github-readiness/README.md`

### Added

- `.github/dependabot.yml`
- `docs/developer-guide/ci.md`
- `tests/test_github_readiness_g6_ci_hardening.py`

## Runtime ZIP audit

- Runtime files: 68
- Forbidden development-policy violations: 0
- ZIP integrity: passed

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
