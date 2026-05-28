# Agent norms — `script.oppo203.iso.external`

Spine: [`AI_RESUME_HANDOFF.md`](AI_RESUME_HANDOFF.md). Read it first; come back here for
the rules below. Contributor norms: [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Issue / PR model (hybrid)

- **Issues** track bugs (`type:bug`) and enhancements (`ENH-` prefix). The operator files
  most; agents file `type:bug` on bug reports per the operator's personal norm.
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

## Session shape — one theme per session, cap ≈ 4 PRs

Each session sticks to **one theme** (e.g. "port screens", "wire SFTP probes", "rename
installer→configurator"). **Don't mix themes within a session** — proven in retros that
mixing themes is where bugs slip in. If the operator nudges into a second theme, suggest
finishing the current one and resuming next session. Soft cap **≤ 4 PRs per session.**

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

## Never edit operator-only / secret files

- `.claude/settings.local.json`
- `.env*`, `*credentials*`, signing keys, anything secret-bearing
