# OppoKodiBridge — Developer Notes & Resume

Everything learned building/verifying v2 against real hardware (2026-06-07/08). Read this first to
resume. The OPPO HTTP API here is community-reverse-engineered (mirrors the operator's working
`emby-chinoppo-bridge`), not an official protocol.

---

## 0. Where we are (resume point)

- **Built + deployed to the box: v2.0.11** (filter, below). v2.0.9 is still the GitHub "Latest" —
  no v2.0.10/v2.0.11 GitHub release published yet (pending the operator's CEC re-confirm).
- **Working, hardware-verified:** browse + play in Kodi → the OPPO plays it (MKV, ISO, m2ts/4K,
  and **BDMV Blu-ray disc folders** all confirmed) → the TCL switches to the OPPO → on stop the TV
  returns to Kodi.
- **v2.0.11 handoff filter (default on):** only **disc images (`.iso`)** and **disc folders
  (BDMV / VIDEO_TS / HVDVD_TS)** are handed to the OPPO; everything else (MKV, MP4, loose m2ts, …)
  just plays in Kodi. Gated at the interception point in `monitor.py` by `is_oppo_target(path)`;
  toggle `disc_iso_only`. NOTE: a *loose* `.m2ts` (not inside a `BDMV/` path) now stays in Kodi —
  only m2ts *within* a BDMV disc folder routes to the OPPO.
- **TV switch mechanism = OPPO power-cycle** (`#POF`/`#PON`) so CEC One-Touch-Play fires on power-on.
  Cost: ~24 s per play. Reclaim on stop = Kodi `CECActivateSource`.
- **Open #1 (faster TV switch):** a `cec-client` "route from the Kodi box" (v2.0.9) worked instantly
  BUT opened a 2nd libCEC client and **broke Kodi's CEC** (reclaim stopped switching back; the input
  kept getting re-grabbed). Reverted in v2.0.10. The promising non-conflicting path is writing the
  CEC frame straight to **`/sys/class/aocec/cmd`** (Amlogic driver) — no 2nd libCEC client. UNTESTED.
- **Open #2 (just reverted, needs operator re-confirm):** after v2.0.10 + Kodi restart, confirm
  (a) stop → TV returns to Kodi, (b) switching to HDMI 2 mid-play no longer gets re-grabbed.

---

## 1. The one supported chain

| Role | Device | Address |
|------|--------|---------|
| Kodi host | Ugoos AM6B+ (CoreELEC, Amlogic) | `192.168.1.100` |
| Player | M9205 V1 (OPPO UDP-205 clone) | `192.168.10.10` (HTTP app API :436, IP control :23) |
| TV | TCL Q9L Pro ("T-Link" = its CEC) | OPPO on **HDMI 1** (phys addr `1.0.0.0`) |

**Dual-homed NAS (critical):** the same TrueNAS content is exported twice —
- Kodi sees it as `nfs://192.168.1.177/mnt/Super3/Super3Share/...`
- the OPPO sees it as NFS server **`192.168.10.20`** exporting **`srv/nfs/media`** (read from
  `/getNfsShareFolderlist`; the OPPO's device is in `/getdevicelist`, `sub_type:"nfs"`).

So Kodi's path and the OPPO's path differ in BOTH server and share root. The add-on bridges this:
strip the Kodi prefix → the in-share relative path → rebase onto the OPPO export → mount + play.

---

## 2. The M9205 HTTP app API (port 436) — the real protocol

The API **sleeps after boot**. Everything below is GET; quirky query encoding (some endpoints encode
the whole `{...}` JSON, others wrap a url-encoded body in literal `{}`). The add-on's `oppo_http.py`
has the exact encodings — mirror it, don't reinvent.

| Step | Endpoint | Notes |
|------|----------|-------|
| **Wake** | UDP `b"NOTIFY OREMOTE LOGIN"` → **:7624** | Starts the :436 API. Retry until :436 opens. NOT a 0x55 packet, NOT broadcast. |
| Firmware | `/getmainfirmwareversion` | part of the init "dance" |
| Setup | `/getsetupmenu` | " |
| Sign in | `/signin?{"appIconType":1,"appIpAddress":"<ip>"}` | the init dance is REQUIRED — without it, signin/mount fail on a fresh session |
| Global info | `/getglobalinfo` | playback state (see below) |
| Device list | `/getdevicelist` | find the OPPO's own NFS server (`sub_type:"nfs"` → `192.168.10.20`) |
| Login NFS | `/loginNfsServer?{"serverName":"<srv>"}` | |
| Share list | `/getNfsShareFolderlist` | binary `\x01`-separated; reveals export `srv/nfs/media` |
| Mount | `/mountNfsSharedFolder?{"server":"<srv>","folder":"<folder>"}` | mounts at **`/mnt/nfs1`** |
| **Play file** | `/playnormalfile?{<urlenc of: "path":"/mnt/nfs1/<basename>","index":0,"type":1,"appDeviceType":2,"extraNetPath":"<srv>","playMode":0>}` | single files |
| **Play disc** | `/checkfolderhasBDMV?{"folderpath":"/mnt/nfs1/<disc folder>"}` | on this OPPO this **STARTS the disc**, not just checks |
| Stop | `/sendremotekey?{"key":"STP"}` | clears a stuck `bd_is_playing` |
| File list | `/getfilelist?{"path":"<p>","fileType":1,"mediaType":3,"flag":1}` | binary; flaky for deep paths |

**`/getglobalinfo` playback flags** (NOT a status string): `is_video_playing` /
`is_audio_playing` / `is_bdmv_playing` / `is_disc_playing` (booleans), `activeapp`
(`scrn_svr` = idle), `cur_media_type` (5 idle/file, 13 disc).

**IP control (port 23, CR-terminated)**: `#PON` power on, `#POF` standby, `#QPW` query power
(`@OK ON/OFF`), `#STP` stop. Used for the power-cycle TV grab.

---

## 3. The handoff sequence (what the add-on does on play)

`monitor.py` intercepts Kodi playback (`onAVStarted` → `player.stop()` → background thread →
`handoff.play_on_oppo`). The handoff:

1. **Map the path** (`split_share_relative` + `oppo_mount_folder`): strip `path_from` from the Kodi
   path → in-share relative → split into folder + basename; rebase folder onto `path_to`.
   - **Disc folders** (`/BDMV/` or `/VIDEO_TS/` in the path): collapse to the disc folder, mount its
     PARENT, play the disc folder name via `/checkfolderhasBDMV`. (The OPPO won't play `index.bdmv`,
     and won't play sub-paths of a mount — so single files mount the file's folder + play basename.)
2. **Grab the TV** (`grab_tv_on_play`): `client.power_cycle()` (`#POF` → wait → `#PON`) so the OPPO's
   One-Touch-Play fires on power-on and the TCL switches to it.
3. **Wake** the API (`wake_and_wait`: OREMOTE notify to :7624 until :436 opens — also rides out the
   power-cycle reboot).
4. **Init dance**: firmware → setup → signin → global info.
5. **Server** = the OPPO's own NFS device from `/getdevicelist` (NOT the Kodi NAS IP).
6. **Login + mount** the (rebased) folder; retry once on failure (re-login).
7. **Play**: `play_file` (single) or `play_bdmv` (disc, with a STOP first).
8. **Watch** `/getglobalinfo` until idle (`_watch_until_idle`), then **reclaim** the TV with
   `xbmc.executebuiltin('CECActivateSource')`.

**Example mapping** (the operator's file):
`nfs://192.168.1.177/mnt/Super3/Super3Share/02TV/01Series/02-MKV/3 Body Problem (2024)/Season 1/3 Body Problem - S01E01 - Countdown.mkv`
→ server `192.168.10.20`, mount `srv/nfs/media/02TV/01Series/02-MKV/3 Body Problem (2024)/Season 1`,
play `/mnt/nfs1/3 Body Problem - S01E01 - Countdown.mkv`.

---

## 4. CEC / TV switching — what works and what doesn't

- **OPPO asserts CEC active-source ONLY on a power-ON transition** — NOT when it starts playing
  while already on (verified: a play-while-on does not switch the TCL; a `#POF`→`#PON` does).
  A redundant `#PON` (already on) does nothing. So the switch needs a real off→on cycle.
- **Reclaim to Kodi** = `xbmc.executebuiltin('CECActivateSource')` (Kodi claims active source). Works.
- **`input.enablecec` is INVALID on CoreELEC** (JSON-RPC `-32602`) — `ensure_kodi_cec_enabled` is a
  graceful no-op there. CEC is on by default on CoreELEC; the operator must enable it on the TV
  (T-Link) and the OPPO (Setup → HDMI → CEC) — hardware toggles the add-on can't flip.
- **FAILED experiment (v2.0.9):** routing from the Kodi box with
  `cec-client -s` sending `<Active Source>` (`tx 4F:82:10:00` for HDMI 1) switched the TCL
  *instantly* — but `cec-client` is a 2nd libCEC client and **corrupted Kodi's CEC**: the reclaim
  stopped working and the input kept getting re-grabbed. Reverted.
- **Next idea for fast switch:** CoreELEC here is **Amlogic aocec** (no `/dev/cec`; there IS
  `/sys/class/aocec/cmd`). Writing the raw CEC frame to `/sys/class/aocec/cmd` injects via the driver
  **without** a 2nd libCEC client, so it shouldn't disturb Kodi. Frame for `<Active Source>` HDMI 1:
  header `4f` (src 4 → broadcast f), opcode `82`, operand `10 00` (phys 1.0.0.0). Format of the sysfs
  write is unconfirmed — TEST it (and re-verify reclaim + no re-grab) before shipping.

---

## 5. Hard-won gotchas

- **NEVER mount a non-exported folder** → it HARD-CRASHES the OPPO (`:436` AND `:23` both die →
  needs a mains power-cycle to recover). Only mount the real export (`srv/nfs/media` or a subdir of
  it). A stuck `bd_is_playing` also blocks mounts — send STOP first.
- **A redeploy DISABLES the add-on** (Kodi shows an "X" in the browser) → re-enable via
  `Addons.SetAddonEnabled` JSON-RPC, or the Enable button. (The X = disabled, not broken.)
- **Stored settings vs defaults:** changing a default in `settings.xml` does NOT change already-stored
  values in `userdata/addon_data/service.oppokodibridge/settings.xml` — edit the stored file too (or
  reset the add-on) when changing prefilled config on a box that's already been installed.
- **Packaging:** PS 5.1 `Compress-Archive` writes BACKSLASH zip entries that break Linux/CoreELEC
  extraction. `packaging/make_addon_zip.ps1` builds forward-slash entries by hand via
  `System.IO.Compression.ZipArchive`. Keep it that way.
- **Code changes need a Kodi restart** to reload (Python modules are cached); settings changes don't.
- Powering the whole rack also reboots the Ugoos (clears `/tmp`).

---

## 6. Config / settings (`resources/settings.xml`, read by `config.from_addon`)

| id | default | meaning |
|----|---------|---------|
| `oppo_ip` | `192.168.10.10` | M9205 IP |
| `path_from` | `nfs://192.168.1.177/mnt/Super3/Super3Share` | Kodi share prefix to strip |
| `path_to` | `srv/nfs/media` | OPPO export root to mount under |
| `grab_tv_on_play` | `true` | power-cycle the OPPO to switch the TV |
| `cec_reclaim_on_stop` | `true` | `CECActivateSource` on stop |
| `oppo_hdmi_phys` | `1.0.0.0` | for the (currently unused) CEC-route path |
| `handoff_enabled` | `true` | master on/off for interception |
| `disc_iso_only` | `true` | **filter**: only `.iso` + disc folders go to the OPPO; off = hand off everything |

The server (`192.168.10.20`) is auto-resolved from `/getdevicelist` — not configured.

---

## 7. Deploy & test recipe (operator's box)

Password SSH from Windows via **PuTTY** (the box's host key changed mid-project, so PIN it; the
password is NOT stored in this repo):
```
plink -ssh -pw <pw> -hostkey SHA256:NjtpCJrUYHx+8Qe+81gagec2qz4hZ0NIqJYrWS0vIN4 -batch root@192.168.1.100 ...
pscp -pw <pw> -hostkey SHA256:... -batch <local.zip> root@192.168.1.100:/tmp/okb.zip
```
Deploy: `pscp` the zip → on the box `python3 -m zipfile -e /tmp/okb.zip /storage/.kodi/addons/` →
overwrite stored settings if needed → `systemctl restart kodi` → re-enable. The re-enable +
verify that works (no auth needed on localhost; pipe scripts through `tr -d '\r'` for line-endings):
```
curl -s http://localhost:8080/jsonrpc -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{"addonid":"service.oppokodibridge","enabled":true}}'
curl -s http://localhost:8080/jsonrpc -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"Addons.GetAddonDetails","params":{"addonid":"service.oppokodibridge","properties":["enabled","broken","version"]}}'
```
New settings keys default from `resources/settings.xml` (no stored-settings edit needed for a fresh
key). Trigger an end-to-end test with Kodi JSON-RPC `Player.Open` and watch
`/storage/.kodi/temp/kodi.log` + the OPPO `/getglobalinfo`. Note: `cec-client` and `cec-ctl` exist at
`/usr/bin`; CEC interface is `/sys/class/aocec/cmd` (no `/dev/cec`).

---

## 8. Version history

- **2.0.0–2.0.2** scaffold + prefilled config (initial API was the wrong/ported v1 protocol).
- **2.0.3** forward-slash zip packaging fix.
- **2.0.4** read the real `/getglobalinfo` playing flags.
- **2.0.5** rewrote the OPPO layer to the real protocol (loginNfsServer/mountNfsSharedFolder/…).
- **2.0.6** wake (:7624) + init dance + folder-mount + basename-play → **playback verified**.
- **2.0.7** TV switch via OPPO power-cycle (CEC One-Touch-Play) → **switch + reclaim verified**.
- **2.0.8** BDMV/disc folders via `/checkfolderhasBDMV`.
- **2.0.9** cec-client TV route — **reverted** (broke Kodi CEC).
- **2.0.10** revert to power-cycle.
- **2.0.11** handoff filter — only `.iso` + disc folders (BDMV/VIDEO_TS) route to the OPPO; the rest
  stays in Kodi (`is_oppo_target`, toggle `disc_iso_only`, default on). Current; deployed to the box.

---

## 9. Next steps

1. Operator confirms v2.0.11 on the box: (a) play an MKV → stays in Kodi (no handoff); (b) play an
   ISO / a BDMV folder → handed to the OPPO; (c) the v2.0.10 CEC revert — stop→reclaim works, no
   input re-grab. Then publish a GitHub release to supersede v2.0.9 ("Latest").
2. Faster TV switch: try the `/sys/class/aocec/cmd` raw-frame inject (no 2nd libCEC client). Verify
   reclaim + no re-grab before shipping. If it works, it replaces the ~24 s power-cycle.
3. Optional: skip the TV-grab when the OPPO is already the active source (binge / back-to-back).
4. Optional: a Windows-free dev loop (currently deploy/test is driven over SSH from Windows+PuTTY).

This add-on is software-verified + hardware-verified for playback and CEC switching on the one
supported chain. It is not a general-purpose OPPO/Kodi bridge and makes no claims beyond that chain.
