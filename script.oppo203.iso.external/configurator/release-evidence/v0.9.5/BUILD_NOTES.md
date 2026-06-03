# Configurator v0.9.5 — build notes

**Released:** 2026-06-03 · **tag:** `configurator-v0.9.5`
**Built + published by:** GitHub Actions (`.github/workflows/configurator-ci.yml` → `release` job) on the tag push.
**Bundles add-on:** v2.9.16 — the CI `bundle:addon` step repackages `main`'s add-on source (now the v2.9.16 maintenance/hardening release) into the installer.

## What shipped

Installer **single old-version prompt** — umbrella [ENH #334](https://github.com/skull-01/script.oppo203.iso.external/issues/334). An upgrade previously could show two "remove previous version" prompts (Tauri's built-in NSIS reinstall page **and** our PREINSTALL hook). This release suppresses the page and unifies removal behind one prompt, via a vendored NSIS template.

### 1. Vendor the Tauri 2.11.2 NSIS template + drift guard — [#335](https://github.com/skull-01/script.oppo203.iso.external/pull/335)

- `configurator/src-tauri/installer.nsi` is the exact `@tauri-apps/cli` **2.11.2** `installer.nsi` (verbatim, version-stamped header added); `bundle.windows.nsis.template` points at it.
- `src/installer-template.test.ts` pins the template's version stamp to the resolved `@tauri-apps/cli` in `package-lock.json` — a silent CLI bump fails the build until the template is re-vendored.
- Behavior-neutral on its own.

### 2. Suppress the reinstall page + broaden the hook — [#336](https://github.com/skull-01/script.oppo203.iso.external/pull/336)

- Removed the stock reinstall custom page (`PageReinstall` / `PageReinstallUpdateSelection` / `PageLeaveReinstall` + the `Page custom` insertion — 202 lines) from the vendored template.
- Broadened `installer-hooks.nsh` `NSIS_HOOK_PREINSTALL` to detect + remove a prior **NSIS** install (its `UninstallString`, run silently in place with `/S _?=<dir>`, settings preserved) in addition to the existing parallel-**MSI** case (disambiguated from our own NSIS key, named `${PRODUCTNAME}`).
- One `MB_YESNO` confirmation now covers any prior install → exactly one prompt on upgrade. The hook runs before files are copied and before the new uninstall key is written, so it sees the prior install's registry state.
- Known change: the silent-install (`/S`) downgrade auto-abort, which relied on the removed page's version compare, is now inert; GUI installs are unaffected.

### 3. Version bump → tag `configurator-v0.9.5`

`package.json` / `tauri.conf.json` / `Cargo.toml` / `Cargo.lock` bumped 0.9.4 → 0.9.5 (pinned by `version.test.ts`).

## Gates (software-verified only)

- Configurator: `tsc -b` clean · **vitest 359** (incl. `version.test.ts` consistency + the new `installer-template.test.ts` drift guard) · **`cargo test` 57** · `vite build`.
- **NSIS compile verified locally**: `tauri build --bundles nsis` ran `makensis` against the edited vendored template + hook and produced a working `*-setup.exe`. The configurator PR gate does **not** run `tauri build` — only this release tag job and the local build do — so the template was compiled before tagging.
- **Hardware validation NOT claimed.** The single old-version prompt on a real upgrade (install v0.9.4, then upgrade to v0.9.5 → confirm exactly one prompt and that settings survive) is Phase-C/operator — see [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## Artifacts + SHA-256

MSI + NSIS installers + `SHA256SUMS.txt` produced by the CI release job, attached to the published
release (**unsigned**). Verify against that file:

- https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.5
