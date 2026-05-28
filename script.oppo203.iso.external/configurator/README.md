# OppoKodiAddon Configurator (Windows companion app)

A Windows desktop app that **configures** the
[`script.oppo203.iso.external`](../README.md) Kodi add-on after it has been
installed in Kodi. Walks the user through setting up the Kodi → TV →
OPPO/clone playback handoff: writes `playercorefactory.xml` + the
remote-bridge keymap into Kodi's `userdata/`, captures HDMI input topology,
and runs honest connectivity probes against the user's TV and player.

It does **not** install the add-on itself — that goes through Kodi's normal
add-on mechanism. The add-on's
[allowlist-driven packager](../tools/package_installable_zip.py) only ships
`addon.xml`, `default.py`, `service.py`, and `resources/`; `configurator/` is
excluded from the Kodi-installable zip by default.

## Status

**Scaffold only.** The shell renders, Direction A theme tokens are wired in,
and the wizard router walks all 23 screens — but only Step 0 (gate + exit
branch) is fully ported from the design prototype. The other 21 screens are
navigable stubs marked `// TODO`. See
[`docs/installuidraft/design_handoff_oppo_installer/`](../docs/installuidraft/design_handoff_oppo_installer/)
for the authoritative design.

## Stack

- **Tauri 2** — Rust core, web frontend, native Windows window chrome
- **React 18 + TypeScript** — frontend, lifted from the prototype's JSX
- **Vite 5** — dev server + bundler
- **No CSS framework** — design tokens copied verbatim from
  [`prototype/styles.css`](../docs/installuidraft/design_handoff_oppo_installer/prototype/styles.css)
  (Direction A only; the other two aesthetic directions and the design-time
  tweaks panel are intentionally dropped)

## Layout

```
configurator/
├── README.md                ← you are here
├── package.json             ← frontend deps + npm scripts
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── index.html               ← Vite entry; loads Google Fonts (DM Sans, JetBrains Mono)
├── src/
│   ├── main.tsx             ← React root mount
│   ├── App.tsx              ← router + wizard state
│   ├── styles.css           ← Direction A (light + dark) tokens + component CSS
│   ├── icons.tsx            ← line-based 24×24 SVG icon set (30+ icons)
│   ├── state.ts             ← WizardState type, chain-completion derivation
│   ├── steps.ts             ← step ↔ screen mapping tables
│   ├── shell/               ← persistent chrome
│   │   ├── WinShell.tsx     ← title bar + body
│   │   ├── Chain.tsx        ← Media → Kodi → TV ⇄ Player topology
│   │   ├── Progress.tsx     ← stepper variant
│   │   ├── Sidebar.tsx      ← sidebar variant
│   │   ├── AppHeader.tsx    ← progress + chain composition
│   │   ├── FooterNav.tsx    ← shared Back/Continue row
│   │   └── DiagLog.tsx      ← diagnostic-log result list (used in 6 screens)
│   └── screens/
│       ├── Step0Gate.tsx    ← ported
│       ├── Step0Exit.tsx    ← ported
│       └── stubs.tsx        ← 21 placeholder screens with nav wired through
└── src-tauri/
    ├── Cargo.toml
    ├── build.rs
    ├── tauri.conf.json      ← 1180×820 default, 1000×720 min, decorations off
    ├── capabilities/
    │   └── default.json
    └── src/
        ├── main.rs
        └── lib.rs
```

## Develop

Requires Node 20+, Rust 1.77+, and (on Windows) the [Tauri 2 Windows
prerequisites](https://v2.tauri.app/start/prerequisites/#windows) (Microsoft
C++ Build Tools + WebView2). On Linux/macOS you can run the frontend bits but
the Tauri shell targets Windows.

```bash
cd configurator
npm install
npm run tauri dev    # launches the native window with hot-reload
```

Frontend-only dev (no Tauri shell, just the React app in a browser):

```bash
npm run dev          # → http://localhost:1420
```

Build a release `.msi` / `.exe`:

```bash
npm run tauri build  # outputs to src-tauri/target/release/bundle/
```

## A note on terminology

The design handoff folder still uses the legacy word "installer" in its
filenames and prose (`design_handoff_oppo_installer/`, `OPPO Installer
Wizard.html`) because it was authored before this distinction was settled.
The product is a **configurator**: the Kodi add-on is installed by Kodi; this
app sets it up.

## Next milestones

1. **Port the remaining 21 screens** from `prototype/screens-1.jsx` and
   `prototype/screens-2.jsx`. Each screen is self-contained and < 120 lines.
2. **Wire side effects** behind the diag logs — replace mocked checks with
   real probes (SFTP via `ssh2-sftp-client`-equivalent, SMB probes, TCP
   port knocks for backend detection, ADB / Roku ECP / Sony / etc.).
3. **State persistence** to `%APPDATA%/OppoKodiAddonConfigurator/state.json`
   so the wizard resumes after a crash or restart.
4. **File generation** for `playercorefactory.xml` + the remote-bridge
   keymap. The add-on's Python side already has the generation logic — the
   configurator either calls into the add-on's tooling over SSH/SMB or
   reimplements the small bits in Rust.
5. **App icon + bundling.** The placeholder `O`-on-gradient title-bar icon
   should be replaced before any release build.

## Design source

- [`docs/installuidraft/design_handoff_oppo_installer/README.md`](../docs/installuidraft/design_handoff_oppo_installer/README.md) —
  full handoff with the 23-screen table, component map, and animation specs
- [`docs/installuidraft/design_handoff_oppo_installer/source_design_doc.md`](../docs/installuidraft/design_handoff_oppo_installer/source_design_doc.md) —
  the product spec; authoritative for behavior
- [`docs/installuidraft/design_handoff_oppo_installer/prototype/`](../docs/installuidraft/design_handoff_oppo_installer/prototype/) —
  clickable HTML reference; open `OPPO Installer Wizard.html` in any modern browser
