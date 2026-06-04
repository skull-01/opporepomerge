# Agent norms — `script.oppo203.iso.external`

Spine: [`AI_RESUME_HANDOFF.md`](AI_RESUME_HANDOFF.md). Read it first; come back here for
the rules below. Contributor norms: [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Issue / PR model (hybrid)

- **Issues** track bugs (`type:bug`) and enhancements (`ENH-` prefix). The operator files
  most; agents file `type:bug` on bug reports per the operator's personal norm.
- **Every issue carries one area label — `area:addon` or `area:configurator`** — so the
  `resume` command can summarize each area independently (see `AI_RESUME_HANDOFF.md` §1).
  Agents apply the area label whenever they file an issue. The two labels are auto-created
  on `resume` if missing (§2a row 14).
- **PRs** deliver. Open drafts; the operator promotes to ready when verified.
- **Only the operator closes issues.** Never `gh issue close`. Never `Closes/Fixes/Resolves
  #N` in commit messages or PR descriptions. When work seems done: comment the implementing
  SHA(s) on the issue, then append a verification entry to
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Branching & commits

- Branch from `main` as `claude/<short-slug>-<8char-suffix>` (matches the existing
  `claude/...` convention used by Claude Code on the web).
- Imperative subject line under 72 chars; body explains *why* (the diff says what).
- Plain commits — **no `Co-Authored-By` agent footer**.
- One commit per cohesive change. Merge via PR; **purge the branch once merged**
  (`gh pr merge --merge --delete-branch`, then `git fetch --prune`).

## Tests + lint must pass before promoting a PR out of draft

- Python tests: `cd /home/user/script.oppo203.iso.external; pytest -n auto`
  (Windows: set `TEMP`/`TMP` to a repo-local dir and pass `--basetemp=build\_pt`.
  Coverage gate runs **serial** — never `-n auto`.)
- Python lint: `cd /home/user/script.oppo203.iso.external; ruff check .`
- TypeScript when touching `configurator/`:
  `cd /home/user/script.oppo203.iso.external/configurator; npx tsc --noEmit && npm run build`

## No inline code comments by default

Default to **no comments**. Add one only when the WHY is non-obvious (a subtle invariant,
a workaround for a specific bug). Never explain WHAT — the identifiers do that. Never
reference the current task or PR — that belongs in the PR description.

## Names must match what the user sees — people read the files

People read this code while looking at the running app, so **file names, identifiers,
component names, and code comments must line up with the labels and numbers shown in the
UI.** A mismatch (a file called `step35.tsx` for a screen labelled "Step 4", or `step2_*`
ids behind a screen the UI calls "Step 3") is a real defect — it sends a reader to the
wrong place and erodes trust in the rest of the code.

- When a displayed label or step number changes, rename the matching files / ids /
  components / comments **in the same change**, not "later". A half-renamed flow is worse
  than either end state.
- The single source of truth for wizard order, numbers, and labels is
  `configurator/src/steps.ts` (`STEPS`). Names elsewhere follow it.
- Keep human-facing strings (`"Fix TV → Step 3"`, `owner="Step 2 · Player …"`) in sync
  with the same numbering — these don't move when you rename an id, so grep for them.
- If a rename would be genuinely costly (e.g. it breaks persisted state or a public
  contract), say so explicitly and leave a one-line comment at the definition explaining
  the intentional divergence — don't leave it silent.

## Session shape — one theme per session, cap ≈ 4 PRs

Each session sticks to **one theme** (e.g. "port screens", "wire SFTP probes", "rename
installer→configurator"). **Don't mix themes within a session** — proven in retros that
mixing themes is where bugs slip in. If the operator nudges into a second theme, suggest
finishing the current one and resuming next session. Soft cap **≤ 4 PRs per session.**

## Plan format — the canonical planning output

When the operator asks for a **plan** — or you reach a multi-PR / multi-step build theme —
produce it in the format below, **every time, at this level of detail**. A plan is a
**deliverable, not a sketch**. **Ground first, plan second, then STOP for a Go** before
writing any code.

### Ground before you plan (don't plan from the doc alone)

- Read the authoritative sources: the relevant issues, the handoff WIP (§3a/§3b), and
  [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) if it exists.
- Open the **actual current code** and confirm every anchor as `file:line`. Line numbers
  drift after merges — verify them, don't trust the doc's.
- Read the central functions/modules so scope is precise, not hand-waved.
- **Diagnose-first for bugs:** locate (and where you can, reproduce) the exact failing
  code path before proposing a fix.
- **Report findings honestly:** confirm the behavior, call out what's **already
  implemented** (don't re-plan done work), and refine the scope/LOC estimate up or down vs
  the doc — lighter-than-expected is a finding, so is heavier.

### The output (every plan contains all of these)

1. **Theme line** — `<id / title> — "<short imperative theme>"`, plus one line of scope +
   constraint: what's in scope, and what is **frozen** and by which guard test
   (e.g. "engine/scoring frozen, pinned by `tests/test_matcher_guardrail.py`").
2. **Per-PR scope blocks** — one block per PR:
   `PR <id> — <title> (~<LOC>) — <issue refs>`, then a bullet per issue giving the
   concrete `file:line` anchor and the exact change, then a `Tests:` line naming the
   regression assertions that PR adds.
3. **Dependency chain** — an ASCII tree showing PR order and what builds on what.
4. **📊 Plan rollup** — a table `PR | Issues | ~LOC | Risk`, one row per PR, each with a
   one-line risk rationale.
5. **⚠️ Risk callouts** — named risks + mitigations: the frozen-behavior guard, the
   **live-verify caveat** (what you *cannot* verify in-session and how you gate it instead
   — e.g. render/unit guards when the real Kodi box / OPPO / TV is out of reach), and any
   overlap with other in-flight work.
6. **Verification regime** — state the per-PR gate explicitly for this repo: add-on
   `pytest -n auto` + `ruff check` + `ruff format --check` + `mypy --gate` + the **serial
   99% coverage gate**; configurator `tsc --noEmit` + `vitest` + `npm run build`. Then a
   draft PR (software-only signature), SHA-comment + a Phase A/B/C row in
   [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md), and
   **only the operator closes**.
7. **✅ Go / 🛑 Wait / 🔁 Replan** — end every plan with this explicit question. **Do not
   start building until the operator says Go.**

### Quality bar

Grounded (real `file:line` anchors, not hand-waving) · honest (claim only verified scope;
flag already-done work; refine the estimate) · risk-aware (name the safety nets and what
you can't verify) · decision-gated (Go/Wait/Replan before any code). The
one-theme-per-session, soft-cap-≤-4-PRs rule above still holds — a plan that needs more is
two sessions.

## Test link — every completed change ends with one copy-paste line

Every change you report as done ends with:
- the run command (a single copy-paste line prefixed with `cd <abs-path>;`), or
- the unittest command + the verification URL (for PRs: PR URL; for runs: localhost or
  bundle path).

No multi-step "now do X, then Y". One line, one paste.

## One-liner shell commands with absolute paths

The operator pastes from any shell, often elevated PowerShell in `system32`. Every shell
command you give: **single line**, prefixed with `cd /absolute/path;`. Never split across
lines, never assume cwd.

## Honest signature — claim only what you verified

Never claim "I verified" / "I tested" / "this works" for anything you didn't actually run
in this session. "Code compiles" ≠ "feature works". State what was actually checked
(typecheck, test names, URLs opened) and what wasn't. Never weaken the project's
**"software-verified / hardware validation not claimed"** wording.

## Scope discipline

Don't refactor, restructure, or "improve" code adjacent to your task. Don't add features,
abstractions, fallbacks, or validation beyond what the task requires. The smaller the
diff, the easier the review. Prefer surfacing real errors over silent fallbacks.

## Configuration is owned by the configurator

The Windows configurator (`configurator/`) is the single source of truth for the
add-on's persistent configuration — TV / OPPO / AVR / Kodi IPs, `playercorefactory.xml`,
the remote-bridge keymap, and hardware presets. The Kodi add-on is **read-mostly**: it
surfaces current values, accepts a small set of in-the-moment overrides, and routes the
user to the configurator for anything that should persist across Kodi restarts.

**Allowed in-add-on exceptions (don't open a discussion for these):**

- Per-session toggles that should not survive a Kodi restart (e.g. verbose mode for a
  single playback test).
- The minimal in-add-on settings menu carved out by
  [#42](https://github.com/skull-01/script.oppo203.iso.external/issues/42) — viewer for
  TV / OPPO / AVR / Kodi IPs plus language selection.
- Diagnostic exports already surfaced in `installer.main()` (AVR readiness reports,
  file-list diagnostic, discovery probe).

**Not allowed without an issue + operator sign-off:**

- New persistent-setting categories in `resources/settings.xml`.
- New first-run or setup dialogs in the add-on.
- Add-on side writers for `playercorefactory.xml`, the remote-bridge keymap, or NAS
  credentials.

If a PR introduces add-on-side configuration outside an allowed exception, the operator
will redirect it to the configurator.

## The seven playback-architecture presets are a maintained matrix

The add-on is **one package with seven runtime presets — not seven builds**
([`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) D-C). Six are the cross-product of **3 routing
modes** (`playercorefactory`, `service_interception`, `http_handoff`) × **2 monitor modes**
(`legacy`, `svm3`); the **7th, `http_handoff_http`, is an asymmetric cell** — the `http`
monitor (pure-HTTP `/getglobalinfo` polling) exists **only** for the `http_handoff` routing,
not as a full column. Single source of truth: `PLAYBACK_ARCHITECTURE_PRESETS` in
`resources/lib/kodi/settings_reader.py`, mirrored cross-language by
`configurator/src/presets-db/playback-presets.json`. `normalize_architecture()` resolves the
chosen one from `playback_architecture_preset` at runtime and **clamps** any invalid
`(routing, "http")` pair to that routing's legacy preset; the configurator emits it
(`configurator/src/mapping.ts` → `` `${routing}_${monitorMode}` ``); **all seven share one
dispatch** in `resources/lib/kodi/playback_session.py`.

**Rule: any change touching playback routing or monitor logic must keep all seven
presets working — on both sides — and exercise them.** Because they share one
dispatch, a fix to one path can silently break another while the rest stay green.

Before promoting such a change out of draft, confirm every box:

- [ ] `PLAYBACK_ARCHITECTURE_PRESETS` is unchanged — **or** changed deliberately on
      *both* sides (the add-on list **and** the configurator routing/monitor enums) **plus
      the shared `playback-presets.json`** in the **same** PR.
- [ ] Add-on matrix guard green — `tests/test_architecture_presets.py`
      (`PresetConsistencyGuard.test_every_preset_round_trips` iterates all of them and pins
      `len(...) == 7`).
- [ ] Cross-language matrix green — `tests/test_playback_presets_consistency.py` +
      `configurator/src/presetsdb.test.ts` (the **asymmetric** matrix, not a full cross-product).
- [ ] Add-on dispatch exercised per routing — `tests/test_playback_session_modes.py`.
- [ ] Configurator emits all of them — `configurator/src/mapping.test.ts` (the "emits exactly
      the seven canonical presets" completeness guard).
- [ ] If a preset was added/removed: the `== 7` count guard, both enums, the shared JSON, the
      configurator Step-4 pills (`configurator/src/screens/step3.tsx`), and the preset
      count in this norm are all updated in lock-step.

Treat the preset set as a **cross-area contract** (like the AVR / TV / players DB
consistency guards): never add or remove a routing/monitor combo on one side without
the other side + its guards in the same change. The default install preset is
`http_handoff_http` ([`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) D-A).

## The README front-page status is part of every release

The repo front page (`README.md`) carries a hand-written **Current status** blurb and a
**Current release** table — both *outside* the `render_docs` generated block, so
`render_docs --write` does **not** touch them. Update them on **every release** to the shipped
versions: the add-on version / build identity / runtime-ZIP name **and** the Windows
configurator's new **Latest** tag, plus `Runtime behavior changed` / `Hardware validation
claimed`. A stale front page (it lagged at add-on v2.9.16 / configurator v0.8.5 while Latest was
v0.9.6) misleads users about what they're installing. The cut order is add-on first, configurator
(the repo's Latest) second; set the configurator line to the configurator version you ship this
session. `tests/test_readme_current_release.py` pins the add-on fields to `version.py` (CI fails
if the front page is stale); the configurator line stays norm-enforced. This is a required step
in the `release` runbook and the `done for the day` / handoff flow.

## CI runs locally — cloud CI is disabled

The add-on + configurator gate and release run **entirely on the local Windows+WSL
machine**; the cloud workflows are **disabled** (reversible). For a solo project the cloud's
only residual value — an independent "passes CI" stamp — wasn't worth ~5–6 min/PR + Claude
credit, and a WSL clean-room run across Python 3.9/3.10/3.12 catches the same issues.
**Merge-on-local-green is the default** (don't wait on a cloud re-run; there isn't one).

- **The gate is `scripts/ci-local.sh`** (`wsl bash scripts/ci-local.sh`) — a clean-room WSL
  gate (fresh `git clone` of HEAD, `uv`-managed venvs) that runs the full add-on gate on
  Python 3.12 (`ruff`, `mypy --gate`, full `pytest`, the **serial 99% coverage gate**,
  `audit_release`, runtime-ZIP + dev-source audits) plus a targeted compat-smoke on 3.9/3.10.
  It is a faithful superset of the old `ci.yml`; `tests/test_ci_local_gate.py` pins it to the
  same gate commands g6 pins for `ci.yml`. `scripts/verify.sh` remains the quick in-place gate
  and `scripts/hooks/pre-push` still enforces the coverage floor. One-time setup:
  `curl -LsSf https://astral.sh/uv/install.sh | sh && uv python install 3.9 3.10 3.12`.
- **Releases publish locally.** Add-on: `scripts/release-addon-local.ps1` (runtime ZIP + sha
  via WSL → `gh release create v<X> --title "v<X> Final" --latest=false`; the configurator
  holds Latest). Configurator: `scripts/release-configurator-local.ps1` (`npm run dist` →
  MSI/NSIS + SHA256SUMS → `gh release create configurator-v<Y> --latest`). Both take `-DryRun`.
  `*.sh` is pinned **LF** in `.gitattributes` so the WSL packaging runs on a Windows checkout.
  See [`docs/developer-guide/release-process.md`](docs/developer-guide/release-process.md).
- **The cloud workflow files stay in the repo, only disabled** (`gh workflow disable "CI"` /
  `"Configurator CI"` / `"Package Installable ZIP"`) — they are pinned by
  `tests/test_github_readiness_g6_ci_hardening.py`, so they are **never edited or deleted**;
  re-enable with `gh workflow enable` if cloud CI is ever wanted again. `claude-review` +
  `Claude Code` were already disabled. **Dependabot stays active.**

## Never edit operator-only / secret files

- `.claude/settings.local.json`
- `.env*`, `*credentials*`, signing keys, anything secret-bearing
