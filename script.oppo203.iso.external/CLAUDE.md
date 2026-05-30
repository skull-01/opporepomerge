# CLAUDE.md

**Resuming work?** Read [`AI_RESUME_HANDOFF.md`](AI_RESUME_HANDOFF.md) first — it is the
session-continuity spine. Then [`AGENTS.md`](AGENTS.md) for the agent norms.

## Session commands

- **`resume`** — follow the **resume** command at the top of `AI_RESUME_HANDOFF.md` (§1).
- **`done for the day`** — follow the **done-for-the-day** command in
  `AI_RESUME_HANDOFF.md` (§2).

`AGENTS.md` rules override defaults. See §1 of the handoff for the full trigger
vocabulary (`confirmation queue`, `bugs`, `enhancements`, `backlog audit`, `dev note:`,
`build plan`, `refresh the build plan`, `plan` / `scope this`). Plan requests follow the
canonical **Plan format** in `AGENTS.md` (ground → per-PR scope → rollup → risks → Go/Wait/Replan).

## Hard rules

- **Pull before changes.** `git pull` before editing.
- **Never touch operator-only files** without permission: `.claude/settings.local.json`,
  anything secret-bearing (`.env`, credentials, signing keys).
- **Only commit successful agent-made changes.** Failing tests stay un-committed unless
  explicitly checkpointed as `wip:` per the done-for-the-day flow.
- **Only the operator closes issues.** Never `gh issue close`. Never
  `Closes/Fixes/Resolves #N` in commit messages or PR descriptions. When work seems done:
  1. Comment the implementing SHA(s) on the issue.
  2. Add verification steps to
     [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md)
     for the operator to verify and close.
