# OppoKodiBridge v3 (playercorefactory)

A fork of **[OppoKodiBridge / v2](https://github.com/skull-01/OppoKodiBridge)** that intercepts
playback with Kodi's **`playercorefactory`** instead of a service monitor — so Kodi never starts the
file itself, and there is **no "Kodi blips, then hands off"** moment before the OPPO takes over.

Same one supported chain (Ugoos AM6B+ / M9205 V1 / TCL Q9L Pro), same OPPO HTTP protocol, same NFS
path mapping. The only thing that changes is *how* Kodi hands a disc to the OPPO — and how the TV is
switched.

## v2 vs v3 — what's different

| | v2 (OppoKodiBridge) | v3 (this) |
|---|---|---|
| Interception | service monitor: Kodi **starts** the file, the add-on stops it and hands off | **playercorefactory** routes the file to an external player *before* Kodi plays it |
| Pre-play blip | brief (Kodi starts, then cuts to the OPPO) | **none** |
| Disc filter | runtime check (`disc_iso_only`) | the playercorefactory **match rules** (`.iso` + BDMV/VIDEO_TS) |
| Stop detection | HTTP `/getglobalinfo` poll every ~5s | HTTP poll until it **starts**, then verbose **`#SVM 3`** push → **instant** stop |
| TV switch | CEC power-cycle + `CECActivateSource` reclaim | **Broadlink IR** (CEC-free) when configured; interim power-cycle, **no** CEC reclaim |

It installs **alongside v2** (different add-on id), so you can A/B the two interception approaches —
**enable one at a time.**

## How it works

```
Kodi play (.iso / BDMV) ─▶ playercorefactory routes it to pcf_player.py (external)
                                          │  (Kodi never starts the file -> no blip)
                                          ▼
  switch TV ─ Broadlink IR (CEC-free) if configured, else interim OPPO power-cycle
  play     ─ OPPO HTTP app API: wake -> signin -> mount NFS -> /playnormalfile (or /checkfolderhasBDMV)
  monitor  ─ HTTP poll until playing, then #SVM 3 verbose push until @UPL STOP (instant)
  switch back ─ Broadlink IR, or Kodi re-asserts the TV when this player exits
```

The OPPO control is pure network, so the external player needs no Kodi APIs and v3 is **CEC-free by
design** (no `CECActivateSource`).

📐 **Full walkthrough + diagrams:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Install & configure

1. Build the zip: `powershell -File packaging\make_addon_zip.ps1` → `dist/service.oppokodibridge.v3-<ver>.zip`.
2. Kodi → **Add-ons → Install from zip file** → pick it. (Disable v2 first if it's installed.)
3. Configure: **OPPO IP**, **Kodi path prefix** (`path_from`), **OPPO path prefix** (`path_to`). The
   service writes `playercorefactory.xml` on start and removes it on stop.
4. *(later)* Set the **Broadlink IR** blaster IP + the TV's input IR codes for instant CEC-free
   switching. Until then it falls back to the OPPO power-cycle.

See the shared [Playing ISO & Blu-ray discs over the network](docs/PLAYING_DISCS_FROM_NETWORK.md)
guide for the underlying protocol.

## Status

Software-verified (pure logic under `tests/`); the playercorefactory routing, the verbose `#SVM 3`
stop detection (confirmed live on the M9205), and the OPPO HTTP handoff are the v3-specific pieces.
The Broadlink IR backend is stubbed until the blaster is in hand. The OPPO HTTP API is
community-reverse-engineered, not official.

## License

MIT — see [LICENSE](LICENSE).
