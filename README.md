# opporepomerge

A consolidation of three related Oppo / Kodi projects into a single repository.
Each source project keeps its full git history and lives in its own subdirectory.

## Contents

| Subdirectory | Source repo | Description |
|---|---|---|
| [`script.oppo203.iso.external/`](script.oppo203.iso.external/) | [skull-01/script.oppo203.iso.external](https://github.com/skull-01/script.oppo203.iso.external) | Kodi script add-on for Oppo BDP-20x external ISO playback (configurator, CI, docs). |
| [`OppoKodiBridge/`](OppoKodiBridge/) | [skull-01/OppoKodiBridge](https://github.com/skull-01/OppoKodiBridge) | Kodi service add-on bridging Kodi and the Oppo player (`service.oppokodibridge`). |
| [`OppoKodiBridge-v3/`](OppoKodiBridge-v3/) | [skull-01/OppoKodiBridge-v3](https://github.com/skull-01/OppoKodiBridge-v3) | v3 of the bridge service add-on (`service.oppokodibridge.v3`). |

## History

This repo was assembled with `git filter-repo --to-subdirectory-filter`, so every
commit from each source repository is preserved with its files already namespaced
under the subdirectory above. `git log` and `git blame` work across the full
timeline of each project.

### Branches

Every branch from all three source repos is preserved, namespaced as `<subdir>/<branch>`
(e.g. `script.oppo203.iso.external/release/v2.9.13`, `OppoKodiBridge-v3/ir-blaster-integration`).
Each repo's `main` is also kept as `<subdir>/main`, and all of them are ancestors of the
consolidated `main`, so the branches share commit identity with the merged history rather than
forming parallel lines.

The combined `main` is the consolidation; the per-repo `<subdir>/main` branches are the exact
original tips of each source repo, relocated under their subdirectory.
