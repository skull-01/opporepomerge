# Version 2.5.2 Build 1 — OPPO/Chinoppo NAS Playback Capability Gates

This build converts the v45 AutoScript / M9702 / TrueNAS / NFS research into software gating rules only. Original OPPO UDP-203/UDP-205 NAS playback support is gated behind jailbreak plus AutoScript-capable firmware, with `20X-56` treated as the minimum and `20X-65-0131` as the recommended jailbreak target. Firmware `20X-54-1127` and older/pre-56 firmware are blocked for AutoScript-based workflows.

Chinoppo-family support is treated as a capability-gated family rather than a single-version firmware rule because the active patched firmware/binary determines available behavior. M9201, M9203, M9205C, M9702, IPUK-UHD8592, GIEC-BDP-G5300, and Magnetar-UDP800 style profiles are candidate clone-family profiles that require user/device confirmation before claiming per-model support.

The user confirmed that NAS-mounted file playback works. This build records that as capability evidence but does not claim universal hardware validation.

---

# V45 AutoScript / M9702 / TrueNAS research source note

The v45 handoff adds the user-supplied file `oppo203_kodi_external_player_reference.md` as embedded research/reference material in `reference.md`. Its inline `[cite:n]` markers were preserved as provided by the user. This documentation-only update did not independently re-browse or verify those source markers and did not add runtime behavior.

# Version 2.5.0 Build 1 — v2.5 development baseline

Build 1 starts the v2.5 series from the v2.2.0 software-merge baseline. It is intentionally low risk: version metadata, v2.5 planning/tracking documentation, release-audit evidence, packaging, and verification are updated while runtime behavior is preserved.

Current v2.5 focus areas:

- Stability-first enhancement.
- User experience and wizard refinement.
- Diagnostics and supportability.
- Hardware-validation-driven fixes after user testing.

Real hardware validation remains pending and must be recorded in `HARDWARE_VALIDATION_TRACKER_v2.5.0.md`.

---

# Version 2.2.0 Build 9 — Merge test-parity audit checkpoint

Build 9 is a narrow v1.1.9 + v0.9.14 superset-merge slice.  It does not broaden runtime behavior.  It records a test-parity audit of already protected v0.9.14 hardware-compatibility behavior and remaining merge work before a merge-complete candidate.

Key points:

- Adds `MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md`.
- Keeps the full merge in progress, not complete.
- Preserves the 99 percent coverage gate.
- Preserves the self-contained handoff reconstruction rule for future builds.
- Does not perform real hardware testing.

Required verification:

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.9
```

# Version 2.2.0 Build 8 - Merge parity audit and self-contained handoff reconstruction

Build 8 continues the gradual v1.1.9 + v0.9.14 superset merge with a narrow merge-parity audit checkpoint. It also starts the forward rule that the latest AI handoff Markdown must contain a copy/paste resume prompt at the top and a reconstruction bundle for the latest build source tree.

## Build 8 verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.9
```

## Build 8 scope

- Adds `MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md`.
- Keeps the full merge in progress, not complete.
- Preserves the 99 percent coverage gate.
- Requires the v22 handoff to include reconstruction data and a resume prompt at the top.
- Does not claim real hardware validation.

## Version 2.2.0 Build 7 source references

No new external web sources were used for Build 7. This is a local merge-hardening build based on the existing v0.9.14 compatibility-watcher requirements and the current v2.2 gradual merge line.

| Decision | Source basis | Implementation impact |
|---|---|---|
| Keep service watcher persistence safe | Existing v0.9.14 watcher behavior in the project handoff | Added tests for save failure and missing add-on-data directory. |
| Keep Reavon warning-only | Existing hardware compatibility research | No Reavon command-map mutation was added. |
| Preserve stock jailbreak payload mode | Existing v0.9.14 compatibility-preset requirement | Verified stock OPPO jailbreak toggle can persist `json_payload`. |

---

## Version 2.2.0 Build 6 source references

### New sources used

No new external web sources were used for this release.

### Reused sources and project evidence

Build 6 reuses the existing project research and v0.9.14 handoff requirements that compatibility warnings should be visible to users and support logs, while Reavon remains warning-only and Chinoppo/M9702 behavior remains model-gated.

### Source-to-decision mapping

| Decision | Source basis | Implementation impact |
|---|---|---|
| Surface warnings in the active wizard path | Existing v0.9.14 wizard-warning behavior | `_surface_hardware_compatibility_warnings()` in `wizard.py` |
| Keep Reavon warning-only | Existing hardware compatibility research | Warning surfacing does not mutate Reavon settings |
| Avoid broad wizard rewrite | Stability-first v2.2 merge strategy | Adapter added without replacing the active wizard |
| Preserve support logging | Existing `[v0.9.14-warning]` convention | Warning helper receives `_wizard_log` |

---

## Version 2.2.0 Build 5 source references

### New sources used

No new external web sources were used for this release.

### Reused sources and project evidence

Build 5 reuses the existing project research and v0.9.14 handoff requirements that compatibility warnings should be visible to users and support logs, while Reavon remains warning-only and Chinoppo/M9702 behavior remains model-gated.

### Source-to-decision mapping

| Decision | Source basis | Implementation impact |
|---|---|---|
| Surface compatibility warnings through UI helpers | Existing v0.9.14 wizard-warning behavior | `surface_compatibility_warnings()` |
| Keep Reavon warning-only | Existing hardware compatibility research | `apply_and_surface_compatibility()` does not mutate Reavon settings |
| Keep support-log marker | Existing `[v0.9.14-warning]` convention | Warning logging is preserved alongside UI surfacing |
| Avoid broad wizard rewrite | Stability-first v2.2 merge strategy | Helpers added without replacing the active wizard flow |

---

## Version 2.2.0 Build 4 source references

### New sources used

No new external web sources were used for this release.

### Reused project sources

| Decision | Source | Impact |
|---|---|---|
| Preserve v0.9.14 model-change watcher behavior | Existing project handoff and v0.9.14 reconstruction context | Service watcher continues compatibility-preset reapplication. |
| Keep Reavon warning-only | Existing compatibility invariant | Persistence path only saves real preset mutations and does not mutate Reavon command maps. |
| Keep merge gradual | Current v2.2 merge strategy | Build 4 is limited to service watcher persistence. |

## Version 2.1.0 Build 5 source references

### New sources used

No new external web sources were used for Build 5. The work is internal coverage and release-audit hardening.

### Source-to-decision mapping

| Decision | Source | Implementation impact |
|---|---|---|
| Raise coverage gate from 97% to 98% | Local measured `coverage.py` report from the Build 5 source tree | `.coveragerc` now enforces `fail_under = 98`. |
| Continue gradual path to 99% before merge | User direction in the continuation chat | Build 5 targets 98%, not the final 99%, to keep the hardening incremental. |
| Avoid full merge | Project handoff and user direction | No v1.1.9 + v0.9.14 superset merge work was started. |

## Version 2.1.0 Build 4 source references

### New external sources used

No new external web sources were used for Build 4.

### Source-to-decision mapping

| Decision | Source used | Implementation impact |
|---|---|---|
| Raise coverage gate from 96% to 97% | Local measured `coverage.py` report from the Build 4 source tree | `.coveragerc` now enforces `fail_under = 97`. |
| Keep the 99% effort gradual | User direction to reach 99% before the full merge | Build 4 targets 97%, not 99%, to avoid brittle line-only tests. |
| Avoid merge work | Current project handoff and user direction | Full v1.1.9 + v0.9.14 merge remains deferred. |

### Reused project references

Existing OPPO protocol, Kodi add-on, and hardware compatibility references remain unchanged. Build 4 is test/audit hardening only.

## Version 2.1.0 Build 3 source references

No new external web sources were used for this build. This was internal coverage hardening and one local bug fix based on automated test evidence. Existing project references and protocol invariants are preserved.

### Source-to-decision mapping

| Decision | Source basis | Implementation impact |
|---|---|---|
| Raise coverage gate from 94% to 96% | Measured local `coverage.py` report from v2.1.0 Build 3 | `.coveragerc` now enforces `fail_under = 96`. |
| Keep 99% gradual | Project direction to reach 99% before the full merge | Build 3 targets 96%, not 99%, to avoid brittle line-only tests. |
| Fix UDP discovery cleanup bug | New local regression test for top-level socket creation failure | `discover_oppo()` now safely returns an empty result when socket creation fails. |

# Version 2.1.0 Build 1 source references

## Version 2.1.0 Build 2 source references

No new external web sources were used for this build. The work is internal test/audit hardening based on existing project requirements: preserve MVP behavior, raise coverage gradually before the full merge, keep tests hermetic, and do not require real OPPO, TV, ADB, or Kodi hardware.

Existing OPPO/Kodi/hardware references already captured in this document remain the source background for protocol and compatibility behavior.


No new external web sources were consulted for this coverage-gate hardening build. The work used the existing v2.0.0 release artifact, the project handoff rules, the staged coverage-gate requirement already documented in the project, and observed test/coverage results from this build session.

| Decision | Source used | Implementation impact |
|---|---|---|
| Address the deferred 92 percent coverage gate | Existing project handoff and user instruction in this conversation | Added coverage-focused tests, raised `.coveragerc` to `fail_under = 92`, and added audit evidence. |
| Preserve MVP runtime scope | v2.0.0 release artifacts and handoff do-not-regress rules | No feature expansion or full superset merge. |
| Fix installer fallback bug | Test-discovered code path during coverage hardening | Added missing `xbmc` import to `resources/lib/installer.py`. |


# Version 2.0.0 Final Release source references

No new external web sources were consulted for this final release repack. The work reused the existing project handoff, the verified Build 6 artifact, and the user's explicit instruction to package this as the 2.0 release while deferring real hardware testing until after the full merge.

| Decision | Source | Implementation impact |
|---|---|---|
| Package current Build 6 line as final 2.0 release | User instruction in this conversation | Restored `addon.xml` version to `2.0.0`, produced `script.oppo203.iso.external-2.0.0.zip`, and generated a matching checksum. |
| Defer real hardware validation until after full merge | User instruction in this conversation | Updated release notes, hardware validation notes, and final handoff caveats; no physical hardware validation is claimed. |
| Preserve MVP scope | Existing v2 handoff and Build 6 release evidence | No runtime feature expansion; full superset merge remains deferred. |

# Version 2.0.0 Build 6 source references

No new external web sources were consulted for this build-id update. The work reused the existing v2.0.0 final package, the project handoff rules, and the user's explicit instruction to change the build id to `2.0.0.6`.

| Decision | Source reused | Implementation impact |
|---|---|---|
| Change build id to `2.0.0.6` | User instruction in this conversation | Updated `addon.xml`, tests, audit expectations, and package name. |
| Keep scope narrow | Existing stability-first release rules | No runtime feature expansion and no superset merge. |
| Preserve final evidence | Existing v2.0.0 package and handoff rules | Kept final release notes, manifest, MVP matrix, and hardware note in the package. |

Physical OPPO, physical M9702/Chinoppo, physical TCL/Android TV, and real ADB behavior were not tested during this build-id update.

---

# Version 2.0.0 Final source references

No new external web sources were consulted for this final packaging step. The work reused the v3.1 AI-friendly handoff, the embedded Build 5 reconstruction bundle, existing project release/audit rules, and the v2.0 MVP final-release checklist.

| Decision | Source reused | Implementation impact |
|---|---|---|
| Convert Build 5 to final `2.0.0` | v3.1 handoff final-release checklist | Updated `addon.xml`, tests, and audit expected version. |
| Add final release notes and manifest | Mandatory handoff/release-output rules | Added `RELEASE_NOTES_v2.0.0.md` and `RELEASE_MANIFEST_v2.0.0.md`. |
| Add final MVP and hardware status evidence | Build 4/5 release-candidate evidence and v2.0 MVP checklist | Added final compliance matrix and hardware-validation note without claiming new physical hardware testing. |
| Preserve staged coverage status | Existing Build 3/4/5 coverage-staging decision | Kept 92% gate deferred to post-MVP hardening. |

Physical OPPO, physical M9702/Chinoppo, physical TCL/Android TV, and real ADB behavior were not tested during this final packaging step.

---

# Version 2.0.0 Build 5 source references

No new external web sources were consulted for this build. The build reused the consolidated project handoff, v2 MVP roadmap, Build 4 MVP compliance posture, and the existing project audit requirements.

| Decision | Source reused | Implementation impact |
|---|---|---|
| Add release audit helper | Project rule requiring tests and audits before packaging | Added `tools/audit_release.py` and tests around its checks. |
| Add release manifest | Local-AI handoff requirement for exact files changed, tests, audit result, and deferrals | Added `RELEASE_MANIFEST_v2.0.0_BUILD5.md`. |
| Keep coverage staged | Existing v2 roadmap staged coverage path | Did not claim the 92% coverage gate is complete. |
| Preserve manual hardware validation evidence | Build 4 user-provided/manual hardware-validation milestone | Retained Build 4 hardware-validation document and referenced it in Build 5 manifest. |

---

# Version 2.0.0 Build 4 source references

No new external web sources were consulted for this build. The build used existing project roadmap requirements and the user-provided instruction to treat the latest real-hardware test as passed with no issues found.

| Decision | Source reused | Implementation impact |
|---|---|---|
| Record manual hardware validation | User instruction in the continuation chat | Added `HARDWARE_VALIDATION_v2.0.0_BUILD4.md` and README/reference notes. |
| Make MVP compliance explicit | v2 MVP roadmap and prior Build 1-3 evidence | Added `MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md`. |
| Restore hidden coverage config | Existing CI/scaffolding tests and v1.x coverage artifact requirement | Added `.coveragerc` back to the packaged source tree and tested for its presence. |
| Keep coverage staged | v2 roadmap Phase 5 staged coverage path | Kept coverage as report-mode in CI while retaining the historical `fail_under = 85` setting. |

The user-provided hardware result is recorded as project input, not as an automated test result.

---

# Version 2.0.0 Build 3 source references

No new external web sources were consulted for this build. The work reused the consolidated project handoff and the v2.0 roadmap item requiring Kodi API mocking and either a raised coverage gate or a documented staged coverage path.

| Decision | Source reused | Implementation impact |
|---|---|---|
| Add Kodi API stubs | v2 roadmap Phase 5: Kodi API mocking and coverage | Added test-only `xbmc`, `xbmcaddon`, `xbmcgui`, `xbmcvfs`, `xbmcplugin`, and `xbmcdrm` stubs under `tests/_stubs/`. |
| Keep stubs opt-in | Existing no-Kodi import-guard tests and roadmap requirement for normal-Python testing | New stub tests use a context manager instead of globally injecting stubs through `conftest.py`. |
| Stage, not fake, the coverage gate | v2 roadmap acceptance criterion allowing a documented staged path | CI still emits a coverage report, but does not enforce the final gate until stub-backed module coverage is expanded honestly. |

Physical OPPO, physical TCL/Android TV, and real Kodi UI behavior were not tested in this build.

---

# Version 2.0.0 Build 2 source references

No new external web sources were consulted for this build. The work reused the consolidated project handoff, the v2.0 MVP roadmap, and the v0.9.14 hardware-compatibility requirements already embedded in the project handoff.

| Decision | Source reused | Implementation impact |
|---|---|---|
| Preserve M9702/Chinoppo wake rewrite | v2 MVP roadmap and v0.9.14 compatibility notes | Kept clone-only `#PON` / `#POW` to `#EJT` resolution. |
| Preserve stock OPPO power commands | Slice 2 acceptance criteria | Fixed stock UDP-203/205 `#POW` so it remains `#POW`. |
| Complete TCL/Android TV switching MVP path | Slice 3 acceptance criteria | Added optional, non-fatal TV switching in External Player flow. |
| Avoid real hardware in tests | MVP test requirements | Added ADB runner injection and fake OPPO loopback server. |
| Do not treat clean TCP disconnect as stop | Do-not-regress list | Split socket disconnect from explicit `@UPL` / `@UPW` stop events. |

Physical OPPO, physical TV, and physical ADB behavior were not tested in this build. Those remain manual hardware-validation items.

---

# Version 2.0.0 Build 1 source references

No new external web sources were consulted for this build. The implementation reused the consolidated project handoff, the v2.0 MVP roadmap, the verified v1.x reconstruction bundle, and the v0.9.14 hardware-compatibility source line embedded in the handoff.

Source-to-decision mapping:

| Decision | Source reused | Implementation impact |
|---|---|---|
| Start from v1.x baseline | v2.0 roadmap / handoff | Reconstructed the v1.x bundle and ran the 305-test baseline before edits. |
| Keep v2 MVP narrow | v2.0 MVP-first roadmap | Started Build 1 as an External Player-first MVP build, not the full v1.3 merge. |
| Preserve M9702 wake behavior | v0.9.14 hardware compatibility notes | Added hardware profiles and `#PON`/`#POW` to `#EJT` send-time resolution for Chinoppo/M9702-style models. |
| Preserve protocol corrections | v0.9.8/v0.9.14 command-map notes | Restored the canonical 76-key command map and regression tests against `#SIS`, `#PGU`, and `#PGD`. |

---

# Web References Used

This file collects the web links used while designing the add-on and records the relevant extracted details. It is meant to be useful even if you do not open the external pages.

## Kodi external-player and `playercorefactory.xml`

### Kodi external-player examples and rule behavior

URL: https://forum.kodi.tv/showthread.php?tid=323728

Relevant notes:

- Kodi external players are configured with `playercorefactory.xml`.
- External-player definitions live under `<players>`.
- Routing rules live under `<rules>`.
- A rule can target specific file types with `filetypes="..."`.
- Example structure from the discussion:

## Version 2.1.0 Build 6 source references

No new external web sources were used for Build 6. The build is a local test, audit, and documentation hardening pass. Existing project protocol and hardware references are preserved unchanged.

Source-to-decision mapping:

| Decision | Source basis |
|---|---|
| Raise coverage gate to 99% | Local coverage measurement and the project's gradual pre-merge hardening plan |
| Avoid full merge in Build 6 | Existing AI handoff continuation rule to defer the v1.1.9 + v0.9.14 superset merge |
| Avoid real hardware claims | Existing release honesty rule and user instruction that real hardware testing will happen later |


## Version 2.1.0 Build 7 source references

No new external web sources were used for Build 7. The build is a local coverage, test, audit, and documentation hardening pass. Existing OPPO/Kodi/hardware references remain preserved from earlier documentation.

| Decision | Source basis | Implementation impact |
|---|---|---|
| Improve raw combined coverage after displayed 99% | User request to try another build to further increase coverage | Added Build 7 branch tests and measured raw line+branch coverage above 99%. |
| Avoid the full merge | Existing project continuation rule | No v1.1.9 + v0.9.14 superset merge work was started. |
| Keep tests hermetic | Existing coverage-hardening policy | Tests use local stubs/fakes only; no OPPO, Kodi, ADB, or TV hardware required. |

## Version 2.1.0 Build 8 source references

No new external web sources were used for Build 8. This build is a local coverage, test, audit, packaging, and documentation hardening pass. Existing OPPO/Kodi/hardware references remain preserved from earlier documentation.

| Decision | Source basis | Implementation impact |
|---|---|---|
| Improve raw combined coverage above Build 7 | User request to do another build to increase coverage | Added Build 8 branch tests and measured raw combined line+branch coverage at 99.44%. |
| Avoid starting the merge | Existing project handoff and user direction | Build 8 changes are limited to coverage/test/docs/audit/package identity. |

## Version 2.2.0 Build 1 source references

No new external web sources were used for Build 1. This build uses the existing project handoff and embedded v0.9.14 reconstruction notes as the source of truth for the compatibility watcher and helper API.

| Decision | Source used | Implementation impact |
|---|---|---|
| Restore model-change compatibility watcher | Existing v0.9.14 handoff/reconstruction content | Added `Monitor.onSettingsChanged()` behavior in `service.py`. |
| Preserve `apply_compatibility_preset()` helper surface | Existing v0.9.13/v0.9.14 project history | Added narrow `first_run_wizard.py` compatibility helper module. |
| Keep Reavon warning-only | Existing hardware-compatibility rules | Tests assert Reavon warnings do not mutate OPPO command maps. |
| Avoid broad feature merge | User direction to merge gradually and focus on stability | Build 1 is limited to one isolated compatibility-watcher slice. |



## Version 2.2.0 Build 2 source references

No new external web sources were used for Build 2. This build uses the existing project handoff and embedded v0.9.14 reconstruction notes as the source of truth for hardware compatibility tests and warning behavior.

| Decision | Source used | Implementation impact |
|---|---|---|
| Port M9203/M9205C targeted tests | Existing v0.9.14 handoff/reconstruction content | Added explicit per-SKU tests for clone wake/profile/preset behavior. |
| Preserve Reavon warning-only behavior | Existing hardware-compatibility rules | Tests assert all Reavon variants warn and do not mutate OPPO commands. |
| Preserve jailbreak JSON payload rule | Existing v0.9.12/v0.9.14 research implementation notes | Tests assert stock OPPO jailbreak payload behavior and no stacking on clones/Reavon. |
| Harden add-on version audit | Local build audit finding | Audit now parses the XML attribute and checks XML declaration explicitly. |
| Avoid broad merge | User direction to merge gradually and focus on stability | Build 2 is limited to test-port/audit-hardening for existing compatibility behavior. |


## Version 2.2.0 Build 3 source references

### New sources used

No new external web sources were used for this release.

### Reused sources

This build reuses the existing v0.9.14 project research and handoff material about AutoScript shell-handler risk, Quick Start warnings, Reavon warning-only behavior, and compatibility warning logging.

### Source-to-implementation mapping

- AutoScript verbose-push warning behavior -> `first_run_wizard.collect_compatibility_warnings()` and `service.Monitor.onSettingsChanged()`.
- Warning logging support traceability -> `[v0.9.14-warning]` log marker.
- Reavon warning-only invariant -> no command-map mutation in the Build 3 tests.


## Version 2.2.0 Build 10 source references

No new external web sources were used for Build 10. This build reuses the existing project handoff, Build 9 artifacts, historical v1.1.9/v0.9.14 reconstruction data, and internal test/audit evidence. The primary source-to-decision artifact is `MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD10.md`.

Build-process note: the `-p no:ddtrace` coverage command is a local container reliability improvement, not a product behavior change.


## Version 2.2.0 Build 11 source references

No new external web sources were used for Build 11. The build uses existing project handoff data, historical v0.9.14 compatibility behavior, Build 10 merge-compliance findings, and internal test/audit evidence.

Source-to-decision mapping:

| Source | Decision |
|---|---|
| v0.9.14 compatibility watcher/wizard history | Add full-wizard capture for jailbreak and AutoScript-shell flags |
| Build 10 merge-compliance matrix | Focus Build 11 on remaining wizard/UI reconciliation gap |
| Existing Reavon warning-only invariant | Preserve warning-only behavior and avoid command-map mutation |

## Version 2.2.0 Release 2.2.0 source references

No new external web sources were used for Release 2.2.0. The build uses the existing project handoff, v1.1.9/v0.9.14 reconstruction history, and prior Build 10/11 merge-compliance records as the source of truth.

Release 2.2.0 adds a software merge-compliance matrix and keeps the hardware-validation caveat explicit. No source claim was added that depends on newly consulted web material.

## Version 2.2.0 source references

No new external web sources were used for the v2.2.0 packaging build. Existing project references, research notes, and prior handoff data were reused.

## v2.5.3 Build 2 reference note

No new external web research was required for this build. The implementation follows the user-approved Option 4 rule from the combined handoff: tag-aware XML rules for 4K/UHD/2160p disc-style ISO, BDMV, and MPLS sources only, with loose/raw video formats left to Kodi.

## v2.5.3 Build 3 reference note

No new external web references were introduced for Build 3. The build is an internal version-identity and audit reconciliation slice based on the existing project handoff and Build 2 source baseline.



## v2.5.3 Build 4 reference note

No new external web reference was added for Build 4. The build is an internal safety hardening step based on the existing project rules for conservative Option 4 XML routing, runtime ZIP cleanliness, and no hardware-validation claims without user-provided device results.


## v2.5.3 Build 5 reference note

No new external web reference was added for Build 5. The build is an internal readiness/evidence standardization step based on the existing project handoff, v2.5.2 NAS capability gates, v2.5.3 Option 4 XML rules, and the standing rule that hardware validation must not be claimed without user-provided real device results.

## v2.5.3 Build 6 reference note

No new external web reference was added for Build 6. The build is an internal pre-hardware release-candidate packaging freeze based on the existing v2.5.3 Build 1 through Build 5 software baseline and the standing handoff rule that hardware validation must not be claimed without user-provided real device results.

## v2.9.0 release reference note

No new external web research was added for Version 2.9.0. This release is a packaging and identity rebuild from the verified v2.5.3 Build 6 candidate. Existing project references and historical reconstruction evidence remain preserved for traceability.

## v2.9.1 Build 1 reference note

No new external web research was added for Version 2.9.1 Build 1. The build is based on the existing v2.9.0 release baseline and changes only first-run wizard wording, tests, audit evidence, documentation, and package identity.

## v2.9.1 Build 2 reference note

No new external web research was added for Version 2.9.1 Build 2. The build implements internal clean-code recommendations by centralizing duplicated disc-classification constants and helpers while preserving existing v2.9.1 runtime behavior and hardware-validation status.

## v2.9.1 Build 3 source/reference note

No new external web research was added for Build 3. The change was internal cleanup based on the user-provided clean-code recommendation to externalize the OPPO command map and preserve the protected 76-key invariant.


## v2.9.1 Build 4 — Dynamic audit evidence discovery

Version 2.9.1 Build 4 adds manifest-based release-evidence discovery to `tools/audit_release.py`. The audit now discovers `release-evidence/*/MANIFEST.txt`, requires each manifest file, and requires every safe root-relative evidence file listed in those manifests. The legacy hard-coded evidence list remains active as a transition fallback so historical checks remain stable while future builds can migrate to manifest-owned evidence.

No playback behavior, OPPO command-map behavior, service interception, XML routing, NAS playback, startup auto-power, or hardware-control behavior changed. Hardware validation is not claimed for this build.

## v2.9.1 Build 5 — Version single source of truth

Build 5 adds `resources/lib/version.py` as the Python source of truth for add-on release identity and `tools/sync_version.py` for checking or synchronizing `addon.xml`. The release audit now verifies that `addon.xml`, `version.py`, and `--expected-version` agree. Runtime playback/control behavior is unchanged, and hardware validation is not claimed.


## v2.9.1 Build 6 — Build/release automation scripts

No new external web references were used. Build 6 is an internal cleanup-roadmap step based on the user-provided recommendation to add build/release automation and the standing handoff rules for one-command-at-a-time verification, runtime-only ZIPs, and no hardware-validation claim without real device results.

## v2.9.1 Build 7 reference note

No new external web research was added for Build 7. The build implements the local cleanup-roadmap recommendation to replace runtime packaging denylist behavior with allowlist-based packaging. Runtime behavior and hardware-validation status are unchanged.

## v2.9.1 Build 8 reference note

No new web research was used for Build 8. The change implements the previously supplied clean-code recommendation to replace broad settings parser exception handling with narrower handlers where safe.


## v2.9.1 Build 9 reference note

No new web research was used for Build 9. The change implements the previously supplied clean-code recommendation to introduce lightweight typed settings validation while preserving Kodi runtime compatibility.

## v2.9.1 Build 10 reference note

No new web research was used for Build 10. The change implements the supplied clean-code recommendation to separate audit orchestration and reporting while preserving existing release-audit behavior.

## v2.9.1 Build 11 reference note

No new web research was used for Build 11. The change implements the supplied clean-code recommendation to replace diagnostic logging print fallback behavior with structured logging while preserving Kodi `xbmc.log` behavior and existing support-friendly prefixes.




## v2.9.10 Build 3 web/reference posture

Build 3 records a conservative software-validation posture: OPPO-like successors are not treated as command-compatible OPPO clones based on naming similarity alone. Real hardware validation is required before Reavon or Magnetar support can move beyond warning-only documentation.



## v2.9.10 Build 4 — Player wizard wording and readiness updates

Build 4 updates player-facing guidance for the v2.9.10 hardware taxonomy. The wizard and readiness report now explain stock OPPO behavior, Chinoppo-style clone behavior, experimental clone readiness gates, and warning-only OPPO-like successor behavior for Reavon and Magnetar. NAS/direct playback remains a readiness gate requiring AutoScript or equivalent local NAS mount support on the player.

No playback routing, OPPO command-map payloads, service interception, Option 4 XML routing, NAS adapter behavior, startup auto-power behavior, TV switching behavior, AVR sequencing, or hardware-control behavior changed. Hardware validation is not claimed.

## v2.9.1 Build 12 reference note

No new web research was used for Build 12. The change implements the supplied clean-code recommendation to reduce README/reference/web-references drift by adding a shared docs metadata source and a local renderer/checker while preserving the existing documentation content.


## v2.9.1 Build 13 reference note

No new web research was used for Build 13. The change implements the supplied clean-code recommendation to add type hints and a non-blocking mypy baseline while preserving all runtime behavior.

## v2.9.1 Build 14 reference note

No new web research was used for Build 14. The change implements the supplied clean-code recommendation to standardize test naming/layout policy while preserving inherited flat test discovery.

## v2.9.1 Build 15 reference note

No new web research was used for Build 15. The change implements the supplied cleanup-roadmap recommendation to introduce Babel/gettext extraction transition tooling while preserving the existing `tools/make_pot.py` fallback for one build.


## v2.9.1 Build 16 reference note

No new web research was used for Build 16. The change implements the supplied cleanup-roadmap follow-up to harden the Babel/gettext extraction transition by marking `tools/make_pot.py` as a legacy compatibility alias and keeping `tools/i18n_extract.py` as the preferred facade.


## v2.9.10 Build 1 — Unified hardware registry foundation

Build 1 starts the v2.9.10 Unified Hardware Ecosystem Expansion by adding a side-effect-free hardware registry foundation for player, TV, and AVR role families. The new registry is documentation/test-oriented in this build and does not change playback routing, OPPO command dispatch, service interception, Option 4 XML routing, NAS behavior, startup auto-power behavior, existing TV switching behavior, or AVR sequencing.

Hardware validation is not performed or claimed.


## Version 2.9.10 Build 2 — OPPO clone taxonomy and aliases

Build 2 expands the software taxonomy for OPPO-compatible player profiles without changing playback routing or OPPO command-map payloads. It adds M9200, M9205, CineUltra V203, CineUltra V204, and Magnetar UDP900 identifiers, plus M9702 V1/V2/V3 and related spelling aliases. Clone-family additions use the existing clone-safe wake classification, while Magnetar UDP900 is warning-only / unverified by default.

No real hardware validation is claimed for the new identifiers. The runtime ZIP remains allowlist-only and development evidence remains outside the installable package.

## v2.9.10 Build 5 — TV backend registry and preset foundation

Build 5 records the TV backend and preset foundation needed by the v2.9.10 roadmap. It preserves the existing ADB, Sony Bravia IP, LG command, Samsung command, and custom command backends, and keeps all new preset data software-only until real hardware validation is supplied.

Source-plan relationship: this implements the TV backend registry and preset foundation slice from the v2.9.10 Unified Hardware Ecosystem Expansion plan. It is not a Roku, SmartThings, Android TV preset-pack, or AVR sequencing build.
## v2.9.10 Build 6 — Android / Google TV preset pack

Version 2.9.10 Build 6: Android / Google TV preset pack.

Build 6 uses the existing v2.9.10 hardware ecosystem roadmap and the Build 5 TV backend registry as its source references. No new external web sources were needed for this software preset metadata slice.

| Requirement | Source | Build 6 result |
|---|---|---|
| Add Android / Google TV ADB presets | v2.9.10 Build 6 resume handoff | Added TCL, Sony, Hisense, Philips, Xiaomi, Sharp, Skyworth/Coocaa, Haier, and generic Android TV presets. |
| Keep commands editable | Build 6 protected scope | Presets reference the existing editable ADB command fields instead of applying commands automatically. |
| Avoid universal HDMI claims | Build 6 protected scope | No universal ADB HDMI command is claimed. Hardware validation is not claimed. |


## Version 2.9.10 Build 9B — SmartThings experimental request helper and fake API tests

No new web research was used for Build 9B. The change implements the local roadmap requirement to split the below-75% SmartThings backend into a safe 9A metadata/validation skeleton before any future live request helper.

| Build 9B requirement | Source | Implementation |
|---|---|---|
| SmartThings experimental only | v2.9.10 roadmap | Added metadata-only `smartthings` backend and presets. |
| Never expose tokens | v2.9.10 security rules | Added token redaction helpers and tests. |
| No live API calls in 9A | User build prompt | Live SmartThings calls remain disabled. |


## Version 2.9.10 Build 12 — Denon / Marantz AVR driver

Build 12 adds guarded Denon/Marantz Telnet-style AVR command support behind the disabled-by-default AVR framework from Build 11. The driver supports `PWON` for power on, `SI<input>` for input selection, and query helpers for `PW?` and `SI?` where supported. Each command opens and closes a socket, uses a short timeout, and returns a non-fatal `AvrResult` on timeout, network failure, invalid input, or unsupported action.

AVR control remains disabled by default, AVR power-off remains disabled by default, volume automation remains disabled by default, and AVR playback sequencing is not hooked in this build. Hardware validation is not claimed.


## Version 2.9.10 Build 13 — Yamaha MusicCast / YXC AVR driver

Build 13 adds guarded Yamaha MusicCast/YXC HTTP command support behind the disabled-by-default AVR framework. The driver uses HTTP GET helpers for `/YamahaExtendedControl/v1/main/setPower?power=on`, `/YamahaExtendedControl/v1/main/setInput?input=<input>`, and `/YamahaExtendedControl/v1/main/getStatus`, parses JSON `response_code`, and returns non-fatal `AvrResult` objects for non-zero response codes, invalid JSON, timeouts, and network failures.

AVR control remains disabled by default, AVR power-off remains disabled by default, volume automation remains disabled by default, and AVR playback sequencing is not hooked in this build. Denon / Marantz AVR driver behavior from Build 12 remains preserved. Hardware validation is not claimed.



## Version 2.9.10 Build 14 — Onkyo / Integra / Pioneer eISCP AVR driver

Build 14 adds guarded Onkyo / Integra / Pioneer eISCP command support behind the disabled-by-default AVR framework. The driver uses TCP port `60128`, eISCP frame magic `ISCP`, power-on payload `!1PWR01`, and input-select payloads `!1SLIxx`. It builds valid eISCP frames, opens and closes a socket per command, handles malformed response frames safely, returns non-fatal `AvrResult` objects for timeout/network/error/malformed-response paths, keeps Pioneer marked experimental/unverified, and does not hook AVR into playback sequencing.

AVR remains disabled by default. AVR power-off and volume automation remain disabled by default. Hardware validation is not claimed.


## Version 2.9.10 Build 15B — Sony AVR experimental request helper

Build 15B adds a Sony Audio Control API experimental request helper behind the disabled-by-default AVR framework. It adds Sony AVR preset metadata, explicit experimental acknowledgement gating, settings placeholders, validation helpers, sanitized diagnostics metadata, and regression tests. It uses guarded fakeable JSON POST helpers only after explicit acknowledgement, refuses Sony AVR execution unless experimental acknowledgement is enabled, never logs or exports Sony PSKs, passwords, credentials, tokens, or secrets, does not hook AVR into playback sequencing, and does not claim hardware validation.

Balanced Gate verification is used for this feature build. Full legacy pytest, full unittest discovery, and full post-unpack coverage remain deferred to Build 18 regression/audit packaging.


## Version 2.9.10 Build 16 — AVR wizard, diagnostics, and safety UI

Build 16 adds AVR setup UI helpers, query-only AVR test actions, explicit user-action gates for power/input tests, sanitized AVR diagnostic export, and safety wording. AVR support remains disabled by default, AVR power-off and volume automation remain disabled by default, no AVR playback sequencing hook is added, diagnostics sanitize credentials and state `hardware_validation_claimed=false`, and hardware validation is not claimed.

<!-- BEGIN GENERATED DOCS METADATA -->
### Generated documentation metadata — v2.9.13 Final

- Target document: `web-references.md`
- Cleanup scope: Testing strategy refresh and faster parallel test tooling
- Runtime behavior changed: `false`
- Hardware validation claimed: `false`
- Source recommendation: v2.9.13 testing strategy and developer-experience roadmap
- Managed documents: `README.md`, `reference.md`, `web-references.md`

Protected behavior preserved:
- 4K/UHD/2160p disc-style interception only
- loose/raw video files stay with Kodi
- Option 4 conservative playercorefactory.xml behavior
- canonical 76-key OPPO command map
- no forbidden OPPO command tokens #SIS #PGU #PGD
- Reavon warning-only behavior
- Chinoppo/M9702 wake rewrite behavior
- stock OPPO pass-through behavior
- Kodi startup auto-power guard behavior
- NAS adapter behavior
- runtime-only installable ZIP policy
<!-- END GENERATED DOCS METADATA -->

## v2.9.10 Build 8 — Roku TV ECP backend

Version 2.9.10 Build 8: Roku TV ECP backend.

Build 7 uses the existing v2.9.10 hardware ecosystem roadmap and the Build 6 source baseline. No new external web references were used for this software implementation slice.

| Requirement | Source | Build 7 result |
|---|---|---|
| Add Roku TV ECP backend | v2.9.10 Build 8 resume prompt | Added `roku_ecp` backend with local HTTP POST to `/keypress/<key>`. |
| Use default port 8060 | Build 7 protected scope | Added `roku_ecp_port` default `8060`. |
| Prevent URL path injection | Build 7 protected scope | Added strict allowlisted Roku ECP keys before URL construction. |
| Keep failures non-fatal | Existing TV switching design | Roku ECP errors flow through the existing non-fatal TV switching wrapper. Hardware validation is not claimed. |

Build 7 implementation note: Roku TV ECP uses HTTP POST to /keypress/<key> with allowlisted input keys.

## Version 2.9.10 Build 8 — Command TV preset polish

Build 8 records command/custom TV preset support without relying on additional web or hardware validation. All command presets remain software-only until real user-owned testing provides device evidence.


## Version 2.9.10 Build 10 — TV diagnostics and dry-run validator

No new web research was used for Build 10. The change implements the local roadmap requirement for TV diagnostics and dry-run validation while preserving the protected OPPO playback path.

## Version 2.9.10 Build 11 — AVR framework and settings skeleton

Build 11 records AVR framework support as software metadata only. Denon/Marantz, Yamaha MusicCast/YXC, Onkyo/Integra eISCP, Pioneer eISCP-compatible, and Sony Audio Control API entries are future-driver placeholders with hardware validation unclaimed. The build intentionally avoids live AVR commands and avoids playback sequencing hooks.


## Version 2.9.10 Build 17 — Unified TV + AVR playback sequencing

Build 17 safely hooks optional TV and AVR pre/post sequencing into the external-player flow. AVR sequencing runs only for eligible OPPO/external-player handoff, the AVR disabled path is a no-op, TV and AVR failures remain non-fatal, optional AVR restore runs only when enabled, and existing TV restore continues to work. Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, runtime ZIP policy, the 99% coverage gate, and the no-hardware-validation-claim posture remain preserved.

### Generated documentation metadata — v2.9.10 Build 17

The generated docs metadata block above records Build 17 as the active v2.9.10 software build. Build 17 uses the shortened Balanced Gate verification strategy and defers full legacy pytest, full unittest discovery, and full post-unpack coverage to Build 18 Full Release Gate.

## Version 2.9.10 Build 18 — Regression, audit, and packaging candidate

Build 18 packages the v2.9.10 regression/audit candidate after the Build 17 unified TV + AVR sequencing slice. It keeps OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, TV restore, AVR nonfatal sequencing, runtime ZIP policy, and no-hardware-validation-claim posture intact.

## Version 2.9.10 Final — Software-verified release packaging

Final v2.9.10 is the software-verified release packaging step after Build 18. It preserves OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, TV/AVR sequencing, startup auto-power behavior, and the runtime ZIP policy.

No real hardware validation is claimed unless separate tester evidence is supplied.
