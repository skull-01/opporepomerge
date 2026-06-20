# Combined AI Handoff and Historical Build Reconstruction — GitHub Ready

## Current baseline

- Add-on: `script.oppo203.iso.external`
- Version: `2.9.10`
- Software baseline: `v2.9.10 Final`
- GitHub-readiness build: `G8 GitHub Ready Final Packaging`
- Runtime behavior changed during GitHub readiness: false
- Hardware validation: not performed / not claimed

## GitHub-readiness sequence

- G0 — Baseline Unpack and Inventory
- G1 — Repository Hygiene and Public Source Layout
- G2 — Public Documentation Pack
- G3 — Developer Documentation Pack
- G4 — GitHub Templates and Community Files
- G5 — Tooling Configuration
- G6 — CI Hardening
- G7 — Safe Format and Lint Cleanup
- G8 — GitHub Ready Final Packaging

## Final package set

- `script.oppo203.iso.external-2.9.10-github-ready.zip`
- `script.oppo203.iso.external-2.9.10-github-ready-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-github-ready-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10-github-ready.sha256`

## Reconstruction instructions

Start from `script.oppo203.iso.external-2.9.10-github-g7-dev-source.zip`. Archive prior G6/G7 GitHub-readiness root reports into `docs/github-readiness/`. Add the final publication checklist under `docs/publication/`. Update GitHub-readiness metadata to G8 in `pyproject.toml`. Update CI/readiness tests so G5 through G8 checks are included. Add `tests/test_github_readiness_g8_final_packaging.py`. Run validation gates, package with `BUILD_SUFFIX=github-ready`, run runtime ZIP audit and post-unpack validation, then create artifact bundle and checksums.

## Non-negotiable rule

Do not claim hardware validation unless real tester evidence is supplied and recorded.
## Final packaging and post-unpack validation

```text
runtime ZIP audit: 68 files, 0 forbidden members, ZIP integrity passed
post-unpack sync_version --check: passed
post-unpack GitHub-readiness G5/G6/G7/G8 + final release tests: 24 passed
post-unpack audit_release --expected-version 2.9.10: PASS 553/553
```
