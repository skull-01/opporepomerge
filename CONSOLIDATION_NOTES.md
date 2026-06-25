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

### v3 working-tree contents (intentional union)

The v3.1.0 line ("Overwrite v3 add-on with the pure-CEC handoff line") replaced the
older Broadlink-IR approach. To retain all unique information, the working tree
keeps **both** approaches side by side under
`OppoKodiBridge-v3/service.oppokodibridge.v3/resources/lib/`:

- **Current (v3.1.0, pure-CEC):** `cec.py`, `service_cec.py`, plus `detector.py`,
  `monitor.py`, `orchestrator.py`, etc.
- **Superseded (pre-v3.1.0 IR):** `ir.py`, `service_v3.py` — retained for
  completeness. The exact pre-v3.1.0 state is also the `OppoKodiBridge-v3/main`
  branch. `addon.xml` ships the pure-CEC service as the entry point.

## Dropped from the consolidated tree

Built release `.zip` artifacts (`service.oppokodibridge-2.0.x`, the v3 / CEC /
cecreclaim zips) were **not** carried over — they are reproducible build output
(gitignored in every source repo) and remain available on each repo's GitHub
Releases. The original standalone working folders were moved to a sibling
`_archive/` directory (outside this repo) rather than deleted.

## Branch layout

`main` is untouched. The consolidation work is on
`consolidate/fold-cec-and-v3.1.0`. Promote to `main` when ready.
