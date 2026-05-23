# CLAUDE.md

Start by reading **[`AI_RESUME_HANDOFF.md`](AI_RESUME_HANDOFF.md)** (session-continuity entry
point), then **[`AGENTS.md`](AGENTS.md)** for the agent norms. Contributor rules:
[`CONTRIBUTING.md`](CONTRIBUTING.md).

Honor the session commands **`resume`** and **`done for the day`** (and the slash commands
`/resume`, `/done-for-the-day`, `/release`) — full specs are in `AI_RESUME_HANDOFF.md` under
"Commands this repo understands". Pull before work; validate with `pytest -n auto` before
committing; branch + PR to `main`; never commit secrets; keep commit messages plain (no
agent co-author footer); and end each change with one copy-paste test command.
