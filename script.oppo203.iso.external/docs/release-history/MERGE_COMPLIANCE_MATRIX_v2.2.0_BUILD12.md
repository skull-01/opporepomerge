# Merge Compliance Matrix — v2.2.0 Release 2.2.0

```yaml
version: 2.2.0
build_role: final_merge_compliance_review_and_release_candidate_stabilization
software_merge_status: complete_no_known_software_gaps
release_status: not_final_pending_real_hardware_validation_and_final_release_packaging
baseline: script.oppo203.iso.external-2.2.0-build11.zip
verification_process: one_command_at_a_time_with_no_ddtrace_for_pytest_coverage
```

## Decision summary

Release 2.2.0 is a **software merge-complete candidate** for the gradual v1.1.9 + v0.9.14 superset merge. The matrix review found no remaining known software gaps in the scoped merge items that can be validated hermetically.

This build is **not** labeled as the final release because real OPPO / Chinoppo / TCL / ADB hardware validation has not yet been performed and a final release packaging pass remains.

## Compliance matrix

| Area | Release 2.2.0 status | Evidence / notes |
|---|---|---|
| 12-SKU hardware compatibility table | Complete | `HARDWARE_COMPAT` and settings enum remain aligned at 12 entries. |
| Chinoppo / M9201 / M9203 / M9205C / M9702 wake rewrite | Complete | Tests preserve `#PON/#POW -> #EJT` for clone family and stock OPPO pass-through. |
| Stock OPPO pass-through behavior | Complete | UDP-203/UDP-205 preserve stock power commands unless jailbreak JSON payload is explicitly enabled. |
| Reavon warning-only behavior | Complete | Reavon UBR-X100/X110/X200 remain warning-only and do not mutate OPPO command maps. |
| No Reavon command-map mutation | Complete | Tests and audit preserve command map invariants. |
| Quick Start warning behavior | Complete | Warnings are collected, logged, and surfaced through compatibility helpers. |
| AutoScript verbose-push warning behavior | Complete | Active wizard and service-warning paths can store/surface the AutoScript port-23 shell-handler warning. |
| Jailbreak JSON payload mode | Complete | Active wizard full path can capture jailbreak flag and apply `oppo_http_payload_mode=json_payload` for stock OPPO. |
| service.Monitor.onSettingsChanged() compatibility watcher | Complete | Model, jailbreak, and AutoScript setting changes are watched; persistence edge cases are tested. |
| Compatibility preset persistence | Complete | `settings_reader.save_settings()` avoids unsafe blank add-on-data writes and persists safe preset values when a valid data dir exists. |
| Wizard/UI warning surfacing | Complete candidate | Active wizard path captures compatibility flags and surfaces warnings without replacing the v1.x wizard. |
| Fake OPPO server tests | Complete | Loopback fake-server tests remain part of the suite. |
| Clean TCP disconnect is not playback stopped | Complete | Existing TCP-client regression tests remain part of the suite. |
| Canonical 76-key command map | Complete | Audit requires 76 keys and forbids `#SIS`, `#PGU`, and `#PGD`. |
| 99 percent coverage gate | Complete | `.coveragerc` keeps `fail_under = 99`; coverage verification reports `TOTAL 99%`. |
| Documentation lockstep | Complete for Release 2.2.0 | README, reference, web-references, build notes, manifest, coverage report, test/audit report, and this matrix were updated. |
| Self-contained AI handoff reconstruction | Complete for Release 2.2.0 | `Combined_DevLog_and_Addon_Research_v26_Handoff.md` embeds the latest Release 2.2.0 reconstruction bundle. |
| Real hardware validation | Pending external validation | Not performed by the AI; must be performed by the user on real OPPO/Chinoppo/TCL/ADB hardware. |
| Final release-candidate packaging | Pending next release decision | Release 2.2.0 is a verified candidate checkpoint; a separate final/RC packaging pass can follow after hardware validation guidance. |

## Remaining release blockers

```text
[external] Real OPPO / Chinoppo / TCL / Android TV / ADB hardware validation.
[release] Final RC or final release packaging decision after user hardware plan.
```

## Honest status statement

```text
Release 2.2.0 closes the known software merge-compliance gaps that can be tested hermetically.
It is a software merge-complete candidate, not a hardware-validated final release.
```
