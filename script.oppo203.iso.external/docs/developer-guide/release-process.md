# Developer Guide — Release Process

## Release philosophy

Releases must be evidence-based. A release is not complete until the package, tests, audit results, hardware-validation status, and handoff are all recorded.

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
