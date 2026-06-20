# Configurator v0.8.6 — CI/release automation + diagnostics + single-prompt installer + i18n (bundles add-on 2.9.15)

**Built:** 2026-06-03 · **Source:** `main`@`2eaf1a7` (tag `configurator-v0.8.6`) ·
**Status:** software-verified only; **unsigned**; no hardware validation.

**First release built and published by CI** — not a manual `npm run dist`. Pushing the
`configurator-v0.8.6` tag triggered `.github/workflows/configurator-ci.yml`: the windows-latest
gate (tsc -b + vite build + vitest + bundle add-on + cargo test) ran, then the release job built
the MSI/NSIS via `npm run dist`, computed SHA-256, and published this GitHub release as Latest.

This is the EOD #14 seven-theme infra/hardening batch (operator: "do all of this automatically"):

- **CI / release automation (PR #272)** — the configurator's first GitHub Actions workflow (gate on
  every configurator PR; tag-triggered MSI/NSIS build + publish). The first run caught a real gap:
  tauri's `build.rs` needs the bundled add-on zip, so the gate runs `bundle:addon` (+ Python) before
  `cargo test`.
- **Diagnostics export (PR #273)** — a dashboard "Export diagnostics" card: a sanitized JSON support
  bundle (app version + OS + recent activity log + session history + config, secrets redacted via the
  shared redactor) written to app-data, plus copy-to-clipboard. Rust `diagnostics_env`/`write_diagnostics`.
- **Single-prompt installer (PR #274)** — `installer-hooks.nsh` scoped to the parallel-MSI case Tauri's
  reinstall page misses, so a normal NSIS upgrade shows one prompt, not two.
- **i18n scaffold (PR #277)** — `i18n.ts` (`t()` + typed English catalog); `WinShell` migrated as the
  first consumer. English-only; remaining screens migrate incrementally.
- **Add-on test hardening (PR #276)** — property tests for the HTTP/SVM3 predicates; caught + fixed a
  real `OverflowError` on `int(float("inf"))` in `http_info_indicates_playing` (issue #275).
- **Repo hygiene (PR #271)** — gitignore local scratch; fix the stale `audit_release` doc version.

The binaries are not committed (`target/` is git-ignored); this file records their identity.

## Artifacts

| Artifact | Size | SHA-256 |
|---|---|---|
| `OppoKodiAddon Configurator_0.8.6_x64_en-US.msi` (MSI) | 3,694,592 B | `63ca1f8c5b5964bf1b8aaab30ad8706e98b91e58bc03b197408ce0f47c796356` |
| `OppoKodiAddon Configurator_0.8.6_x64-setup.exe` (NSIS) | 2,554,907 B | `8988059a77151e8462749fe468e279baa22d02151c9fa178bc9ce351b713558d` |

A `SHA256SUMS.txt` is attached to the release. Bundled add-on: **v2.9.15**.

## Build environment

- GitHub Actions `windows-latest`; Node 20; Python 3.12; Rust stable (MSVC); Tauri CLI 2 — via
  `.github/workflows/configurator-ci.yml` (`npm run dist`).

## Software gates (this release)

- Gate job green: `tsc -b` + `vite build` + vitest + `cargo test` (after `bundle:addon`).
- Add-on tests on `main` (PR #276): `pytest -n auto` 1158/3, serial coverage 99%, mypy --strict 51/0,
  ruff clean.

## Caveats

- **Unsigned**; **software-verified only.** Installer runtime, the on-box reset path, the diagnostics
  file write/clipboard, and the single-prompt upgrade flow are **operator (Phase C)** — see the EOD #14
  batch entry in `docs/MANUAL_VERIFICATION_CHECKLIST.md`.

## Phase C — operator end-to-end (real Windows host)

1. Install the published MSI/NSIS; verify SHA-256 against the table above; smoke-test the wizard.
2. Upgrade over a prior **NSIS** install → confirm a single old-version prompt (not two).
3. On the dashboard, **Export diagnostics** → confirm the JSON writes, secrets read `[redacted]`, and
   copy-to-clipboard works.
