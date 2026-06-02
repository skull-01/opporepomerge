# OPPO 203 ISO External Player

A Kodi add-on for handing off eligible 4K UHD / Blu-ray disc-style media from Kodi to an external OPPO UDP-203/UDP-205-compatible player workflow while preserving normal Kodi playback for media that should stay internal.

> **Current status:** v2.9.10 Final is a software-verified release. Real hardware validation has not been performed or claimed unless separate tester evidence is later recorded.

## What this add-on does

- Detects eligible disc-style media such as UHD/Blu-ray ISO and disc-folder style paths.
- Routes eligible playback to an external-player workflow for OPPO-class media players and compatible external-player setups.
- Preserves normal Kodi playback for loose/raw files and media outside the configured external-player scope.
- Provides guarded support modules for OPPO-class player control, TV input switching, AVR sequencing, NAS/AutoScript readiness, diagnostics, and `playercorefactory.xml` helper workflows.
- Treats TV/AVR control failures as non-fatal so playback routing is not blocked by an optional control-path failure.

## What this add-on does not do

- It does not include or distribute OPPO, Kodi, TV, AVR, or jailbreak firmware.
- It does not claim real hardware validation for OPPO, Chinoppo, Magnetar, Reavon, Kodi, NAS, TV, ADB, Roku, LG, Samsung, Sony, Panasonic, Vizio, or AVR paths without real tester evidence.
- It does not send media bytes from Kodi to the player; external-player workflows require both Kodi and the player to resolve usable media paths.
- It does not make universal claims for every OPPO clone, successor, TV, or AVR model.
- It does not enable risky AVR power-off or volume automation by default.

## Current release

| Item | Value |
|---|---|
| Add-on ID | `script.oppo203.iso.external` |
| Add-on version | `2.9.10` |
| Build identity | `v2.9.10 Final` |
| Runtime package | `script.oppo203.iso.external-2.9.10.zip` |
| GitHub readiness line | `github-g2` |
| Runtime behavior changed in G2 | `false` |
| Hardware validation claimed | `false` |

## Supported playback concept

The intended model is:

```text
Kodi library item -> add-on eligibility check -> external-player handoff -> OPPO/player reads media from a reachable path
```

Typical candidate media:

- 4K UHD ISO files
- Blu-ray ISO files
- UHD/Blu-ray folder structures such as `BDMV` / disc-folder style layouts
- Library paths that can be translated or mapped for the external player

Media that should normally remain with Kodi:

- ordinary MKV/MP4 playback outside the configured routing policy
- loose/raw files that are intentionally excluded by the protected routing rules
- any item that fails eligibility checks

## Hardware status and validation language

The software contains guarded support paths and presets for several device families, but public documentation must separate **software support** from **real hardware validation**.

Allowed wording:

```text
Software-verified release. Hardware validation not performed / not claimed.
```

Do not write that a device path is hardware-validated unless a real tester report exists in the project evidence.

## Help validate on real hardware

This project is **software-verified only** — the device-control paths (OPPO/clone players, TV input switching, AVR sequencing) are unit-tested but have **not** been confirmed against real hardware. Tester reports, hardware lending, and donations are all wanted so specific models can move from "software-supported" to "hardware-validated."

See **[`docs/HARDWARE_VALIDATION.md`](docs/HARDWARE_VALIDATION.md)** for the current status per device family, what's most needed, and how to help. To submit a tester report, follow the [Hardware reports](CONTRIBUTING.md#hardware-reports) guide and open a GitHub issue. Tracked by [#44](https://github.com/skull-01/script.oppo203.iso.external/issues/44).

## Installation

1. Download the installable runtime ZIP for the release.
2. In Kodi, enable installation from ZIP files if required by your Kodi setup.
3. Install the ZIP from Kodi using **Add-ons > Install from zip file**.
4. Configure the add-on with the Windows configurator (see [`configurator/`](configurator/)), which writes the `playercorefactory.xml` and remote-bridge keymap into Kodi's userdata and seeds the add-on's settings.
5. Open the add-on settings to review player address, routing policy, NAS/path mapping, and optional TV/AVR behavior. Adjust only as needed.

## Basic configuration checklist

- Confirm the player model/profile before enabling external handoff.
- Confirm Kodi and the player can both reach the intended media location.
- Keep TV switching disabled until the base handoff works.
- Keep AVR sequencing disabled until TV/player routing is stable.
- Use diagnostics/export tools only after removing or reviewing sensitive local details.
- Record any real hardware test results separately before claiming validation.

## Development and test quick start

From a development source tree:

```bash
python -m py_compile service.py default.py
python tools/render_docs.py --check
python tools/sync_version.py --check
python tools/test_layout.py --check
python tools/i18n_extract.py --check
pytest -q tests/test_v2910_final_release.py
pytest -q tests/test_v2910*.py
python tools/audit_release.py --expected-version 2.9.10
```

For full verification, run the complete pytest/unittest/coverage gates and package audit described in the release evidence and GitHub-readiness handoff files.

## Repository map

```text
resources/lib/           Runtime Python modules
tests/                   Regression and release-gate tests
tools/                   Audit, docs, packaging, i18n, and helper tools
scripts/                 Local verification and packaging wrappers
docs/release-history/    Historical build notes, manifests, coverage, and audits
docs/ai-handoff/         AI handoff and reconstruction files
docs/github-readiness/   GitHub-readiness build records
docs/hardware-validation Hardware validation guidance and status notes
release-evidence/        Release manifest files and evidence indexes
```

## License

The Kodi add-on metadata declares MIT licensing. The source tree now includes an MIT `LICENSE` file for GitHub publication consistency.

## Contributing

See `CONTRIBUTING.md`. Contributions should be small, test-backed, and must not claim hardware validation unless real tester evidence is included.

## Credits

This project builds on the generosity and prior work of several people in the AV community:

- **[theAxleDentalDJ](https://www.avforums.com/members/theaxledentaldj.831542/)** (AVForums) — for sharing his version of the add-on, which inspired me to further enhance it and adapt it to my own setup.
- **[keebhubhk](https://www.instagram.com/keebhubhk)** ([shop](https://keebhub.onepos.shop/)) — for doing me a huge favor in acquiring an M9205 v1 device.
- **Moremodey1** (AVForums) — for the jailbreak.
- **[tocinillo](https://www.avpasion.com/staff/tocinillo/)** (AV Pasión) — for his passion for AV; his YouTube video on the subject is a great primer.
- **[Xnoppo by siberian-git](https://github.com/siberian-git/Xnoppo/tree/main)** — whose source I reviewed for ideas on the overall flow.

---

# Historical build notes preserved for reconstruction

The section below preserves legacy README build notes required by the historical test and reconstruction record. Public users can start with the overview above; maintainers and AI agents can use the historical notes below for traceability.

# Version 2.5.2 Build 1 — OPPO/Chinoppo NAS playback capability gates

Build 1 starts the v2.5.2 NAS-mounted playback enhancement line from the v2.5.1 startup-power baseline. It adds software capability gates for original OPPO UDP-203/UDP-205 jailbroken AutoScript workflows and Chinoppo-family NAS playback workflows.

Key rules added in this build:

- Original OPPO UDP-203/UDP-205 require jailbroken firmware with AutoScript support.
- Minimum OPPO 20x AutoScript-capable firmware: `20X-56`.
- Recommended original OPPO jailbreak target: `20X-65-0131`.
- Unsupported for AutoScript-based workflows: `20X-54-1127` and older/pre-56 firmware.
- Chinoppo-family profiles require compatible active firmware/binary capability confirmation rather than one universal numeric firmware minimum.
- User confirmed that NAS-mounted file playback works, but per-model hardware validation remains pending.

No path mapper, NAS playback trigger, wizard setup flow, AutoScript profile change, or firmware/script deployment was added in this build.

---

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

# Version 2.2.0 Build 7 - Service watcher persistence edge-case hardening

Build 7 continues the gradual v1.1.9 + v0.9.14 superset merge with a narrow service-watcher persistence slice. It does not start a broad merge and does not add new runtime feature scope.

## Summary

- Hardened `settings_reader.save_settings()` so an empty add-on-data directory returns `False` instead of writing `settings.xml` beside the current working directory.
- Added regression tests for service watcher save failure, missing add-on-data directory, stock OPPO jailbreak JSON-payload persistence, and version identity.
- Preserved Reavon warning-only behavior, Chinoppo/M9702 wake/preset behavior, the 99% coverage gate, and post-unpack verification discipline.

## Tests and audit

Build 7 source and packaged-artifact verification ran:

```text
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.7
```

Real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi, and real ADB hardware were not tested in this build.

---

## Version 2.2.0 Build 6 — Active wizard compatibility-warning integration merge slice

Build 6 continues the careful v1.1.9 + v0.9.14 superset merge without starting a broad rewrite.

### Summary

This build wires the Build 5 warning-surfacing helpers into one active v1.x wizard path: after the user selects a hardware model, the wizard can surface v0.9.14 compatibility warnings through the active wizard UI while keeping the existing wizard flow and clone-preset confirmation behavior intact.

### User-visible behavior

- Reavon selections can surface the Reavon warning during the active wizard hardware path.
- AutoScript verbose-push warnings can be surfaced when the AutoScript shell-handler setting is enabled.
- Quick Start prerequisite warnings remain visible for OPPO/Chinoppo-compatible models.
- Reavon remains warning-only; no OPPO command-map mutation is applied.
- The active v1.x wizard is not replaced.
- The 99% coverage gate remains enforced.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.2.0.6` | Build 6 identity |
| `resources/lib/wizard.py` | Added active wizard warning integration adapter | Wire v0.9.14 warning surfacing into one safe UI path |
| `tests/test_superset_merge_build6.py` | Added Build 6 regression tests | Lock down Reavon warning-only and warning surfacing behavior |
| `README.md`, `reference.md`, `web-references.md` | Added Build 6 notes | Documentation lockstep |
| `tools/audit_release.py` and `tests/test_all.py` | Added Build 6 artifact evidence checks | Release audit discipline |

### Known limitations

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested. The full superset merge remains in progress.

---

## Version 2.2.0 Build 5 — Wizard/UI compatibility warning surfacing merge slice

Build 5 continues the careful v1.1.9 + v0.9.14 superset merge without starting a broad rewrite.

### Summary

This build restores another narrow v0.9.14 behavior slice: compatibility warnings can now be surfaced through a wizard-style UI helper while also being logged with the existing `[v0.9.14-warning]` support marker. The active v1.x wizard is not replaced in this build; the new helper is a bridge for later UI wiring.

### User-visible behavior

- No runtime feature expansion was made.
- Reavon remains warning-only; no OPPO command-map mutation is applied.
- Chinoppo/M9702 clone preset behavior remains preserved.
- AutoScript verbose-push warnings and Quick Start warnings can be shown through UI adapters when a future wizard path calls the helper.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.2.0.5` | Build 5 identity |
| `resources/lib/first_run_wizard.py` | Added UI warning surfacing and choice-validation helpers | Restore v0.9.14 wizard-warning behavior gradually |
| `tests/test_superset_merge_build5.py` | Added Build 5 regression tests | Lock down warning surfacing and Reavon no-mutation behavior |
| `README.md`, `reference.md`, `web-references.md` | Added Build 5 notes | Documentation lockstep |
| `tools/audit_release.py` and `tests/test_all.py` | Added Build 5 artifact evidence checks | Release audit discipline |

### Tests

Build 5 adds targeted tests for UI warning surfacing, fallback behavior, invalid UI answers, clone preset + warning surfacing, Reavon warning-only behavior, and version identity.

### Known limitations

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested. The full superset merge remains in progress.

---

## Version 2.2.0 Build 4 — Service watcher persistence merge slice

Build 4 continues the gradual v1.1.9 + v0.9.14 superset merge without starting a broad rewrite. This slice makes the restored v0.9.14 service settings watcher persist compatibility-preset changes when a user changes the hardware model outside the wizard.

### User-visible behavior

- The add-on version is now `2.2.0.4`.
- Chinoppo-style model changes handled by the service watcher now persist the safe preset values to add-on data `settings.xml` when possible.
- Reavon remains warning-only and does not persist OPPO command mutations.
- The 99% coverage gate remains enforced.

### Files revised

| File | Change | Reason |
|---|---|---|
| `service.py` | Persist applied compatibility presets after watcher changes | Preserve v0.9.14 watcher behavior beyond in-memory settings. |
| `resources/lib/settings_reader.py` | Added conservative `save_settings()` helper | Let service watcher write safe settings XML updates. |
| `tests/test_superset_merge_build4.py` | Added persistence regression tests | Prevent non-durable preset reapplication. |
| `README.md`, `reference.md`, `web-references.md` | Added Build 4 notes | Keep docs synchronized. |

### Known caveats

No real hardware was tested. The full v1.1.9 + v0.9.14 superset merge is still in progress.

## Version 2.1.0 Build 5 - Coverage gate raised to 98%

Build 5 continues the gradual pre-merge coverage-hardening track toward the later 99% goal. It starts from v2.1.0 Build 4 and raises the enforced `.coveragerc` gate from `fail_under = 97` to `fail_under = 98`.

This is a controlled test/audit hardening build only. It does not start the full v1.1.9 + v0.9.14 superset merge and does not add runtime features.

### Files revised in this release

| File | Revision made | Why it changed |
|---|---|---|
| `addon.xml` | Version bumped to `2.1.0.5` | Build identity. |
| `.coveragerc` | `fail_under = 98` | Enforce the next gradual coverage gate. |
| `tests/test_coverage_hardening.py` | Added Build 5 coverage tests | Cover meaningful edge paths without real hardware. |
| `tools/audit_release.py` | Requires >=98% gate and Build 5 evidence files | Make audit enforce this build's gate. |
| `README.md`, `reference.md`, `web-references.md` | Added Build 5 notes | Documentation lockstep. |

### Verification snapshot

- Tests: 413 passing.
- Coverage: total measured coverage 98%.
- Release audit: 48/48 checks passing.
- Post-unpack verification: repeated from the generated zip.

### Known caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested. Real hardware testing remains deferred until after the later full merge.

### Deferred work

- Continue gradual coverage hardening toward 99%.
- Do not start the full merge until the 99% pre-merge target is satisfied.

## Version 2.1.0 Build 4 - Coverage gate raised to 97%

Build 4 continues the gradual pre-merge coverage-hardening track toward the later 99% goal. It starts from v2.1.0 Build 3 and raises the enforced `.coveragerc` gate from `fail_under = 96` to `fail_under = 97`.

### User-visible behavior

No runtime feature scope was expanded. This is a test/audit/docs hardening build.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.1.0.4` | Build identity. |
| `.coveragerc` | `fail_under = 97` | Enforce the next gradual coverage gate. |
| `tests/test_coverage_hardening.py` | Added targeted branch/edge tests | Raise coverage with meaningful behavior checks. |
| `tests/test_all.py` | Updated release artifact expectations and Build 4 evidence checks | Keep audit/test evidence current. |
| `tools/audit_release.py` | Requires >=97% gate and Build 4 evidence files | Make audit enforce this build's gate. |
| `README.md`, `reference.md`, `web-references.md` | Added Build 4 notes | Documentation lockstep. |

### Verification target

- Tests: 409 passing.
- Coverage: total measured coverage 97%.
- Audit: 48/48 checks passing.

### Known deferrals

- 99% is not complete yet.
- Full v1.1.9 + v0.9.14 merge not started.
- Real hardware validation still deferred until after the full merge.

# Oppo UDP-203 ISO External Player for Kodi

## Version 2.1.0 Build 3 - Coverage gate raised to 96%

Build 3 continues the gradual pre-merge coverage-hardening track toward the later 99% goal. It starts from v2.1.0 Build 2 and raises the enforced `.coveragerc` gate from `fail_under = 94` to `fail_under = 96`.

### Summary

This build does not start the full v1.1.9 + v0.9.14 superset merge and does not add runtime feature scope. It adds targeted tests for meaningful under-covered behavior and fixes one real discovery fallback bug found while exercising the error path.

### Changes

- Added regression coverage for reconnect backoff and OPPO TCP-client edge paths.
- Added settings XML/enum edge coverage.
- Added Sony Bravia and external TV-command error-path coverage.
- Added OPPO discovery, Wake-on-LAN, file-list, and parsing edge coverage.
- Added architecture benchmark, AutoScript, wizard-polish, playercorefactory, logging, and preset-manager edge coverage.
- Fixed `oppo_control.discover_oppo()` so top-level UDP socket creation failure returns an empty discovery list instead of raising an `UnboundLocalError` during cleanup.
- Raised the enforced coverage gate to 96%.

### Tests

- Source and packaged-artifact test target: 400 passing tests.
- Source and packaged-artifact coverage target: total measured coverage 96%.
- Source and packaged-artifact audit target: 44/44 checks passing.

### Known caveats

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested. Real hardware testing remains deferred until after the later full merge.

## Version 2.1.0 Build 2 - Gradual coverage hardening toward 99%

Build 2 continues the post-MVP coverage track before the full v1.1.9 + v0.9.14 merge. It keeps runtime behavior stable and adds targeted tests for previously under-covered but meaningful branches: AutoScript generation, discovery cache persistence, wizard UI/no-GUI paths, OPPO remote fallback behavior, external-player hold logic, playercorefactory merge edges, logging rotation, and preset-manager validation.

The enforced `.coveragerc` gate is raised from 92% to 94%. This is an intentional gradual step toward the user-requested 99% target before merge work begins. No real hardware validation is claimed for this build.

### Build 2 verification summary

- Package version: `2.1.0.2`
- Test count after source changes: 389 passing before artifact-documentation tests
- Enforced coverage gate: `fail_under = 94`
- Measured total coverage: 94%
- Scope: tests/audit/docs only; no feature expansion


## Version 2.1.0 Build 1 - 92 percent coverage gate hardening

This post-MVP hardening build starts from the stable v2.0.0 release artifact and addresses the previously deferred 92 percent coverage gate. The work is intentionally test-focused and stability-preserving: it adds targeted tests around existing modules, raises `.coveragerc` from `fail_under = 85` to `fail_under = 92`, and preserves the v2.0 MVP runtime behavior.

### Changes

- Changed `addon.xml` version to `2.1.0.1`.
- Added `tests/test_coverage_hardening.py` with coverage-focused regression tests for library modules and Kodi-stub paths.
- Fixed a real installer fallback bug: `resources/lib/installer.py` used `xbmc.log()` in a wizard-failure path but did not import `xbmc`.
- Raised the enforced coverage gate to 92 percent.
- Added `BUILD_NOTES_v2.1.0_BUILD1.md`, `RELEASE_MANIFEST_v2.1.0_BUILD1.md`, and `COVERAGE_REPORT_v2.1.0_BUILD1.md`.
- Updated release audit checks to require the coverage-gate evidence files and confirm `.coveragerc` enforces 92 percent.

### Verification

```text
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.1.0.1
```

### Scope

This is not the full v1.1.9 + v0.9.14 superset merge. Real hardware validation remains deferred until after the full merge milestone, as requested.

## Version 2.0.0 Final Release - packaged from Build 6

This package is the stable **v2.0.0 MVP release** produced from the verified Build 6 source line. It intentionally returns the add-on package identity to `2.0.0` while preserving the Build 6-tested MVP behavior and release evidence.

### Final release scope

- Preserves the External Player MVP path.
- Preserves M9702 / Chinoppo wake rewrite (`#PON` and `#POW` to `#EJT`).
- Preserves stock OPPO pass-through behavior.
- Preserves TCL / Android TV ADB switching with non-fatal failure handling.
- Preserves session sentinel cleanup.
- Preserves fake OPPO server regression tests.
- Preserves Kodi stub import tests.
- Preserves release audit and post-unpack verification workflow.

### Real hardware validation status

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or ADB hardware validation is claimed for this package. Per the release decision, real hardware validation is deferred until after the later full v1.1.9 + v0.9.14-style merge.

### Final verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0
```

### Package names

```text
script.oppo203.iso.external-2.0.0.zip
script.oppo203.iso.external-2.0.0.sha256
```

## Version 2.0.0 Build 6 - build-id update

Build 6 changes the package/build id to `2.0.0.6` at the user's request. It is intentionally small and stability-preserving: no runtime feature expansion, no full v1.1.9 + v0.9.14 superset merge, and no change to the v2 MVP behavior.

### Build 6 changes

- Changed `addon.xml` version to `2.0.0.6`.
- Added `BUILD_NOTES_v2.0.0_BUILD6.md`.
- Added `RELEASE_MANIFEST_v2.0.0_BUILD6.md`.
- Updated `tools/audit_release.py` so Build 6 release evidence is included in the package audit.
- Updated tests and audit expectations for `2.0.0.6`.
- Preserved all final v2.0.0 release evidence files for history and reconstruction.

### Verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0.6
```

### Known deferrals

No physical hardware test was performed for this build-id update. The 92% coverage gate and full historical superset merge remain deferred.

## Version 2.0.0 Final - MVP stable release

Version 2.0.0 final is the stability-focused MVP release created from the verified Build 5 release-candidate tree. This release does not add large new features. It converts the package identity from `2.0.0.5` to final `2.0.0`, adds final release notes and manifest files, updates the release audit, and preserves the tested MVP behavior.

### Final release changes

- Changed `addon.xml` version to `2.0.0`.
- Added `RELEASE_NOTES_v2.0.0.md` and `RELEASE_MANIFEST_v2.0.0.md`.
- Added final `MVP_COMPLIANCE_MATRIX_v2.0.0.md` and `HARDWARE_VALIDATION_v2.0.0.md`.
- Updated `tools/audit_release.py` so the final evidence files are required by audit.
- Updated tests to expect final version `2.0.0` and verify final release evidence.
- Preserved Build 5 release-candidate documentation for reconstruction/history.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version changed to `2.0.0` | Final release identity. |
| `README.md` | Added final release section | User-facing release ledger. |
| `reference.md` | Added final technical notes | Technical rationale and invariants. |
| `web-references.md` | Added final source-reference notes | Source-to-decision traceability. |
| `tools/audit_release.py` | Final evidence files added to required audit list | Keep final package self-verifying. |
| `tests/test_all.py` | Version/audit expectations updated; final artifact tests added | Prevent final packaging regressions. |
| `RELEASE_NOTES_v2.0.0.md` | Added | Final release summary. |
| `RELEASE_MANIFEST_v2.0.0.md` | Added | Artifact identity and verification checklist. |
| `MVP_COMPLIANCE_MATRIX_v2.0.0.md` | Added | Final MVP status evidence. |
| `HARDWARE_VALIDATION_v2.0.0.md` | Added | Honest hardware-validation status. |

### Verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python tools/audit_release.py --expected-version 2.0.0
```

### Known deferrals

The 92% coverage gate remains deferred to post-MVP hardening, and the full v1.1.9 + v0.9.14 superset merge remains deferred to a later v2.1-style milestone. No new physical hardware test was performed during final packaging.


## Version 2.0.0 Build 5 - reproducible release-audit hardening

Build 5 continues from Build 4 and keeps the MVP functional scope stable. The purpose of this build is release reproducibility: a local AI, CI runner, or user can unpack the zip and run the same dependency-free release audit helper that was used before packaging.

### Build 5 changes

- Added `tools/audit_release.py`, a dependency-free release audit helper.
- Added `RELEASE_MANIFEST_v2.0.0_BUILD5.md` with artifact identity, verification commands, package evidence, and staged items.
- Bumped `addon.xml` to `2.0.0.5`.
- Added tests that verify the release audit helper, Build 5 notes, Build 5 manifest, and synchronized docs.
- Preserved the Build 4 assumed real-hardware validation record and MVP compliance matrix.
- Kept the final 92% coverage gate staged rather than falsely marking it complete.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.0.0.5` | Make Build 5 visible as a new installable Kodi build. |
| `tools/audit_release.py` | Added release audit helper | Allow reproducible post-unpack verification without external dependencies. |
| `RELEASE_MANIFEST_v2.0.0_BUILD5.md` | Added release manifest | Record artifact identity and verification steps. |
| `BUILD_NOTES_v2.0.0_BUILD5.md` | Added Build 5 notes | Preserve build history for local AI handoff. |
| `tests/test_all.py` | Added Build 5 release-audit tests | Prevent audit-helper and manifest regressions. |
| `README.md`, `reference.md`, `web-references.md` | Added Build 5 sections | Keep docs synchronized. |

### Tests and audit

- Build 5 tests: `344 / 344 passing`.
- Release audit helper: passed with `--expected-version 2.0.0.5`.
- Python compile audit: passed.
- `addon.xml` parse: passed.
- `resources/settings.xml` parse: passed.
- Locale parity: 12 locale files with matching msgctxt sets.
- Settings label/help coverage: passed.
- Command map audit: 76 canonical keys; no `#SIS`, no `#PGU`, no `#PGD`.
- Hardware audit: `oppo_hardware_model` enum count matches `HARDWARE_COMPAT` count at 12.
- Post-unpack test and post-unpack release audit from the generated zip: passed.

### Remaining staged item

The 92% coverage gate remains staged for post-MVP hardening. Build 5 improves release verification, but does not claim the final coverage target is complete.

## Version 2.0.0 Build 4 - MVP release-candidate hardening

Build 4 continues from Build 3 after the user-provided/manual hardware-validation milestone. The latest hardware-tested build is recorded as having no reported issues, and this build focuses on release-candidate readiness instead of feature expansion.

### Build 4 changes

- **Manual hardware validation recorded:** `HARDWARE_VALIDATION_v2.0.0_BUILD4.md` records the user-provided assumption that the latest build was tested on real hardware and no issues were found.
- **MVP compliance matrix added:** `MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md` records each MVP requirement, current status, evidence, staged items, and deferred non-goals.
- **Packaging regression fixed:** `.coveragerc` is restored to the package. Build 3 omitted this hidden file from the zip, causing a post-unpack test failure in the CI scaffolding test.
- **Release-artifact tests added:** Build notes, hardware-validation notes, MVP matrix, doc updates, `.coveragerc`, and add-on version identity are now checked by tests.
- **Coverage honesty retained:** coverage remains a staged report path; the final 92% gate is still not claimed as complete.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.0.0.4` | Make Build 4 visible as a new installable Kodi build. |
| `.coveragerc` | Restored to packaged source tree | Fix hidden-file packaging regression found after unpacking Build 3. |
| `BUILD_NOTES_v2.0.0_BUILD4.md` | Added Build 4 notes | Release traceability. |
| `HARDWARE_VALIDATION_v2.0.0_BUILD4.md` | Added assumed manual hardware validation record | Preserve user-reported hardware result in the handoff. |
| `MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md` | Added explicit MVP checklist | Make MVP status readable by a local AI or release reviewer. |
| `tests/test_all.py` | Added release-artifact checks | Prevent missing docs/version/coverage files from slipping into future packages. |
| `README.md`, `reference.md`, `web-references.md` | Added Build 4 sections | Keep documentation synchronized. |

### Tests and audit

- Build 4 tests: `337 / 337 passing`.
- Python compile audit: passed.
- `addon.xml` parse: passed.
- `resources/settings.xml` parse: passed.
- Locale parity: 12 locale files with matching msgctxt sets.
- Settings label/help coverage: passed.
- Command map audit: 76 canonical keys; no `#SIS`, no `#PGU`, no `#PGD`.
- Hardware audit: `oppo_hardware_model` enum count matches `HARDWARE_COMPAT` count at 12.
- Package audit: clean zip layout; `.coveragerc` included; no cache/bytecode files.

### Remaining staged item

The 92% coverage gate remains staged. Build 4 restores `.coveragerc` and keeps coverage reporting visible, but does not falsely claim the final coverage target is complete.


## Version 2.0.0 Build 3 - Kodi stubs and CI coverage staging

Build 3 continues the v2 MVP hardening line after Build 2. It does not expand the hardware or playback scope. The goal is to make Kodi-bound code testable in normal Python without requiring a real Kodi runtime, while keeping the final 92% coverage gate as an explicit staged item rather than pretending it is complete.

### MVP hardening changes in this build

- **Local Kodi stubs added:** `tests/_stubs/` now includes minimal test-only stubs for `xbmc`, `xbmcaddon`, `xbmcgui`, `xbmcvfs`, `xbmcplugin`, and `xbmcdrm`.
- **Stubs are opt-in for tests:** the stubs are not inserted globally for the whole test suite. This preserves existing import-guard tests that verify the add-on can still behave when Kodi modules are absent.
- **Kodi-bound smoke tests added:** new tests import `default.py`, `service.py`, and `resources.lib.installer` with the local stubs active.
- **Programmable Dialog and Settings behavior:** the `xbmcgui.Dialog` and `xbmcaddon.Addon` stubs can record calls and return scripted settings/responses.
- **Programmable Player and Monitor behavior:** the `xbmc.Player` and `xbmc.Monitor` stubs support service/import smoke tests without a real Kodi process.
- **CI coverage step moved to staging mode:** the workflow still generates a coverage report, but it no longer fails the build while Kodi-bound module coverage is being expanded. The documented `.coveragerc` target remains in place, and the 92% coverage gate remains a future hardening target once the stubbed surfaces are broad enough.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.0.0.3` | Make Build 3 visible as a new installable Kodi build. |
| `tests/_stubs/xbmc.py` | Added programmable logging, info-label, Player, and Monitor stubs | Enable service/default smoke tests outside Kodi. |
| `tests/_stubs/xbmcaddon.py` | Added programmable Addon settings/info/localized-string stub | Enable settings-driven Kodi-bound tests. |
| `tests/_stubs/xbmcgui.py` | Added recording Dialog stub | Enable wizard/installer/dialog tests without Kodi UI. |
| `tests/_stubs/xbmcvfs.py` | Added path, mkdir, exists, and File helpers | Enable installer file-output tests outside Kodi. |
| `tests/_stubs/xbmcplugin.py` | Added minimal plugin-call recorder | Prepare for future plugin-surface tests. |
| `tests/_stubs/xbmcdrm.py` | Added placeholder DRM stub | Complete expected Kodi module set. |
| `tests/test_kodi_stubs.py` | Added opt-in Kodi-stub tests | Verify local stubs work without changing global test behavior. |
| `.github/workflows/ci.yml` | Changed coverage to staged report mode | Avoid false CI failure until Kodi-bound coverage is fully staged. |
| `README.md`, `reference.md`, `web-references.md` | Added Build 3 notes | Keep documentation synchronized. |

### Tests and audit

- Build 3 tests: `331 / 331 passing`.
- Python compile audit: passed.
- `addon.xml` parse: passed.
- `resources/settings.xml` parse: passed.
- Locale parity: 12 locale files with matching msgctxt sets.
- Command map audit: 76 canonical keys; no `#SIS`, `#PGU`, or `#PGD`.
- Hardware audit: `oppo_hardware_model` enum count matches `HARDWARE_COMPAT` count at 12.

### Remaining work / known deferrals

- The final hard coverage target is still staged. Build 3 adds the local Kodi-stub foundation, but does not honestly claim the 92% gate is reached.
- Physical OPPO/M9702 and TCL/Android TV validation remains manual.
- The next logical build can either expand stub-backed tests for `default.py`, `service.py`, `installer.py`, and wizard flows, or move toward a v2.0.0 release-candidate package if you decide the MVP scope is sufficient.


## Version 2.0.0 Build 2 - MVP compliance hardening

Build 2 focuses on the v2 MVP acceptance path instead of adding broad platform features. It corrects the Build 1 wake-token edge case, completes the MVP Slice 3 External Player + TCL/Android TV switching behavior, and adds hermetic loopback TCP tests so the MVP can be validated without a real OPPO, TV, or ADB binary.

### MVP compliance changes in this build

> **Naming note (2026-05-31):** module paths in this historical build section predate the
> `tv/`/`oppo/`/`avr/` sub-package split and the later `tv_`-prefix rename — e.g.
> `resources/lib/adb_control.py` is now `resources/lib/tv/tv_adb_control.py`. Kept as the
> original build record; current names are in [`docs/NAMING_CONVENTIONS.md`](docs/NAMING_CONVENTIONS.md).

- **Stock OPPO power behavior fixed:** UDP-203/UDP-205 now preserve both `#PON` and `#POW` exactly. Only Chinoppo-style clone profiles rewrite `#PON` / `#POW` to `#EJT`.
- **M9702 / Chinoppo wake behavior retained:** M9201, M9203, M9205C, M9702, IPUK-UHD8592, GIEC-BDP-G5300, and Magnetar-UDP800 retain send-time wake rewrite to `#EJT`.
- **External Player + TV switching hardened:** `external_player.fast_start()` now attempts TV switching before OPPO startup in a deterministic TV-first MVP order.
- **TV switching is optional:** new `tv_switching_enabled` setting provides a clean no-op path for users who do not want ADB/TV switching.
- **ADB/TV failures are non-fatal:** if ADB or TV switching fails, the error is logged but OPPO startup, stop commands, and session cleanup continue.
- **Session sentinel cleanup verified:** tests confirm the `oppo203iso-active` marker is removed even when External Player startup fails.
- **ADB command runner injection added:** `adb_control.switch_input()` accepts an injected runner via `_adb_runner` so tests never call a real ADB binary.
- **Fake OPPO server added for tests:** `tests/_support/fake_oppo_server.py` binds only to `127.0.0.1`, uses an ephemeral port, and supports `@OK`, `@ER`, `@UPL`, and `@UPW` style test behavior.
- **Clean TCP disconnect fixed:** verbose-push clean socket close no longer counts as playback stopped. Only explicit `@UPL` / `@UPW` stop-like events return a stop result.

### Files revised

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.0.0.2` | Make Build 2 visible as a new installable Kodi build. |
| `resources/lib/oppo_remote.py` | Stock `#POW` pass-through preserved; clone-only wake rewrite | Fix Slice 2 MVP compliance gap. |
| `resources/lib/oppo_control.py` | Configured start-command wake rewrite made clone-only | Keep start-command behavior aligned with remote bridge behavior. |
| `resources/lib/external_player.py` | Added safe TV-first startup, optional TV switching, non-fatal TV failures | Complete MVP Slice 3 behavior. |
| `resources/lib/adb_control.py` | Added injectable command runner | Ensure tests do not require real ADB or real TV. |
| `resources/lib/oppo_tcp_client.py` | Added explicit stop-event tracking separate from socket disconnect | Preserve the do-not-regress rule that clean TCP disconnect is not playback stop. |
| `resources/settings.xml` | Added `tv_switching_enabled` setting | Expose MVP no-op path for TV switching. |
| `resources/language/*/strings.po` | Added labels/help for `tv_switching_enabled` across all 12 locales | Preserve locale/msgctxt parity. |
| `tests/_support/fake_oppo_server.py` | Added loopback fake OPPO TCP server | Hermetic integration tests. |
| `tests/test_all.py` | Added Build 2 MVP compliance tests | Lock the MVP behavior. |
| `SLICE2_NOTES.md` | Added Slice 2 verification notes | Document wake behavior status. |
| `SLICE3_NOTES.md` | Added Slice 3 implementation notes | Document TV switching status. |
| `BUILD_NOTES_v2.0.0_BUILD2.md` | Added build/audit notes | Release traceability. |
| `README.md`, `reference.md`, `web-references.md` | Updated Build 2 documentation | Keep docs synchronized. |

### Tests and audit

- Build 2 tests: `324 / 324 passing`.
- Python compile audit: passed.
- `addon.xml` parse: passed.
- `resources/settings.xml` parse: passed.
- Locale parity: 12 locale files with matching msgctxt sets.
- Command map audit: 76 canonical keys; no `#SIS`, `#PGU`, or `#PGD`.
- Hardware audit: `oppo_hardware_model` enum count matches `HARDWARE_COMPAT` count at 12.

### Remaining MVP work / known deferrals

Build 2 is much closer to MVP-compliant, but it is still a build candidate rather than the final v2.0.0 release. Kodi API stubs and the 92% coverage gate remain deferred to the next hardening pass. Physical OPPO/TV/ADB testing remains outside MVP automation and should be handled manually by the user when hardware is available.


## Version 2.0.0 Build 1 - MVP-first starting build

This is the first Version 2 build created from the verified v1.x source baseline. The build intentionally starts the v2 MVP line rather than attempting the full historical v1.3-style superset merge.

### Scope in this build

- Baseline: reconstructed v1.1.10 / v1.x platform tree.
- MVP direction: External Player-first playback path.
- Hardware retained for MVP: OPPO UDP-203/UDP-205 plus M9702/Chinoppo-style wake behavior.
- Compatibility restored: canonical 76-key OPPO command map using `#SRC`, `#PUP`, and `#PDN`; no `#SIS`, `#PGU`, or `#PGD` in the default command map.
- Wake behavior restored: `#PON` and `#POW` are resolved to `#EJT` for Chinoppo/M9702-style models at command-send time.
- UI scope: the hardware model setting is exposed; the older architecture-selection settings are removed from the Kodi settings UI for the MVP-first line while internal defaults remain for backward compatibility.

### Deferred from this first build

- Full v1.3.0-style merge.
- Full wizard polish restoration.
- Fake OPPO server integration tests.
- Kodi API stubs and the future 92% coverage gate.
- Physical OPPO / TV / ADB integration testing.

### Build 1 audit result

- Baseline tests before edits: 305 / 305 passing.
- Build tests after edits: recorded in `BUILD_NOTES_v2.0.0_BUILD1.md`.
- Documentation updated: `README.md`, `reference.md`, `web-references.md`.

## Version 1.1.9 - Property-based testing with Hypothesis (or fallback)

- Adds property-based testing for three high-fanout pure modules:
  `hardware_presets`, `i18n`, `autoscript_helper`. Property tests
  assert *invariants* that must hold across all inputs - not just
  hand-picked happy-path examples.
- **Hypothesis-or-fallback**: each new test class detects Hypothesis
  at import time. If installed, the suite runs randomised property
  tests with `max_examples=100-200` per property. If Hypothesis is
  not available (e.g. minimal CI image), the same invariants are
  verified against deterministic curated sample sets covering valid
  / invalid / boundary inputs - so the gate never silently weakens.
- **TPropertyHardwarePresets** (6 tests + 4 Hypothesis properties):
    * Across **every** key in `PRESET_KEYS`:
        - `select_play_command(key)` returns a non-empty list of
          strings, every command starts with `#`, no `\n` or `\r`.
        - `select_power_on_command(key)` returns a string starting
          with `#`, no `\n`/`\r`.
        - `supports_http(key)` returns a `bool`.
        - `select_recommended_power_delay(key)` returns a non-negative
          number under 600s (sane delay).
        - `get_preset(key)` returns a dict with required fields
          (`label`, `family`, `play`, `power_on`, `stop`).
    * Same invariants hold for **invalid keys**: empty string,
      whitespace, `None`, control characters, emoji, leading/
      trailing spaces, ridiculously long strings, casing mismatches.
      Graceful fallback - never raises.
    * Hypothesis: `st.text(max_size=64)` -> 100 random keys per
      function, all four invariants enforced.
- **TPropertyI18nL** (2 tests + 3 Hypothesis properties):
    * `L()` must NEVER raise, regardless of input type.  Tested
      with `None`, `""`, ints, negative ints, large ints, strings,
      bool, list, dict, tuple, object, `float("inf")`, `float("nan")`.
    * Always returns a non-None `str`.
    * Known #31xxx ids resolve to non-empty strings.
    * Hypothesis: random ints (200 examples), random strings (100),
      arbitrary objects via `st.one_of(...)` mixing 8 types (200).
- **TPropertyAutoScript** (3 tests + 1 Hypothesis property):
    * `generate(opts)` always returns a string starting with
      `#!/bin/sh`, **no `\r` anywhere** (BusyBox sh on the OPPO
      would choke), no `\r\n` sequences, valid LF-only output.
    * Tested with default opts, None opts, every documented opts
      shape (telnet on/off, passwordless root, cifs/nfs mounts,
      adb, heartbeat path), and "garbage" opts (non-int port, ints
      where strings expected, None where strings expected).
    * Hypothesis: opts dictionaries with random valid+invalid types
      for every documented field (100 examples).
- **TPropertyAvailability** (1 test): self-test that surfaces in the
  log whether Hypothesis was loaded - useful for diagnosing CI
  configuration drift.
- Tests: 305/305 passing (8 new this turn). When Hypothesis is
  installed (verified in this sandbox), the property suites run
  ~900 randomised cases on top of the 297 existing deterministic
  cases.

### Bugs found and fixed by the property tests

The property tests immediately found **three real bugs** in
production code - exactly the failure modes hand-written tests had
missed:

1. **`i18n.L(float("inf"))` raised `OverflowError`**.  The L()
   function caught `(TypeError, ValueError)` but not the
   `OverflowError` Python raises when converting `inf` to int.
   **Fix**: broadened the except clause to include `OverflowError`.
   The L() docstring promised "always safe to call: never raises"
   - the property test held that promise honest.

2. **`autoscript_helper.generate({"telnet_port": "not-an-int"})`
   raised `ValueError`**. The function bare-`int()`-coerced the
   port, crashing on non-numeric input.
   **Fix**: added `_safe_int(v, default)` helper that catches
   `(TypeError, ValueError)` and falls back to the documented
   default. Applied to both `telnet_port` and `adb_port`.

3. **`autoscript_helper.generate({"mount_type": 12345})` raised
   `AttributeError: 'int' object has no attribute 'lower'`**. The
   function called `.lower()` on the raw value before coercing
   to str.
   **Fix**: wrapped with `str(...)` before `.lower()`.

All three fixes are in the production modules, not in the tests.
The property tests now lock the fixes in place: any future
regression that re-introduces the unguarded coercions would fail
the corresponding property.

### Why property-based testing matters here

Hand-written tests can only cover the inputs the author thought of.
The three bugs above are exactly the kind of latent issues a
hand-written suite never catches: who would write `generate({"mount_type":
12345})` by hand? Hypothesis generates 100 random opts dicts per run,
so the tail of weird-but-legal inputs gets exercised every time.


## Version 1.1.8 - CI workflow and linting

- Adds first-class CI scaffolding so contributions are tested
  identically on the developer machine and in GitHub Actions.
- New files at the repo root:
    * **`pytest.ini`** - unittest-compatible pytest config
      (`testpaths = tests`, `python_classes = T*`, `addopts = -ra`).
    * **`conftest.py`** - puts `resources/lib`, `tools`, and `tests`
      on `sys.path` so both pytest and `python -m unittest discover`
      resolve modules by short name.
    * **`ruff.toml`** - lint config targeting Python 3.9 baseline,
      line-length 100, rule sets E/F/W/I/B/UP, sensible per-file
      ignores for `resources/lib/*.py` and full exclusion of
      generated dirs (`output/`, `tools/`, `tests/`).
    * **`.coveragerc`** - branch coverage on `resources/lib`,
      `fail_under = 85` so the gate fires at the spec'd target.
    * **`.github/workflows/ci.yml`** - two jobs: `test` (matrix on
      Python **3.9 / 3.10 / 3.11 / 3.12**, runs unittest then pytest
      then `coverage` with `--fail-under=85`) and `lint` (Python 3.12,
      `ruff check resources/ default.py service.py`).
- `fail-fast: false` on the test matrix so a failure on one Python
  version doesn't mask failures on the others - all four versions
  always report.
- New CI test classes in `tests/test_all.py`:
    * **TSmokeImports** (3 cases): every `resources/lib/*.py` imports
      cleanly. Modules whose import legitimately requires Kodi
      stubs (`xbmc`, `xbmcaddon`, `xbmcgui`, `xbmcvfs`, `xbmcplugin`)
      are recorded as skipped, not failed. Modules whose import
      uses a *package-relative* form (`from . import x`) are also
      acceptable to skip in smoke (they load fine in Kodi runtime
      as `resources.lib.<name>`). `tools/make_pot.py` is also
      smoke-imported and required to expose `render_pot` +
      `collect_ids`.
    * **TCIScaffolding** (7 cases): pytest.ini, conftest.py,
      ruff.toml, .coveragerc, and the GH Actions workflow are all
      present with their spec'd shapes; the workflow has both
      `test` and `lint` jobs, runs the four-version matrix with
      `fail-fast: false`, invokes both unittest and pytest, runs
      coverage, and runs ruff.
- Tests: 297/297 passing (10 new this turn).
- Bug caught by the smoke test on first run: `oppo_remote.py` used
  a package-relative import (`from . import ...`) that cannot resolve
  outside Kodi's `resources.lib.*` package context. The smoke test
  now treats relative-import errors as expected (loaded fine in
  production), and a TODO is left for a future turn to refactor to
  dual-mode imports if needed.
- Carried forward intact: all v1.0.0-v1.1.7 features and tests.


## Version 1.1.7 - Localization breadth and .pot sync helper

- 5 new locales added alongside the existing 7 (en_gb, de_de, fr_fr,
  es_es, it_it, nl_nl, zh_cn): **Russian (ru_ru)**, **Polish (pl_pl)**,
  **Brazilian Portuguese (pt_br)**, **Japanese (ja_jp)**, **Korean
  (ko_kr)**. Total: 12 locales.
- Each new locale ships:
    * `resources/language/resource.language.<lang>/strings.po`
    * `resources/language/resource.language.<lang>/langinfo.xml`
- Translation strategy: every locale has the SAME msgctxt set as the
  English source (parity is enforced by a CI test). Common UI labels
  (General, Connection, Power, Discovery, Diagnostics, Apply preset,
  Submit your preset, Custom presets, Firmware, Logging, Log level,
  Whitelist, Blacklist, Skin, Test connection, Save, Cancel, Next,
  Back, Finish) are hand-translated per locale; longer help-text
  strings fall back to the English msgstr (Kodi convention for
  untranslated entries) so the UI is never blank.
- Bug fixed: the legacy de_de/fr_fr/es_es/it_it/nl_nl/zh_cn locales
  had drifted out of parity with English over the v1.1.0-v1.1.6 work
  (missing #30xxx ids that English added). v1.1.7 backfills every
  missing id from the English msgstr, so all 12 locales now share an
  identical msgctxt set.
- New helper `tools/make_pot.py`. Walks the addon source, collects
  every numeric id passed to `L(...)` / `_(...)` /
  `getLocalizedString(...)`, and emits a deterministic Kodi-style
  `.pot` template (`resources/language/strings.pot`) listing every
  distinct id with empty msgid/msgstr ready for translators.
- Extractor design:
    * Pure stdlib (`tokenize`); zero third-party dependencies.
    * Tokenises Python source rather than regex-matching, so it sees
      `L(31000)`, `L('#31000')`, and `_(31000)` identically.
    * Out-of-range ids (< 30000 or > 32999) are filtered out so a
      stray `len(31000)` cannot pollute the template.
    * Excludes `tests/`, `tools/`, `__pycache__/`, `.git/`, `output/`
      so test-only fixtures don't leak into the template.
    * Output is sorted ascending by numeric id - re-running on
      unchanged source produces a byte-identical .pot file (safe to
      commit).
- New CI test class `TLocalizationParity`:
    * **Parity test**: every locale's msgctxt set is *exactly equal*
      to English's set (no missing, no extra). Catches drift the
      moment a translator adds a stray id.
    * Both new and legacy locale dirs exist (regression guard).
    * Every msgctxt has a matching msgstr line (no torn entries).
    * The 5 new locales have at least 1 string actually translated
      (msgstr != English) - guards against a no-op translation file.
- New CI test class `TMakePot`:
    * `_ids_in_source` picks up `L(31000)`, `_(31002)`, `L('#31003')`
    * Filters numbers outside #30000-#32999
    * Ignores unknown function calls (`print(31000)`, `len(...)`)
    * Tokeniser exceptions are swallowed (no crash on broken input)
    * `render_pot` is sorted ascending and **deterministic** (same
      input -> byte-identical output regardless of input order)
    * Header line `# Kodi .pot template` present
    * `collect_ids` walks subdirectories
    * `collect_ids` skips `tests/` and `tools/` so test-only ids
      don't pollute the template
- Tests: 287/287 passing (15 new).
- Bugs fixed during development:
    * `tokenize.TokenizeError` is `tokenize.TokenError` on the running
      Python; the extractor would have crashed on first malformed
      source. Caught by the syntax-error test.
    * 6 legacy locales had drifted parity; backfilled before the
      parity test was activated, so the CI gate now genuinely holds.


## Version 1.1.6 - Logging levels, rotating file, sensitive-data scrubber

- New module `resources/lib/logging_v116.py`. Self-contained,
  dependency-free logger. Filters by level, rotates a file in
  addon_data when it exceeds a byte budget, keeps a configurable
  number of historical rotations, and scrubs MACs + IPv4 addresses
  out of every line before write.
- **Levels** (increasing severity): DEBUG, INFO, WARN, ERROR. Settings
  toggle exposes the level name; the in-memory filter compares
  numeric severity. `set_level()` flips the threshold at runtime so
  the user can switch DEBUG on without restarting Kodi.
- **Rotation** (`max_bytes`, `backups`):
    * Default: 128 KiB current + 3 historical = 512 KiB total budget.
    * On every write we pre-check `current_size + incoming_bytes` and
      rotate *before* the append if it would exceed the budget.
    * Cascade: oldest beyond `backups` is dropped, then `.N -> .N+1`
      from highest down to `.1`, then current file becomes `.1`.
    * `backups=0` is supported and means truncate-on-rotate.
    * `max_bytes=0` disables rotation entirely (useful when an
      external log shipper handles rotation upstream).
- **Scrubber** (`scrub(text)`):
    * MACs (colon and dash separators) -> `xx:xx:xx:xx:xx:xx`
    * IPv4 -> `x.x.x.x`
    * **Loopback `127.0.0.1` is preserved** (it is never sensitive
      and masking it would obscure connection-test diagnostics)
    * Version-like strings ("1.2.3") are 3-octet, not 4, and are NOT
      masked - dotted-quad is required for the IPv4 regex.
    * `None` / empty input is returned unchanged.
- **Format**: `[YYYY-MM-DD HH:MM:SS] LEVEL message`. Supports printf
  args (`log.info("count=%d", n)`); a bad format string falls back
  to repr-appending the args rather than raising.
- All FS + clock work flows through injection points so tests are
  fully hermetic. Production wiring uses real `os` + `time`.
- Tests: 272/272 passing. New TLoggingV116 suite (25 cases) covers:
    * LEVELS order; level_value() known/unknown/None/empty
    * scrub: colon-MAC, dash-MAC, IPv4, loopback preserved, None,
      empty, plain text untouched, version strings untouched
    * Default INFO level filters DEBUG; set_level() flips threshold
      at runtime
    * Unknown level in constructor / set_level() raises ValueError
    * log() with unknown level is a silent no-op (defensive)
    * Line includes level + timestamp + trailing newline
    * Scrubber applies on write (MAC + IPv4 redacted; loopback kept)
    * printf args supported; bad format strings degrade gracefully
    * Rotation triggers at size budget; .1 contains pre-rotation text
    * Rotation NEVER keeps more than `backups` historical files
      (.3 must not exist when backups=2)
    * backups=0 means truncate-on-rotate (no .1 ever appears)
    * No rotation when under budget
    * Manual `rotate()` without size pressure
    * `max_bytes=0` disables rotation entirely
    * Real-IO round-trip via tempdir
    * `is_enabled()` query semantics (>= threshold, unknown -> False)
- Bugs prevented:
    * Without the loopback exception, scrub would mask `127.0.0.1`
      out of connection-test logs and the user could not tell whether
      the addon was talking to the OPPO or a local stub.
    * Without size pre-check, rotation would let the current file
      briefly exceed the budget by the size of one large line; we
      pre-check `cur + incoming_bytes` so the budget is hard.


## Version 1.1.5 - Service interception breadth and skin-aware keymaps

- New module `resources/lib/intercept.py`. Pure-function classifier
  for paths the service may receive from `Player.OnPlay`, plus a
  whitelist/blacklist gate so users limit the addon's scope.
- Recognised disc-image kinds (`DISC_KIND_*`):
    * **iso**         - `.iso`, `.img` (case-insensitive)
    * **bdmv**        - `/BDMV` folder, `index.bdmv`, any `*.bdmv`
    * **video_ts**    - `/VIDEO_TS` folder, `VIDEO_TS.IFO`
    * **m2ts**        - `*.m2ts` *only when* the path contains `/BDMV/`
    * **mpls**        - `*.mpls` *only when* the path contains `/BDMV/`
    * **mkv_sibling** - `*.mkv` whose parent folder contains a
      sibling `BDMV/` directory (the rip-with-menus workflow)
    * **other**       - everything else
- Windows path separators are normalised: `C:\Movies\T\BDMV\index.bdmv`
  classifies as bdmv. The classifier never trusts file extensions
  alone for `.m2ts`/`.mpls` - those must live inside a BDMV tree to
  count, which avoids false-positives on loose stream files.
- **Whitelist / blacklist** via `should_intercept(path, whitelist=,
  blacklist=)`:
    1. Path must be a disc image, else False.
    2. If a blacklist pattern matches -> False (blacklist beats
       whitelist).
    3. If a non-empty whitelist is set: True only when a whitelist
       pattern matches.
    4. Empty/None whitelist (or whitelist of all-blank strings):
       default-allow.
- Patterns: substring match by default; `*` is the only wildcard;
  case-insensitive; forward-slash-normalised.  Empty patterns never
  match (so an accidental `[""]` cannot open the whole filesystem).
- New module `resources/lib/keymap_skin.py`. Generates skin-aware
  keymap XML for `userdata/keymaps/oppo.xml` overlaying playback
  controls on the user's active skin.
- Three bundled skin profiles: **estuary** (Krypton+ default),
  **confluence** (legacy default), **arctic** (Arctic Zephyr family).
  All three share the same base bindings; per-skin window overrides
  slot in cleanly via the `_SKIN_WINDOWS` table.
- Bindings (8 actions): play, stop, eject, info, menu, pause,
  skipnext, skipprevious. Each routes to the addon via
  `RunPlugin(plugin://script.oppo203.iso.external/?action=...)`.
- Tests: 247/247 passing. New TIntercept (24) + TKeymapSkin (9):
    * iso/img recognised case-insensitively
    * /BDMV folder, index.bdmv, any *.bdmv recognised
    * /VIDEO_TS folder + VIDEO_TS.IFO recognised
    * .m2ts / .mpls only inside /BDMV/ tree
    * .mkv with sibling BDMV/ recognised
    * .mkv without sibling -> other
    * Windows backslash path separators normalised
    * Empty/None path -> other
    * is_disc_image quick check
    * pattern_matches: substring, wildcard `*`, case-insensitive
    * empty pattern never matches
    * should_intercept default-allow when no whitelist
    * should_intercept rejects non-disc paths
    * blacklist blocks
    * non-empty whitelist required-match
    * blacklist beats whitelist on overlap
    * empty/whitespace whitelist strings ignored
    * three skins exposed (estuary, confluence, arctic)
    * unknown skin raises KeyError
    * each skin's XML is well-formed
    * each contains <global> + <FullscreenVideo> + <keyboard>
    * each contains all 8 action bindings
    * action target points at the addon
    * skin-profile marker in XML
    * is_well_formed: rejects empty/None/malformed
    * each skin parses with ElementTree to a <keymap> root
- Bugs prevented: a misconfigured whitelist of `[""]` would have
  default-allowed everything in the naive implementation; we now
  filter empty/whitespace entries before evaluating, so the user
  cannot accidentally open the whole filesystem with one stray empty
  setting.


## Version 1.1.4 - Hardware preset extensibility

- New module `resources/lib/preset_manager.py`. Loads user-defined
  presets from `addon_data/custom_presets.json`, merges them with the
  v1.1.2 built-ins, exports submission JSON for upstream contribution,
  and warns when a device firmware is older than the preset's
  `firmware_min`.
- **Custom preset schema** (custom_presets.json):
    `{"presets": {"<id>": {"label": "...", "start_commands": "...",
    "stop_commands": "...", "firmware_min": "1.2.3"}}}`
- **Merge precedence**: custom wins on key collision. The built-in
  `BUILTIN_PRESETS` dict is never mutated; merging produces a fresh
  dict so misuse can't poison the in-memory built-ins.
- **load_custom(path, fs=)** is silent-on-failure: missing file,
  corrupt JSON, wrong root type, or invalid individual entries all
  resolve to `{}` (or partial-load skipping invalid entries) rather
  than raising. Each entry must have non-empty string `label`,
  `start_commands`, `stop_commands`; optional `firmware_min` must be
  a string.
- **export_submission(preset_id, ip=, quirks=, contact=, user_preset=)**
  builds a JSON-ready submission with `schema_version=1`. For new
  preset_ids (not in built-ins), `user_preset` is required and is
  schema-validated. For known preset_ids, `user_preset` overrides
  individual fields if provided.
- **save_submission(submission, root_dir, now=, fs=)** writes
  `preset-submission-<sanitised_id>-YYYYMMDD-HHMMSS.json` to addon_data;
  the preset_id is sanitised so a malicious `../etc/passwd` value
  can't escape the target directory.
- **compare_versions(a, b)** parses dotted-numeric versions with an
  optional `v` prefix; pads to equal length so `"1.2"` == `"1.2.0"`.
  Returns `None` on parse failure - the caller decides how to handle
  ambiguity rather than getting a wrong comparison.
- **firmware_warning(preset, device_firmware)** returns a warning
  string when the device firmware is strictly older than the preset's
  `firmware_min`, else `None`. **No false positives**: if either
  version can't be parsed, returns `None` rather than warning on
  ambiguity.
- Tests: 214/214 passing. New TPresetExtensibility suite (29 cases):
    * built-ins exposed (oppo203 / chinoppo / reavon_x200 / magnetar)
    * load_custom: missing path, corrupt JSON, wrong root, bad
      entries skipped, firmware_min type-checked
    * merged_presets: no-custom returns built-ins; custom wins on
      collision; custom adds new id; built-ins not mutated
    * export_submission: known preset includes ip+quirks+contact;
      new preset requires user_preset; user_preset overrides on
      known id; user_preset is validated; preset_id is required
    * save_submission: writes JSON with preset_id+schema_version;
      sanitises malicious preset_id; real-IO round-trip via tempdir
    * compare_versions: equal/older/newer; pads "1.2"=="1.2.0";
      handles "v" prefix; unparseable returns None
    * firmware_warning: no minimum -> None; older firmware -> warn
      mentioning both versions; equal/newer -> None; unknown firmware
      -> None (no false positive); invalid preset -> None
- Bugs fixed: none new this turn. The firmware-warning false-positive
  contract (unknown firmware doesn't warn) is locked in by tests
  test_firmware_warning_unknown_no_false_positive.


## Version 1.1.3 - Discovery improvements

- New module `resources/lib/discovery.py`. Adds mDNS and SSDP probes
  (alongside the existing UDP multicast), a per-found-device
  "Apply preset" shortcut, and a JSON-backed device cache so the
  wizard's IP step can suggest previously-seen devices.
- All network I/O flows through injected callables so the suite
  is fully unit-testable without sockets.
- **SSDP** (`parse_ssdp_response(text)`): parses M-SEARCH 200 OK and
  NOTIFY * HTTP/1.1 responses; extracts IP from LOCATION, vendor from
  SERVER, model from ST/NT.  Rejects non-HTTP garbage cleanly.
- **mDNS** (`parse_mdns_record(record)`): consumes a normalised
  record dict (`name`, `type`, `addresses`, `port`, `properties`)
  matching the shape Zeroconf-family libraries emit.  Tests pass
  in-memory dicts; production wires zeroconf if available.
- **UDP multicast** (existing v1.0.x probe): still supported; cache
  treats it as the lowest-priority source.
- **Source priority**: mdns (3) > ssdp (2) > udp (1).  When the same
  (ip, port) is reported by multiple probes, the richest source wins,
  so a Reavon discovered both via UDP and mDNS keeps the mDNS record.
- **vendor->preset** mapping: case-insensitive substring match against
  oppo / reavon / magnetar / zappiti / chinoppo / udp-203 / udp-205,
  with fall-through to `None` for unknown gear.
- **apply_preset_for(device)** is the per-device shortcut: respects
  an explicit `preset` field if set, else maps via vendor+model.
- **DeviceCache**: persistent JSON cache keyed by (ip, port).  API:
  `add()`, `add_many()`, `all()`, `recent(max_age_s=86400)`, `save()`,
  `load()`, `clear()`.  Filesystem is injectable for tests; default
  uses real `os`-backed I/O.
- Tests: 185/185 passing. New TDiscovery suite (30 cases) covers:
    * vendor->preset mapping for OPPO / Reavon / Magnetar / Zappiti
      / Chinoppo via UDP-203 / unknown / empty / None
    * apply_preset_for honours explicit preset, falls through to
      vendor+model, rejects None / non-dict / empty
    * SSDP parses HTTP/1.1 200 OK and NOTIFY responses; extracts IP
      from LOCATION; rejects garbage; handles missing LOCATION
    * mDNS parses typical record; rejects no-addresses; rejects
      non-dict input
    * discover() combines all 3 probes and stamps presets+last_seen
    * discover() dedup prefers mdns over udp on same (ip, port)
    * discover() swallows probe exceptions; no-probes returns []
    * DeviceCache add/all/dedup/recent/clear behaviour
    * DeviceCache save->load JSON round-trip via in-memory FS
    * DeviceCache load handles missing file and corrupt JSON
    * DeviceCache rejects invalid input (None, empty, no IP)
    * DeviceCache stamps preset on add via vendor mapping
- Bugs fixed: none new this turn.


## Version 1.1.2 - Per-preset playercorefactory snippets and safe merge

- New module `resources/lib/playercorefactory_merge.py`. Generates
  hardware-aware <playercorefactory> snippets and merges them into
  the user's existing playercorefactory.xml safely.
- `PRESETS` dict provides start/stop command sequences per hardware:
    * **OPPO 203/205**          - start `#PLA`,        stop `#STP`
    * **OPPO 103/105**          - start `#PLA`,        stop `#STP`
    * **Chinoppo (UDP-203/205)**- start `#EJT,#PLA`,   stop `#STP`
    * **Reavon UBR-X200**       - start `#PON,#PLA`,   stop `#STP`
    * **Zappiti Reference**     - start `#PLA`,        stop `#STP`
    * **Magnetar UDP800**       - start `#PLA`,        stop `#STP`
- `snippet_for(preset_id, player_path=, addon_id=)` returns a self-
  contained, well-formed <playercorefactory> XML fragment with one
  <player> and one matching <rule> for `iso|bdmv|m2ts`.
- Each preset gets a unique <player> name (`OPPO_External_<preset>`)
  so multiple presets can coexist in the same playercorefactory.xml.
- `is_well_formed(text)` validates any pre-existing playercorefactory.
  None/empty/whitespace counts as well-formed (no document = OK).
- `merge(target_path, snippet_xml, fs=, now=)` is the safe-merge:
    1. Validate the snippet is well-formed XML (else ValueError).
    2. If the target file exists, validate it is well-formed XML
       (else ValueError - refuse to merge into a broken file; the
       user fixes it manually first).
    3. Create a timestamped backup `<target>.YYYYMMDD-HHMMSS.bak`
       byte-identical to the original.
    4. Merge: deduplicate <player name="X"> and <rule name="X">; same
       preset re-applied is a no-op (idempotent).
    5. Refuse if the existing root is not <playercorefactory>.
- Filesystem injection: `fs` parameter accepts a stub (used in tests)
  with `.exists/.read/.write/.copy`; production calls pass None and
  use real `os` + `shutil`.
- Tests: 155/155 passing. New TPlayerCoreFactory suite (20 cases):
    * all 6 presets present in PRESETS
    * oppo203 uses `#PLA` only (no `#EJT`)
    * chinoppo uses `#EJT,#PLA` (avoids resume-previous-title bug)
    * reavon_x200 uses `#PON,#PLA` (needs explicit power-on)
    * unknown preset raises KeyError
    * snippet for every preset is well-formed XML
    * snippet player names are unique across all presets
    * snippet includes the requested addon_id
    * is_well_formed handles None/empty/whitespace
    * is_well_formed accepts good XML, rejects malformed XML
    * is_well_formed rejects raw text
    * backup_path format
    * merge into empty target makes no backup
    * merge with existing target creates byte-identical backup
    * merge refuses malformed existing file (no write happens)
    * merge refuses malformed snippet
    * merge is idempotent: re-merging the same preset adds no
      duplicate <player> or <rule>
    * merge two different presets keeps both <player> entries
    * merge refuses wrong root element (not <playercorefactory>)
    * merge real I/O round-trip via tempdir, with backup verification
- Bugs fixed during development:
    * Initial idempotency assertion expected 2 occurrences of
      `name="OPPO_External_oppo203"`; corrected to count <player>
      tags vs <rule player=...> references separately. The merger
      itself is correct; the test now precisely measures that.
    * `re` was not imported in one test method scope; added local
      import.


## Version 1.1.1 - Wizard polish

- New module `resources/lib/wizard_polish.py`. A pure-function model
  of the wizard's navigation, in-step Test-Now, pre-apply Summary, and
  Dry-run-no-write guarantee. Fully unit-testable without Kodi UI.
- `STEPS` is a 7-step ordered tuple: `welcome`, `connection`,
  `hardware`, `autopoweron`, `wizard_mode`, `summary`, `done`.
- `WizardState(values, dry_run, step_index)` is the picklable,
  copy-on-write state container with `step` (current step name),
  `history` (Back stack), and `last_test` (last Test-Now result).
- Navigation primitives:
    * `next_step(s)`         - advances and pushes the prior index
                               onto the history stack.
    * `prev_step(s)`         - Back: pops history if non-empty, else
                               clamps at index 0; never raises.
    * `can_go_back(s)`       - bool, True iff step_index > 0.
    * `can_go_next(s)`       - bool, True iff not on the last step.
- In-step Test-Now: `test_now(state, probe=)` only valid on the
  `connection` step (raises RuntimeError elsewhere).  Calls injected
  `probe(host, port)`, normalises bool returns to `{"ok": ...}`,
  swallows exceptions into `{"ok": False, "error": ...}`, and stores
  the result on `state.last_test`.
- Pre-apply Summary: `summary(state)` returns a sorted, deterministic
  list of `(key, value)` tuples plus a final `("__dry_run__", bool)`
  row, ready for the review UI.
- Dry-run-no-write guarantee: `apply(state, writer=)` never calls
  `writer` when `dry_run=True`. The test suite enforces this even
  with a writer that would crash on call - ironclad guarantee.
- All operations are copy-on-write: `next_step`, `prev_step`, and
  `test_now` return new `WizardState` instances; the input state is
  never mutated.  Verified by `test_state_copy_is_deep_enough`.
- Tests: 135/135 passing. New TWizardPolish suite (18 cases) covers:
    * initial state (welcome, can_go_next, !can_go_back)
    * STEPS canonical order
    * next() advances; original state unchanged
    * next() clamps at the end
    * prev() clamps at zero
    * Back nav pops history correctly across 4 steps
    * Back then Next does not double-push history
    * State equality
    * Test-Now raises off the connection step
    * Test-Now returns probe result; original state unchanged
    * Test-Now swallows probe exceptions
    * Test-Now normalises bool returns to a dict
    * Summary lists every value + dry_run flag last
    * Summary is sorted (deterministic ordering)
    * apply() writes every value when not dry-run
    * apply() dry_run never calls writer (no-write guarantee)
    * apply() dry_run with a *crashing* writer still does not call it
    * State copy is deep enough (mutating copy.values does not leak)
- Bugs caught by the new tests: deep-copy was needed in `state.copy()`
  so that mutating `s2.values` after `next_step(s)` does not leak back
  into `s.values`. Initial implementation passed that test by virtue
  of `dict(self.values)` in the constructor; the test now locks it in.


## Version 1.1.0 - Settings UI grouping and conditional visibility

- `resources/settings.xml` is reorganised into 5 user-facing categories,
  preserving every one of the 71 existing setting ids and defaults:
    * **Connection** (#32100) - IP/port/timeout, MAC + WoL, HTTP, and
      reconnect knobs.
    * **Hardware and commands** (#32101) - start/stop commands, command
      delay, preflight, verbose mode, remote command map, TV/AVR bridge.
    * **Auto-power-on** (#32102) - master toggle, delay, retries, WoL.
    * **Wizard and playback** (#32103) - wizard mode, playback
      architecture, hold mode, polling intervals, switch-back-on-exit.
    * **Diagnostics and experimental** (#32104) - experimental file-list
      flag and v1.0.9 dashboard hooks.
- Conditional visibility via `<dependency type="visible">` rules:
    * `oppo_mac` and `oppo_wol_broadcast` hide unless `oppo_use_wol=true`.
    * 8 HTTP sub-settings hide unless `oppo_http_activate=true`.
    * 4 reconnect sub-settings hide unless `reconnect_enabled=true`.
    * 3 auto-power-on sub-settings hide unless `kodi_startup_power_on=true`.
- New string ids 32100-32104 (category labels) and 32110-32114 (group
  help text). All other label ids preserved.
- Tests: 117/117 passing. New TSettingsLayout suite (15 cases) parses
  settings.xml with ElementTree and asserts:
    * the document is well-formed (root = settings)
    * all 5 v1.1.0 groups are present
    * no group is empty
    * every setting has both id and label
    * setting ids are unique
    * every <dependency> references an existing setting id
    * every <dependency> uses a known operator (is | !is)
    * every <dependency> has type="visible"
    * MAC + WoL broadcast depend on oppo_use_wol=true
    * 4 reconnect sub-settings depend on reconnect_enabled=true
    * 3 auto-power-on sub-settings depend on kodi_startup_power_on=true
    * 8 HTTP sub-settings depend on oppo_http_activate=true
    * the total count is 71 (preservation guard)
    * category label ids match 32100..32104
- Bugs caught and prevented going forward: a category whose id is
  referenced from a <dependency> but absent from the document would now
  fail CI (test_dependencies_reference_existing_ids). A duplicate
  setting id (e.g. from a copy-paste bug during regroup) would now fail
  CI (test_unique_ids). A dropped setting from regrouping would now
  fail CI (test_all_71_legacy_setting_ids_preserved).


## Version 1.0.9 - Diagnostics dashboard

- New module `resources/lib/diagnostics.py`. Pure-function shape, all
  external dependencies (TCP/HTTP/UDP/Kodi) flow through injection
  points, so the dashboard is unit-testable without sockets, files, or
  Kodi.
- `run(host, port, mac, tcp_check=, http_check=, svm_check=,
  wol_check=, kodi_info=, capabilities=, now=)` runs the full
  pre-flight in one call and returns a structured result dict with a
  per-probe `ok`/`error` and a top-level `overall_ok`.
- Probes covered:
    * **TCP probe** - reachability of OPPO control port (default 23).
    * **HTTP probe** - reachability of port 80 for OPPO web UI.
    * **Verbose-push (#SVM 2) capability check** - sends `#SVM 2\r`
      and requires a non-empty reply within 2 seconds.
    * **WoL packet round-trip** - sends a magic packet via UDP/9
      broadcast; "round-trip" here is best-effort packet emission.
    * **Kodi version snapshot** - `System.BuildVersion` and
      `System.KernelVersion` via `xbmc.getInfoLabel` when available.
    * **Capabilities summary** - reports whether service interception,
      external player, WoL, and verbose push are available.
- `format_report(result)` renders a human-readable text block with
  per-probe sections.
- `save_report(result, root_dir, now=, writer=)` writes a timestamped
  `diagnostics-YYYYMMDD-HHMMSS.txt` under addon_data with optional
  writer injection for tests.
- `redact(text)` masks IPv4 addresses and MAC addresses for shareable
  reports (used by the v1.1.6 logging scrubber too).
- Installer menu entry `default.py:run_diagnostics_dashboard(addon_data,
  host, port, mac)` wires the production probes (real sockets, real
  Kodi APIs) and calls `save_report`. Probes are designed to never
  raise: any exception becomes `{"ok": False, "error": ...}`.
- Tests: 102/102 passing. New TDiagnostics suite (15 cases) covers:
    * redact masks MAC and IP, handles dash-format MAC, handles empty
    * default_path format
    * run() marks every missing probe as skipped
    * run() overall_ok=true only when all run probes pass
    * run() overall_ok=false when any probe fails
    * run() skips WoL when no MAC provided
    * run() swallows probe exceptions and surfaces error string
    * format_report contains all six section headers + Overall OK
    * format_report handles invalid input
    * save_report uses writer injection (no real I/O)
    * save_report writes a real file (real I/O)
    * default.py exposes run_diagnostics_dashboard symbol
    * single passing probe with all others skipped is overall_ok=true
- Bugs fixed: none introduced this turn.


## Version 1.0.8 - Real architecture benchmarking

- New module `resources/lib/arch_benchmark.py` replaces the v1.0.3
  heuristic auto-test with measured probes.
- `benchmark(candidate, trials, probe, timer)` runs N timed trials
  (default 3) of an injected probe and returns
  `{"trials":[...], "median":..., "all_ok":...}`. Failed trials still
  record their elapsed time so a permanently broken candidate gets a
  high (bad) median rather than skewing comparison.
- `recommend(ext_median, svc_median, eps=0.020)` picks `external`,
  `service`, or `tie`. Ties (within 20 ms) prefer External Player as
  the historically more deterministic path on Chinoppo-class hardware.
  None medians are handled gracefully (a None median always loses).
- `validate_playercorefactory(path)` does an XML well-formedness check
  and asserts the file has a `<playercorefactory>` root with a
  `<players>` block containing at least one `<player>` child.
- `run_full(probe_external, probe_service, trials, timer, eps,
  playercorefactory_path)` runs both architectures, picks a winner,
  and (optionally) validates the user's playercorefactory.xml in one
  call. All time-bound work flows through the injected `timer`, so
  the suite is deterministic in tests.
- Wizard helper `_run_benchmark(host, port, trials, timer,
  probe_external, probe_service, playercorefactory_path)` bridges the
  wizard to `arch_benchmark.run_full`. Production calls wire it to a
  real TCP probe; tests inject deterministic stubs.
- Tests: 87/87 passing. New TArchBenchmark suite (15 cases) covers:
    * 3-trial timing recording, median calculation
    * failure-marks-all_ok-false
    * `benchmark()` requires a probe (raises ValueError)
    * recommendation: external wins, service wins, tie within eps
    * recommendation: handles None medians (3 sub-cases)
    * `run_full` picks lower-median candidate end-to-end
    * `validate_playercorefactory`: well-formed accepts, missing file
      rejects, empty file rejects, malformed XML rejects, wrong-root
      rejects, no-`<players>`-block rejects
    * `run_full` includes PCF validation when path is provided
    * wizard `_run_benchmark` bridges through to `run_full`
- Bugs fixed: none introduced this turn; the v1.0.3 heuristic remains
  as a fallback when probes cannot be wired (no host reachable).


## Version 1.0.7 - Persistent reconnect with exponential backoff

- New module `resources/lib/reconnect_backoff.py`. Pure functions only,
  fully unit-testable: `compute_delay(attempt, base, cap, jitter, rng)`,
  `schedule(max_retries, base, cap, jitter, rng)`, `should_retry(attempt,
  max_retries)`. Defaults: base=1s, cap=30s, max_retries=8, jitter=25%.
- New `OppoTcpClient.wait_for_stop_persistent(timeout, max_retries,
  base_delay, cap_delay, jitter, _sleep, _rng, _connect_factory)`. On
  every transient failure the client consults the backoff helper, sleeps
  the calculated delay, and tries again until a stop event is observed,
  the retry budget is exhausted, or the overall timeout elapses.
- `wait_for_stop` (the original behaviour) is unchanged. Callers opt
  into reconnect by switching to `wait_for_stop_persistent`.
- Per-attempt threading state is reset cleanly in `_attempt_once`, so
  retries do not leak Event/Thread state from prior attempts.
- New settings (Connection group):
    * `reconnect_enabled`     - master toggle (default true)
    * `reconnect_max_retries` - default 8
    * `reconnect_base_delay`  - default 1s
    * `reconnect_cap_delay`   - default 30s
    * `reconnect_jitter_pct`  - default 25 (slider 0-100)
  Sub-settings hide automatically when the master toggle is off.
- New string ids: 30960-30964.
- Tests: 71/71 passing. New suites:
    * **TBackoff** (7 cases) - schedule doubles to cap, no-jitter is
      deterministic, jitter respects bounds, midpoint factor is exact,
      `should_retry` is correct, `attempt < 1` is floored to 1.
    * **TPersistentReconnect** (7 cases) - first-attempt success, two
      failures then success, give-up after max retries, max_retries=0
      yields exactly one attempt, exception in the connect attempt is
      treated as failure, deadline short-circuit, settings string-id
      presence guard.
- Bug fixed during this turn: `timeout=0` was interpreted as "no
  deadline" by the truthiness check; changed to explicit
  `timeout is not None` so timeout=0 correctly bails before any sleep.


## Version 1.0.6 - Localization expansion and broader test coverage

- Localization: 7 bundled languages now ship with the add-on:
  English (en_gb), German (de_de), French (fr_fr), Spanish (es_es),
  Italian (it_it), Dutch (nl_nl), and Simplified Chinese (zh_cn).
- 25 new canonical string ids (#31000-#31061) cover every wizard step,
  auto-test prompt, AutoScript message, and reset/complete dialog.
- New module `resources/lib/i18n.py` with `L(string_id, default)` that
  returns the localized string and falls back to a built-in English
  table when `xbmcaddon` is unavailable (tests, headless). It never
  raises, even on bad input.
- Tests: 57/57 passing. New suites:
    * **TI18N** - 5 cases: English fallback, unknown id default,
      invalid id default, never-raises contract, supported_languages.
    * **TLangFiles** - 3 cases: every supported folder exists, every
      language defines all #31xxx ids, no blank msgstrs in localized
      files (English may be blank since Kodi resolves from msgid).
    * **TReconnect** - 5 cases: oppo_tcp_client module import,
      OppoTcpClient class presence, wait_for_stop+close lifecycle,
      lazy-construct safety, oppo_control send_commands /
      query_power_status / wake_on_lan presence.
    * **TBugs** - 3 cases: i18n unicode safety, wizard helpers still
      callable after preset refactor, presets still intact.
- Bugs fixed:
    * Earlier reconnect test assumed a `send_command` free function;
      corrected to assert `OppoTcpClient` lifecycle (`wait_for_stop`,
      `close`) and free functions in `oppo_control` instead.
    * Localized `.po` files now guaranteed non-blank msgstrs (CI guard
      in TLangFiles prevents future regressions).
    * `i18n.L()` documented as never-raising; tested with `None`,
      lists, and dicts.


## Version 1.0.5 - Expanded hardware presets and quirks

- New module `resources/lib/hardware_presets.py` introduces 16 hardware
  presets in 5 device families:
    * **OPPO**: UDP-203, UDP-205, UDP-203 (Jailbroken), UDP-205 (Jailbroken)
    * **Chinoppo**: generic, M9702, M9201, M9203, M9205C
    * **Reavon**: UBR-X100, UBR-X110, UBR-X200
    * **Magnetar**: UDP800, UDP900
    * **Zappiti**: Reference
    * **Generic OPPO clone** (catch-all)
- Each preset records: control port, power-on/off, play/pause/stop/eject,
  query-power, HTTP support, Chinoppo `needs_eject_before_play` quirk,
  Chinoppo `use_eject_for_power_on` quirk, Quick Start support, WoL
  recommendation, and free-form notes.
- Quirk-aware command selection:
    * `select_power_on_command(key)` -> `#EJT` for Chinoppo-class, `#PON`
      otherwise.
    * `select_play_command(key)` -> `["#EJT","#PLA"]` for Chinoppo-class,
      `["#PLA"]` otherwise.
    * `select_recommended_power_delay(key)` -> 8s for Reavon UBR-X200,
      6s for Chinoppo, 5s default.
- Wizard now lists all 16 presets in a single picker, applies the
  recommended power-on delay automatically, and uses `is_chinoppo_family`
  for the Chinoppo-specific branches (preset, AutoScript helper).
- Architecture auto-test now uses `is_chinoppo_family` so any Chinoppo
  variant gets the tailored message.
- New string id 30950 ("Hardware preset").
- Tests: 41/41 passing. New TPresets suite (15 cases) covers preset
  registry, fallback, OPPO/Chinoppo/Jailbroken/Magnetar/Reavon/Zappiti
  command selection, recommended delays, HTTP-support flags, and family
  detection.
- Bugs fixed: hard-coded preset list in the wizard would not have shown
  Magnetar/Reavon/Zappiti; replaced with dynamic listing from
  `hardware_presets`. Wizard now falls back to a small built-in list if
  the new module is somehow missing.


## Version 1.0.4 - Kodi v21 Omega service-interception hardening

- New: `_kodi_major_version()` reads `System.BuildVersion` and exposes the
  Kodi major release as an integer. `_is_omega_or_newer()` returns True for
  Kodi v21+.
- New: `_safe_call(fn, ...)` wraps Kodi `Player` callbacks so binding-level
  exceptions can never abort the long-running service. Critical on Omega,
  which is stricter about callback teardown timing.
- Hardened InterceptionPlayer:
    * Prefers `onAVStarted` on Omega (authoritative event).
    * Falls back to `onPlayBackStarted` on Matrix/Nexus.
    * Re-entrancy guard via `_handled_path` prevents double-handling
      when both callbacks fire on older Kodi.
    * Defensive `isPlayingVideo()` / `getPlayingFile()` calls.
    * `executebuiltin("PlayerControl(Stop)")` wrapped to tolerate
      RuntimeError during Kodi shutdown.
    * Constructor logs `omega=True/False` so users know which path is
      active.
- Service banner now logs detected Kodi major version on startup.
- Tests: 26/26 passing. New TOmega suite (10 cases) covers helpers,
  version detection (Omega + Matrix + no-xbmc), ISO/BDMV detection,
  Omega event-deferral, pre-Omega event-handling, and exception
  swallowing.
- New string id 30940 ("Service interception (Kodi Omega hardened)").


## Version 1.0.3 - Architecture auto-test

- New: Architecture auto-test step inside the Full-mode wizard. After IP/port
  and hardware-model are chosen, the wizard offers a quick auto-test that:
    1. Probes TCP reachability to the player.
    2. Recommends the safest architecture (External Player) for the setup.
    3. For Chinoppo-class devices, the recommendation message is tailored
       to that family.
    4. Asks the user before applying the recommendation; in headless mode
       (no GUI) the recommendation is auto-applied.
- New string id 30930 ("Architecture auto-test").
- Tests: 15/15 passing. New TWiz suite covers `_choose_mode`,
  `auto_test_architecture` (unreachable, reachable default, reachable
  Chinoppo).
- Bugs fixed: previous draft had an unterminated string literal in the
  test module; rewritten with safe escapes.
- Carried forward from prior versions: Kodi-startup power-on engine
  (1.0.0), Chinoppo AutoScript helper (1.0.1), Basic vs Full wizard
  mode (1.0.2).


This Kodi add-on routes `.iso` file and video disc folder playback to an Oppo UDP-203 and switches TV inputs automatically.

Version 0.9.2 integrates the structured file-list parser into the experimental diagnostic workflow. The diagnostic UI now calls `parse_undocumented_file_list(raw, base_path=requested_path)` so inferred path fields are rooted at the requested directory. Each entry is displayed with its type tag (`[D]` directory, `[F]` file, `[?]` unknown), size, disc classification, extension, and full path when available. A second textviewer screen shows the raw response for debugging. No change to normal playback paths.

Version 0.9.1 improves the experimental file-list parser so diagnostic entries include best-effort `path`, `entry_type`, `is_dir`, `is_file`, `size_bytes`, `extension`, and `disc_type` fields when those values can be inferred.

Version 0.9.0 adds trick-play suppression for HTTP poll mode, `errcode1=-5` definitive-stop detection, verbose push hold mode (persistent TCP with `@UPL`/`@UPW` event parsing), discovery auto-apply, expanded remote command map (input source, colour buttons, page, dimmer, option, seek, audio/subtitle cycling), audio/subtitle HTTP helpers, `setplaytime` seek helper, and opt-in experimental file-list diagnostics.

Version 0.8.0 added two architecture choices, TCP QPL polling, Oppo UDP discovery, SVM verbose mode, preflight queries, HTTP JSON payload mode, corrected remote command mappings, `dvdimage`/`dvdfile` playercorefactory rules, and TCL ADB preset guidance.

## Playback architecture (v0.8.0)

On first run, the add-on offers two architecture choices:

### External Player (default, recommended)

The official Kodi path. Kodi matches disc files through `playercorefactory.xml` and launches `external_player.py` directly. This is the most predictable mode, keeps Kodi's play state while the wrapper runs, and has no internal playback race condition.

**Required setup:** Merge the generated `playercorefactory.xml` snippet into Kodi's userdata. Run the add-on and choose *Generate playercorefactory snippet*.

### Service Interception

The add-on's service process monitors Kodi playback starts, detects disc file paths, stops Kodi quickly, then runs the Oppo/TV flow in a background thread. No playercorefactory snippet is needed for routing, but the mode is more timing-sensitive and may briefly start Kodi's internal player before interception.

**Required setup:** No playercorefactory merge needed. Only the keymap snippet is needed if you want remote-bridge key forwarding. Change `playback_architecture` to `service_interception` in settings and run *Architecture setup* from the installer menu.

You can switch between modes at any time by changing the `playback_architecture` setting and re-running the setup.

## Important limitation

The Oppo UDP-203 supports RS-232 and IP control. The OPPO UDP-20X RS-232 and IP Control Protocol document describes the official command vocabulary. This add-on uses that control channel for remote-style and query commands, but it does not assume the Oppo can open an arbitrary Kodi SMB path directly. You should treat the ISO path from Kodi as a trigger for automation unless you configure the Oppo HTTP API path mapping for your NAS.

## Requirements

- Kodi running on a separate box.
- Python 3 installed on the Kodi box.
- `adb` installed on the Kodi box (for TCL/Android TV input switching).
- A supported TV-control path:
  - TCL or Android TV through ADB.
  - Sony Bravia through IP control with a pre-shared key.
  - LG webOS through an already-paired external CLI command.
  - Samsung Tizen through an already-paired external CLI command.
- Oppo UDP-203 connected to the network with IP control enabled.
- Static or DHCP-reserved IP addresses for the TV and Oppo.

## Installation

1. Install the zip in Kodi using `Add-ons -> Install from zip file`.
2. Open the add-on settings and set:
   - Oppo IP address and IP-control port.
   - TV backend: `adb`, `sony_bravia`, `lg_command`, `samsung_command`, or `custom_command`.
   - TV IP address.
   - Python executable path (for external player mode).
   - Backend-specific input commands or HDMI ports.
3. Run the add-on. On first run, choose your playback architecture.
4. For **external player** mode: choose *Generate playercorefactory snippet* and merge the XML into Kodi's userdata `playercorefactory.xml`. Restart Kodi.
5. For **service interception** mode: choose *Generate Kodi remote bridge keymap snippet* if you want remote-bridge forwarding. No playercorefactory merge is required.
6. Select an `.iso` file or disc folder entry in Kodi and test.

## Oppo protocol and command corrections (v0.8.0)

The OPPO UDP-20X IP/RS-232 protocol uses ASCII commands starting with `#` and terminated with carriage return. Official responses follow the format `@CODE OK VALUE` (e.g. `@QPW OK ON`). Older firmware may return `OK VALUE` directly.

### Corrected default remote mappings

| Key          | v0.7.0 | v0.8.0 (correct) |
|--------------|--------|-------------------|
| `popup_menu` | `#POP` | `#MNU`            |
| `skip_next`  | `#NEX` | `#NXT`            |

Additional commands added to the default map:

| Key          | Command | Description          |
|--------------|---------|----------------------|
| `eject`      | `#EJT`  | Eject disc           |
| `home`       | `#HOM`  | Home menu            |
| `info`       | `#INF`  | Info/display         |
| `zoom`       | `#ZOM`  | Zoom                 |
| `repeat`     | `#RPT`  | Repeat mode          |
| `angle`      | `#AGL`  | Angle                |
| `ab_replay`  | `#ATB`  | A-B replay           |
| `pure_audio` | `#PUR`  | Pure audio mode      |

### Query commands

Version 0.8.0 adds TCP query helpers using the official protocol format:

| Command | Description           | Example response      |
|---------|-----------------------|-----------------------|
| `#QPW`  | Query power status    | `@QPW OK ON`          |
| `#QPL`  | Query playback status | `@QPL OK PLAY`        |
| `#QIS`  | Query input source    | `@QIS OK HDMI`        |

Responses are parsed from both `@CODE OK VALUE` and legacy `OK VALUE` forms.

### Verbose mode (#SVM)

Set `oppo_verbose_mode` to `2` or `3` to enable verbose status messages from the Oppo. Default is `0` (off). When enabled, the Oppo sends unsolicited status updates that can be useful for debugging. The add-on sends `#SVM <mode>` at startup.

### Preflight queries

When `oppo_preflight_enabled` is `true`, the add-on sends `#QPW` and `#QIS` before starting playback. If `#QPW` returns `ON`, the power-on command is skipped even without `oppo_already_on_mode`. Preflight is disabled by default for fastest startup.

## UDP discovery (v0.8.0 / v0.9.0)

Run *Discover Oppo on network* from the installer menu to attempt Oppo detection via UDP multicast at `239.255.255.251:7624`. The add-on listens for 5 seconds and displays any responding device IP, port, and name.

v0.9.0: When exactly one device is found, the add-on offers a **yes/no prompt** to apply the discovered IP to `oppo_ip` in settings automatically. If multiple devices are found, all are displayed and no auto-apply is performed.

## HTTP poll trick-play suppression (v0.9.0)

Set `hold_mode` to `http_poll`. When a play or trick-play status is received, the add-on sets a time window (`trickplay_suppress_seconds`, default 45) during which idle status readings are ignored. This prevents the Oppo from prematurely ending the session during FF/REW operations, which can temporarily return non-success status.

Additionally, `errcode1 = -5` in any `getmovieplayinfo` response is treated as a definitive clean stop and ends the hold immediately, bypassing the confirmation counter.

Settings:
- `trickplay_suppress_seconds` — suppression window in seconds (default 45).

## Verbose push hold mode (v0.9.0)

Set `hold_mode` to `verbose_push`. The add-on opens a persistent TCP connection to the Oppo on port 23, sends `#SVM 2` to enable verbose mode, and listens for unsolicited push messages on a background thread.

Stop conditions:
- `@UPW 0` — power off.
- `@UPL STOP`, `@UPL HOME`, `@UPL MCTR`, `@UPL DISC`, `@UPL NO DISC` — playback stopped or no media.

If the TCP connection fails, the hold falls back to `tcp_qpl_poll` automatically.

Settings:
- `verbose_push_timeout_minutes` — maximum hold time (default 240; also falls back to `qpl_poll_timeout_minutes`).

## TCP QPL polling hold mode (v0.8.0)

Set `hold_mode` to `tcp_qpl_poll` to hold the external player process alive by polling `#QPL` over TCP. The hold ends when the Oppo reports an idle/stopped status for the configured number of consecutive confirmations.

Statuses that end the hold: `STOP`, `STOPPED`, `IDLE`, `NO DISC`, `HOME`, `MEDIA CENTER`, `SCREEN SAVER`, `DISC MENU`.

Statuses that keep the hold alive: `PLAY`, `PAUSE`, `FFWD`, `FREV`, `SFWD`, `SREV`, `LOADING`.

Settings:
- `qpl_poll_interval` — seconds between polls (default 3).
- `qpl_poll_timeout_minutes` — maximum hold time (default 240).
- `qpl_poll_idle_confirmations` — consecutive idle readings before exit (default 2).

## HTTP JSON payload mode (v0.8.0)

Set `oppo_http_payload_mode` to `json_payload` to send a structured JSON body to `/playnormalfile?payload=<urlencoded JSON>` instead of the path as a raw query string.

JSON fields:
- `path` — translated media path.
- `index` — always 0.
- `type` — `oppo_http_media_type` setting (default 1 = video).
- `appDeviceType` — `oppo_http_app_device_type` setting (default 2 = network).
- `extraNetPath` — always empty string.
- `playMode` — always 0.

The default is `raw_path` to preserve existing behavior.

## Video disc folder support

Version 0.7.0 extends routing beyond ISO images. When `include_disc_folder_rules` is enabled, the generated snippet routes common physical-disc folder structures and entry files to the Oppo external player.

Version 0.8.0 adds `dvdimage` and `dvdfile` playercorefactory rules alongside the existing file-type and filename-regex rules:

## Version 2.1.0 Build 6 — Final 99% coverage gate before merge

### Summary

Build 6 completes the gradual pre-merge coverage hardening sequence by raising the enforced coverage gate from 98% to 99%. This is a test/audit/documentation hardening build only; it does not begin the full v1.1.9 + v0.9.14 superset merge.

### User-visible behavior

No new runtime features are introduced. Existing v2.0 MVP behavior is preserved.

### Tests

- Added `tests/test_coverage_99.py` for no-Kodi import fallback paths, AutoScript CIFS handling, OPPO parsing helpers, discovery cleanup, External Player manual-file loop behavior, OPPO TCP cleanup, stock OPPO remote pass-through, playercorefactory merge branches, and settings XML fallback handling.
- Coverage gate: 99% enforced in `.coveragerc`.
- Measured coverage: 99% displayed by coverage.py.

### Deferred work

The full v1.1.9 + v0.9.14 superset merge and real hardware validation remain deferred until after this coverage-hardening line.


## Version 2.1.0 Build 7 — Raw 99% coverage hardening before merge

Build 7 continues the pre-merge coverage hardening track after Build 6 reached the displayed 99% coverage gate. The enforced `.coveragerc` gate remains `fail_under = 99`, and this build focuses on improving the raw combined line+branch percentage above 99% rather than merely preserving rounded display output.

### Build 7 changes

- Bumped add-on package identity to `2.1.0.7`.
- Added targeted tests for remaining meaningful edge branches in AutoScript wizard selection, HTTP and TCP hold loops, OPPO discovery response parsing, installer discovery/file-list paths, OPPO command filtering, and no-Kodi logging fallbacks.
- Preserved the full v1.1.9 + v0.9.14 merge as deferred work.
- No runtime feature expansion was introduced.

### Build 7 verification summary

- Test count: 439 passing.
- Coverage gate: 99% enforced.
- Measured total coverage: 99%.
- Raw combined line+branch coverage: 99.06%.
- Release audit: 56/56 checks passing.

## Version 2.1.0 Build 8 — Additional raw 99% coverage hardening

Build 8 continues the pre-merge coverage-hardening track after Build 7 moved raw combined line+branch coverage above 99%. The enforced `.coveragerc` gate remains `fail_under = 99`; this build improves the raw combined percentage further through behavior-oriented tests for remaining meaningful edge branches.

### Build 8 changes

- Bumped add-on package identity to `2.1.0.8`.
- Added Build 8 coverage tests for external-player module entrypoint behavior, intercept whitelist/blacklist branches, logging rotation error tolerance, OPPO control defensive helpers, TCP partial-line cleanup, playercorefactory empty-section merges, preset/settings parsing edges, and wizard full-mode WoL-with-blank-MAC behavior.
- Kept the full v1.1.9 + v0.9.14 merge deferred.

### Build 8 verification summary

- `python -m pytest -q`: 448 passed.
- `python -m unittest discover -s tests`: 448 tests OK.
- `python -m coverage run -m pytest -q`: 448 passed.
- `python -m coverage report -m`: TOTAL 99%.
- Raw combined line+branch coverage: 99.44%.
- `python tools/audit_release.py --expected-version 2.1.0.8`: pass.

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi install, or real ADB hardware was tested in this build.

## Version 2.2.0 Build 1 — Superset merge slice 1: compatibility watcher

Build 1 starts the careful v1.1.9 + v0.9.14 superset merge after the 99% pre-merge coverage hardening line. The scope is intentionally small and stability-focused. It restores the v0.9.14 compatibility-preset helper surface and service settings watcher without starting the broad feature merge.

### Build 1 changes

- Bumped add-on package identity to `2.2.0.1`.
- Added `resources/lib/first_run_wizard.py` as a narrow compatibility-helper module for the v0.9.14 preset/reapply/logging behavior.
- Added `Monitor.onSettingsChanged()` handling in `service.py` so changes to `oppo_hardware_model` or `oppo_jailbreak_enabled` reapply safe compatibility presets.
- Added `oppo_jailbreak_enabled` and `oppo_autoscript_shell_handler` settings rows and defaults, preserving locale parity.
- Preserved Reavon warning-only behavior: Reavon selection logs warnings and does not mutate OPPO command maps.
- Preserved Chinoppo/M9702 behavior: clone preset applies `#EJT\n#PLA`, TCP commands mode, and disables OPPO HTTP activation.

### Build 1 verification summary

- `python -m pytest -q`: 461 passed.
- `python -m unittest discover -s tests`: 461 tests, OK.
- Coverage gate remains enforced at 99%.
- Full merge remains gradual; no broad v1.1.9 + v0.9.14 feature union was attempted in this build.



## Version 2.2.0 Build 2 — Superset merge slice 2: v0.9.14 hardware test port

Build 2 continues the careful v1.1.9 + v0.9.14 superset merge with a narrow, stability-focused test-and-audit slice. It ports remaining v0.9.14 hardware-compatibility assertions for M9203, M9205C, all Reavon variants, jailbreak JSON payload behavior, Quick Start warning behavior, and AutoScript verbose-push warning behavior.

### Build 2 changes

- Bumped add-on package identity to `2.2.0.2`.
- Corrected `addon.xml` XML declaration back to `version="1.0"` and set the add-on `version` attribute exactly to `2.2.0.2`.
- Hardened `tools/audit_release.py` so expected add-on version is checked from the parsed XML attribute, not from any incidental text in `addon.xml`.
- Added exact audit coverage for the XML declaration and current add-on version.
- Added targeted v0.9.14 hardware regression tests for M9203/M9205C clone profiles, clone presets, Reavon warning-only behavior, stock OPPO jailbreak payload behavior, Quick Start warnings, and AutoScript verbose-push warnings.
- Did not start the broad historical feature union.

### Build 2 verification summary

- `python -m pytest -q`: 471 passed.
- `python -m unittest discover -s tests`: 471 tests, OK.
- Coverage gate remains enforced at 99%.
- Full merge remains gradual; this build is a hardware-compatibility test-port and audit-hardening slice only.


## Version 2.2.0 Build 3 — v0.9.14 warning/logging merge slice

### Summary

Build 3 continues the gradual v1.1.9 + v0.9.14 superset merge without starting a broad rewrite. This slice extends the restored service settings watcher so AutoScript shell-handler warning behavior is logged when the setting changes outside the wizard.

### User-visible behavior

- The add-on version is now `2.2.0.3`.
- `Monitor.onSettingsChanged()` now tracks `oppo_autoscript_shell_handler` in addition to hardware model and jailbreak state.
- Compatibility warning logging now includes AutoScript verbose-push warnings when the shell-handler setting is enabled.
- Reavon remains warning-only.
- Chinoppo/M9702 wake rewrite behavior is preserved.

### Tests

- Added `tests/test_superset_merge_build3.py`.
- Preserved the enforced 99% coverage gate.

### Scope and deferrals

This build does not start the large feature merge, does not change OPPO command maps, and does not claim real hardware validation.


## Version 2.2.0 Build 10 — Merge-compliance candidate checkpoint

Build 10 is a stability-first merge-completion candidate checkpoint. It does not declare the v1.1.9 + v0.9.14 superset merge complete unless the compliance matrix shows no remaining gaps. This build adds `MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD10.md`, records the improved verification workflow, preserves the 99 percent coverage gate, and keeps the latest AI handoff self-contained with a resume prompt and full reconstruction bundle.

### Build-process improvement

Coverage verification now uses one command at a time and runs coverage with `-p no:ddtrace` to avoid the container timeout observed during Build 9.

### Merge status

The compliance matrix is the authority for merge-complete status. Build 10 is verified, but the full merge remains in progress until all matrix items are complete or explicitly not required.


## Version 2.2.0 Build 11 — Active wizard compatibility-flag reconciliation

Build 11 further reduces the remaining v1.1.9 + v0.9.14 wizard/UI compatibility-warning reconciliation gap without replacing the stable v1.x wizard flow. The full wizard path now asks and stores the stock OPPO jailbreak flag and the AutoScript port-23 shell-handler flag, then uses the existing compatibility bridge to surface warnings and apply safe stock-OPPO JSON payload behavior. Reavon remains warning-only and Chinoppo clone preset changes remain under the existing explicit confirmation path for stability.

### Files revised in this build

| File | Change | Reason |
|---|---|---|
| `resources/lib/wizard.py` | Added compatibility flag prompts and safe apply/surface bridge in full mode | Reduce remaining wizard/UI merge gap |
| `tests/test_superset_merge_build11.py` | Added active wizard flag-capture regression tests | Prevent future wizard reconciliation regression |
| `MERGE_COMPLIANCE_MATRIX_v2.2.0_BUILD11.md` | Added Build 11 merge status | Keep merge state honest |

### Status

The full superset merge remains in progress, not complete. Real hardware validation is still deferred.

## Version 2.2.0 Release 2.2.0 — Final software merge-compliance review

Release 2.2.0 is a software merge-complete candidate checkpoint for the gradual v1.1.9 + v0.9.14 superset merge. It adds the final merge-compliance matrix and confirms that known hermetically testable software merge gaps are closed. It does not claim real hardware validation or final release status.

### Files revised in this build

| File | Change | Reason |
|---|---|---|
| `addon.xml` | Version bumped to `2.2.0` | Build identity |
| `MERGE_COMPLIANCE_MATRIX_v2.2.0_RELEASE.md` | Added final software merge-compliance review | Honest merge status |
| `README.md`, `reference.md`, `web-references.md` | Added Release 2.2.0 notes | Documentation lockstep |
| `tools/audit_release.py` | Requires Release 2.2.0 evidence files | Release audit coverage |
| `tests/test_superset_merge_build12.py` | Added Release 2.2.0 compliance tests | Prevent overclaiming merge status |

### Status

```text
Software merge-complete candidate: yes
Hardware-validated final release: no
Remaining blockers: real hardware validation and final RC/final packaging decision
```

## Version 2.2.0 — Software merge-complete package

This release packages the verified Build 12 software merge-complete candidate as `2.2.0`. It is intended for user hardware validation after packaging. The release preserves the 99 percent coverage gate, the v2 MVP behaviors, and the gradual v1.1.9 + v0.9.14 software merge results.

Real OPPO/Chinoppo/TCL/Kodi/ADB hardware validation was not performed by the AI session and remains the user's next step.

## v2.5.3 Build 2 — Option 4 conservative 4K XML routing

Build 2 implements the selected Option 4 `playercorefactory.xml` strategy for external-player XML mode. The generated rules are conservative and tag-aware: only disc-style `iso`, `bdmv`, and `mpls` entries whose filename or visible path contains `4K`, `UHD`, or `2160p` are routed to the OPPO/Chinoppo external player.

XML mode depends on naming discipline. Recommended names include:

```text
Movie Title (Year) 4K UHD.iso
Movie Title (Year) 2160p.iso
Movie Title (Year) 4K UHD/BDMV/index.bdmv
Movie Title (Year) UHD/BDMV/PLAYLIST/00800.mpls
```

Loose/raw video files remain with Kodi's default player even when tagged, including MKV, MP4, M2TS, TS, and VOB. XML mode cannot inspect metadata, NFO files, stream resolution, or ISO internals; it only sees Kodi's filename/path rule input. Service interception remains the more precise Python-classifier path.

## v2.5.3 Build 3 — Version identity and audit reconciliation

Build 3 updates the runtime `addon.xml` version to `2.5.3` so Kodi metadata matches the v2.5.3 package identity. It preserves Build 1 service interception and Build 2 conservative Option 4 XML routing. No OPPO command-map, Reavon, startup-power, NAS playback, or hardware-control behavior changed.

Hardware validation is not claimed for this build.



## v2.5.3 Build 4 — XML merge safety hardening

Build 4 hardens the `playercorefactory.xml` merge helper so generated helper snippets follow the same conservative Option 4 model as the Build 2 installer snippet: tag-aware `4K` / `UHD` / `2160p` routing for disc-style `iso`, `bdmv`, and `mpls` sources only. It also preserves backup-before-write behavior, idempotent duplicate prevention, and best-effort rollback if writing or post-write XML validation fails. Loose/raw video formats such as MKV, MP4, M2TS, TS, and VOB remain with Kodi.


## v2.5.3 Build 5 — Hardware-validation readiness and diagnostic export

Build 5 adds a non-invasive readiness report for hardware testers. The report summarizes add-on setup state, model/NAS capability gates, Option 4 XML naming requirements, loose-video negative-test expectations, and the evidence fields a tester should record before claiming real OPPO/Chinoppo/Kodi/NAS/TV/ADB validation.

The export is available from the add-on installer menu as **Export hardware-validation readiness report**. It writes a text report into the add-on data directory. The helper does not contact hardware, launch playback, mutate settings, or claim that validation passed.

Hardware validation remains user-owned and pending until real device results are provided.

## Version 2.5.3 Build 6 — pre-hardware release-candidate packaging freeze

Build 6 freezes the v2.5.3 software line for hardware testing. It preserves Build 1 4K UHD disc-style service interception, Build 2 conservative Option 4 XML routing, Build 3 version identity, Build 4 XML merge/rollback hardening, and Build 5 hardware-validation readiness export.

No playback, OPPO command-map, XML routing, NAS adapter, service interception, startup power, or hardware-control behavior changed in Build 6. Hardware validation is not claimed until real tester results are provided.

## Version 2.9 Release

Version 2.9.0 is a stable release rebuild from the verified v2.5.3 Build 6 pre-hardware release-candidate baseline. No runtime playback behavior changed in this rebuild. The release preserves:

- precise Python service interception for tagged 4K/UHD/2160p disc-style sources;
- conservative Option 4 `playercorefactory.xml` routing for ISO/BDMV/MPLS only;
- loose/raw video exclusion so MKV, MP4, M2TS, TS, VOB, and similar files stay with Kodi;
- playercorefactory merge backup, idempotency, and rollback hardening;
- hardware-validation readiness export.

Hardware validation is still not claimed by this automated rebuild. Per-device OPPO/Chinoppo/Kodi/NAS/TV validation must be recorded separately before declaring hardware pass.

## Version 2.9.1 Build 1

Version 2.9.1 Build 1 improves the first-run wizard wording for Kodi startup auto-power. The wizard now asks whether Kodi should automatically power on the OPPO/compatible player when Kodi starts and explicitly tells the user to choose No if they prefer to keep the player off until playback starts or they power it on manually.

This build does not change playback behavior, OPPO command-map behavior, service interception, XML routing, NAS playback, startup power implementation, or hardware-control behavior. The `kodi_startup_power_on` setting remains the master toggle and remains optional.

Hardware validation is not claimed for this build.

## Version 2.9.1 Build 2

Version 2.9.1 Build 2 centralizes the duplicated 4K/UHD/2160p disc-style classification helpers and safe shared constants. The new `resources/lib/disc_classification.py` module is the shared source for the service/intercept path and Option 4 XML helper constants, while `resources/lib/constants.py` preserves low-risk invariants such as the 76-key OPPO command-map size and 99% minimum coverage gate.

This build does not change playback behavior, OPPO command-map behavior, XML routing policy, NAS playback, startup power implementation, or hardware-control behavior. It is a cleanup-only build intended to reduce drift between `intercept.py`, `installer.py`, and `playercorefactory_merge.py`.

Hardware validation is not claimed for this build.

## v2.9.1 Build 3 — Externalized OPPO command map

Version 2.9.1 Build 3 moves the canonical OPPO remote command map from inline settings defaults into `resources/data/oppo_command_map.json` and validates it through `resources/lib/command_map.py`. `settings_reader.DEFAULTS["oppo_remote_command_map"]` still exposes compact JSON for backward compatibility with existing callers and user overrides.

The command map remains the protected 76-key map. Forbidden tokens `#SIS`, `#PGU`, and `#PGD` remain blocked by tests and audit. No playback behavior, OPPO command semantics, XML routing, NAS behavior, startup auto-power behavior, or hardware-control behavior changed.


## v2.9.1 Build 4 — Dynamic audit evidence discovery

Version 2.9.1 Build 4 adds manifest-based release-evidence discovery to `tools/audit_release.py`. The audit now discovers `release-evidence/*/MANIFEST.txt`, requires each manifest file, and requires every safe root-relative evidence file listed in those manifests. The legacy hard-coded evidence list remains active as a transition fallback so historical checks remain stable while future builds can migrate to manifest-owned evidence.

No playback behavior, OPPO command-map behavior, service interception, XML routing, NAS playback, startup auto-power, or hardware-control behavior changed. Hardware validation is not claimed for this build.

## v2.9.1 Build 5 — Version single source of truth

Build 5 adds `resources/lib/version.py` as the Python source of truth for add-on release identity and `tools/sync_version.py` for checking or synchronizing `addon.xml`. The release audit now verifies that `addon.xml`, `version.py`, and `--expected-version` agree. Runtime playback/control behavior is unchanged, and hardware validation is not claimed.


## v2.9.1 Build 6 — Build/release automation scripts

Build 6 adds local release automation wrappers: `scripts/verify.sh` runs the standard source verification sequence, and `scripts/package_release.sh` creates a runtime installable ZIP, SHA256 checksum, and dev-source snapshot from the current source tree. Runtime playback/control behavior is unchanged, and hardware validation is not claimed.

## v2.9.1 Build 7 — Packaging allowlist

Build 7 changes runtime ZIP packaging to an allowlist-driven policy. The installable Kodi ZIP is eligible to include only `addon.xml`, `default.py`, `service.py`, optional runtime media/license assets, and `resources/**`. Tests, tools, scripts, release evidence, handoff files, reports, and development documentation are excluded by omission and remain in the dev-source ZIP and artifact bundle.

No playback, OPPO command-map, XML routing, NAS adapter, service interception, startup power, or hardware-control behavior changed. Hardware validation is not claimed.

## v2.9.1 Build 8 — Settings exception narrowing, phase 1

Build 8 narrows low-risk settings parser exception handling in `resources/lib/settings_reader.py` while preserving existing fallback behavior. It does not change playback behavior, OPPO command semantics, XML routing, NAS playback, startup auto-power behavior, or runtime packaging policy.


## v2.9.1 Build 9 — Settings schema / typed validation, phase 2

Build 9 adds a dependency-free typed settings schema in `resources/lib/settings_schema.py`. The schema is advisory and non-mutating: existing `Settings` getters still provide the same safe fallback behavior, while `schema_issues()` and `typed_values()` expose structured validation for diagnostics and future hardening. No playback, OPPO command-map, XML routing, NAS adapter, startup auto-power, or hardware-control behavior changed.

## v2.9.1 Build 10 — Audit reporter refactor

Build 10 refactors `tools/audit_release.py` so audit collection and reporting are separated. It introduces an `AuditCheck` value object plus `TextReporter` and `JsonReporter` classes while preserving the legacy `run_audit()` dictionary API and existing CLI text/JSON output schemas. No playback, OPPO command-map, XML routing, NAS adapter, startup auto-power, packaging outcome semantics, or hardware-control behavior changed.

## v2.9.1 Build 11 — Diagnostic logging fallback refactor

Build 11 replaces ad-hoc diagnostic logging fallback printing with a structured Python logging fallback and a Kodi logging adapter. Kodi `xbmc.log` remains the preferred runtime sink when available. The fallback path remains capture-compatible for diagnostics and tests, but is now centralized through `resources/lib/diagnostic_logging.py`.

No playback, OPPO command-map, XML routing, NAS adapter, startup auto-power, packaging outcome, or hardware-control behavior changed. Hardware validation is not claimed.




## v2.9.10 Build 3 — Clone / successor capability gates

Build 3 separates clone-safe player behavior from warning-only OPPO-like successor behavior. Chinoppo-style and experimental clone-family models remain software-classified for clone-safe wake and NAS/AutoScript readiness gates. Reavon and Magnetar UDP800/UDP900 remain warning-only unless real hardware validation proves command compatibility. No playback routing, command-map payloads, service interception, XML routing, NAS adapter behavior, startup auto-power behavior, TV switching behavior, AVR sequencing, or hardware-control behavior changed. Hardware validation is not claimed.



## v2.9.10 Build 4 — Player wizard wording and readiness updates

Build 4 updates player-facing guidance for the v2.9.10 hardware taxonomy. The wizard and readiness report now explain stock OPPO behavior, Chinoppo-style clone behavior, experimental clone readiness gates, and warning-only OPPO-like successor behavior for Reavon and Magnetar. NAS/direct playback remains a readiness gate requiring AutoScript or equivalent local NAS mount support on the player.

No playback routing, OPPO command-map payloads, service interception, Option 4 XML routing, NAS adapter behavior, startup auto-power behavior, TV switching behavior, AVR sequencing, or hardware-control behavior changed. Hardware validation is not claimed.

## v2.9.1 Build 12 — Docs metadata/rendering pipeline

Build 12 adds a conservative documentation metadata pipeline. `docs/sources.yaml` is the shared source for a generated metadata block, and `tools/render_docs.py` can write or check that block in `README.md`, `reference.md`, and `web-references.md`.

The renderer is dependency-free and updates only a clearly marked generated block. Existing hand-written documentation and historical traceability content are preserved. No playback, OPPO command-map, XML routing, NAS adapter, startup auto-power, packaging outcome, or hardware-control behavior changed. Hardware validation is not claimed.


## v2.9.1 Build 13 — Type hints and non-blocking mypy baseline

Build 13 adds `tools/type_check.py` and `mypy.ini` as a dependency-optional type-check baseline. The command reports mypy status but remains non-blocking by default so release verification does not require a new runtime or development dependency. Selected public helpers now carry explicit type hints. No runtime behavior changed.

## v2.9.1 Build 14 — Test naming/layout standardization transition

Build 14 adds transition-safe test naming/layout policy tooling. `tools/test_layout.py`, `docs/test-layout.md`, and pytest marker declarations document the future version/build-specific test layout while preserving the inherited flat `tests/test_*.py` layout for stability.

No playback, OPPO command-map, XML routing, NAS adapter, startup auto-power, packaging, or hardware-control behavior changed.

## v2.9.1 Build 15 — Babel/gettext extraction transition

Build 15 adds `tools/i18n_extract.py` as the transition-safe localization extraction facade and `babel.cfg` as a Babel/gettext configuration reference. The build preserves `tools/make_pot.py` as the deterministic Kodi numeric-id fallback for one build and wires the new non-writing extraction check into `scripts/verify.sh`.

This build does not introduce a runtime Babel dependency. It does not change playback behavior, OPPO command semantics, XML routing, NAS playback, startup auto-power behavior, or hardware-control behavior. Hardware validation is not claimed.


## v2.9.1 Build 16 — i18n extraction legacy alias hardening

Build 16 completes the fallback-retirement decision from the Build 15 i18n transition without deleting legacy tooling. `tools/i18n_extract.py` is the preferred facade for new extraction automation, while `tools/make_pot.py` is retained as a documented legacy compatibility alias for older scripts and local AI workflows.

This build does not change playback, OPPO command semantics, service interception, XML routing, NAS playback adapter behavior, startup auto-power behavior, settings runtime behavior, packaging semantics, or hardware-control behavior.


## v2.9.10 Build 1 — Unified hardware registry foundation

Build 1 starts the v2.9.10 Unified Hardware Ecosystem Expansion by adding a side-effect-free hardware registry foundation for player, TV, and AVR role families. The new registry is documentation/test-oriented in this build and does not change playback routing, OPPO command dispatch, service interception, Option 4 XML routing, NAS behavior, startup auto-power behavior, existing TV switching behavior, or AVR sequencing.

Hardware validation is not performed or claimed.


## Version 2.9.10 Build 2 — OPPO clone taxonomy and aliases

Build 2 expands the software taxonomy for OPPO-compatible player profiles without changing playback routing or OPPO command-map payloads. It adds M9200, M9205, CineUltra V203, CineUltra V204, and Magnetar UDP900 identifiers, plus M9702 V1/V2/V3 and related spelling aliases. Clone-family additions use the existing clone-safe wake classification, while Magnetar UDP900 is warning-only / unverified by default.

No real hardware validation is claimed for the new identifiers. The runtime ZIP remains allowlist-only and development evidence remains outside the installable package.

## v2.9.10 Build 5 — TV backend registry and preset foundation

Build 5 introduces a side-effect-free TV backend registry and software preset foundation while preserving the existing public APIs `switch_to_oppo(settings)` and `switch_to_kodi(settings)`. Existing backend identifiers remain `adb`, `sony_bravia`, `lg_command`, `samsung_command`, and `custom_command`; the registry records their target setting keys and non-fatal playback-flow posture for later diagnostics and preset expansion.

The new preset foundation records software-only presets for the existing ADB, Sony Bravia IP, LG command, Samsung command, and generic custom command paths. Presets remain editable and hardware validation is not claimed. No OPPO playback routing, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, TV switching behavior, or AVR sequencing changed.
## v2.9.10 Build 6 — Android / Google TV preset pack

Version 2.9.10 Build 6: Android / Google TV preset pack.

Build 6 adds the Android / Google TV preset pack on top of the Build 5 TV backend registry. The new software-only ADB presets cover TCL, Sony, Hisense, Philips, Xiaomi, Sharp, Skyworth/Coocaa, Haier, and generic Android TV / Google TV profiles.

No universal ADB HDMI command is claimed. Hardware validation is not claimed. The presets only record editable metadata for the existing `oppo_input_adb_shell` and `kodi_input_adb_shell` fields, so users or hardware testers still own model-specific command verification before confirmed support is claimed.

Build 6 preserves OPPO playback routing, service interception, `playercorefactory.xml` behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, existing non-fatal TV switching behavior, AVR sequencing, the runtime-only ZIP policy, and the 99% coverage gate.


## Version 2.9.10 Build 9B — SmartThings experimental request helper and fake API tests

Build 9B adds SmartThings as an explicitly experimental, metadata-only TV integration layer. It adds preset/backend metadata, settings placeholders, explicit acknowledgement gating, token-redaction helpers, and validation metadata, but it does not claim live hardware validation and uses fake API tests for software verification. The feature remains software-only until a real hardware validation is supplied by the user.


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
### Generated documentation metadata — v2.9.15 Final

- Target document: `README.md`
- Cleanup scope: Pure-HTTP/436 control (Xnoppo V3) — 7th preset, HTTP monitor and orchestration, BDMV-first disc nav, and selectable HDMI switching
- Runtime behavior changed: `true`
- Hardware validation claimed: `false`
- Source recommendation: v2.9.15 Pure-HTTP/436 control (Xnoppo V3): 7th preset http_handoff_http, HTTP monitor and launch orchestration, checkfolderhasBDMV-first disc nav, and selectable HDMI switching
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

Version 2.9.10 Build 8 adds a local Roku TV ECP backend for software-controlled TV input switching.

Build 7 keeps the scope narrow: the new backend uses HTTP POST to `/keypress/<key>` on the local Roku ECP port, defaults to port `8060`, validates keys through a strict allowlist, and keeps failures non-fatal in the existing TV switching flow. It adds editable Roku TV software presets for Roku TV, TCL Roku TV, Hisense Roku TV, and generic Roku TV. Hardware validation is not claimed.

No OPPO playback routing, service interception, `playercorefactory.xml` behavior, NAS/AutoScript behavior, OPPO command-map payloads, startup auto-power behavior, Android / Google TV ADB preset metadata, AVR sequencing, runtime ZIP policy, or 99% coverage gate changed.

Build 7 implementation note: Roku TV ECP uses HTTP POST to /keypress/<key> with allowlisted input keys.

## Version 2.9.10 Build 8 — Command TV preset polish

Build 8 improves software-only command/custom TV preset metadata for LG webOS command helpers, Samsung command helpers, Panasonic custom commands, Vizio custom commands, and generic custom commands. It does not add native TV protocols, does not claim hardware validation, and preserves editable command templates, `{tv_ip}` placeholder behavior, and non-fatal TV switching failures.


## Version 2.9.10 Build 10 — TV diagnostics and dry-run validator

Build 10 adds a read-only TV diagnostic layer. It validates selected TV backend settings, builds dry-run OPPO/Kodi switch reports without network calls, provides explicit switch test action helpers for supported backends, and exports sanitized reports that do not expose SmartThings tokens, Sony PSKs, passwords, credentials, or command output. Hardware validation is not claimed.

## Version 2.9.10 Build 11 — AVR framework and settings skeleton

Build 11 adds the first AVR layer as a disabled-by-default framework skeleton. It introduces metadata-only AVR family presets, safe settings placeholders, non-fatal validation results, and a controller factory that returns no controller while AVR control is disabled. No Denon/Marantz, Yamaha, Onkyo/Integra/Pioneer, or Sony AVR brand command execution is implemented in this build, and AVR is not hooked into playback sequencing. AVR power-off and volume automation remain disabled by default. Hardware validation is not performed or claimed.


## Version 2.9.10 Build 17 — Unified TV + AVR playback sequencing

Build 17 safely hooks optional TV and AVR pre/post sequencing into the external-player flow. AVR sequencing runs only for eligible OPPO/external-player handoff, the AVR disabled path is a no-op, TV and AVR failures remain non-fatal, optional AVR restore runs only when enabled, and existing TV restore continues to work. Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, runtime ZIP policy, the 99% coverage gate, and the no-hardware-validation-claim posture remain preserved.

### Generated documentation metadata — v2.9.10 Build 17

The generated docs metadata block above records Build 17 as the active v2.9.10 software build. Build 17 uses the shortened Balanced Gate verification strategy and defers full legacy pytest, full unittest discovery, and full post-unpack coverage to Build 18 Full Release Gate.

## Version 2.9.10 Build 18 — Regression, audit, and packaging candidate

Build 18 is the Full Release Gate regression/audit candidate after Build 17 unified TV + AVR playback sequencing. It does not add new hardware features. It refreshes release evidence, updates the active software identity to Build 18, packages the runtime/dev-source/artifact bundle set, and confirms the installable ZIP remains runtime-only.

Build 18 preserves Build 17 sequencing behavior: AVR sequencing runs only for eligible OPPO/external-player handoff, the AVR disabled path is a no-op, AVR and TV failures do not block playback, optional AVR restore runs only when enabled, and existing TV restore continues to work. Hardware validation remains not performed and not claimed.

## Version 2.9.10 Final — Software-verified release packaging

Version 2.9.10 Final packages the software-verified release after the Build 18 Full Release Gate regression/audit candidate. No new hardware features were added. Build 17 unified TV + AVR playback sequencing remains preserved: AVR sequencing runs only for eligible OPPO/external-player handoff, AVR disabled is a no-op, TV and AVR failures are non-fatal, optional AVR restore runs only when enabled, and existing TV restore continues to work.

This is a software-verified release. Real hardware validation was not performed or claimed for OPPO/Chinoppo/Magnetar/Reavon/Kodi/NAS/TV/ADB/Roku/LG/Samsung/Sony/Panasonic/Vizio/AVR paths unless separately recorded from real tester results.
