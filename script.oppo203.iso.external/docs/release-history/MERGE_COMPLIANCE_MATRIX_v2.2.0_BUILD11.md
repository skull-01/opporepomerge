# Merge Compliance Matrix — v2.2.0 Build 11

```yaml
version: 2.2.0.11
full_merge_status: in_progress_not_complete
build_focus: further reduce wizard/UI compatibility-warning reconciliation gap
```

| Area | Build 11 status | Evidence |
|---|---|---|
| Active wizard warning surfacing | Further reduced gap | Full wizard now captures jailbreak and AutoScript-shell flags and surfaces warnings through existing UI adapters. |
| Stock OPPO jailbreak JSON payload | Complete for active wizard full path | Full wizard can store jailbreak flag and apply `oppo_http_payload_mode=json_payload`. |
| Reavon warning-only | Preserved | Reavon warning surfaces without OPPO command-map mutation. |
| Chinoppo clone preset | Preserved, explicit confirmation retained | Existing active wizard prompt remains for stability. |
| 99 percent coverage gate | Preserved | `.coveragerc` gate remains at 99. |
| Real hardware validation | Needs hardware validation | Not performed in this build. |

## Remaining gaps before full merge completion

- Final wizard/UI reconciliation review after this Build 11 slice.
- Real hardware validation after full merge candidate is ready.
- Final release-candidate stabilization build.
