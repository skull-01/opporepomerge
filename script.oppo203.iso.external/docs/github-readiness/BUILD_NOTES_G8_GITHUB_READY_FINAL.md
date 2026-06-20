# Build Notes — GitHub Readiness G8 GitHub Ready Final Packaging

## Scope

G8 finalizes the GitHub-ready source layout and package set for `script.oppo203.iso.external` v2.9.10. This build does not change runtime playback, OPPO control, TV control, AVR sequencing, NAS, service interception, or `playercorefactory.xml` behavior.

## Baseline

- Input baseline: `script.oppo203.iso.external-2.9.10-github-g7-dev-source.zip`
- Protected software baseline: `v2.9.10 Final`
- Add-on version: `2.9.10`
- Hardware validation: not performed / not claimed

## Changes

- Archived G6/G7 GitHub-readiness reports from the repository root into `docs/github-readiness/`.
- Added `docs/publication/GITHUB_PUBLICATION_CHECKLIST.md`.
- Updated `docs/publication/GITHUB_PUBLICATION_NOTES.md`.
- Updated `docs/github-readiness/README.md` to reflect the full G0-G8 sequence.
- Updated GitHub Actions readiness tests to include G7 and G8 checks.
- Added `tests/test_github_readiness_g8_final_packaging.py`.
- Updated `pyproject.toml` GitHub-readiness metadata to G8.

## Runtime behavior

Runtime behavior changed: false.

## Hardware validation

Hardware validation remains not performed / not claimed.
## Final packaging and post-unpack validation

```text
runtime ZIP audit: 68 files, 0 forbidden members, ZIP integrity passed
post-unpack sync_version --check: passed
post-unpack GitHub-readiness G5/G6/G7/G8 + final release tests: 24 passed
post-unpack audit_release --expected-version 2.9.10: PASS 553/553
```
