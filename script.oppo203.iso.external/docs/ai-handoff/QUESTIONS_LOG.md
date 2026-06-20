# Questions log — operator reference

Moved from `AI_RESUME_HANDOFF.md` §21 to stay out of the resume-read handoff. Q&A pairs
from substantive conversations (clarifying scope, picking between approaches, defining
terminology). Append-only, newest-last (the `done for the day` flow appends here).

---

### 2026-05-28 — Aesthetic + stack + repo layout for the configurator

- **Q:** Which tech stack should we build the configurator in?
  **A:** Tauri 2 (Rust + web UI) — natural port from the React/CSS prototype.
- **Q:** Where should the configurator code live?
  **A:** Subdirectory in this repo (`configurator/`).
- **Q:** Which aesthetic direction?
  **A:** Direction A — Warm Paper (default per design handoff).

### 2026-05-28 — Naming

- **Q:** Is "installer" the right word?
  **A:** No — the Kodi add-on is installed by Kodi; this Windows app *configures* the
  already-installed add-on. Renamed everything to "OppoKodiAddon Configurator" / verb
  "configure" / "set up". Directory `installer/` → `configurator/`.

### 2026-05-28 — Issue model under the new handoff

- **Q:** GitHub Issues, PR-only, or hybrid?
  **A:** Hybrid — Issues for bug/enhancement tracking, PRs for delivery.

### 2026-05-29 — Sequencing ENH-#41 against PR #40; in-add-on guidance hint mechanism

- **Q:** Should ENH-#41 (configurator-owns-config) ship as one PR or be split
  against PR #40 (strip-wizard, still draft)?
  **A:** Split into three parts. **Part A** (policy doc to
  [`AGENTS.md`](AGENTS.md) + [`CONTRIBUTING.md`](CONTRIBUTING.md)) ships now
  from `main` — no overlap with #40's diff. **Parts B** (in-add-on guidance
  hint on settings open) and **C** (settings.xml ownership marker) wait until
  #40 merges; both modify `resources/settings.xml`, which #40 renames
  (`<category id="wizard">` → `<category id="playback">`) and trims
  (`wizard_mode` removed). Doing B + C now would create avoidable merge
  friction.
- **Q:** For Part B's in-add-on guidance hint, which mechanism — a static
  label at the top of `settings.xml`, a `service.py` first-open-per-session
  `xbmcgui.Dialog().notification`, or both?
  **A:** Both. Static label is permanent visible guidance; the notification
  draws attention exactly once per Kodi session (tracked via
  `xbmcgui.Window(10000).setProperty(...)`, which clears on Kodi restart).
  Most code, strongest UX guarantee.

### 2026-05-29 — Merge order + stacked-PR auto-close (the `merge all pending` directive)

- **Q:** With three open PRs (#52 configurator, #54 mypy PR 2, #55 mypy PR 3 stacked
  on #54), what order merges safely?
  **A:** Stacking dictates it: **#54 → #55 → #52.** #55's base branch *is* #54's
  branch, so #54 must land first. #52 is independent (configurator-only) and goes
  last. Verified each was MERGEABLE/CLEAN and CI-green before merging.
- **Q:** What happened to #55?
  **A:** Merging #54 with `--delete-branch` deleted the branch #55 was based on, which
  **auto-closed #55** — GitHub *closes* (does not retarget) a PR whose base branch is
  removed, and a closed PR whose base is gone can't be reopened or retargeted. The
  fix: recreate the identical branch/commits as a new PR (**#56**) against `main` and
  merge that. Confirmed via `git merge-tree` it was 0-conflict and did **not** revert
  `main`'s newer `AI_RESUME_HANDOFF.md` (pr3 never touched that file, so the 3-way
  merge keeps main's copy). **General rule for stacks:** retarget the child PR to
  `main` *before* deleting the parent's branch, or expect the recreate dance.

### 2026-05-30 — ENH-#51 rollout scope ("do all of these" → how far in one session)

- **Q:** On `resume` the operator picked **both** ENH-#51 candidate themes at once — "PR 4
  (import-fallback strategy for the no-redef idiom modules)" **and** "the cascade group" —
  with "do all of these". One theme or many PRs?
  **A:** One theme (ENH-#51), delivered as a stack. The cascade group is blocked on the two
  un-migrated hubs (`settings_reader` 72 + `oppo_control` 111 errors), so the real sequence is
  PR 4 (leaves) → PR 5 (hubs) → PR 6 (cascade) → PR 7 (the larger hub-dependent idiom modules
  oppo_remote/external_player/installer/preset_manager). Four PRs — at §4's soft cap.
- **Q:** After PRs 4+5 (the hubs unblock everything), the remaining work was ~425 strict
  errors / 11 modules — larger than the two bullets implied. Continue now or checkpoint?
  **A:** Operator chose **"everything now (PR 6 + 7)"** (popup). Proceeded; parallelized the
  mechanical per-module annotation across general-purpose sub-agents to fit it in one session
  while keeping verification (gate + full suite + coverage + diff review) on the main thread.
