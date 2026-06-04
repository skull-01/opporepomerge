# Dev notes — operator's verbatim instructions

Operator reference, extracted from `AI_RESUME_HANDOFF.md` §20 so it stays out of the
resume-read handoff. **Append-only.** Each entry: `### YYYY-MM-DD HH:MM — dev note` followed by
the operator's text **VERBATIM** — no summarizing, no editing. Added via the `dev note:` trigger.

### 2026-05-31 13:05 — dev note

main's CI is red on ruff format --check — but it's pre-existing and unrelated to these PRs. Three add-on test files (tests/test_all.py, test_players_db_consistency.py, test_v2910_build2_player_taxonomy.py) have formatting drift; ruff check itself passes. None of the merged PRs touch Python, so they neither caused nor worsened it. I've queued a task chip to fix it (one ruff format run + full-suite re-verify, as a draft area:addon PR) — click to spin it off, or dismiss.
