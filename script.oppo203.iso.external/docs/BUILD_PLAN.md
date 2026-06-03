# Build plan

**Audience:** any AI agent or human contributor planning the next slice of work on
`script.oppo203.iso.external`. This file is the **map** — the current state of both areas, the
active initiative, and the backlog. Read [`AI_RESUME_HANDOFF.md`](../AI_RESUME_HANDOFF.md) first for
session continuity and [`AGENTS.md`](../AGENTS.md) for the build norms.

**Source of truth:** the live [`gh issue list --state open`](https://github.com/skull-01/script.oppo203.iso.external/issues)
plus the code on `main`. This file is regenerated on demand by the **`refresh the build plan`**
trigger and is allowed to lag the live state between refreshes. Phase/PR IDs below are **planning
placeholders** until the operator files the matching `area:addon` / `area:configurator` issues.

**Last refreshed:** 2026-06-03 (post-EOD #14 + same-day follow-ups through configurator v0.8.7).
**Shipped:** add-on **v2.9.15** · configurator **v0.8.7** (holds the repo "Latest"). Releases now:
add-on via `/release` + `package.yml`; **configurator via `git tag configurator-v*` → GitHub Actions
CI builds MSI/NSIS + publishes** (manual `npm run dist` is a fallback — see
[[configurator-release-is-manual]]).

> **This file lives on `main`; feature branches must NOT edit it** (add/add merge conflicts per the
> session-continuity convention). Edit it on a short-lived docs branch → PR → merge.

---

## §1 Current state

### Two areas, one tree
- **Add-on** (`area:addon`): Python under `resources/`, entry points `default.py`/`service.py`,
  release tooling in `tools/`, tests in `tests/`. Released via `/release` + the `package.yml` workflow.
- **Configurator** (`area:configurator`): Tauri 2 + React/TS under `configurator/`. **Now has CI** —
  `.github/workflows/configurator-ci.yml`: a `windows-latest` gate (`npm ci` → `tsc -b` + `vite build`
  → vitest → bundle add-on → `cargo test`) on every configurator-touching PR, and a `configurator-v*`
  tag builds the MSI/NSIS and publishes the release as Latest.

### Delivered initiatives (context — no longer active work)
- **Guided install + full setup flow** (Phases 0–5) — SHIPPED. The configurator installs and
  configures the add-on end to end: bundle+install, SSH-first flow, HDMI switch test, OPPO automated
  self-test, live session dashboard + dashboard memory.
- **Xnoppo V3 / Pure-HTTP/436** — SHIPPED (add-on **v2.9.15** + configurator **v0.8.0**): the 7th
  preset `http_handoff_http`, the `http` monitor axis, pure-HTTP launch orchestration, `checkfolderhasBDMV`-first
  disc nav, selectable HDMI switching, default flip to Pure HTTP. Adopted the `emby-chinoppo-bridge`
  approach (credited in the README).
- **2026-06-03 follow-ups** (configurator **v0.8.4 → v0.8.7**): Reset-all reachability (#263) + hang
  fix & live progress (#266); the **configurator CI/release automation** (#272); dashboard
  **diagnostics export** (#273); **single-prompt installer** (#274); **i18n scaffold** (#277); add-on
  **property-test hardening** that found+fixed a real `OverflowError` (#275/#276); **Hisense E8N Pro**
  TV-DB row under a new `hisense-china-android` lineup (#280) + **TV family sizes** display (#282); the
  **OPPO HTTP command catalog** — 61 endpoints, tester-contributed (#285).

### Standing remaining work: operator **Phase-C hardware validation**
Everything above is **software-verified only**. Real-device validation (OPPO / Kodi / TV / AVR / NAS)
is the operator's, scripted in [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](MANUAL_VERIFICATION_CHECKLIST.md).
No agent code remains for the delivered initiatives.

---

## §2 ▶ ACTIVE INITIATIVE (queued — at the Go gate): Developer Options console

A confirm-gated **Developer Options** surface that mirrors the Reset-all persistent entry (a header
button + a dedicated screen + `steps.ts` routing), with per-device sub-sections — **Kodi / TV / OPPO /
AVR / NAS** — each offering a **live view + remote control**, plus Kodi dev tooling and a LAN scan.

**Frozen / reused:** the wizard flow and the seven-preset contract are untouched; it reuses the
existing liveness (`tcp_probe`/`tv_port_probe`/`oppo_query`/`kodi_now_playing`), the `oppo-live`
verbose-push stream, the remote-control commands (`oppo_power`/`tv_switch_*`/`avr_switch_*`/
`smartthings_switch_request`), and the install/enable commands (`install_addon`/`kodi_set_addon_enabled`/
`bundled_addon_info`).

**Status: PLANNED — awaiting operator Go.** The OPPO **HTTP command catalog** already landed as the
data layer (PR #285 → `configurator/src/oppo-commands/http-commands.ts`). All five device
sub-sections (Kodi / TV / OPPO / AVR / NAS) are now fully specified.

### Per-PR scope
- **PR A — Dev-tab shell + nav** (~150 LOC, UI only). Header "Developer…" entry (hidden on dev
  screens, like "Reset all…"); a `developer` screen with 5 sub-section tabs; register in `App.tsx`
  `SCREEN_RENDERERS` + `steps.ts` (`ScreenId` + both exhaustive maps, pinned by `steps.test.ts`).
- **PR B-OPPO — OPPO command console** (~220 LOC + ~3 thin Rust cmds).
  - **TCP palette:** the documented OPPO UDP-20x `#XXX` set (power / transport / nav / source /
    queries / `#SVM`) fired via `oppo_query`, plus a free-text **raw-command box** (any command,
    incl. undocumented). *Pending: a tester-supplied TCP list to seed the curated set; else use the
    documented set.*
  - **HTTP palette:** renders the landed 61-endpoint catalog (`http-commands.ts`), grouped by
    category, fired via a new generic `oppo_http_get(endpoint, query)` (reuses `oppo_http_request`/
    `oppo_http_exchange`); `sensitive` endpoints (`/loginNfsServer`, `/loginSambaWithID`) redacted in
    the transcript.
  - **Live transcript with a TCP ⇄ HTTP monitor switch:** TCP = the verbose-push `oppo-live` stream
    (`start/stop_oppo_live_monitor`); HTTP = an interval poll of `getmovieplayinfo` / `getglobalinfo`.
    Reuses the existing `debug-wire` capture (TCP frames) + the IPC log (HTTP). Caveats surfaced in
    the UI: TCP push needs `#SVM` (a device-global setting); the live stream has a single-subscriber
    gate (`canStartLiveStream`) shared with the dashboard.
- **PR C — Kodi dev sub-section** (~250 LOC + 1 Rust cmd). Installed vs bundled add-on version
  (`bundled_addon_info` + read the box's `addon.xml` over SSH); add-on settings table (reuse
  `captureSettingsSnapshot`); remote restart; **register-without-restart** (`kodi_set_addon_enabled`);
  **upload-any-version** = a new `install_addon_zip(path)` (deploy a user-picked `.zip` + JSON-RPC
  enable, to minimize restarts during test cycles).
- **PR D-TV — TV command console** (~220 LOC + ~2 thin Rust cmds). **All TV backends available for
  experimentation regardless of the configured one** — per-backend palettes: **Roku ECP** (any
  keypress/launch via `tv_switch_roku`, which already takes a `key`), **ADB** (any `input
  keyevent`/`am start` via `tv_switch_adb`), **Sony Bravia** (IRCC + REST), **Samsung** (`samsungctl
  KEY_*`), **LG webOS**, **SmartThings** (device commands via `smartthings_switch_request`),
  **custom_command** (raw shell) — each grouped with its command set + a free-text **raw box**; fired
  via the existing `tv_switch_*`/`smartthings_switch_request` (+ thin generic fire commands where
  today's are input-only). **Live transcript** of command → response (reuse the IPC log; TVs expose no
  telemetry feed, so it's a command/response log + reachability — stated honestly).
- **PR D-AVR — AVR command console** (~180 LOC). Same pattern for **all AVR backends** —
  **Denon/Marantz** (`SI`/`MV`/`PW`, :23), **Onkyo/Pioneer/Integra eISCP** (`!1xxx`, :60128),
  **Yamaha** (`setInput`/setX, :80), **Sony audio** (REST) — per-backend palette + raw box, fired via
  `avr_switch_*`, with the same live command/response transcript.
- **PR D-NAS — NAS panel** (~220 LOC + ~2 Rust cmds). **Scan** the LAN for NAS hosts (`scan_nas_hosts`:
  subnet sweep of NAS service ports via the existing `tv_port_probe`/`connect_timeout` logic —
  **445/139 SMB, 2049 NFS, 548 AFP, 21 FTP**) and **identify the protocol** by which port answers;
  **test-login to a share** for troubleshooting (`nas_test_login`: SMB auth + list, reusing/extending
  `smb_test_write`; NFS mount/access check) — credentials **redacted in the transcript + never
  persisted**; a **live message panel** of scan results, login attempts, and errors.
- **PR E — LAN scan for a Kodi box** (~120 LOC + 1 Rust cmd). New `scan_kodi_hosts`: enumerate the
  configurator host's local IPv4 /24, parallel-probe each host on :8080 with a short timeout, confirm
  each hit via JSON-RPC `Application.GetProperties` (also yields the Kodi version); a "Scan network"
  button lists found boxes (IP + version) and fills the Kodi IP. (mDNS `_xbmc-jsonrpc-h._tcp` is an
  optional later alternative.)

```
PR A (shell) ──┬─► PR B-OPPO (console; HTTP catalog ✅ landed #285)
               ├─► PR C (Kodi dev tools)
               ├─► PR D-TV (TV command console)
               ├─► PR D-AVR (AVR command console)
               ├─► PR D-NAS (scan + protocol + test-login + live)
               └─► PR E (Kodi LAN scan)   ← shares a subnet-sweep helper with D-NAS
```

### 📊 Rollup
| PR | ~LOC | New Rust cmds | Risk |
|----|------|---------------|------|
| A — shell | 150 | 0 | Low — mirrors the #264 reset-all pattern |
| B-OPPO — console | 220 | ~3 (generic HTTP GET + getglobalinfo/checkfolderhasBDMV/remote-key) | Med — device I/O is Phase-C; `#SVM` + single-stream caveats |
| C — Kodi dev | 250 | 1 (`install_addon_zip`) | **Med-High** — arbitrary-zip upload + restart (powerful; dev-gated) |
| D-TV — TV console | 220 | ~2 | Med — all-backend command catalogs; control is Phase-C; no TV telemetry feed |
| D-AVR — AVR console | 180 | 0 | Med — all-backend command catalogs; control is Phase-C |
| D-NAS — NAS panel | 220 | ~2 (`scan_nas_hosts`, `nas_test_login`) | Med-High — scan + share test-login (creds redacted); Phase-C |
| E — Kodi LAN scan | 120 | 1 (`scan_kodi_hosts`) | Med — scan perf (parallel + timeout); real-network Phase-C |

### ⚠️ Risks & open inputs
- **Nearly all behavior is Phase-C** (real devices). In-session only the UI + pure logic (command
  catalogs, subnet enumeration, JSON-RPC builders, transcript folding) are software-verifiable.
- **Safety:** arbitrary-zip upload + Kodi restart + share-login commands are powerful but within the
  configurator's existing remit; kept behind the Developer Options label/confirm; credential-bearing
  endpoints are redacted in the transcript and never persisted.
- **>4 PRs → spans sessions** (one-theme-per-session, ≤4-PR soft cap). Recommended first slice:
  **PR A + PR B-OPPO**.
- **Open inputs:** a tester **OPPO TCP `#XXX` command list** (else use the documented set); whether to
  file the umbrella + per-PR **ENH issues** (operator norm).

---

## §3 Backlog (live source: `gh issue list --state open`)

**44 open issues at this refresh — almost entirely the confirmation queue:** implemented +
SHA-commented + shipped, **awaiting operator verification + close** (only-operator-closes), not pending
build.
- **33 `type:bug`** — the 2026-06-02 full-audit findings (#221–#256) + #266 (reset hang) + #275
  (OverflowError). All fixed + merged.
- **11 `ENH`** — Pure-HTTP adoption (#207–#217), dashboard memory (#167/#168), DB (#103/#105). All
  implemented + shipped.
- **One genuinely-open non-code item:** **#44** — hardware-validation tester solicitation umbrella.

There are **no unbuilt feature issues**; new work is the Developer Options initiative (§2). The
operator's pending action on the backlog is to **verify + close** the confirmation queue.

---

## §4 Build norms in force (see `AGENTS.md` for detail)

- **The seven playback-architecture presets are a maintained matrix.** Any change touching playback
  routing or monitor logic must keep all seven working on both sides + the shared
  `configurator/src/presets-db/playback-presets.json`, pinned by `tests/test_architecture_presets.py`,
  `tests/test_playback_presets_consistency.py`, `presetsdb.test.ts`, and `mapping.test.ts`. Default
  install preset: `http_handoff_http`.
- **Configuration is owned by the configurator.** The add-on is read-mostly; new persistent settings,
  first-run/setup dialogs, or config writers need an issue + operator sign-off.
- **Two-copy DB guards.** The TV / AVR / players DBs ship two byte-identical copies (consistency
  tests). The canonical `docs/configurator/*` copy is what the in-app **"Update database"** button
  fetches — **bump `db_version`** (date-only `YYYY.MM.DD` for TV) so the button sees it as newer.
- **Honest signature.** Keep "software-verified" vs "hardware-validated" distinct; never claim
  hardware validation without a tester report.

### Verification regime (per PR)
- **Add-on:** `pytest -n auto` + `ruff check` + `ruff format --check` + `mypy --gate` + the **serial
  99% coverage gate** (never `-n auto` for coverage).
- **Configurator:** `tsc -b` + `vitest` + `vite build` — now **enforced in CI** on every PR.
- Then a draft PR → CI gate → SHA-comment + a Phase A/B/C row in
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](MANUAL_VERIFICATION_CHECKLIST.md) → **only the operator
  closes** the issue.

---

## §5 How to keep this file useful

Regenerate with **`refresh the build plan`** when initiatives ship or the backlog shifts. Keep it
forward-looking — delivered work moves to the §1 ledger (full history lives in `AI_RESUME_HANDOFF.md`
and git). Edit on a short-lived branch (never a feature branch). Ground every plan against the real
code (`file:line` anchors) before proposing it, and end multi-PR plans with an explicit
**Go / Wait / Replan**.
