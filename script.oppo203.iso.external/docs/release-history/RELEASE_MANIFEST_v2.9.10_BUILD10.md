# Release Manifest — v2.9.10 Build 10

- Runtime package: `script.oppo203.iso.external-2.9.10-build10.zip`
- Dev-source package: `script.oppo203.iso.external-2.9.10-build10-dev-source.zip`
- Artifact bundle: `script.oppo203.iso.external-2.9.10-build10-artifacts-bundle.zip`
- Checksum file: `script.oppo203.iso.external-2.9.10-build10.sha256`
- Baseline: `script.oppo203.iso.external-2.9.10-build9b-dev-source.zip`
- Hardware validation: not performed / not claimed

## Runtime/source changes

- Added `resources/lib/tv_diagnostics.py`.
- Added `tests/test_v2910_build10_tv_diagnostics.py`.
- Updated version/build metadata, package suffix, generated docs metadata, README, reference, web references, addon metadata, and current-build test expectations.

## Verification summary

```text
Source targeted Build 10 tests: 8 passed
Source v2.9.10 targeted suite: 96 passed
Source pytest split/file-by-file run: 842 passed, 12 subtests passed
Source unittest split/file-by-file run: 571 tests OK
Source coverage: TOTAL 99%
Source audit_release: PASS 457/457
Post-unpack targeted Build 10 tests: 8 passed
Post-unpack v2.9.10 targeted suite: 96 passed
Post-unpack audit_release: PASS 457/457
Runtime ZIP audit: 58 runtime files, forbidden dev/evidence files 0, integrity passed
```

## Protected behavior

OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, AVR sequencing, runtime ZIP policy, and the 99% coverage gate are preserved.
