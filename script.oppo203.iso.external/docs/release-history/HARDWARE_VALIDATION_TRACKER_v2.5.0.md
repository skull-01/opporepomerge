# Hardware Validation Tracker — v2.5 Series

Real hardware validation is user-owned. The AI must not mark hardware validation as passed unless the user provides results.

## Baseline

- Baseline package: v2.2.0 release package.
- Active development series: v2.5.x.
- Current build: v2.5.0 Build 1.
- AI-performed hardware validation: not performed.

## Test matrix

| Area | Device / environment | Status | Notes |
|---|---|---:|---|
| OPPO UDP-203 stock workflow | Real hardware | Pending user validation | Not tested by AI |
| Chinoppo / M9702 workflow | Real hardware | Pending user validation | Not tested by AI |
| Reavon warning-only behavior | Real hardware or user workflow | Pending user validation | Software behavior preserved |
| TCL / Android TV switching | Real hardware | Pending user validation | Not tested by AI |
| ADB switching | Real device/environment | Pending user validation | Not tested by AI |
| ISO playback launch | User environment | Pending user validation | Not tested by AI |
| Wizard fresh install | User/Kodi environment | Pending user validation | Software tests only |
| Upgrade from v2.2.0 | User/Kodi environment | Pending user validation | Software tests only |

## Findings log

| Date | Build | Finding | Severity | Reproduction steps | Resolution status |
|---|---|---|---|---|---|
| 2026-05-16 | v2.5.0 Build 1 | No user hardware findings recorded yet. | N/A | N/A | Open tracker |

## Rule for future builds

Any hardware issue discovered against v2.2.0 or v2.5.x should become a tracked v2.5 fix item. Future AI agents must preserve v2.2.0 behavior unless a specific hardware result, regression, or user instruction justifies a change.
