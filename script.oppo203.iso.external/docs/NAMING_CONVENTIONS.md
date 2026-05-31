# Naming conventions

How the four control domains are named across the add-on, the configurator, and the UI, plus
the 2026-05-31 consistency renames. This is the canonical reference that the "naming note"
flags scattered through the historical docs point at.

## The four domains

The system controls four things; each owns a name used consistently across layers:

| Domain | Add-on package | Settings prefix | Configurator | UI label |
|---|---|---|---|---|
| **Kodi box** (the host) | `resources/lib/kodi/` | — (held configurator-side) | `kodi*` state | "Kodi box" |
| **TV** | `resources/lib/tv/` | `tv_*` | `tv-models.json` / `tvdb.ts` / `tv*` state | "TV" |
| **OPPO / clone player** | `resources/lib/oppo/` | `oppo_*` | `players-models.json` / `playersdb.ts` / `player*` state | "Player" |
| **AV receiver** | `resources/lib/avr/` | `avr_*` | `avr-models.json` / `avrdb.ts` / `avr*` state | "AV Receiver" |

### Two rules worth knowing

1. **Sub-package = namespace.** A module inside a bucket need not repeat the bucket name — the
   import path already carries it (`tv.tv_control`). The **TV and AVR backend *drivers* do carry
   the domain prefix** (`tv_adb_control`, `avr_denon_marantz`) so a file "about TV" reads as TV;
   generic helpers (`oppo/command_map`, `kodi/installer`) stay function-named.
2. **OPPO has two legitimate names — by role.** Its *chain role* is **player** (the thing that
   plays the disc): UI "Player", `player*` state, `external_player`, `avr_player_input`,
   `playercorefactory`. Its *brand / protocol / settings identity* is **oppo**: the `oppo/`
   package, `oppo_control`, and the install-base-locked `oppo_*` settings. `mapping.ts` is the
   seam (`playerIp → oppo_ip`). OPPO is also just one `playerBrand` among the clones (Chinoppo,
   Magnetar, Reavon, CineUltra, GIEC, IPUK), which is why the configurator DB is "players".

## 2026-05-31 consistency renames

A naming audit found three inconsistencies; all three were fixed (PRs #124–#127):

| What | Before | After | Why |
|---|---|---|---|
| TV backend modules | `adb_control.py`, `roku_ecp_control.py`, `smartthings_control.py` | `tv_adb_control.py`, `tv_roku_ecp_control.py`, `tv_smartthings_control.py` | Parity with the `avr_`-prefixed AVR drivers — a file "about TV" now carries `tv_`. |
| Player DB filename | `players.json` | `players-models.json` | Parity with `tv-models.json` / `avr-models.json`. |
| Configurator state field | `oppoInput` | `playerInput` | It was the lone `oppo`-named field in an otherwise `player*` state slice. |

Renames were content-preserving (module bodies unchanged; the two DB copies stay byte-identical).
Intentionally **not** renamed: the install-base-locked `oppo_*` settings (stored values), and the
numbered wizard screens (`step2.tsx` = "Player", etc., which match the displayed step numbers).

## Historical docs

Build notes, changelogs, `docs/release-history/*`, the `Combined_AI_Handoff_*` files, and closed
verification-checklist entries that predate these renames keep the **old** names on purpose —
they record what shipped at the time (some even cite the pre-`tv/`/`oppo/` flat paths like
`resources/lib/adb_control.py`). Those spots carry a short **"naming note"** flag pointing here,
so a reader knows the current name differs without the historical record being rewritten.
