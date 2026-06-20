# Release Manifest — v2.9.10 Final

Final artifacts:

- `script.oppo203.iso.external-2.9.10.zip`
- `script.oppo203.iso.external-2.9.10-dev-source.zip`
- `script.oppo203.iso.external-2.9.10-artifacts-bundle.zip`
- `script.oppo203.iso.external-2.9.10.sha256`
- `Combined_AI_Handoff_and_Historical_Build_Reconstruction_v104_v2.9.10_FINAL.md`

## Gate

The final release uses the Final Release Gate: source checks, final targeted tests, all v2.9.10 tests, focused playback-sequencing regression tests, full pytest, full unittest discovery, source coverage at TOTAL 99%, release audit, final packaging, post-unpack verification including coverage, and runtime ZIP audit.

## Runtime ZIP policy

The installable runtime ZIP excludes tests, tools, scripts, docs, release evidence, reports, handoff files, Markdown evidence files, caches, compiled Python files, and other development artifacts.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
