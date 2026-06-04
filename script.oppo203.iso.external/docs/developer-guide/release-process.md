# Developer Guide — Release Process

## Release philosophy

Releases must be evidence-based. A release is not complete until the package, tests, audit results, hardware-validation status, and handoff are all recorded.

## Local build & publish (local-first)

CI and releases run on the local Windows+WSL machine; the cloud workflows are disabled
(see [ci.md](ci.md)). The release flow:

1. **Gate:** `wsl bash scripts/ci-local.sh` — clean-room full add-on gate on Python 3.12 +
   compat-smoke on 3.9/3.10 (a superset of the old `ci.yml`). Merge-on-local-green.
2. **Add-on release:** `powershell -File scripts/release-addon-local.ps1` — builds the runtime
   installable ZIP + `.sha256` (via `tools/package_installable_zip.py` under WSL) and runs
   `gh release create v<X> --title "v<X> Final" --latest=false` (the configurator holds the repo
   Latest badge). `-DryRun` builds the artifacts without publishing.
3. **Configurator release:** `powershell -File scripts/release-configurator-local.ps1` —
   `npm run dist` → MSI/NSIS + `SHA256SUMS` → `gh release create configurator-v<Y> --latest`.
   `-DryRun` / `-SkipBuild` for checks.
4. **Every release** also refreshes the README front-page **Current status** + **Current
   release** (add-on + configurator versions) — pinned by `tests/test_readme_current_release.py`.

## Build sequence

For GitHub readiness, use the G-series build sequence:

```text
G0 — Baseline Unpack and Inventory
G1 — Repository Hygiene and Public Source Layout
G2 — Public Documentation Pack
G3 — Developer Documentation Pack
G4 — GitHub Templates and Community Files
G5 — Tooling Configuration
G6 — CI Hardening
G7 — Safe Format and Lint Cleanup
G8 — GitHub Ready Final Packaging
```

## Required files per build

Every build must create:

```text
BUILD_NOTES_*.md
RELEASE_MANIFEST_*.md
TEST_AUDIT_REPORT_*.md
COVERAGE_REPORT_*.md when applicable
HARDWARE_VALIDATION_*.md
AI_HANDOFF_*.md
Combined_AI_Handoff_and_Historical_Build_Reconstruction_*.md
```

## Release evidence rules

Each release or readiness build must answer:

- What changed?
- What did not change?
- What tests ran?
- What tests did not run?
- Did runtime behavior change?
- Was hardware validation performed?
- Can the build be reconstructed from the handoff?

## Hardware validation rule

Do not claim hardware validation unless real tester evidence is recorded. Software tests and mocks are not hardware validation.

## Version identity

Version identity is controlled by:

- `addon.xml`
- `resources/lib/version.py`
- docs metadata
- release tests

Use `tools/sync_version.py --check` before packaging.

## GitHub-ready release checklist

Before public GitHub publication:

- README is public-friendly.
- License status is clear.
- Contributing instructions exist.
- Security policy exists.
- Issue and PR templates exist.
- Developer docs exist.
- Runtime ZIP is clean.
- Dev-source ZIP reconstructs the build.
- Hardware status is truthful.
