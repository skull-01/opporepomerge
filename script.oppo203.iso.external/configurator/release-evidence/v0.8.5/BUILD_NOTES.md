# Configurator v0.8.5 — Reset-all: no hang on unreachable devices + live progress (bundles add-on 2.9.15)

**Built:** 2026-06-03 · **Source:** `main`@`4176d0c` (Tauri 2 + React/TS configurator) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

The Windows binary of the OppoKodiAddon Configurator, distributed as the GitHub release tagged
`configurator-v0.8.5` (holds the repo "Latest"). It fixes the Reset-all hang on unreachable devices,
adds live progress, and bundles the add-on (v2.9.15).

- **Reset-all hang fix + live progress (PR #267, issue #266).** Reset-all previously froze the UI for
  ~40s when the Kodi box was unreachable (tier A fires five sequential `ssh` `ConnectTimeout=8` calls)
  or on dead-SMB filesystem timeouts (tier B), with the window stuck on "Resetting…"; a box failure
  also aborted the whole reset before the local state was cleared.
  - `reset_box_ssh` (Rust) does a fast SSH-port-22 reachability pre-probe (`connect_timeout` 2.5s) and
    fails in seconds with a clear message; `reset_box_userdata` probes the SMB share (port 445) for a
    UNC target first. Both emit a `reset-progress` event per step. New pure `unc_host()` + `ResetProgress`.
  - `resetEverything` (TS) runs the box and local resets as **separate stages**, so a box failure no
    longer blocks the local reset — "start over" always works; reports `boxFailed` for partial success.
  - `ResetAllCard` renders a live step list (pending/running/done/failed) + the granular `reset-progress`
    line, shown on both reachable entry points (header / Step 0 → ResetAll screen, and the dashboard).
  - The set of deleted paths is unchanged (the four configurator-owned paths, pinned by `box_reset_targets`).

The binaries are not committed (`target/` is git-ignored); this file records their identity.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.8.5_x64_en-US.msi` (MSI) | 3,690,496 B | `8ec13a9bacbc2a9179294632aa97382ec4a55430f9144324234958be3ab89440` |
| `OppoKodiAddon Configurator_0.8.5_x64-setup.exe` (NSIS) | 2,549,305 B | `94d60f65015768662566715047a98c44a947ea319416ee99240d818259c81be7` |

Bundled add-on: **v2.9.15** (verified inside `src-tauri/resources/addon/script.oppo203.iso.external.zip`).

## Build environment

- Windows 11 (x64); Node 24 / npm 11; Rust / cargo 1.95 (MSVC); Tauri CLI 2 — `npm run dist`.

## Software gates (this build)

- `cargo test` **43** (+1 `unc_host`) · `tsc -b` 0 · **311 vitest** (+7 in `reset.test.ts`) · `vite build`
  OK · `npm run dist` produced the MSI + NSIS above.
- **Browser-verified** (vite dev): both entry points reach the ResetAll screen; the live "Reset progress"
  step list renders; because vite dev has no Tauri runtime the `invoke` fails and the step shows `failed`
  with its detail + the summary message — proving the step list + failure rendering and that it does
  **not freeze**; no console errors.

## Caveats

- **Unsigned**; **software-verified only**. The destructive on-box deletion + Kodi restart and the real
  fast-fail timing against a powered-off box are **NOT hardware-validated** — unchanged from v0.8.2.

## Phase C — operator end-to-end (real Windows host / Kodi box)

1. With the **Kodi box powered off / unreachable**, run **Reset all configurations**; confirm it fails
   fast (~2.5s, not a ~40s freeze) with a clear message, and that the configurator **still returns to
   first-run** (local state cleared).
2. With the **box reachable**, run the reset; confirm the live step list shows each owned path being
   removed and the Kodi restart, and that the add-on + deployed files are actually deleted from the box.
3. Verify SHA-256 of the downloaded artifacts against the table above.
