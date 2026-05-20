# Developer Guide — Continuous Integration

## Purpose

GitHub Readiness Build G6 adds a GitHub Actions workflow that mirrors the project release gates as closely as practical in a hosted Linux runner.

The CI workflow is a safety net for pull requests. It does not replace real hardware validation and it must not be used to claim that OPPO, TV, AVR, NAS, or serial-control paths were tested on physical devices.

## Workflow file

```text
.github/workflows/ci.yml
```

The workflow runs on:

- pushes to `main` and `master`
- pull requests targeting `main` and `master`
- manual `workflow_dispatch`

## Release-gate job

The `test` job is the release-gate job and runs on Python 3.11 and performs the main software verification path:

1. install development dependencies from `requirements-dev.txt`
2. syntax compile
3. documentation check
4. version sync check
5. layout check
6. i18n extraction check
7. GitHub-readiness tests
8. v2.9.10 targeted tests
9. full pytest suite
10. unittest discovery
11. coverage gate
12. release audit
13. runtime ZIP package audit
14. dev-source unpack smoke gate

The expected version is pinned through the workflow environment:

```text
EXPECTED_VERSION=2.9.10
```

## Compatibility-smoke job

The `compatibility-smoke` job runs lighter checks across Python 3.9, 3.10, and 3.12. Its purpose is to catch broad interpreter compatibility issues without multiplying the full release-gate runtime across every Python version.

## Runtime package protection

The CI runtime ZIP audit rejects development-only paths in the installable package, including:

```text
tests/
tools/
scripts/
docs/
release-evidence/
.github/
```

This keeps the public source repository rich while keeping the Kodi installable ZIP clean.

## Dependabot

Build G6 also adds:

```text
.github/dependabot.yml
```

Dependabot checks GitHub Actions and Python development dependencies weekly. Dependency PRs must still pass the same release gates and must not claim hardware validation.

## If CI fails

Treat CI failures as blockers unless the failure is clearly environmental and documented. For normal code or documentation changes, do not merge until:

- targeted tests pass
- release audit passes
- runtime ZIP audit passes
- hardware-validation wording remains truthful
- handoff/reconstruction notes are updated when required
