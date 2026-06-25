# OppoKodiBridge-v3 — Pull Requests (1)

Archived 2026-06-25. Full machine-readable data in [`pulls.json`](pulls.json). Where a PR had discussion, its conversation and inline review comments are inlined below and stored in [`comments/pr-<N>-*.json`](comments/). The code changes themselves live in this repo's git history.

| PR | Title | State | Author | Base ← Head | Date |
|---|---|---|---|---|---|
| [#1](https://github.com/skull-01/OppoKodiBridge-v3/pull/1) | Broadlink RM4 IR integration for v3 (superseded by the CEC fork) | MERGED | skull-01 | `main` ← `ir-blaster-integration` | 2026-06-20 |

---

## PR descriptions & discussion

### #1 — Broadlink RM4 IR integration for v3 (superseded by the CEC fork) [MERGED]
A complete, tested Broadlink RM4 mini IR-blaster path for CEC-free TV input switching, built before the operator chose the pure-CEC (power-cycle) approach and forked it into skull-01/CEC-Control-Experiment instead. Preserved here OFF main in case the IR option resurfaces (e.g. if CEC proves unreliable on hardware).

  - resources/lib/broadlink_rm4.py: minimal RM4 client (discover/auth/send/learn) + vendored pure-Python AES-128 (CoreELEC lacks cryptography); FIPS-197 KAT-pinned
  - resources/lib/ir.py: sequencing/reliability layer (discrete code OR nav sequence)
  - resources/lib/handoff.py: fire the IR switch at the post-is_playing boundary, threaded
  - resources/lib/config.py: from_addon reads the broadlink/ir settings (a real wiring fix)
  - tools/learn_ir.py: capture/replay tool; docs/IR_INTEGRATION.md: the full verified design
  - 47 off-box tests pass

Not on main; v3 main stays the no-IR playercorefactory fork.

---
