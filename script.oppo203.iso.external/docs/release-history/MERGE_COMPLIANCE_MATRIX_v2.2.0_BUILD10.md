# Merge Compliance Matrix — v2.2.0 Build 10

```yaml
build: v2.2.0 Build 10
addon_version: 2.2.0.10
baseline: script.oppo203.iso.external-2.2.0-build9.zip
scope: merge-completion candidate checkpoint
full_merge_status: in_progress_not_complete
coverage_gate: 99 percent enforced
hardware_validation: not_performed
```

## Purpose

Build 10 is a merge-compliance candidate checkpoint for the gradual v1.1.9 + v0.9.14 superset merge. It does not declare the merge complete unless every relevant matrix item is complete or explicitly not required for this release line.

## Decision

```text
Merge-complete status: NOT COMPLETE
Reason: remaining wizard/UI flow reconciliation and real hardware validation remain outside this build.
```

## Compliance matrix

| Area | Status | Evidence / next action |
|---|---|---|
| 12-SKU hardware compatibility table | Complete | `HARDWARE_COMPAT` and settings enum remain aligned and audited. |
| Chinoppo/M9201/M9203/M9205C/M9702 wake rewrite | Complete | Automated tests cover `#PON/#POW -> #EJT` model-gated behavior. |
| Stock OPPO pass-through | Complete | Automated tests preserve stock `#PON/#POW` behavior. |
| Reavon warning-only behavior | Complete | Reavon tests and audits ensure no OPPO command-map mutation. |
| Quick Start warning helper | Complete | Build 2/3/5/6 tests cover helper collection and surfacing. |
| AutoScript verbose-push warning helper | Complete | Build 2/3/5/6 tests cover helper, log marker, and UI surfacing. |
| Jailbroken stock OPPO JSON payload mode | Complete | Tests cover `oppo_http_payload_mode=json_payload` for stock OPPO with jailbreak enabled. |
| Service `Monitor.onSettingsChanged()` compatibility watcher | Mostly complete | Builds 1/3/4/6/7 cover model, jailbreak, AutoScript, persistence, and save-failure behavior. |
| Active wizard warning surfacing | Partially complete | One active v1.x wizard path is wired. Remaining broad wizard/UI reconciliation is deferred to a later slice. |
| v0.9.14 unique hardware tests | Mostly complete | Build 2 and later test slices port core unique behavior. Build 10 finds no additional safe one-build test gap beyond the recorded wizard/UI reconciliation. |
| v1.1.9 platform modules | Preserved | No broad rewrite; existing diagnostics, discovery, installer, stubs, fake server tests, and coverage-hardening tests remain passing. |
| Fake OPPO server tests | Complete | Existing fake server and reconnect tests remain passing. |
| Clean TCP disconnect is not playback stopped | Complete | Reconnect/verbose-push tests remain passing. |
| Canonical 76-key command map | Complete | Audit enforces 76 keys and blocks `#SIS`, `#PGU`, and `#PGD`. |
| 99 percent coverage gate | Complete | `.coveragerc` keeps `fail_under = 99`; coverage reports `TOTAL 99%`. |
| Release audit | Complete | Build 10 source and post-unpack audit are required to pass. |
| Self-contained AI handoff | Complete | v24 handoff must include top resume prompt and full Build 10 reconstruction bundle. |
| Real hardware validation | Needs hardware validation | No real OPPO, M9702/Chinoppo, TCL/Android TV, Kodi installation, or ADB hardware was tested. |
| Full merge-complete declaration | Deferred | Not declared complete in Build 10 because active wizard/UI reconciliation and hardware validation remain open. |

## Remaining gaps before full merge completion

```text
[ ] Reconcile remaining wizard/UI compatibility-warning flows without replacing the stable v1.x wizard in one large step.
[ ] Perform real hardware validation after the full merge candidate is ready.
[ ] Run a final release-candidate stabilization build after the remaining wizard/UI reconciliation is complete.
```

## Build 10 non-goals

```text
[not done] broad/full wizard replacement
[not done] real hardware validation
[not done] Reavon command-map support
[not done] lowering the 99 percent coverage gate
[not done] deleting historical reconstruction data
```
