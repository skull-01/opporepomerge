# CEC Switcher (desktop)

A tiny Windows app: two buttons that switch the TV between the **OPPO** and the **Kodi** box, set up by
pinging both over the LAN.

**It does not do CEC itself.** A PC isn't on the HDMI/CEC bus, so the app *triggers each device to take
CEC ownership itself* — the legitimate, spec-clean pattern (each device announces only its **own**
active source; nothing is spoofed):

| Button | Over the LAN it… | Speed | Needs |
|--------|------------------|-------|-------|
| ▶ Switch to OPPO | power-cycles the OPPO over TCP `:23` (`#POF`→`#PON`) so its **own** One-Touch-Play grabs the TV | ~20–24 s (its boot) | nothing |
| 🏠 Switch to Kodi | calls Kodi JSON-RPC `Addons.ExecuteAddon` → `script.cecreclaim` → `CECActivateSource` (Kodi's **own** source) | instant | the helper add-on (below) |

The OPPO leg is slow because the OPPO only asserts active source on a **power-ON transition** — an
already-on OPPO told to play does *not* switch — so the only reliable lever is a power-cycle.

## Setup

1. **Kodi box:**
   - Enable **Settings → Services → Control → Allow remote control via HTTP** (default port `8080`).
   - Install the helper add-on [`../kodi-helper/script.cecreclaim`](../kodi-helper/script.cecreclaim):
     zip that folder and use **Add-ons → Install from zip file**. (One-time.)
   - Make sure Kodi's CEC adapter is enabled (it is, if v2/v3/the CEC add-on already switch via CEC).
2. **OPPO:** enable IP/serial control; the app talks to TCP `:23`.
3. **App:** enter the OPPO + Kodi IPs, click **Test (ping both)**, then **Save**.

## Run / build

- **From source:** `python app.py` (needs Python 3 with tkinter — bundled with the standard Windows installer).
- **Build the exe:** `pip install pyinstaller`, then `./build.ps1` → `dist/CEC-Switcher.exe`
  (single file, no console window). `./build.ps1 -Clean` to rebuild from scratch.

## Tests

The network logic is unit-tested off-box (no hardware, no GUI):

```
cd desktop/cec_switcher
python -m pytest test_cec_core.py -q
```

## Why this exists

The manual desktop twin of the [CEC Control Experiment](../../README.md) add-on: the same legitimate-CEC
switching (OPPO's own One-Touch-Play + Kodi's own active source), driven by hand from the desktop instead
of automatically from the Kodi add-on. No IR, no CEC injection, no spoofing.
