# Release Manifest — v2.9.10 Build 18

Expected artifacts:

- `script.oppo203.iso.external-2.9.10-build18.zip`
- `script.oppo203.iso.external-2.9.10-build18-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-build18-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10-build18.sha256`
- `Combined_AI_Handoff_and_Historical_Build_Reconstruction_v103_v2.9.10_BUILD18.md`

## Gate

Build 18 uses the Full Release Gate: source checks, targeted Build 18 tests, all v2.9.10 tests, focused playback-sequencing regression tests, full pytest, full unittest discovery, source coverage at TOTAL 99%, release audit, packaging, post-unpack verification including coverage, and runtime ZIP audit.

## Runtime ZIP policy

The installable runtime ZIP must exclude tests, tools, scripts, docs, release evidence, reports, handoff files, Markdown evidence files, caches, compiled Python files, and other development artifacts.
