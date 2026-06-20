# AI Handoff G1 — Repository Hygiene

**Build:** GitHub Readiness Build G1 — Repository Hygiene and Public Source Layout
**Date:** 2026-05-20
**Baseline:** `script.oppo203.iso.external-2.9.10-dev-source.zip`
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Current status

- Current build: GitHub Readiness Build G1
- Baseline: `script.oppo203.iso.external-2.9.10-dev-source.zip`
- Runtime behavior changed: No
- Hardware validation: Not performed / not claimed

## Scope completed

G1 cleaned the public source layout by moving historical Markdown artifacts out of the repository root while preserving reconstruction traceability.

## Files changed

- `tools/audit_release.py` now resolves archived release artifacts from `docs/release-history/` and `docs/ai-handoff/` while retaining stable legacy audit names.
- v2.9.10 test files that checked root-only evidence were updated to accept the archived location.

## Files added

- `.gitignore`
- `.editorconfig`
- `docs/release-history/INDEX.md`
- `docs/ai-handoff/INDEX.md`
- `docs/github-readiness/README.md`
- `docs/github-readiness/G1_ROOT_MARKDOWN_MOVE_MAP.md`
- `docs/hardware-validation/README.md`
- G1 build notes, manifest, test audit, hardware status, and this handoff

## Files moved

- Historical release/report Markdown files moved to `docs/release-history/`.
- AI handoff/reconstruction Markdown files moved to `docs/ai-handoff/`.

## Validation performed

```text
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
pytest -q tests/test_v2910_final_release.py: 3 passed
pytest -q tests/test_v2910*.py: 189 passed
audit_release --expected-version 2.9.10: PASS 553/553
runtime ZIP audit: 67 files, 0 forbidden files, ZIP integrity OK
post-unpack dev-source v2.9.10 tests: 189 passed
post-unpack audit: PASS 553/553
```

## Validation not performed / incomplete

Full unsplit `pytest -q` was attempted but timed out before a complete summary. Do not represent it as passed for G1.

## Historical reconstruction entry

```yaml
build_id: GitHub Readiness Build G1
baseline: script.oppo203.iso.external-2.9.10-dev-source.zip
scope: repository hygiene and public source layout
planned_success_rate: 90 percent
actual_outcome: successful for planned G1 gate
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
root_markdown_before: 509
root_markdown_after: 3
root_top_level_files_before: 518
root_top_level_files_after: 14
runtime_zip_files: 67
runtime_zip_forbidden_files: 0
```

## Resume prompt for next AI

```text
Continue the Kodi add-on GitHub readiness work from Build G1.

Use this baseline:
script.oppo203.iso.external-2.9.10-github-g1-dev-source.zip

Next build:
GitHub Readiness Build G2 — Public Documentation Pack.

Rules:
- Preserve v2.9.10 Final runtime behavior.
- Do not claim hardware validation.
- Keep runtime ZIP clean.
- Keep README, reference, and web-references compatible with tools/render_docs.py.
- Add or polish public-facing docs: README, LICENSE or LICENSE_PENDING, CHANGELOG, CONTRIBUTING, SECURITY, SUPPORT, CODE_OF_CONDUCT.
- Be explicit if license choice is still pending.
- Produce build notes, manifest, test audit, hardware-validation status, AI handoff Markdown, historical reconstruction entry, runtime/dev-source packages, and artifact bundle.
```
