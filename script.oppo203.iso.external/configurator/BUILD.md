# Building the Windows binary

The configurator is a Windows desktop app (Tauri 2). A release build produces an
MSI installer, an NSIS setup `.exe`, and a raw `.exe`.

## Prerequisites

One-time setup (see [`AI_RESUME_HANDOFF.md`](../AI_RESUME_HANDOFF.md) §2a rows 7–13
for exact winget commands):

- **Node 20+** and **npm 10+**
- **Rust 1.77+** (`rustup`, MSVC toolchain)
- **MSVC Build Tools** (the C++ linker Tauri needs)
- **WebView2 runtime** (bundled with Windows 11)
- the committed icon set under `src-tauri/icons/` (already present)

Install JS deps once: `cd configurator; npm install`.

## Build

```
cd configurator; npm run dist
```

`npm run dist` is an alias for `tauri build` (equivalently `npm run tauri -- build`).

- The first build on a fresh machine downloads the **WiX** (MSI) and **NSIS**
  toolchains, so it needs network access; later builds use the cache and run
  offline. *(Agents: this is why the build step runs with the sandbox disabled.)*
- Release compile + bundle takes ~1–2 minutes warm.

## Outputs

Under `configurator/src-tauri/target/release/`:

| Artifact | Path |
|---|---|
| MSI installer | `bundle/msi/OppoKodiAddon Configurator_<version>_x64_en-US.msi` |
| NSIS setup | `bundle/nsis/OppoKodiAddon Configurator_<version>_x64-setup.exe` |
| Raw executable | `oppokodiaddon-configurator.exe` |

`target/` is git-ignored — **never commit the binaries.** Attach them to a GitHub
release and record SHA256 checksums under `release-evidence/`.

## Versioning

The version is pinned in **three** files that must agree (guarded by
`src/version.test.ts`): `package.json`, `src-tauri/Cargo.toml`, and
`src-tauri/tauri.conf.json`. Bump all three together, then tag
**`configurator-v<version>`** — a distinct namespace from the add-on's `v*` tags,
so the add-on's `package.yml` workflow is not triggered.

## Signing

The first binaries are **unsigned**, so Windows SmartScreen shows an "unknown
publisher" warning on install. State this in the release notes. Code signing (an
OV/EV certificate + a CI secret) is a future enhancement.
