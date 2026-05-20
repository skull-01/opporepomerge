# Hardware Validation Tracker — v2.5.2

Real hardware validation remains user-owned. The AI must not mark a model as fully validated unless the user provides results for that exact device/firmware/workflow.

## Baseline

- Baseline package: v2.5.1 Build 1 startup-power release package.
- Active development series: v2.5.2.
- Current build: v2.5.2 Build 1.
- AI-performed hardware validation: not performed.

## User-provided finding

| Date | Build | Finding | Status |
|---|---|---|---|
| 2026-05-17 | v2.5.2 Build 1 planning | User confirmed that playing a NAS-mounted file on OPPO/Chinoppo-compatible hardware works. | Accepted as user-provided capability evidence; per-model validation still pending. |

## Firmware gates

| Device family | Minimum requirement | Recommended target | Status |
|---|---|---|---|
| Original OPPO UDP-203/UDP-205 | Jailbroken firmware with AutoScript support, minimum `20X-56` | `20X-65-0131` jailbreak-compatible line | Software gate added; hardware validation pending |
| Chinoppo / M9201 / M9203 / M9205C / M9702 / similar clone-family profiles | Compatible active firmware/binary with AutoScript or equivalent boot-time scripting, SMB/NFS playback, and confirmed NAS-mounted playback behavior | Model-specific user confirmation | Software gate added; per-model validation pending |

## Test matrix

| Area | Device / environment | Status | Notes |
|---|---|---:|---|
| OPPO UDP-203 jailbroken NAS playback | Real hardware | Pending user validation | Requires firmware >= 20X-56; 20X-65-0131 recommended |
| OPPO UDP-205 jailbroken NAS playback | Real hardware | Pending user validation | Requires firmware >= 20X-56; 20X-65-0131 recommended |
| Chinoppo M9702 NAS playback | Real hardware | User capability confirmed broadly; exact build retest pending | Per-model firmware/binary should be recorded |
| Chinoppo M9201/M9203/M9205C NAS playback | Real hardware | Pending user validation | Requires compatible active firmware/binary |
| IPUK/GIEC/Magnetar-style clone profiles | Real hardware | Pending user validation | Treated as clone-family candidates only |
| Path mapping | Software helper | Deferred | Planned for v2.5.2 Build 3 after Build 2 packaging cleanup |
| NAS playback trigger adapter | Real hardware + software | Deferred | Planned after path mapping |
