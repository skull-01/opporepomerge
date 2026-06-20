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


---

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


---

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


---

# Test Audit Report G1

**Build:** GitHub Readiness Build G1 — Repository Hygiene and Public Source Layout
**Date:** 2026-05-20
**Baseline:** `script.oppo203.iso.external-2.9.10-dev-source.zip`
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Validation performed from working source

```text
py_compile selected entry/tool files: passed
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
pytest -q tests/test_v2910_final_release.py: 3 passed
pytest -q tests/test_v2910*.py: 189 passed
audit_release --expected-version 2.9.10: PASS 553/553
runtime ZIP audit: 67 files, 0 forbidden files, ZIP integrity OK
```

## Post-unpack dev-source verification

```text
render_docs --check: passed
sync_version --check: passed
test_layout.py --check: passed
i18n_extract.py --check: passed
pytest -q tests/test_v2910_final_release.py: 3 passed
pytest -q tests/test_v2910*.py: 189 passed
audit_release --expected-version 2.9.10: PASS 553/553
```

## Full pytest note

A full unsplit `pytest -q` run was attempted but timed out before a complete summary was produced. Because G1 is a repository-layout build and not a runtime behavior build, the accepted G1 gate is targeted v2.9.10 split tests plus release audit and package audit. Future G8 should run the complete final gate after the GitHub-readiness series stabilizes.

## Result

G1 validation passed for its planned scope.


---

# Hardware Validation G1

**Build:** GitHub Readiness Build G1 — Repository Hygiene and Public Source Layout
**Date:** 2026-05-20
**Baseline:** `script.oppo203.iso.external-2.9.10-dev-source.zip`
**Runtime behavior changed:** No
**Hardware validation:** Not performed / not claimed

## Status

Real hardware validation was not performed in GitHub Readiness Build G1.

No hardware validation is claimed for:

- OPPO UDP-203 / UDP-205
- Chinoppo / M9205 variants
- Magnetar
- Reavon
- Kodi installations
- NAS / AutoScript workflows
- TV control backends
- ADB / Roku / LG / Samsung / Sony / Panasonic / Vizio
- AVR control paths

## G1 impact

G1 did not change runtime playback behavior, hardware control behavior, or device communication logic.

Allowed wording remains:

```text
Software-verified release. Hardware validation not performed / not claimed.
```
