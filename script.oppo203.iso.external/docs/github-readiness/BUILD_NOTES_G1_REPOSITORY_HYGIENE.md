# Build Notes G1 — Repository Hygiene and Public Source Layout

**Build:** GitHub Readiness Build G1 — Repository Hygiene and Public Source Layout
**Date:** 2026-05-20
**Baseline:** `script.oppo203.iso.external-2.9.10-dev-source.zip`
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Scope

G1 reorganized the source tree for future public GitHub publication without changing runtime playback behavior.

## Completed

- Added `.gitignore`.
- Added `.editorconfig`.
- Created `docs/release-history/`.
- Created `docs/ai-handoff/`.
- Created `docs/github-readiness/`.
- Created `docs/hardware-validation/`.
- Moved 506 historical root Markdown files into documentation archive folders.
- Preserved `README.md`, `reference.md`, and `web-references.md` in the root because they are still managed by `tools/render_docs.py`.
- Added archive indexes:
  - `docs/release-history/INDEX.md`
  - `docs/ai-handoff/INDEX.md`
- Added `docs/github-readiness/G1_ROOT_MARKDOWN_MOVE_MAP.md` so another AI can trace every moved Markdown artifact.
- Updated `tools/audit_release.py` with an archived artifact resolver. Legacy audit names remain stable while moved files are resolved from `docs/release-history/` or `docs/ai-handoff/`.
- Updated v2.9.10 tests that checked root-only historical artifacts so they accept the new archived location.

## Layout result

Before G1, the source root contained 518 top-level files and 509 root Markdown files. After G1, the source root contains 14 top-level files and 3 root Markdown files.

Root Markdown files intentionally retained:

- `README.md`
- `reference.md`
- `web-references.md`

## Files changed

Runtime files were not changed. Modified non-runtime/test/tool files:

- `tools/audit_release.py`
- `tests/test_v2910_final_release.py`
- `tests/test_v2910_build11_avr_framework.py`
- `tests/test_v2910_build12_denon_marantz_avr.py`
- `tests/test_v2910_build13_yamaha_yxc_avr.py`
- `tests/test_v2910_build14_onkyo_eiscp_avr.py`
- `tests/test_v2910_build15a_sony_avr_skeleton.py`
- `tests/test_v2910_build15b_sony_avr_request_helper.py`
- `tests/test_v2910_build16_avr_wizard_diagnostics.py`
- `tests/test_v2910_build18_regression_audit_candidate.py`

## Files added

- `.gitignore`
- `.editorconfig`
- `docs/release-history/INDEX.md`
- `docs/ai-handoff/INDEX.md`
- `docs/github-readiness/README.md`
- `docs/github-readiness/G1_ROOT_MARKDOWN_MOVE_MAP.md`
- `docs/hardware-validation/README.md`
- G1 report and handoff files in `docs/github-readiness/`

## Files moved

- 489 historical release/reconstruction/report Markdown files moved to `docs/release-history/`.
- 17 AI handoff/reconstruction Markdown files moved to `docs/ai-handoff/`.

A complete move map is preserved in `docs/github-readiness/G1_ROOT_MARKDOWN_MOVE_MAP.md`.

## Known limitation

A full unsplit `pytest -q` run was attempted after the large root artifact move, but it timed out before producing a complete summary. The G1 validation gate therefore used targeted v2.9.10 split tests, source checks, audit, packaging audit, and post-unpack verification.

## Acceptance status

G1 acceptance passed: repository root is cleaner, historical traceability is preserved, audit can locate moved artifacts, runtime ZIP remains clean, and hardware validation is still not claimed.
