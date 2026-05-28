# Application icons

Placeholder directory. Before any release build, drop in real icons matching
the names in `../tauri.conf.json`:

- `32x32.png`
- `128x128.png`
- `icon.icns` (macOS)
- `icon.ico` (Windows)

`npm run tauri icon path/to/source.png` generates the full set from a single
1024×1024 PNG source.
