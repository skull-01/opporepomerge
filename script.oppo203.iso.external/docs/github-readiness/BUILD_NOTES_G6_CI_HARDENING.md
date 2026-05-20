# Build Notes — GitHub Readiness Build G6 — CI Hardening

## Build identity

- Build: GitHub Readiness G6
- Scope: CI hardening and dependency-update automation
- Baseline: `script.oppo203.iso.external-2.9.10-github-g5-dev-source.zip`
- Runtime behavior changed: false
- Hardware validation: not performed / not claimed

## Summary

G6 replaces the legacy/light CI workflow with a release-gate-oriented GitHub Actions workflow and adds Dependabot configuration for GitHub Actions and Python development dependencies. The build also updates `scripts/verify.sh` so the default expected version matches the current protected baseline, `2.9.10`.

This build does not change playback routing, OPPO control, TV control, AVR sequencing, NAS/AutoScript behavior, settings behavior, or runtime packaging logic.

## Files changed

- `.github/workflows/ci.yml`
- `scripts/verify.sh`
- `pyproject.toml`
- `docs/README.md`
- `docs/developer-guide/README.md`
- `docs/developer-guide/testing.md`
- `docs/developer-guide/code-quality.md`
- `docs/github-readiness/README.md`

## Files added

- `.github/dependabot.yml`
- `docs/developer-guide/ci.md`
- `tests/test_github_readiness_g6_ci_hardening.py`
- `BUILD_NOTES_G6_CI_HARDENING.md`
- `RELEASE_MANIFEST_G6.md`
- `TEST_AUDIT_REPORT_G6.md`
- `COVERAGE_REPORT_G6.md`
- `HARDWARE_VALIDATION_G6.md`
- `AI_HANDOFF_G6_CI_HARDENING.md`
- `Combined_AI_Handoff_and_Historical_Build_Reconstruction_GITHUB_G6.md`

## CI changes

The new `.github/workflows/ci.yml` includes:

- `test` job: full release-gate-oriented validation on Python 3.11
- `lint` job: Ruff and Black check-only gates on Python 3.11
- `compatibility-smoke` job: targeted checks on Python 3.9, 3.10, and 3.12
- runtime ZIP audit that rejects development-only paths
- dev-source post-unpack smoke validation

## Dependabot changes

The new `.github/dependabot.yml` checks:

- GitHub Actions updates
- Python development dependency updates from `requirements-dev.txt`

## Notes

- The GitHub Actions workflow was authored and YAML-validated locally, but was not executed on GitHub in this environment.
- Ruff and Black are referenced in CI and `requirements-dev.txt`, but are not installed in this local container, so local Ruff/Black results are not claimed.
- G6 remains a software-only validation build.
