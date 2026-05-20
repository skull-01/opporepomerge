# Release Manifest — GitHub Readiness G8 GitHub Ready Final Packaging

## Packages

- `script.oppo203.iso.external-2.9.10-github-ready.zip`
- `script.oppo203.iso.external-2.9.10-github-ready-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-github-ready-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10-github-ready.sha256`

## Source changes

- `.github/workflows/ci.yml`
- `docs/README.md`
- `docs/github-readiness/README.md`
- `docs/publication/GITHUB_PUBLICATION_NOTES.md`
- `docs/publication/GITHUB_PUBLICATION_CHECKLIST.md`
- `pyproject.toml`
- `tests/test_github_readiness_g6_ci_hardening.py`
- `tests/test_github_readiness_g7_safe_format_cleanup.py`
- `tests/test_github_readiness_g8_final_packaging.py`

## Archived root reports

The G6/G7 build notes, manifests, test audits, coverage notes, hardware-validation notes, AI handoffs, and combined reconstruction files were moved from the source root into `docs/github-readiness/`.

## Runtime behavior

No runtime behavior changed.

## Verification summary

```text
GitHub-readiness G5/G6/G7/G8 tests: 21 passed
v2.9.10 final release tests: 3 passed
v2.9.10 tests: 189 passed
full pytest split aggregate: 964 passed, 12 subtests passed
unittest discover -s tests: 571 tests OK
audit_release: PASS 553/553
runtime ZIP audit: 68 files, 0 forbidden members, ZIP integrity passed
post-unpack targeted validation: 24 passed
post-unpack audit_release: PASS 553/553
```
