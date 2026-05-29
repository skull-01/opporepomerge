# Application icons

Generated from the add-on artwork at the repository root (`icon.png`, 256×256) via:

```
cd configurator; npm run tauri -- icon ..\icon.png
```

The names here match `bundle.icon` in `../tauri.conf.json` (`32x32.png`,
`128x128.png`, `icon.icns`, `icon.ico`) plus the rest of the standard Tauri
desktop set (extra PNG sizes and the `Square*Logo.png` / `StoreLogo.png` Windows
Store assets).

Notes:

- The source is 256×256, so the larger macOS (`icon.icns`) and Store logo sizes
  are upscaled. The Windows MSI/NSIS bundle only uses sizes ≤256, so its icons
  are not upscaled.
- `tauri icon` also emits `ios/` and `android/` folders; they are intentionally
  not committed — this is a Windows desktop app.
- To swap in a purpose-built icon later, drop a 1024×1024 PNG and re-run the
  command above.
