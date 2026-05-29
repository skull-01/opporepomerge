# Build plan

**Audience:** any AI agent or human contributor planning the next slice of
work. This file is the **map** — it groups live open issues by area + theme,
records the strategic direction the operator has set, and links out to the
authoritative GitHub state.

**Source of truth:** open issues at
[`gh issue list --state open`](https://github.com/skull-01/script.oppo203.iso.external/issues).
This document is regenerated on demand by the `refresh the build plan`
trigger and is allowed to lag the live state between refreshes.

**Last refreshed:** 2026-05-29

---

## §1 Strategic direction (2026-05-29)

### Two areas, one tree

Work is split into **`area:addon`** (Kodi add-on, Python under `resources/`)
and **`area:configurator`** (Tauri 2 + React under `configurator/`). Every
issue carries one area label. See `AI_RESUME_HANDOFF.md` §1.

### Configurator owns add-on configuration

Since [`#40`](https://github.com/skull-01/script.oppo203.iso.external/pull/40)
stripped the in-Kodi setup wizard, the **configurator is the single source of
truth for add-on configuration**. The add-on stays read-mostly: it surfaces
current values, accepts a small set of in-the-moment overrides, and routes
the user to the configurator for anything persistent. Tracked under
[`#41`](https://github.com/skull-01/script.oppo203.iso.external/issues/41).

### Honest signature

Release language remains **"software-verified; hardware validation not
performed / not claimed"** until real tester reports back it up. Hardware
sourcing (lending / donation / remote testing) is being solicited under
[`#44`](https://github.com/skull-01/script.oppo203.iso.external/issues/44).

---

## §2 Add-on (`area:addon`)

### Themes in flight / queued

| # | Title | One-liner | Status |
|---|---|---|---|
| [#22](https://github.com/skull-01/script.oppo203.iso.external/issues/22) | Wizard launch failure (`No module named 'wizard'`) | Bug; closed 2026-05-28 | CLOSED |
| [#38](https://github.com/skull-01/script.oppo203.iso.external/issues/38) | Clear ruff backlog on main (336 errors, 172 auto-fixable, 66% in 3 test files) | Mechanical cleanup, 3-PR plan | OPEN |
| [#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41) | Configurator owns configuration; add-on is read-mostly | Policy doc + user-guidance dialog + settings-file ownership marker | OPEN |
| [#42](https://github.com/skull-01/script.oppo203.iso.external/issues/42) | Minimal in-add-on settings menu (TV/OPPO/AVR/Kodi IPs + language) | Carve-out from the configurator-owned policy in #41 | OPEN |
| [#43](https://github.com/skull-01/script.oppo203.iso.external/issues/43) | Split `resources/lib` into TV / Oppo / AVR / Kodi sub-packages | Hardware-family layout; keeps flat-name imports working | OPEN |
| [#44](https://github.com/skull-01/script.oppo203.iso.external/issues/44) | Hardware-validation testing — lending, donations, tester reports | Living "wanted board" | OPEN |

### Suggested ordering (operator's call)

1. **Land [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40)** (strip wizard) — unblocks every theme below.
2. **#41** sets the configurator-owns-config policy in stone (docs +
   in-add-on dialog + ownership marker). Cheap, high-leverage.
3. **#43** module split — best done **before** #42 so the new settings menu
   lands in the right sub-package from day one.
4. **#42** settings menu — depends on the #43 layout and #41 policy doc.
5. **#38** ruff backlog — independent of all of the above; can be done in
   parallel by a separate session.
6. **#44** stays open as a living board; community engagement.

---

## §3 Configurator (`area:configurator`)

### Themes in flight / queued

| # | Title | Status |
|---|---|---|
| [#30](https://github.com/skull-01/script.oppo203.iso.external/pull/30) | Scaffold OppoKodiAddon Configurator (Tauri 2 + React) | MERGED 2026-05-29 |
| [#32](https://github.com/skull-01/script.oppo203.iso.external/pull/32) | Align AGENTS.md ruff target with CI; refresh handoff §3 for #30 merge | DRAFT — partially redundant with the 2026-05-29 spine revision |
| [#33](https://github.com/skull-01/script.oppo203.iso.external/pull/33) | Wire window-control IPC on custom title bar | DRAFT |
| [#34](https://github.com/skull-01/script.oppo203.iso.external/pull/34) | Persist `WizardState` to `%APPDATA%` across restarts | DRAFT |
| [#35](https://github.com/skull-01/script.oppo203.iso.external/pull/35) | Unblock first-time `cargo build` (icon + lockfile + winget docs) | DRAFT |
| [#36](https://github.com/skull-01/script.oppo203.iso.external/pull/36) | End-of-day handoff 2026-05-29 (mid-day continuation) | OPEN — likely close as stale |

### Suggested ordering (operator's call)

1. **Triage the four open draft PRs** (#32, #33, #34, #35) — apply the
   `area:configurator` label, decide which to promote.
2. **#35** unblocks `cargo build` for first-time clones; lowest-risk to
   promote first.
3. **#33** + **#34** are infrastructure that every later screen depends on.
4. After triage, the next big theme is real side-effects behind the diag
   logs (SFTP for Tier A, SMB for Tier B, TCP port knock for TV-backend
   detection, OPPO `#EJT`/`#QPW` over port 23). Multi-PR; depends on #33 +
   #34 landing first. No tracking issue filed yet.

---

## §4 How to keep this file useful

- Add a row when filing a new `ENH-` issue.
- Strike a row when the issue closes.
- Move ordering notes around as the operator's priorities shift.
- Don't duplicate the issue body here — link to GitHub for the real text.
- This file lives on `main`; feature branches should not edit it (causes
  add/add merge conflicts per the session-continuity convention).
