# Merge Compliance Matrix — v2.2.0 Release

software_merge_status: complete_no_known_software_gaps
release_status: not_final_pending_real_hardware_validation_and_final_release_packaging
release_packaging_status: packaged_pending_real_hardware_validation

This v2.2.0 package is a software merge-complete candidate from the v1.1.9 + v0.9.14 gradual superset merge line. It is not a hardware-validated final release. Final packaging has been completed, but real hardware validation remains pending external validation.

## Compliance checklist

| Area | Status | Notes |
|---|---|---|
| 12-SKU hardware compatibility table | Complete | Preserved from v0.9.14 behavior. |
| Chinoppo / M9201 / M9203 / M9205C / M9702 wake rewrite | Complete | `#PON/#POW -> #EJT` model-gated behavior preserved. |
| Stock OPPO pass-through behavior | Complete | Stock OPPO `#PON/#POW` remains unchanged. |
| Reavon warning-only behavior | Complete | No Reavon command-map mutation. |
| No Reavon command-map mutation | Complete | Warning-only rule retained. |
| Quick Start warning behavior | Complete | Helper and wizard/UI surfacing tested. |
| AutoScript verbose-push warning behavior | Complete | Helper, logging, and wizard/UI surfacing tested. |
| Jailbreak JSON payload mode | Complete | Stock OPPO jailbreak flag maps to JSON payload mode. |
| service.Monitor.onSettingsChanged() compatibility watcher | Complete | Compatibility preset and persistence behavior tested. |
| Wizard/UI warning surfacing | Complete | Active wizard path includes compatibility warning surfacing. |
| Fake OPPO server tests | Complete | Hermetic test coverage retained. |
| Clean TCP disconnect is not playback stopped | Complete | Invariant retained. |
| Canonical 76-key command map | Complete | No `#SIS`, `#PGU`, or `#PGD`. |
| 99 percent coverage gate | Complete | Enforced through `.coveragerc`. |
| Self-contained AI handoff reconstruction | Complete | Latest handoff must include full source reconstruction. |
| Real hardware validation | Pending external validation | User will perform after packaging. |

## Decision

No known software merge gaps remain that can be validated hermetically. Real hardware validation remains external and pending.
