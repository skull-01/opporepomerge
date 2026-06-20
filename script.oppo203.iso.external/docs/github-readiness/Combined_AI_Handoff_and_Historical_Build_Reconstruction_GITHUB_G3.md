# GitHub Readiness Build G3 — Developer Documentation Pack

**Project:** `script.oppo203.iso.external`
**Version:** `2.9.10`
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip`
**Build type:** documentation-only GitHub readiness build
**Runtime behavior changed:** false
**Hardware validation:** not performed / not claimed


## Current status

G3 is complete. The project now has developer-facing documentation for architecture, testing, packaging, release process, code quality, AI maintainer rules, hardware-validation planning, and a hardware support matrix.

## Scope completed

- Added `docs/developer-guide/` documentation set.
- Added hardware-validation plan and support matrix.
- Updated `docs/README.md` navigation.
- Preserved runtime behavior and package cleanliness.

## Files changed or added

- `docs/developer-guide/README.md`
- `docs/developer-guide/architecture.md`
- `docs/developer-guide/testing.md`
- `docs/developer-guide/packaging.md`
- `docs/developer-guide/release-process.md`
- `docs/developer-guide/code-quality.md`
- `docs/developer-guide/ai-maintainer-rules.md`
- `docs/hardware-validation/hardware-validation-plan.md`
- `docs/hardware-validation/hardware-support-matrix.md`
- `docs/README.md`

## Validation performed

- `python -m py_compile service.py default.py`: passed
- `python tools/render_docs.py --check`: passed
- `python tools/sync_version.py --check`: passed
- `python tools/test_layout.py --check`: passed
- `python tools/i18n_extract.py --check`: passed
- `pytest -q tests/test_v2910_final_release.py`: 3 passed
- `pytest -q tests/test_v2910*.py`: 189 passed
- `python -m unittest discover -s tests`: 571 tests OK
- `python tools/audit_release.py --expected-version 2.9.10`: PASS 553/553
- Runtime ZIP audit: 68 runtime files, 0 forbidden files, ZIP integrity OK
- Post-unpack dev-source verification: sync version passed, v2.9.10 tests 189 passed, audit PASS 553/553

## Validation not performed / limitations

- Full unsplit `pytest -q` was attempted and timed out before summary, so it is not claimed as passed for G3.
- No new coverage run is claimed for G3. This build added documentation only and did not change runtime modules.
- No real hardware validation was performed.

## Packaging notes

Runtime ZIP was built with `BUILD_SUFFIX=github-g3`. Runtime ZIP audit found 68 files, 0 forbidden files, and valid ZIP integrity. Dev-source was unpacked and revalidated with v2.9.10 targeted tests and release audit.

## Historical reconstruction entry

```yaml
build_id: GitHub Readiness G3 — Developer Documentation Pack
baseline: script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip
scope: developer documentation, hardware validation documentation, AI maintainer rules
planned_success_rate: 95 percent
actual_outcome: successful documentation-only build
hardware_validation: not_performed_not_claimed
runtime_behavior_changed: false
```

## Resume prompt for next AI

```text
Proceed with GitHub Readiness Build G4 — GitHub Templates and Community Files.

Use this baseline:
script.oppo203.iso.external-2.9.10-github-g3-dev-source.zip

Rules:
- Do not change runtime behavior.
- Do not add features.
- Do not claim hardware validation.
- Add GitHub issue templates and pull request template only.
- Preserve v2.9.10 Final behavior and runtime ZIP cleanliness.
- Run practical validation and document limitations honestly.
- Produce build notes, manifest, test audit, hardware validation status, AI handoff, combined historical reconstruction handoff, and artifact bundle.
```


---

# Historical Build Reconstruction — G3

To reconstruct G3:

1. Start from `script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip`.
2. Create `docs/developer-guide/`.
3. Add architecture, testing, packaging, release process, code quality, and AI maintainer rule documents.
4. Add `docs/hardware-validation/hardware-validation-plan.md` and `docs/hardware-validation/hardware-support-matrix.md`.
5. Update `docs/README.md` to link the new documentation.
6. Run documentation, version, layout, i18n, targeted v2.9.10, unittest, audit, packaging, runtime ZIP audit, and post-unpack checks.
7. Package G3 runtime/dev-source/artifact outputs.
8. Keep hardware validation as `not_performed_not_claimed`.
