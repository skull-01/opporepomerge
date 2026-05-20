# Release Manifest G1 — Repository Hygiene

**Build:** GitHub Readiness Build G1 — Repository Hygiene and Public Source Layout
**Date:** 2026-05-20
**Baseline:** `script.oppo203.iso.external-2.9.10-dev-source.zip`
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Output artifacts

- `script.oppo203.iso.external-2.9.10-github-g1.zip`
- `script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-github-g1-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10-github-g1.sha256`

## Source layout changes

- Root Markdown count reduced from 509 to 3.
- Top-level root file count reduced from 518 to 14.
- Historical Markdown artifacts preserved under `docs/release-history/`.
- AI handoff files preserved under `docs/ai-handoff/`.
- GitHub-readiness working docs stored under `docs/github-readiness/`.
- Hardware-validation docs placeholder created under `docs/hardware-validation/`.

## Runtime package

The runtime package remains allowlist-only and contains 67 runtime files. No tests, tools, scripts, docs, release-evidence, or handoff files are included in the installable ZIP.

## Hardware validation

Not performed and not claimed.
