# OppoKodiBridge

**Browse in Kodi. Your OPPO plays everything. The TV follows by CEC.**

OppoKodiBridge is a clean-slate **v2** — a single Kodi service add-on that supports exactly
one hardware chain and nothing else. No Windows configurator, no TV-control backends, no
seven-preset playback matrix. You browse and press play in Kodi; the file plays on the
OPPO; the TV switches itself by HDMI-CEC.

📖 **Guides:**
- [Playing ISO & Blu-ray (BDMV) discs to an OPPO over the network](docs/PLAYING_DISCS_FROM_NETWORK.md)
  — task-oriented (the add-on + the raw HTTP method).
- [OPPO / M9205 network-playback developer guide](docs/OPPO_PLAYBACK_PROTOCOL.md) — protocol-level:
  HTTP vs TCP, the play-by-path limitation, endpoint reference, monitoring strategies, failed
  approaches, and references.

## The one supported chain

| Role | Device |
|------|--------|
| Kodi host | **Ugoos AM6B+** (CoreELEC) |
| Player | **M9205 V1** (OPPO clone) over its HTTP API |
| TV | **TCL Q9L Pro** via HDMI-CEC |

This is deliberate. v2 trades the old project's broad hardware support for a setup that is
simple to reason about and to keep working.

## How it works

```
Browse in Kodi ─▶ service intercepts the play ─▶ ensure Kodi CEC is on
                                              ─▶ HTTP handoff to the M9205
                                                 (activate → wake → signin → mount → /playnormalfile)
                                              ─▶ OPPO asserts CEC One Touch Play ─▶ TCL switches to the OPPO
                                              ─▶ poll /getglobalinfo until playback ends
                       OPPO stops ────────────▶ Kodi reclaims the TV: CECActivateSource ─▶ TCL back to Kodi
```

**Why CEC?** There is no HDMI-input command on the OPPO (HTTP or TCP) and no reliable way
to drive the TCL to a specific input from a normal app. But CEC **One Touch Play** is a
hardware side-effect: the OPPO grabs the TV the instant it starts playing, and Kodi — running
the add-on in-process — grabs it back with the `CECActivateSource` builtin. No TV backend
needed.

## Install

1. Build the installable zip (Windows):
   ```
   cd D:\Git\OppoKodiBridge; powershell -File packaging\make_addon_zip.ps1
   ```
   This writes `dist/service.oppokodibridge-2.0.0.zip`.
2. In Kodi: **Add-ons → Install from zip file →** pick that zip.
3. The service starts automatically and shows the one-time CEC setup steps.

## Configure (all in Kodi)

**Add-ons → My add-ons → Services → OppoKodiBridge → Configure**

| Setting | Meaning |
|---------|---------|
| OPPO IP address | The M9205's LAN IP |
| HTTP API port | Default `436` |
| Hand off playback to the OPPO | Master on/off for interception |
| Kodi path prefix / OPPO path prefix | Rewrite the share path Kodi sees (e.g. `nfs://192.168.10.20/srv/nfs/media`) to the path the OPPO sees once mounted (e.g. `/mnt/nas/media`) |
| Auto-enable Kodi CEC | Best-effort enable of Kodi's CEC adapter on start |
| Reclaim the TV when playback ends | Run `CECActivateSource` when the OPPO stops |

## CEC setup (once, on the hardware)

The add-on manages Kodi's CEC adapter, but the TV and the OPPO are hardware toggles:

- **TCL Q9L Pro:** Settings → System → **CEC / T-Link → On**
- **OPPO / M9205:** Setup → HDMI → **CEC → On**

## Status & limitations

- **Software-verified only.** The pure logic (HTTP handoff URL building, path rewrite,
  status parsing, CEC enable/reclaim) is covered by the test-suite. End-to-end behaviour on
  the real Ugoos / M9205 / TCL chain is **not yet hardware-validated** — that's the next step.
- The OPPO HTTP API is **community-reverse-engineered**, not an official OPPO protocol.
- The Kodi CEC-enable setting id (`input.enablecec`) is best-effort and may differ by
  CoreELEC build; reclaim via `CECActivateSource` is the reliable path. Confirm on hardware.

## Development

Pure-logic tests run off-box (no Kodi needed):

```
cd D:\Git\OppoKodiBridge; python -m pytest tests -q
```

## License

MIT — see [LICENSE](LICENSE).
