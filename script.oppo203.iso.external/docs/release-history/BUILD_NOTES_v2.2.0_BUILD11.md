# Build Notes — v2.2.0 Build 11

Build 11 further reduces the remaining wizard/UI compatibility-warning reconciliation gap.

## Scope

- Baseline: `script.oppo203.iso.external-2.2.0-build10.zip`
- Version: `2.2.0.11`
- Slice: active wizard compatibility-flag capture and safe warning/preset bridge
- Full merge status: still in progress, not declared complete

## Changes

- Active full wizard path now asks/stores the v0.9.14 jailbreak flag for stock OPPO selections.
- Active full wizard path now asks/stores the AutoScript port-23 shell-handler flag.
- Stock jailbroken OPPO wizard selections can apply `oppo_http_payload_mode=json_payload` through the existing compatibility bridge.
- Reavon remains warning-only and does not mutate OPPO command maps.
- Chinoppo clone preset confirmation remains explicit in the active wizard for stability.
- 99 percent coverage gate remains enforced.

## Build-process improvements preserved

Verification commands are run one at a time, and coverage runs use `-p no:ddtrace` to avoid local plugin timeout behavior.
