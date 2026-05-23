---
description: Stop cleanly — push all work, refresh AI_RESUME_HANDOFF.md, end-of-day summary
---

The maintainer typed `done for the day`. Follow the spec in `AI_RESUME_HANDOFF.md`
("Commands this repo understands") exactly. Do NOT start new feature work.

1. **Push ALL current work** — nothing stays only on this machine. On the current branch:
   `git add -A` (do NOT stage `.claude/settings.local.json`), run the tests
   (`pytest -n auto` with the Windows temp workaround from the handoff doc), then commit —
   a normal message if finished and green, or a `wip:` checkpoint commit that notes what's
   unfinished and the test status if not — then `git push`.
2. **Overwrite "Work in progress (resume here first)"** in `AI_RESUME_HANDOFF.md` with:
   date, current commit, task in flight, what's done, what's left, key files, related
   PR/branch, and whether tests pass (or "None — clean stopping point").
3. **Run the maintenance recipe** ("How to update this document") to refresh the journey,
   issue-tracker state, tests, and the header "last sync ≈ commit".
4. **Commit & push the updated doc.** It lives on `main`; your work was committed in step 1,
   so updating `main` is safe (see the doc's recipe; open a quick doc-only PR if branch
   protection requires it).
5. Reply with an **end-of-day summary** (what shipped or was checkpointed, and where to
   resume next time).
