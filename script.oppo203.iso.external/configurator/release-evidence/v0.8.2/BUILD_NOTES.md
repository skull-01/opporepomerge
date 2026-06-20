# Configurator v0.8.2 — Reset all configurations (bundles add-on 2.9.15)

**Built:** 2026-06-03 · **Source:** `main`@`0105002` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

The Windows binary of the OppoKodiAddon Configurator, distributed as the GitHub release tagged
`configurator-v0.8.2` (holds the repo "Latest"). It adds the Reset-all action and bundles the
add-on (v2.9.15 code with the 2026-06-02 audit-remediation fixes).

- **Reset all configurations (Danger zone, PR #260).** A confirm-gated dashboard button that
  deletes the add-on + every file the configurator copied to the Kodi box (the add-on folder
  under addons/, and under userdata/: playercorefactory.xml, keymaps/oppo203iso.xml,
  addon_data/<id>) via the deployed tier (SSH for A + Kodi restart; SMB/local for B; tier C
  copied nothing), then resets the configurator to first-run (clears state.json, dashboard/,
  generated/) and returns to the first screen. Only the four configurator-owned paths are
  removed; the userdata/addons roots and unrelated files survive. New Rust reset_box_ssh /
  reset_box_userdata / reset_app_data + reset.ts (pure per-tier router) + ResetAllCard.tsx.

The binaries are not committed (target/ is git-ignored); this file records their identity.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.8.2_x64_en-US.msi` (MSI) | 3,686,400 B | `cd47691ddde4d5791457f3371f25a46d39b9543eb859993d21fb1876d872a58a` |
| `OppoKodiAddon Configurator_0.8.2_x64-setup.exe` (NSIS) | 2,539,158 B | `619bff5ff4dd18dce7ec222ac13c778d239bfeeb7c719cb5dd5056bc6f01d268` |

Bundled add-on: **v2.9.15** (verified inside `src-tauri/resources/addon/script.oppo203.iso.external.zip`).
Verify after download (PowerShell): `Get-FileHash <file> -Algorithm SHA256`.

## Build environment

- Windows 11 (x64); Node 20+ / npm 10+; Rust / cargo (MSVC toolchain); Tauri CLI 2 —
  `npm run dist` (= `bundle:addon` + `tauri build`); see [`configurator/BUILD.md`](../../BUILD.md).

## Software gates (this build)

- `tsc --noEmit` 0 · **301 vitest** (incl. the reset per-tier routing, `version.test.ts` 3-file
  pin, and the `tv_db_consistency` two-copy guard) · `cargo test` (incl. the reset path-construction
  + idempotent-removal tests) · `vite build` OK.

## Caveats

- **Unsigned**; **software-verified only**. The on-box deletion + Kodi restart are **NOT
  hardware-validated** — verify the Reset action against a test box before relying on it.

## Phase C — operator end-to-end (clean Windows host + a TEST Kodi box)

1. Install from the `configurator-v0.8.2` release; verify SHA-256; confirm it launches.
2. Configure + Apply to a **test** Kodi box, then use **Danger zone → Reset all configurations**;
   confirm the add-on folder + `playercorefactory.xml` + the keymap + `addon_data/<id>` are gone,
   unrelated `userdata` files survive, Kodi restarts (tier A), and the configurator returns to
   first-run.
3. Re-run the wizard from scratch to confirm pristine first-run state.
4. Uninstall via Apps & features (or the MSI); confirm clean removal.
