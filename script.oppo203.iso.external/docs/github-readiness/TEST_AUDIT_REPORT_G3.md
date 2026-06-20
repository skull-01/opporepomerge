# GitHub Readiness Build G3 — Developer Documentation Pack

**Project:** `script.oppo203.iso.external`
**Version:** `2.9.10`
**Baseline:** `script.oppo203.iso.external-2.9.10-github-g2-dev-source.zip`
**Build type:** documentation-only GitHub readiness build
**Runtime behavior changed:** false
**Hardware validation:** not performed / not claimed


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

## Validation not claimed

- Full unsplit `pytest -q` was attempted and timed out before summary, so it is not claimed as passed for G3.
- No new coverage run is claimed for G3. This build added documentation only and did not change runtime modules.
- No real hardware validation was performed.

## Interpretation

The documentation-only changes passed targeted v2.9.10 checks, release audit, runtime ZIP audit, unittest discovery, and post-unpack checks. The full unsplit pytest command timed out, so G3 relies on the targeted v2.9.10 suite, unittest discovery, audit, and post-unpack evidence instead of claiming a full unsplit pytest pass.
