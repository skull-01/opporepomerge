# Build plan

**Audience:** any AI agent or human contributor planning the next slice of
work. This file is the **map** — it groups live open issues by area + theme,
records the strategic direction the operator has set, and links out to the
authoritative GitHub state.

**Source of truth:** open issues at
[`gh issue list --state open`](https://github.com/skull-01/script.oppo203.iso.external/issues).
This document is regenerated on demand by the `refresh the build plan`
trigger and is allowed to lag the live state between refreshes.

**Last refreshed:** 2026-05-30

---

## §1 Strategic direction (2026-05-30)

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

### Where each area stands

- **Add-on — mature, at a clean baseline.** The type-hardening arc is complete
  (ruff [`#38`](https://github.com/skull-01/script.oppo203.iso.external/issues/38)
  → mypy [`#51`](https://github.com/skull-01/script.oppo203.iso.external/issues/51),
  gate 49/0; #51 closed). Released at **v2.9.13**; CI-backed (`pytest -n auto`,
  99% coverage, `mypy --gate`, ruff). Every open add-on issue is delivered +
  merged, awaiting operator close.
- **Configurator — feature-complete on paper, unproven on hardware.** The
  7-slice wizard wiring
  ([`#68`](https://github.com/skull-01/script.oppo203.iso.external/pull/68),
  merged `454e5ab`) generates `playercorefactory.xml` + keymap + `settings.xml`
  and deploys via three tiers (SSH / SMB / local copy). A `/code-review` filed
  16 bugs (#72–#87), all fixed across #68 +
  [`#88`](https://github.com/skull-01/script.oppo203.iso.external/pull/88).
  **Software-verified only — no Kodi box / OPPO / TV has validated any deploy
  path.** No CI of its own; the first Windows binary is in progress (see §3).

### Honest signature

Release language remains **"software-verified; hardware validation not
performed / not claimed"** until real tester reports back it up. Hardware
sourcing (lending / donation / remote testing) is being solicited under
[`#44`](https://github.com/skull-01/script.oppo203.iso.external/issues/44).

---

## §2 Add-on (`area:addon`)

### Open issues — all delivered, awaiting operator close

| # | Title | Delivered by | Status |
|---|---|---|---|
| [#38](https://github.com/skull-01/script.oppo203.iso.external/issues/38) | Clear ruff backlog on main | PR #50 `092444a` | merged — ruff clean whole-tree + CI |
| [#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41) | Configurator owns config; add-on read-mostly | PRs #45 / #46 + #88 (Part C) | merged — Phase A/C pending |
| [#42](https://github.com/skull-01/script.oppo203.iso.external/issues/42) | Minimal in-add-on settings menu (IPs + language) | PRs #48 / #49 | merged — Phase A/C pending |
| [#43](https://github.com/skull-01/script.oppo203.iso.external/issues/43) | Split `resources/lib` into TV / Oppo / AVR / Kodi | PR #47 `3ba5009` | merged — Phase A pending |
| [#44](https://github.com/skull-01/script.oppo203.iso.external/issues/44) | Hardware-validation solicitation | PR #89 `9401fb3` | merged — standing community call |
| [#57](https://github.com/skull-01/script.oppo203.iso.external/issues/57) | Change-scoped fast local test loop (testmon) | PRs #59 / #61 | merged — Phase C software check |

Recently closed: **#51** mypy `--strict` rollout (gate 49/0), **#22** wizard launch bug.

### Suggested ordering (operator's call)

The type-hardening arc (ruff #38 → mypy #51) is **complete** and config
ownership has moved to the configurator, so the add-on is at a **clean
baseline**:

1. **Operator close-out** — verify + close the 6 merged-awaiting-close issues
   (Phase A/C steps in `docs/MANUAL_VERIFICATION_CHECKLIST.md`).
2. **Phase A/C on-device verification** of the merged work (operator/hardware,
   no agent code).
3. **A net-new enhancement** when one is picked — no add-on work is blocked.

---

## §3 Configurator (`area:configurator`)

### Themes — recent + in flight

| # / theme | Title | Status |
|---|---|---|
| [#68](https://github.com/skull-01/script.oppo203.iso.external/pull/68) | Wire the wizard to the add-on contract (7 slices) | MERGED `454e5ab` (+ #88 cleanup, #89 doc) |
| #72–#87 | 16 `/code-review` bugs — ssh/probe/deploy hardening, config-write safety, IP-control test, persisted state, cleanups | Fixed across #68 + [#88](https://github.com/skull-01/script.oppo203.iso.external/pull/88) — **awaiting operator close**; Phase C on-device pending |
| #52 | App icon + first MSI/NSIS bundle | MERGED `859238e` (PR-only theme) |
| Chinoppo M9205 V1 split | Distinct `chinoppo_m9205_v1` / `M9205-V1` hardware model (cross-area) | **PR [#91](https://github.com/skull-01/script.oppo203.iso.external/pull/91) (draft)** — software-verified |
| **First Windows binary** | Official versioned `configurator-v0.1.0` MSI/NSIS | **In progress** — build proven on current `main` (3.0 MB MSI + 2.0 MB NSIS, unsigned); recipe + version guard + checksums + draft GitHub pre-release; CI deferred. PR-only |

### Suggested ordering (operator's call)

1. **Ship the first Windows binary** — `configurator-v0.1.0` (build recipe +
   version-consistency guard + `BUILD.md` → SHA256 checksums + release-evidence
   → draft GitHub pre-release for the operator to publish). Unsigned 0.x;
   `windows-latest` CI deferred. **In progress this session.**
2. **On-hardware validation** of the three deploy paths (Tier A SSH+restart /
   Tier B SMB / Tier C copy) against a real Kodi box / OPPO / TV — operator
   action; the paths are software-verified only.
3. **Operator close-out** of the 16 review bugs (#72–#87) after Phase C.
4. **Grow the TV DB** at `docs/configurator/tv-db/tv-models.json` (small seed,
   all `validated:false`; lineups carry the platform→backend mapping).
5. **Real test ISO** — swap the placeholder once the asset exists.

---

## §4 How to keep this file useful

- Add a row when filing a new `ENH-` issue.
- Strike a row when the issue closes.
- Move ordering notes around as the operator's priorities shift.
- Don't duplicate the issue body here — link to GitHub for the real text.
- This file lives on `main`; feature branches should not edit it (causes
  add/add merge conflicts per the session-continuity convention).
