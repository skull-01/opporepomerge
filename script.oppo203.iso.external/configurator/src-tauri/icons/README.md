# Application icons

Generated from the configurator's purpose-built source artwork `icon-source.png`
(1024×1024, committed alongside the generated set) via:

```
cd configurator; npm run tauri -- icon src-tauri/icons/icon-source.png
```

The names here match `bundle.icon` in `../tauri.conf.json` (`32x32.png`,
`128x128.png`, `icon.icns`, `icon.ico`) plus the rest of the standard Tauri
desktop set (extra PNG sizes and the `Square*Logo.png` / `StoreLogo.png` Windows
Store assets).

Notes:

- The source is 1024×1024, so every generated size (including the macOS
  `icon.icns` and the Store logos) is downscaled from it — nothing is upscaled.
- `tauri icon` also emits `ios/` and `android/` folders; they are intentionally
  not committed — this is a Windows desktop app.
- To swap the icon again, replace `icon-source.png` with a new 1024×1024 PNG and
  re-run the command above.
