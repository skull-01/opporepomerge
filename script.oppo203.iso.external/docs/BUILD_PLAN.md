# Build plan

**Audience:** any AI agent or human contributor planning the next slice of
work. This file is the **map** — it records the strategic direction the
operator has set, the current state of both areas, and the phased roadmap for
the active initiative.

**Source of truth:** open issues at
[`gh issue list --state open`](https://github.com/skull-01/script.oppo203.iso.external/issues).
This document is regenerated on demand by the `refresh the build plan`
trigger and is allowed to lag the live state between refreshes. Phase/PR IDs
below are **planning placeholders** (`ENH-…`) until the operator files the
matching `area:configurator` / `area:addon` issues.

**Last refreshed:** 2026-06-02 (EOD #10) · **▶ ACTIVE INITIATIVE QUEUED: Pure-HTTP/436 OPPO control (PRs 1–6)** — full plan in the **Active initiative** section just below; queued as the next theme (Session A = PR1+PR2). This session shipped add-on **v2.9.14** + configurator **v0.7.0** (both stable; configurator holds the repo "Latest" badge). _Prior:_ **GUIDED-INSTALL INITIATIVE SOFTWARE-COMPLETE — all of
Phases 0–5 are built + merged to `main`; only operator Phase-C hardware validation + a configurator
release remain.** This session also built the dashboard-memory follow-on as stacked PRs #200 → #201
→ #202 (issues #167/#168), and confirmed the DB backlog #103/#105 was already implemented on `main`
(verify + close). **Live open backlog:** addon **#44** (tester solicitation); configurator
**#103/#105/#167/#168** (all implemented — ready for operator close); 0 unclassified.
**Phase → delivery map:** Ph0 → dissolved into decision **D-1=C** (the configurator bundles `main`
fresh at build time; no separate add-on release) · Ph1 install #170 · Ph1b NAS-path capture #174 ·
Ph2 SSH-first re-sequence #171 · Ph3 HDMI switch #172/#177/#179/#184/#188 · Ph4 OPPO self-test
#181/#185/#187/#190 · Ph5 monitor + richer status #183/#186/#189 + dashboard memory #200–#202.
_Prior refresh:_ **backend layer for Phases 3/4/5 built + merged to `main`**
(operator: "build all of Phases 3/4/5, merge as I go, finer PRs"). Foundation #174/#175 merged; then
**Phase 3.1** AVR switch ([#177](https://github.com/skull-01/script.oppo203.iso.external/pull/177), issue #176) + TV switch
([#179](https://github.com/skull-01/script.oppo203.iso.external/pull/179), issue #178); **Phase 4.1** `oppo_power`
([#181](https://github.com/skull-01/script.oppo203.iso.external/pull/181), issue #180); **Phase 5.1** add-on richer status
([#183](https://github.com/skull-01/script.oppo203.iso.external/pull/183), issue #182). **Software-verified only — hardware-pending.**
**UI layer ALSO merged** (via 3 parallel sub-agents): Phase 3.2/3.3 ([#184](https://github.com/skull-01/script.oppo203.iso.external/pull/184)/[#188](https://github.com/skull-01/script.oppo203.iso.external/pull/188)),
4.2/4.3/4.4 ([#185](https://github.com/skull-01/script.oppo203.iso.external/pull/185)/[#187](https://github.com/skull-01/script.oppo203.iso.external/pull/187)/[#190](https://github.com/skull-01/script.oppo203.iso.external/pull/190)),
5.2/5.3 ([#186](https://github.com/skull-01/script.oppo203.iso.external/pull/186)/[#189](https://github.com/skull-01/script.oppo203.iso.external/pull/189)) — issues #191–#197. **ALL of Phases 3/4/5 now on `main`**
(combined gate: `tsc` / **247 vitest** / `vite build` / `cargo` **37**); only Phase-C hardware validation remains. See `AI_RESUME_HANDOFF.md` §3b. · Prior:
2026-06-02 · added **D-4** (NAS-path observe-and-verify capture + manual fallback, **SMB/NFS only**) and **Phase 1b**. Prior:
2026-06-01 · **committed to `main`** together with the six-preset matrix norm (`AGENTS.md`) + the handoff §4 pointer.

**This file lives on `main`; feature branches should not edit it** (causes
add/add merge conflicts per the session-continuity convention).

---

## ▶ Active initiative (queued 2026-06-02): Pure-HTTP/436 OPPO control — PRs 1–6

> **Status: PLANNED — awaiting build (operator said Go-on-next-resume).** Adopts the
> Xnoppo Elite V3 / `emby-chinoppo-bridge` (MIT) pure-HTTP/436 control model into **both**
> the add-on and the configurator. Decision tree: `build/configurator_decision_tree.html`.
> Reference: `Xnoppo_Elite_V3_OPPO_HTTP_Flows_Functions_Commands.md`.

**Theme.** A literal **7th preset `http_handoff_http`** (launch + monitor + command + mount all
over HTTP) as the **new default for all installs**; a new **`http` monitor** axis
(`getglobalinfo`+`getplayingtime`) — the monitor transport (TCP vs HTTP) is the **Step-4 decision**
and flows through to the post-install process monitor (two provisions); **`checkfolderhasBDMV`-first
-with-fallback** BD navigation on **both** HTTP and TCP launch paths; **selectable confirm-gated HDMI
switching** (`play_delay_hdmi`/`av_delay_hdmi`, ISO/BDMV ≥6s); **Refresh Rate** (5s) and **Auto-Healing**
(ISO resend-once) options. **Frozen & guarded:** the 6 existing presets + their TV/AVR sequencing stay
byte-identical unless a new (default-off) option is opted into — pinned by `test_architecture_presets.py`,
`test_playback_session_modes.py`, `test_v2910_build18`, `mapping.test.ts`; OPPO TCP command map untouched.

**PRs (area: 🟦 add-on · 🟩 configurator).**

- **PR 1 — HTTP primitives (🟦 function-only, unwired) ~300 LOC · Low.** `oppo_control.py`:
  `send_remote_key_http`, `get_global_info`/`global_info_is_playing`, `get_playing_time`,
  `login_smb`/`login_nfs` + share-lists + `mount_smb`/`mount_nfs` (`lstrip("/")`, no-unmount-first),
  `check_folder_has_bdmv`, `detect_nfs`. Tests: `test_oppo_http_pure.py` (mock `urlopen`; every failure
  raises). No matrix/dispatch change.
- **PR 2 — 7th preset + `http` monitor (🟦🟩 CROSS-AREA, one PR) ~240 LOC · High.** 🟦
  `PLAYBACK_MONITOR_MODES += "http"` (`settings_reader.py:218`); `PLAYBACK_ARCHITECTURE_PRESETS +=
  "http_handoff_http"` →7 (`:219`); single cell `("http_handoff","http")` (`:237`); clamp invalid
  `(routing,"http")` (`:248/:263`); `OppoHttpPlaybackMonitor` (polls every `oppo_http_refresh_seconds`,
  fallback-safe) + `http` branch in `_dispatch_monitor` (`playback_session.py:151`). 🟩 monitor enum
  (`state.ts`), combined "Pure HTTP" pill (`step3.tsx`), `mapping.ts:220` yields `http_handoff_http`,
  shared `playback-presets.json`/`presetsdb.ts` →7. Guards both sides (==6→==7 + clamp + emits-7).
- **PR 3 — pure-HTTP orchestration: mount + HTTP command + ISO auto-heal + HTTP-path BDMV (🟦) ~260 LOC
  · High (HW).** Wire into `fast_start_http`: wake (`sendremotekey PON`+UDP) → signin →
  `getdevicelist`/`detect_nfs` → login → share-list → mount → disc-aware play (ISO `STP`+resend after
  `oppo_http_iso_autoheal_after_seconds` when `oppo_http_iso_autoheal`; **BDMV → `check_folder_has_bdmv`
  → fallback `playnormalfile`**; normal → `playnormalfile`) → confirm via `getglobalinfo`. Capability-gated
  + fallback-safe.
- **PR 4 — default flip (all installs) + process-monitor TCP/HTTP + docs (🟦🟩) ~160 LOC · High.** 🟩
  Step-4 default = Pure HTTP; process monitor honors **TCP (QPL/#SVM3) OR HTTP (getglobalinfo)** per the
  Step-4 choice, refresh `oppo_http_refresh_seconds`; refresh-rate UI. 🟦 `normalize_architecture` keeps
  legacy derivation when no preset set. Docs: D-A default → `http_handoff_http`; AGENTS norm; checklist.
- **PR 5 — selectable confirm-gated HDMI switching (🟦🟩 cross-cutting, gated) ~180 LOC · High.** 🟦 new
  `hdmi_sequencing.py` (`compute_play_delay` → ISO/BDMV `max(play_delay_hdmi,6)`; ordering helper) gated
  into the shared switch path (confirm source = active monitor; legacy = timed delay). **Default
  `immediate` = frozen.** 🟩 `hdmi_switch_mode`/`play_delay_hdmi`/`av_delay_hdmi` + UI.
- **PR 6 — TCP-path BDMV adoption (🟦🟩 frozen-routing, gated) ~140 LOC · High.** Extract PR3's disc-aware
  play helper; wire `checkfolderhasBDMV`-first-fallback into the **TCP** launch path (`fast_start`,
  `external_player.py:148`). Setting `oppo_bdmv_checkfolder` (default **on**, capability-gated +
  fallback-safe to today's `_disc_folder_root`). 🟩 BDMV toggle. Tests pin the **off path = current frozen
  behavior**.

**Dependency chain.**
```
PR1 ─┬─> PR2 ───────────────> PR4
     ├─> PR3 ──> PR6 ────────> PR4
     └──────────────────────── PR5 (independent)
```

**New settings (all 🟩 configurator-owned; the build Go is the AGENTS sign-off for new persistent keys).**

| Setting | Type | Default | Drives | PR |
|---|---|---|---|---|
| `playback_architecture_preset` (extended) | enum | derived | adds `http_handoff_http` (7th) | 2 |
| `oppo_http_refresh_seconds` | int | 5 | monitor + process-monitor poll ("Refresh Rate") | 2/4 |
| `oppo_http_iso_autoheal` | bool | true | ISO resend-once ("Auto-Healing") | 3 |
| `oppo_http_iso_autoheal_after_seconds` | int | 20 | auto-heal threshold | 3 |
| `oppo_bdmv_checkfolder` | bool | true | checkfolderhasBDMV-first (both paths) | 6 |
| `hdmi_switch_mode` | enum | immediate | selectable confirm-gated HDMI switching | 5 |
| `play_delay_hdmi` | int | 2 | pre-TV render delay (ISO/BDMV ≥6) | 5 |
| `av_delay_hdmi` | int | 0 | TV→AVR stagger | 5 |

**Risks.** Undocumented API as default-for-all → every HTTP step fallback-safe (PR3/PR6) is a merge-blocker
(stock OPPO never bricks). PR5/PR6 touch frozen sequencing/routing → gated (HDMI default-off; BDMV
fallback-safe default-on), both pin the unchanged path with regression tests. `legacy` monitor has no
start-confirmation (#113) → `after_playback_confirm` degrades to a timed delay there. **Software-verified
only** — HTTP/436 mount/monitor/command/BDMV is undocumented + firmware-dependent; PR3/PR5/PR6 real
behavior is **Phase-C, not hardware-validated**.

**Session split (one theme/session, ≤4 PRs).** Session A: PR1+PR2 (software-complete). Session B:
PR3+PR6+PR4. Session C: PR5 (independent).

---


---

## §1 Strategic direction (2026-06-01)

### Two areas, one tree

Work is split into **`area:addon`** (Kodi add-on, Python under `resources/`)
and **`area:configurator`** (Tauri 2 + React under `configurator/`). Every
issue carries one area label. See `AI_RESUME_HANDOFF.md` §1.

### Active initiative — *guided install + full setup flow*

The configurator graduates from a **config-file writer** into a **guided
installer + live monitor**: it gets SSH access to Kodi, sets up and **tests**
HDMI switching, drives an **OPPO playback self-test** (copy a test ISO →
power-cycle → mount → play → confirm via SVM3), then **installs the add-on
itself** (pre-configured from the test results) and **transforms into a
process monitor** for the whole playback chain.

**This is a two-track effort. Both the add-on and the configurator need new
builds.** The add-on's `http_handoff` / SVM3 / preset runtime already exists in
source on `main` but is **not in any Final release** (it post-dates v2.9.13),
so it must be built/released for the configurator to bundle a *working*
add-on. Later phases add real add-on *code* (configurator handshake, richer
live status).

### Configurator owns add-on configuration

Since [`#40`](https://github.com/skull-01/script.oppo203.iso.external/pull/40)
stripped the in-Kodi setup wizard, the **configurator is the single source of
truth for add-on configuration** (tracked under
[`#41`](https://github.com/skull-01/script.oppo203.iso.external/issues/41)).
The add-on stays read-mostly. This initiative extends that ownership from
*configuration* to *installation*.

### Honest signature

Release language remains **"software-verified; hardware validation not
performed / not claimed"** until a real tester reports back. Every new
automation step in this initiative (real HDMI switch, OPPO power-cycle, HTTP
play, multi-GB copy) is **unverifiable in-session** — gated by unit tests +
render guards, with operator Phase A/B/C hardware verification. Hardware
sourcing is solicited under
[`#44`](https://github.com/skull-01/script.oppo203.iso.external/issues/44).

---

## §2 Current state (2026-06-01 snapshot)

### Add-on (`area:addon`)

- **Last Final release: `v2.9.13`.** A large post-2.9.13 refactor sits on
  `main` and is **not in any Final release**: `resources/lib` reorganised into
  `kodi/` / `oppo/` / `tv/`, plus new runtime — `oppo/playback_monitor_svm3.py`,
  `kodi/playback_session.py`, `kodi/i18n.py` — and `wizard.py` / `wizard_polish.py`
  removed (72 files, +2,722 / −3,582 vs the `v2.9.13` tag).
- **`v2.9.14-experimental` cut 2026-06-01** (pre-release, tag
  `v2.9.14-experimental`) **is** a build of that post-2.9.13 `main` — i.e. the
  add-on build that *can* do `http_handoff_svm3`. It is the candidate the
  configurator would bundle (see §4 decision D-1).
- **Architecture is settings-driven, single package — no per-arch builds.**
  `playback_session.py:162,168-171` routes at runtime; the source of truth is
  the `playback_architecture_preset` setting
  (`settings_reader.py:266,273` — six presets at `:219-226`).

### Configurator (`area:configurator`)

- **At `configurator-v0.5.0`** (`src-tauri/tauri.conf.json:4`,
  `package.json` version `0.5.0`). Far past the README's stale "scaffold only"
  line: working Tier A/B/C deploy, connectivity probes, choice→preset mapping,
  debug capture, and a live dashboard.
- **Decision→preset is already correct.** `mapping.ts:155` writes
  `playback_architecture_preset = \`${routing}_${monitorMode}\``, which the
  add-on prefers (`settings_reader.py:273`). The configurator also writes the
  HTTP-path settings the add-on reads (`oppo_control.py:365-433`,
  `settings_reader.py:70-136`).
- **Does NOT install the add-on, and several control steps are simulations.**
  (`step5.tsx:167` "Sent switch-to HDMI" has no `invoke`; `test.tsx:80-143`
  test-disc copy is cosmetic — known scaffold.)

### Audit — proposed flow vs. today

| # | Proposed step | Status | Anchor / gap |
|---|---|---|---|
| 1 | SSH to Kodi **first** | 🟡 Partial | SSH = Tier A in Step 1 (`step1.tsx:153`, `ssh_test` `lib.rs:346`); not first; creds not persisted |
| 2 | TV-vs-AVR switcher choice | 🟢 Exists | topology `Step0Chain.tsx:11-59` |
| 3 | Switcher IP + set up switching | 🟡 Partial | AVR IP persisted; **TV IP never stored** (`dashboard_targets.ts`) |
| 4 | Find Kodi + OPPO HDMI input | 🟡 Partial | manual picker `step5.tsx:84-193`; auto-find unstubbed |
| 5 | HDMI switch **test** + confirm | 🔴 Simulated | `step5.tsx:167` cosmetic; TV mute test is a UI sim |
| 6 | OPPO IP + **SVM3 monitor during setup** | 🟡 Partial | one-shot probe `step2.tsx:150`; live monitor only in dashboard `lib.rs:555` |
| 7 | Copy test file to ISO dir | 🔴 Stub | `test.tsx:80-143` cosmetic; no backend copy |
| 8 | Power **off** then on OPPO | 🟡 Partial | wake `#PON`/`#EJT` exist; **`#POF` absent** |
| 9 | Mount + play the file | 🔴 Absent | no mount/play automation |
| 10 | Copy control mapping (keymap) | 🟢 Exists | `generate.ts:114-198`, deployed on apply |
| 11 | Confirm ISO played | 🟢 Exists | `test_confirm` `test.tsx:326` |
| 12 | User tests control forwarding | 🟢 Exists | same `test_confirm` |
| 13 | Debug collection throughout | 🟢 Exists | `debug/log.ts`, `ipc.ts`, wire capture `lib.rs:196` |
| 14 | Create settings from result | 🟢 Exists | `mapping.ts` → `apply.ts:52` (writes correct preset) |
| 15 | **Copy the add-on** (default preset) | 🔴 Absent | Phase 1 |
| 16 | Restart Kodi | 🟡 Partial | auto on Tier A (`lib.rs:406`); manual on Tier B |
| 17 | Transform into process monitor | 🟡 Partial | dashboard exists; read-only; TV absent; not auto-started |

**Net:** the back half (settings, keymap, confirm, debug, dashboard) is built
and correct; the front half (SSH-first re-sequence, *real* HDMI test, OPPO
power-cycle/mount/play, test-file copy) plus the **add-on copy** is the new work.

---

## §3 Locked decisions & the foundational dependency

### Decisions locked (2026-06-01)

- **D-A · Default preset = `http_handoff_http`** (flipped from `http_handoff_svm3` by the
  Xnoppo V3 PR4 on 2026-06-02 — see the **Active initiative** section above; the rationale
  below describes the prior `http_handoff_svm3` default). Kodi launches the external
  player via `playercorefactory.xml`; the OPPO is started with the undocumented
  HTTP commands (`/playnormalfile`, `oppo_control.py:432`); SVM3 confirms
  playback. Downgrades to `http_handoff_legacy` if the SVM3 probe fails.
- **D-B · Playback test = full automated copy of a real test ISO**, then
  power-cycle + mount + play. (Forces Phase-4 sub-decisions, see §4.)
- **D-C · Add-on packaging = one package + preset — NOT six builds.** Six
  separate per-architecture add-ons were considered (2026-06-01) and rejected:
  the six "versions" are the six `playback_architecture_preset` values of a
  single package, resolved at runtime (`settings_reader.py:263-283`). Six builds
  would force configurator-wide add-on-id parameterisation (`generate.ts:19`
  threads everywhere) + 6× releases for zero runtime benefit. The configurator
  copies one add-on and writes the chosen preset.
- **D-4 · NAS-path capture = observe-and-verify (primary), manual entry
  (fallback). (locked 2026-06-02)** The OPPO-visible path can't be guessed, so
  the configurator *learns* it: the user plays a file in Kodi (configurator reads
  the exact Kodi path over SSH via JSON-RPC `Player.GetItem{file}`), then plays
  the **same** file on the OPPO (configurator auto-reads the path from the
  undocumented HTTP `/getmovieplayinfo` + confirms via `#QFN` and SVM3
  `@UPL PLAY`), diffs the two → `oppo_http_path_from/to`, and **proves** it by
  firing `/playnormalfile` and watching SVM3. **Fallback** (if `/getmovieplayinfo`
  lacks the path — hardware-TBD): the user types the OPPO-visible share root with
  in-UI SMB/NFS syntax reminders (see the §3 foundational-dependency
  table). The documented RS-232/IP protocol does **not** return the playing path
  (only the truncated `#QFN` filename + the `#QDR` browse tree), so the HTTP API
  or manual entry is unavoidable. Built as **Phase 1b** (§4); the manual fallback
  is the small part already on the #170 branch.

### Open decisions

- **D-1 · Which add-on build does the configurator bundle?**
  **(A)** cut a Final `v2.9.14` from `main` and bundle it *(recommended — a
  real, evidenced release for an install flow)*; **(B)** bundle the existing
  `v2.9.14-experimental`; **(C)** build `main` fresh at configurator-build time
  (unpinned). **RESOLVED 2026-06-01 → C.** No separate add-on release; the
  configurator build runs `tools/package_installable_zip.py` on `main` (PR-1.1),
  bundling an *unpinned* `main` snapshot. **Phase 0 dissolves into PR-1.1.**
  ⚠️ Labelling wrinkle: `main`'s `version.py` (`2.9.13`) lags its post-2.9.13 code,
  so a fresh bundle self-reports `2.9.13` — fixed in PR-1.1 (bump `main` to a dev
  version, or stamp the bundled ZIP at build time).
- **D-2 · Test-ISO source (Phase 4). RESOLVED 2026-06-02 → user-supplies.** The
  operator supplies the master ISO/disc separately; PR-4.2 ships **placeholder
  wiring** (a user-chosen source path, no bundled/downloaded master). The real
  test uses the operator's own disc.
- **D-3 · Add-on *enablement* after file-drop. RESOLVED 2026-06-02 → JSON-RPC
  with manual fallback.** Enable via Kodi JSON-RPC `Addons.SetAddonEnabled`
  (over the existing SSH channel); **if it fails, instruct the operator to
  restart Kodi manually.**

### ⛓ Foundational dependency — OPPO NAS-path mapping

Both D-A and D-B require the configurator to learn **the path the OPPO sees**
for the media share. `http_handoff` plays via `/playnormalfile?path=<oppo-path>`
and the code admits *"the wizard cannot know the player's NAS mount namespace,
so the operator sets it"* (`mapping.ts:176-177`). Until captured, an
`http_handoff_svm3` default is **written but inert**.

**Resolved (D-4) — observe-and-verify capture, manual fallback.** The path is
*learned*, not guessed:

1. **Capture the Kodi path (auto).** The user plays a file in Kodi; the
   configurator reads the exact path over the existing SSH channel via Kodi
   JSON-RPC — `Player.GetActivePlayers` → `Player.GetItem{properties:["file"]}`
   (fallbacks: raw JSON-RPC TCP `:9090`, or tail `~/.kodi/temp/kodi.log`).
2. **Capture the OPPO path (auto, hardware-TBD).** The user plays the **same**
   file on the OPPO; the configurator auto-reads the OPPO-visible path from the
   undocumented HTTP `/getmovieplayinfo` (port 436, already fetched raw by
   `oppo_control.probe_player_status`) and confirms identity via `#QFN`
   (truncated filename) + liveness via SVM3 `@UPL PLAY`.
3. **Derive + verify.** Diff Kodi-path vs OPPO-path → `oppo_http_path_from/to`;
   fire `/playnormalfile` and use SVM3 `@UPL PLAY` + `#QFN` as the pass/fail
   oracle, iterating until it plays.

⚠️ The **documented** RS-232/IP protocol does *not* report the playing path —
`#QFN` is a truncated filename (`OK Rocky Mou*.wav`) and `#QDR` only walks the
browse tree (SMB/NFS/DLNA servers shown as *labels*, e.g. `S MyPC`). So
auto-capture rides the **undocumented** HTTP API; if `/getmovieplayinfo` lacks
the path, the flow falls back to **manual entry**.

**Manual-entry share-syntax reminder** — the Kodi-visible `from` path the user
copies (shown in the fallback field):

| Share | Kodi URL form | Example |
|---|---|---|
| **SMB** (Windows / Samba) | `smb://[user[:pass]@]host/share/path/file` | `smb://192.168.1.10/Movies/Film.iso` |
| **NFS** (Unix export) | `nfs://host/export/path/file` | `nfs://192.168.1.10/volume1/Movies/Film.iso` |

The OPPO-visible `to` is the player's own mount label (e.g. the SMB server name
`MyPC` as the OPPO shows it in its browser), **not** the IP — which is why it
must be observed or entered, not derived from the Kodi URL. *Scope: SMB and NFS
only* — these are the share types the OPPO's own browser natively lists
(`S MyPC` / `N MyNFS`). WebDAV / FTP are out of scope: for `http_handoff` the
**OPPO itself** must reach the share, and it can't necessarily mount those.

---

## §4 Roadmap — two tracks, six phases

> **✅ DELIVERED (2026-06-02).** Every phase below is built + merged to `main` — see the
> **Phase → delivery map** in the header for the PR refs. This section is retained as the original
> roadmap and design record; the only outstanding work is **operator Phase-C hardware validation**
> of the whole flow (`docs/MANUAL_VERIFICATION_CHECKLIST.md`) and an optional **configurator
> release** bundling `main` fresh (D-1=C).

Each phase ≈ one session (one theme, ≤ 4 PRs per AGENTS.md). The add-on track
(🟦) interleaves with the configurator track (🟩). Phase order is the build
order; the *user-facing* flow order is delivered by Phase 2.

```
🟦 add-on:    v2.9.13 ─▶ Ph0: build v2.9.14 (carries http_handoff/SVM3/preset)
                                   │ bundled by ▼               ┌▶ Ph2 handshake ─▶ Ph5 rich status
🟩 configurator: v0.5.0 ─▶ Ph1 install ─▶ Ph2 re-sequence ─▶ Ph3 HDMI test ─▶ Ph4 OPPO self-test ─▶ Ph5 monitor
```

### 🟦 Phase 0 — add-on release the configurator will bundle *(area:addon)*

Per **D-1** (recommended **A**): promote `main` → **Final `v2.9.14`** via the
`release` skill runbook (78-file bump, evidence, CI, tag, GitHub release). This
is the add-on build carrying `http_handoff` / SVM3 / the preset system. No new
add-on *code* — it ships existing `main`. *(If D-1 = B, Phase 0 is "adopt
`v2.9.14-experimental`"; if C, Phase 0 folds into Phase 1 PR-1.1.)*

### 🟩 Phase 1 — bundle + install the add-on, working `http_handoff_svm3` default

**Theme:** configurator ships the add-on, installs it to Kodi, and configures a
*functional* `http_handoff_svm3` default. **Frozen:** add-on runtime (consumed
as a build artifact via `tools/package_installable_zip.py`); config-gen
additive-only (pinned by `apply.test.ts` / `mapping.test.ts` / `generate.test.ts`
/ `settings_xml.test.ts`).

- **PR-1.1 — Bundle add-on** (~110): `package.json` `bundle:addon` runs
  `package_installable_zip.py` → `src-tauri/resources/addon/…zip`;
  `tauri.conf.json:31-40` `bundle.resources`; `lib.rs` `bundled_addon_info()`
  (parse embedded `addon.xml`), register at `lib.rs:637-653`. *Tests:* Rust
  version-parse on a fixture ZIP.
- **PR-1.2 — Rust `install_addon`** (~200 + `zip` crate): Tier A pushes the ZIP
  via `run_ssh_stdin` (`lib.rs:322-343`) + `python3 -m zipfile -e` into
  `<addons>/` (backup via `backup_suffix` `lib.rs:72-78`, restart `lib.rs:406`);
  Tier B extracts with the `zip` crate (pattern of `deploy_to_userdata`
  `lib.rs:117-146`); Tier C drops the ZIP for Kodi "Install from zip". *Tests:*
  Rust extraction + backup unit tests.
- **PR-1.3 — OPPO NAS-path manual entry (D-4 fallback)** (~120): the state
  plumbing is **already on the #170 branch** (`oppoPathFrom`/`oppoPathTo` in
  `state.ts` + `INITIAL_STATE`, emitted by `mapping.ts:180-181` when set). This PR
  adds the **manual-entry field with the SMB/NFS share-syntax reminder**
  (§3 table) near the OPPO step (`step2.tsx:76-84`) + `oppo_http_disc_folder_root`.
  The **primary** auto-capture is **Phase 1b**. *Tests:* `mapping.test.ts`
  http_handoff → correct `oppo_http_*`.
- **PR-1.4 — Wire install + default** (~140): `INITIAL_STATE.playbackArchitecture
  = "http_handoff"`, `monitorMode = "svm3"` (`state.ts:124-125`);
  `installAddonToKodi(state)` in `apply.ts` (tier dispatch mirroring
  `applyToKodi` `:52-105`); run install **before** the playback test in
  `test.tsx`. *Tests:* `apply.test.ts` per-tier install; `state.test.ts` default
  preset = `http_handoff_svm3`.

Dep: `1.1 → 1.2 → 1.4`; `1.3 → 1.4`. **Risk:** binary expand; Tier A needs
`python3` on box; the default is only as good as PR-1.3's path; add-on
*enabled* ≠ present (D-3).

### 🟩 Phase 1b — NAS-path auto-capture (observe-and-verify; D-4 primary)

**Theme:** *learn* the OPPO-visible path instead of asking for it, so the
`http_handoff_svm3` default becomes **functional**, not just written. Reuses the
SSH channel (`run_ssh_capture` `lib.rs:309`), `oppo_query` (`#QFN`/`#QPL`), and
the SVM3 live monitor (`start_oppo_live_monitor` `lib.rs:555`); PR-1.3's manual
field stays as the fallback. **Frozen:** the path-rewrite contract
(`oppo_control._translate_media_path` `oppo_http_path_from/to`), pinned by
`mapping.test.ts` + the add-on's `_translate_media_path` tests.

- **PR-1b.1 — Kodi now-playing over SSH** (~120): Rust `kodi_now_playing` runs
  Kodi JSON-RPC `Player.GetActivePlayers` → `Player.GetItem{properties:["file"]}`
  via `run_ssh_capture` (fallback: tail `~/.kodi/temp/kodi.log`); returns the
  exact Kodi path. *Tests:* Rust JSON-RPC + log-line parse (fixtures).
- **PR-1b.2 — OPPO path auto-read + derive** (~140): extend `probe_player_status`
  to parse the OPPO-visible path out of `/getmovieplayinfo`; a pure
  `deriveRewrite(kodiPath, oppoPath)` → `oppo_http_path_from/to`; confirm file
  identity via `#QFN`. *Tests:* `deriveRewrite` table (SMB/NFS prefixes) +
  a playinfo-parse fixture. **Hardware-gated:** whether `/getmovieplayinfo`
  carries the path is unverified — the operator probe decides; else manual.
- **PR-1b.3 — Verify-by-playing loop** (~140): fire `/playnormalfile` from the
  derived rewrite and gate on SVM3 `@UPL PLAY` + `#QFN` match as the pass/fail
  oracle (reuse the live monitor); iterate, escalate to manual on failure.
  *Tests:* loop state-machine units (mocked monitor).

Dep: `1b.1 → 1b.2 → 1b.3`; needs Phase 1 (preset wired) + Phase 2's SSH-first
creds. **Risk (high, hardware-gated):** auto-read only works if
`/getmovieplayinfo` exposes the path; the `/playnormalfile` format is
undocumented, so the verify loop is the real proof — none of it is in-session
verifiable (operator Phase B/C).

### 🟩 Phase 2 — re-sequence to the SSH-first flow + 🟦 add-on handshake

**Theme:** deliver the user-facing order. **Names↔UI must stay in sync**
(`steps.ts` is the source of truth, AGENTS.md:44-61).

- **PR-2.1 — Persist creds + switcher IP** (~120): capture/persist SSH user+host
  and the **TV/switcher IP** (today the TV IP is never stored,
  `dashboard_targets.ts`); needed by the HDMI test (Ph3) and the monitor (Ph5).
- **PR-2.2 — SSH-access-first + reorder** (~180): make SSH access the entry
  gate; reorder `steps.ts` STEPS/ScreenId/SCREEN_TO_STEP to
  *SSH → switcher choice+IP → HDMI setup → input capture → OPPO access (incl.
  NAS path) → test*; rename files/ids/labels in lock-step.
- **PR-2.3 — 🟦 add-on "configured-by-configurator" marker** *(area:addon →
  new add-on build)* (~80): a marker so the add-on defers to configurator-owned
  `playercorefactory.xml` and never re-runs first-run setup
  (`installer.py:505-531`; the dialog is already suppressed by
  `architecture_choice_made`, `mapping.ts:150` — this hardens it). *Tests:*
  add-on `pytest` for the marker gate.
- **PR-2.4 — De-stub honestly** (~60): replace the cosmetic `step5.tsx:167`
  switch label and the `test.tsx` "Copied" message with honest "manual step"
  copy until Ph3/Ph4 make them real.

### 🟩 Phase 3 — real HDMI switching test

**Theme:** turn the simulated switch into a real, verified action.

- **PR-3.1 — Rust input-switch commands** (~200): per-backend HDMI input select
  — TV (`adb` / `roku_ecp` / `sony_bravia` / `smartthings` / `lg_command` /
  `samsung_command` / `custom_command`) and AVR (`denon_marantz` / `yamaha_yxc`
  / `onkyo_eiscp` / `pioneer_eiscp` / `sony_audio_api`), mirroring the add-on's
  drivers under `resources/lib/tv/` and `resources/lib/avr/`. *Tests:* Rust
  command-builder unit tests (no I/O).
- **PR-3.2 — Switch-and-verify** (~140): replace the manual confirm in the HDMI
  step with an automated switch then a verifiable check where possible (e.g.
  power/state read-back); honest manual fallback otherwise.
- **PR-3.3 — Auto-find inputs** (~120): auto-detect the Kodi + OPPO HDMI input
  where the backend allows (replaces the `step5.tsx` "find it for me" stub).

**Risk:** most TV/AVR backends give no switch *confirmation* — verification may
stay user-confirmed; label honestly.

### 🟩 Phase 4 — OPPO automated self-test (full ISO copy + mount + play) — **D-B**

**Theme:** the headline self-test. Depends on the OPPO NAS path (Ph1) + **D-2**.

- **PR-4.1 — Rust OPPO play/power** (~180): add `#POF` power-off and the
  http_handoff start sequence — `activate_http_api` (UDP broadcast),
  `signin_http_api`, `play_media_http_api` (`/playnormalfile?path=`) — porting
  the add-on's documented commands (`oppo_control.py:346-445`) into the Rust
  backend. *Tests:* Rust request-builder unit tests.
- **PR-4.2 — Test-ISO copy** (~160): per **D-2**, obtain a master test ISO and
  copy it to the OPPO's share with **progress UI** (multi-GB; reuse the SMB/SSH
  transport). *Decision-gated.*
- **PR-4.3 — Live SVM3 during setup** (~140): run the live monitor
  (`start_oppo_live_monitor` `lib.rs:555`) *during* the self-test; confirm
  playback on `@UPL PLAY` + advancing `@UTC` (not a manual yes/no).
- **PR-4.4 — Self-test orchestration** (~120): power-cycle → mount → play →
  SVM3-confirm → user tests control forwarding (`test_confirm` mostly exists).

**Risk (high):** multi-GB transfer time/reliability; the OPPO mount namespace
(Ph1) must be exactly right; entirely hardware-gated.

### 🟩 Phase 5 — process monitor + 🟦 richer add-on status

**Theme:** the configurator "transforms into a process-monitoring tool."

- **PR-5.1 — 🟦 add-on live status** *(area:addon → new add-on build)* (~120):
  extend the add-on's status emission beyond the last-session
  `oppo203iso-status.json` (`oppo_status.ts` fields) into finer live telemetry
  for the monitor. *Tests:* add-on `pytest` for the status writer.
- **PR-5.2 — Dashboard upgrade** (~160): add **TV liveness** (now that the TV IP
  is persisted, Ph2), auto-start the live stream, consume the richer status
  (`dashboard.tsx`, `dashboard_status.ts`, `dashboard_targets.ts`).
- **PR-5.3 — Full chain view** (~140): unified live status + activity for every
  node (Kodi / OPPO / TV / AVR) along the playback chain.

---

## §5 Rollup, risks & verification

### 📊 Phase rollup

| Phase | Track | ~PRs | Headline risk |
|---|---|---|---|
| 0 Add-on build | 🟦 | 1 (release) | Release mechanics only; no new code |
| 1 Install + default | 🟩 | 4 | Binary expand; inert default until NAS path (Ph1b); enable≠present |
| 1b NAS-path auto-capture | 🟩 | 3 | Auto-read only if `/getmovieplayinfo` carries the path; verify-by-playing is the proof; hardware-gated |
| 2 Re-sequence + handshake | 🟩+🟦 | 4 | Names↔UI sync; cross-area add-on build |
| 3 HDMI test | 🟩 | 3 | Backends rarely confirm a switch |
| 4 OPPO self-test | 🟩 | 4 | Multi-GB copy + mount namespace; fully hardware-gated |
| 5 Process monitor | 🟩+🟦 | 3 | Needs TV IP (Ph2) + add-on status (5.1) |

### ⚠️ Standing risks

- **Version-matching.** The configurator bundles **one** add-on build; that
  build must contain every feature the configurator relies on (Ph1: preset;
  Ph2: marker; Ph5: status). Ship the pair matched; bump the bundled add-on
  whenever an add-on-side phase lands.
- **Live-verify caveat.** No Kodi / OPPO / TV is reachable in-session. SSH push,
  real HDMI switch, power-cycle, HTTP play, and multi-GB copy are **not**
  verifiable here — gated by unit tests + render guards, then operator Phase
  A/B/C in `docs/MANUAL_VERIFICATION_CHECKLIST.md`.
- **Honest signature.** Keep "software-verified · hardware validation not
  claimed" (`test.tsx:636`) on every new automation step until a tester confirms.

### Verification regime (per PR)

- **Configurator TS:** `cd D:\Git\script.oppo203.iso.external\configurator; npx tsc --noEmit; npm run build; npx vitest run`
- **Configurator Rust:** `cd D:\Git\script.oppo203.iso.external\configurator\src-tauri; cargo build; cargo test`
- **Add-on (Ph0/2.3/5.1):** `cd D:\Git\script.oppo203.iso.external; pytest -n auto; ruff check .; ruff format --check .` + the **serial 99% coverage gate** (`coverage run -m pytest` then `coverage report`).
- Then a **draft PR** (`claude/cfg-…-<8char>` / `claude/addon-…`), SHA-comment +
  a Phase A/B/C row in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. **Only the
  operator closes.**

---

## §6 Per-area open-issue status (may lag GitHub — see source of truth)

### Add-on (`area:addon`) — at a clean baseline; post-2.9.13 work unreleased as Final

Type-hardening arc complete (ruff
[`#38`](https://github.com/skull-01/script.oppo203.iso.external/issues/38) →
mypy [`#51`](https://github.com/skull-01/script.oppo203.iso.external/issues/51),
gate 49/0). The merged-awaiting-close set (#41/#42/#43/#44/#57) still awaits
operator close + Phase A/C. **New for this initiative:** Phase 0 (release
`v2.9.14`), Phase 2.3 (configurator handshake), Phase 5.1 (live status).

### Configurator (`area:configurator`) — at v0.5.0

Wizard wiring ([`#68`](https://github.com/skull-01/script.oppo203.iso.external/pull/68))
+ the 16 `/code-review` fixes (#72–#87) are merged, awaiting Phase C. Windows
binaries shipping on the `configurator-v0.x` line. **New for this initiative:**
Phases 1–5 above.

**Six-preset cross-area completeness guard (delivered 2026-06-01).** A
`configurator/src/mapping.test.ts` *completeness* test asserts the routing × monitor
matrix emits **exactly the six** canonical presets (pins `size == 6` on the configurator
side, mirroring the add-on's `PLAYBACK_ARCHITECTURE_PRESETS` `len == 6` in
`tests/test_architecture_presets.py`). It backs the **"six playback-architecture presets
are a maintained matrix"** norm now in `AGENTS.md` + §4 of the handoff. *Optional future
hardening:* a single shared preset source consumed by both sides + a Python parity test
(the AVR/TV-DB-guard pattern) for fully-automated cross-language parity.

**Phase 1 built + released as `configurator-v0.6.0-experimental2` (2026-06-01).** The
bundle-and-install feature (PR-1.1 / 1.2 / 1.4 + the NAS-path plumbing of 1.3) is on branch
`claude/cfg-phase1-install-addon-5c1d8a30` (`46deeb2`) and shipped as a GitHub **pre-release**
(MSI + NSIS + SHA256), **off `main`** — main's configurator stays at v0.5.0. Software-verified
only (cargo test 7/7, `tsc` + 178 vitest + `vite build`); the on-box install + OPPO NAS path are
**hardware-pending**. **Deferred:** the Step-2 NAS-path capture UI (the `http_handoff` default is
*inert* until set) and the add-on version stamp (bundle self-reports `2.9.13`). **Draft PRs (off `main`, 2026-06-01):**
[#170](https://github.com/skull-01/script.oppo203.iso.external/pull/170) Phase 1 (install; also
released as `configurator-v0.6.0-experimental2`) ·
[#171](https://github.com/skull-01/script.oppo203.iso.external/pull/171) Phase 2 (SSH-first flow +
honesty de-stub + persist TV IP; **browser-verified**) ·
[#172](https://github.com/skull-01/script.oppo203.iso.external/pull/172) Phase 3 slice (Roku ECP
TV-input switch). All **software-verified only** — the hardware paths (SSH install + unzip, OPPO
HTTP play, the Roku switch) are **unvalidated**. **Next:** hardware-verify on a real Kodi / OPPO /
TV, then promote the PRs to ready and merge. Phase 3 remaining (adb / Sony / AVR switch backends +
switch-and-verify UI) and Phase 4 (OPPO power-cycle + ISO copy + play) are paused pending hardware.

**`configurator-v0.6.0-experimental3` (2026-06-01)** = the three branches **integrated** (branch
`claude/cfg-experimental3-integration`, `5dcb087`) and published as one GitHub pre-release (MSI +
NSIS + SHA256): the cumulative **install + SSH-first flow + Roku switch**. The `lib.rs` merge kept
both command sets; gate `cargo test` 9/9 · `tsc` · **180 vitest** · `vite build`. Off `main`;
software-verified only, hardware-pending.

---

## §7 How to keep this file useful

- Update §1/§2 dates + status when reality moves; refresh the §3 decisions as
  the operator settles D-1 / D-2 / D-3.
- Add a row when filing a new `ENH-` issue; strike it when the issue closes.
- Replace placeholder `ENH-…` / `Phase N PR-x` IDs with real issue numbers once
  filed.
- Don't duplicate issue bodies here — link to GitHub for the real text.
- Keep file:line anchors honest: re-confirm them at plan time (line numbers
  drift after merges).
