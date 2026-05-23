# Agent instructions — `script.oppo203.iso.external`

**Read [`AI_RESUME_HANDOFF.md`](AI_RESUME_HANDOFF.md) first.** It is the session-continuity
entry point: how to run/test, build norms, architecture, the development journey, and the
**"Work in progress (resume here first)"** pointer. Deeper companion:
[`docs/ai-handoff/AI_RESUME_GUIDE.md`](docs/ai-handoff/AI_RESUME_GUIDE.md). Contributor
norms: [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Session commands (honor these exactly — full specs in AI_RESUME_HANDOFF.md)
- **`resume`** — read `AI_RESUME_HANDOFF.md` (esp. "Work in progress") and these instruction
  files; run the **environment preflight** (readiness checklist in §2 — auto-install missing
  `.venv`/dev deps/paramiko, surface missing system tools like Python/git/gh auth); report
  the **last 5 PRs created** and **last 5 PRs merged** (`gh pr list ...` — this repo tracks
  work as PRs, not Issues); suggest next steps with any unfinished "Work in progress" task
  FIRST; then STOP for the maintainer.
- **`done for the day`** — push ALL current work (a normal commit if green, else a `wip:`
  checkpoint; then `git push` — nothing left only on this machine); overwrite "Work in
  progress"; run the doc's maintenance recipe; commit & push the doc; give an end-of-day
  summary. Do NOT start new feature work.
- **`update AI_RESUME_HANDOFF.md`** — run the maintenance recipe in that doc.

Slash-command equivalents: `/resume`, `/done-for-the-day`, `/release`.

## Working norms (see CONTRIBUTING.md + the handoff doc)
- Pull before work. Make changes on a branch and open a PR to `main` (merge commit); don't
  commit code directly to `main`.
- Validate with the project's tests before committing: `pytest -n auto` (Windows: set
  `TEMP`/`TMP` to a repo-local dir and pass `--basetemp=build\_pt`). The coverage gate runs
  **serial** (never `-n auto`).
- Never edit user-specific/secret files (`.claude/settings.local.json`) or commit
  credentials. Never weaken the "software-verified / hardware validation not claimed" wording.
- Prefer surfacing real errors over silent fallbacks.
- Plain commit messages — **no `Co-Authored-By` agent footer**.
- ALWAYS end a change with a single copy-paste command the maintainer can run to test it.
