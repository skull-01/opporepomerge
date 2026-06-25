# Consolidation notes

This repository (`opporepomerge`) is the single consolidated home for all the
related Oppo / Kodi add-on projects. It was originally assembled with
`git filter-repo --to-subdirectory-filter` so each source project keeps its full
git history under its own subdirectory (see `README.md`).

## 2026-06-25 — folded in the two remaining standalone projects

Two projects that previously lived in sibling folders were folded in on the
branch `consolidate/fold-cec-and-v3.1.0`, each preserved with full history and a
namespaced branch (matching the existing `<subdir>/<branch>` convention):

| Subdirectory | Source repo | Namespaced branch | Notes |
|---|---|---|---|
| `CEC-Control-Experiment/` | `skull-01/CEC-Control-Experiment` | `CEC-Control-Experiment/main` | 4th project: `service.oppokodibridge.cec` 0.4.5 + `script.cecreclaim` 0.1.0 + a desktop `cec_switcher` helper. Not previously in this repo. |
| `OppoKodiBridge-v3/` (updated to **v3.1.0**) | `skull-01/OppoKodiBridge-v3` (newer tip) | `OppoKodiBridge-v3/v3.1.0-rel` | The "pure-CEC handoff" v3.1.0 line, plus `docs/IR_INTEGRATION.md`, `tools/learn_ir.py`, `settings_tests.py`, and the full test suite. |

### v3 working-tree contents — and where the IR path actually lives

The v3.1.0 line ("Overwrite v3 add-on with the pure-CEC handoff line", `b4c4759`)
replaced the older Broadlink-IR approach. The v3 **working tree** under
`OppoKodiBridge-v3/service.oppokodibridge.v3/resources/lib/` therefore holds:

- **Current (v3.1.0, pure-CEC):** `cec.py`, `service_cec.py`, plus `detector.py`,
  `monitor.py`, `orchestrator.py`, etc. `addon.xml` ships `service_cec.py` as the
  entry point.
- **Two pre-v3.1.0 leftovers re-added by the consolidation (`bfa7753`):**
  `ir.py` and `service_v3.py`. **Important:** the working-tree `ir.py` is only the
  38-line **v3.0.0 stub** ("stubbed until the RM4 is in hand / not yet
  implemented") — it is **not** the real IR client.

**The complete IR implementation is NOT in the working tree.** The hand-rolled
364-line `broadlink_rm4.py` (stdlib-only Broadlink client + vendored pure-Python
AES-128), the real ~94-line `ir.py` sequencing/reliability layer, and
`tests/test_broadlink_rm4.py` were deleted from v3 at `b4c4759` and were **not**
re-added here. They survive — fully — on the preserved branches
**`OppoKodiBridge-v3/ir-blaster-integration`** and **`OppoKodiBridge-v3/main`**.
So per the "preserve full history" choice, no unique information is lost, but the
IR subsystem is recoverable only from those branches, e.g.:

```
git show OppoKodiBridge-v3/ir-blaster-integration:OppoKodiBridge-v3/service.oppokodibridge.v3/resources/lib/broadlink_rm4.py
```

(This corrects an earlier draft of these notes that described the working tree as
an IR/CEC "union" — the real IR code was never in the tree.)

## Dropped from the consolidated tree

Built release `.zip` artifacts (`service.oppokodibridge-2.0.x`, the v3 / CEC /
cecreclaim zips) were **not** carried over — they are reproducible build output
(gitignored in every source repo) and remain available on each repo's GitHub
Releases. The original standalone working folders were moved to a sibling
`_archive/` directory (outside this repo) rather than deleted.

## Branch layout

`main` is untouched. The consolidation work is on
`consolidate/fold-cec-and-v3.1.0`. Promote to `main` when ready.
