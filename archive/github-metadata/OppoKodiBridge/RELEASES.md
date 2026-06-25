# OppoKodiBridge — Releases (8)

Archived 2026-06-25. Full machine-readable data in [`releases.json`](releases.json). No releases had binary assets attached; the notes below are the unique content.

## v2.0.11 — OppoKodiBridge v2.0.11 - disc/ISO playback filter
published 2026-06-08 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.11)

**Only disc content is handed to the OPPO now — everything else just plays in Kodi.**

### What's new since v2.0.8
- **Playback filter (default on):** only **disc images (`.iso`)** and **disc folders (BDMV / VIDEO_TS)** are handed to the OPPO. MKV, MP4, loose `.m2ts`, etc. play in Kodi as usual. Toggle in settings: *"Only hand discs & ISO files to the OPPO"* (turn off to hand off everything).
- **TV switching:** reliable OPPO power-cycle (CEC One-Touch-Play on power-on) to switch the TV to the OPPO, and Kodi `CECActivateSource` to reclaim the TV when playback stops. (A `cec-client` fast-switch route was tried in between and reverted — running a second libCEC client disrupted Kodi's own CEC.)

### Verified
Live on the one supported chain — Kodi/CoreELEC (Ugoos AM6B+) + M9205 V1 + TCL Q9L Pro: all content types (MKV / ISO / m2ts / BDMV) play on the OPPO; the TV switches to the OPPO on play and returns to Kodi on stop.

### Install
Download `service.oppokodibridge-2.0.11.zip` and install via **Kodi → Add-ons → Install from zip file**. The OPPO HTTP API is community-reverse-engineered, not an official protocol.

---

## v2.0.8 — OppoKodiBridge v2.0.8 - all content types + CEC
published 2026-06-08 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.8)

Complete OppoKodiBridge for the Ugoos/M9205/TCL chain, verified end-to-end on hardware. Press play in Kodi -> add-on intercepts -> power-cycles the OPPO so CEC switches the TV to it -> hands off and plays. Content types all confirmed: single files (MKV / ISO / m2ts incl. 4K) play via /playnormalfile to /mnt/nfs1; Blu-ray disc folders (BDMV/VIDEO_TS) play via /checkfolderhasBDMV on the disc folder. On stop, Kodi reclaims the TV (CECActivateSource). Install: Add-ons -> Install from zip -> service.oppokodibridge-2.0.8.zip

---

## v2.0.7 — OppoKodiBridge v2.0.7 - COMPLETE (playback + CEC switching)
published 2026-06-08 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.7)

Full chain verified end-to-end on hardware (Ugoos/CoreELEC + M9205 + TCL Q9L Pro): press play in Kodi -> the add-on intercepts, power-cycles the OPPO so CEC One-Touch-Play switches the TV to it, hands off over the OPPO HTTP API (wake :7624 / loginNfsServer / mountNfsSharedFolder / playnormalfile to /mnt/nfs1), and the OPPO plays. Confirmed for both MKV and 4K-disc ISO. On stop, Kodi reclaims the TV via CECActivateSource. Config: oppo_ip + path_from (Kodi share prefix) + path_to (OPPO export); server auto-resolved from the OPPO device list. Install: Add-ons -> Install from zip -> service.oppokodibridge-2.0.7.zip

---

## v2.0.6 — OppoKodiBridge v2.0.6 - playback handoff WORKING
published 2026-06-08 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.6)

Kodi -> OPPO playback handoff verified end-to-end on an M9205: press play in Kodi and the add-on wakes the OPPO (NOTIFY OREMOTE LOGIN :7624), runs the init dance, logs in to the OPPO's own NFS server (from its device list), mounts the file's folder, and plays it from /mnt/nfs1. Path mapping nfs://192.168.1.177/mnt/Super3/Super3Share -> OPPO export srv/nfs/media; set yours in Settings. The TV auto-switch (CEC) is the remaining piece. Software- and hardware-verified for playback (not CEC). Install: Add-ons -> Install from zip -> service.oppokodibridge-2.0.6.zip

---

## v2.0.4 — OppoKodiBridge v2.0.4 (test build)
published 2026-06-07 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.4)

Playback monitor now reads the OPPO's real /getglobalinfo flags (is_video_playing / is_audio_playing / is_bdmv_playing / is_disc_playing), confirmed live on an M9205 -- fixes the TV being reclaimed mid-playback. Fully preconfigured (OPPO 192.168.10.10, NFS nfs://192.168.10.20/srv/nfs/media -> /srv/nfs/media). Software-verified (21 tests); HTTP path + reachability confirmed on hardware. Install: Add-ons -> Install from zip -> service.oppokodibridge-2.0.4.zip

---

## v2.0.3 — OppoKodiBridge v2.0.3 (test build)
published 2026-06-07 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.3)

Packaging fix: the install zip now uses spec-correct forward-slash paths (the earlier Compress-Archive builds wrote backslashes that break extraction on Linux/CoreELEC). Same fully-preconfigured chain: OPPO 192.168.10.10, NFS nfs://192.168.10.20/srv/nfs/media -> /srv/nfs/media. Install and play. Software-verified only (20 tests); not hardware-validated. Install in Kodi: Add-ons -> Install from zip file -> service.oppokodibridge-2.0.3.zip

---

## v2.0.2 — OppoKodiBridge v2.0.2 (test build)
published 2026-06-07 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.2)

Fully preconfigured for the Ugoos/M9205/TCL chain: OPPO IP 192.168.10.10, NFS mapping nfs://192.168.10.20/srv/nfs/media -> /srv/nfs/media, URL-decode for spaces/parens. Install and play a file -- no setup needed. Software-verified only (20 tests); not hardware-validated. Install in Kodi: Add-ons -> Install from zip file -> service.oppokodibridge-2.0.2.zip

---

## v2.0.1 — OppoKodiBridge v2.0.1 (test build)
published 2026-06-07 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge/releases/tag/v2.0.1)

Test build for the Ugoos/M9205/TCL chain. Prefilled NFS mapping (nfs://192.168.10.20/srv/nfs/media -> /srv/nfs/media) and URL-decode for spaces/parens in filenames. Set your OPPO's IP in the add-on settings, then play a file. Software-verified only (20 tests); not hardware-validated. Install in Kodi: Add-ons -> Install from zip file -> service.oppokodibridge-2.0.1.zip

---
