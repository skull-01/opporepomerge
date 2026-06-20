# Release Manifest — v2.9.10 Build 12

## Baseline

- Source baseline: `script.oppo203.iso.external-2.9.10-build11-dev-source.zip`
- Add-on version: `2.9.10`
- Build identity: `v2.9.10 Build 12`

## Outputs

- `script.oppo203.iso.external-2.9.10-build12.zip`
- `script.oppo203.iso.external-2.9.10-build12-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-build12-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10-build12.sha256`

## Verification plan

Use the Build 11 timeout-safe verification strategy: source checks, targeted Build 12 tests, deterministic pytest shards, unittest discovery, coverage shards/combine, release audit, package, post-unpack verification, and runtime ZIP audit.
