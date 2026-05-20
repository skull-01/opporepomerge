# Documentation

This folder contains public user documentation, developer/release history, AI reconstruction handoffs, and hardware-validation guidance.

## Public user docs

- `user-guide/INSTALLATION.md`
- `user-guide/CONFIGURATION.md`
- `user-guide/TROUBLESHOOTING.md`
- `hardware-validation/README.md`

## Maintainer docs

- `release-history/` keeps historical build notes, manifests, audits, coverage reports, and hardware-validation status files.
- `ai-handoff/` keeps AI resume/reconstruction files.
- `github-readiness/` keeps GitHub-readiness build records.

Developer architecture and release-process documentation will be expanded in GitHub Readiness Build G3.

## Developer documentation

- [Developer Guide](developer-guide/README.md)
  - [Continuous Integration](developer-guide/ci.md)
- [Architecture](developer-guide/architecture.md)
- [Testing](developer-guide/testing.md)
- [Packaging](developer-guide/packaging.md)
- [Release Process](developer-guide/release-process.md)
- [Code Quality](developer-guide/code-quality.md)
- [AI Maintainer Rules](developer-guide/ai-maintainer-rules.md)

## Hardware validation documentation

- [Hardware Validation Plan](hardware-validation/hardware-validation-plan.md)
- [Hardware Support Matrix](hardware-validation/hardware-support-matrix.md)

## GitHub community templates

The repository includes GitHub issue forms and a pull request template under `.github/`. Use these templates to keep bug reports, feature requests, documentation fixes, and real hardware-validation evidence structured and reviewable. Hardware-validation reports must be based on real device testing and do not become official support claims until maintainer review updates the hardware-validation matrix.

## Development tooling

GitHub Readiness Build G5 adds `pyproject.toml` and `requirements-dev.txt` for contributor tooling. These files are development-only and are excluded from the installable Kodi runtime ZIP by the existing allowlist packaging policy.

## GitHub readiness note — G7

G7 adds a narrow safe format-cleanup baseline for archived GitHub-readiness Markdown and documents that broader lint/format rewrites must remain separate, reviewable, and test-backed.

## Publication

- [GitHub Publication Notes](publication/GITHUB_PUBLICATION_NOTES.md)
- [GitHub Publication Checklist](publication/GITHUB_PUBLICATION_CHECKLIST.md)
