# OPPO UDP-20X control-protocol reference (query + status surface)

Transcribed from OPPO's published control-protocol PDFs so add-on work doesn't
need the source docs. Focused on the **read-back / status** surface the add-on
uses to answer "what is the player doing?" — see [`oppo_control.py`](../resources/lib/oppo/oppo_control.py)
(`query_command`, `query_*`, `probe_player_status`, `oppo_tcp_client` verbose push).

## Two source documents — use the newer one

| Doc | Date / firmware | Has media-identity queries (`#QFN`, `#QFT`, `#QTN`, …)? |
|---|---|---|
| **RS-232 & IP Control Protocol** | Dec 2017, firmware **`UDP20X-54-1127`+** | **Yes** — this is the current UDP-203/205 protocol |
| Simple IP Control Protocol | Nov 2015, "preliminary" (`QVR` → `BDT101-…`) | No — older subset, query list stops at `QZM` |

Everything below is from the **Dec 2017 RS-232 & IP** doc.

## Transport

- **IP control = TCP port 23** (not telnet — send whole commands, not keystrokes).
- Discovery: the player UDP-broadcasts `Notify: OPPO Player Start` (+ IP/port/name) to **`239.255.255.251:7624`** every 10 s. If the IP is known, connect to `:23` directly.
- **Command:** `#` + 3-char code `[+ space + params]` + CR (`0x0d`). ≤ 25 bytes.
- **Response:** `@` + code + space + `OK`|`ER` `[+ value]` + CR. ≤ 25 bytes.
  - **Verbose 0 (default):** the `@CODE ` prefix is **omitted** → reply is just `OK <value>` (BDP-8x/9x/10x compatibility).
  - **Verbose 1+:** full `@CODE OK <value>`.
  - `query_command`/`_parse_response` handle both forms. `probe_player_status` additionally preserves value **case** (needed for `#QFN`).
- If no response within 10 s, the command/response may be considered lost.

## Query commands (`#Q..`) — the status read-back surface

The player answers with its current status. Times are `HH:MM:SS`.

| Code | Query | Example reply |
|---|---|---|
| `#QPW` | Power status | `OK ON` / `OK OFF` |
| `#QPL` | **Playback status** | `OK PLAY` / `PAUSE` / `STOP` / `STEP` / `FREV` / `FFWD` / `SFWD` / `SREV` / `SETUP` / `HOME MENU` / `MEDIA CENTER` / `SCREEN SAVER` / `DISC MENU` |
| `#QFN` | **Media file name** | `OK Rocky Mou*.wav` · `ER INVALID` |
| `#QFT` | **Media file format** | `OK FLAC` / `WAV` / `MKV` / `JPG` · `ER INVALID` |
| `#QTN` | Track name | `OK Rocky Mountain*` · `ER INVALID` |
| `#QTA` | Track album | `OK Rise And Fall, Rage*` · `ER INVALID` |
| `#QTP` | Track performer | `OK The Offspring` · `ER INVALID` |
| `#QTK` | Track / Title (cur/total) | `OK 02/10` |
| `#QCH` | Chapter (cur/total) | `OK 03/03` |
| `#QTE` / `#QTR` | Track/Title elapsed / remaining | `OK 00:01:34` |
| `#QCE` / `#QCR` | Chapter elapsed / remaining | `OK 00:01:34` |
| `#QEL` / `#QRE` | Total elapsed / remaining | `OK 00:05:12` |
| `#QDT` | Disc type | `OK BD-MV` / `DVD-VIDEO` / `DVD-AUDIO` / `SACD` / `CDDA` / `DATA-DISC` / `UHBD` / `NO-DISC` / `UNKNOW-DISC` |
| `#QAT` | Audio type | `OK DTS-HD 1/4 English` |
| `#QST` | Subtitle type | `OK 1/1 English` / `OK OFF` |
| `#QIS` | Input source | `OK 0 BD-PLAYER` / `1 HDMI-IN` / `2 ARC-HDMI-OUT` / `3 OPTICAL-IN` / `4 COAXIAL-IN` / `5 USB-AUDIO-IN` |
| `#QHD` | HDMI resolution | `OK UHD_AUTO` / `1080P24` / … |
| `#QVL` | Volume | `OK 100` / `OK MUTE` |
| `#QVR` | Firmware version | `OK UDP20X-xx-xxxx` |
| `#QVM` | Verbose mode | `OK 0`..`3` |
| `#QDR n` | Directory item `n` | `OK F Rocky-mou*.wav` (file) / `OK D My Music` (dir) / `OK S MyPC` (SMB) / … |
| `#QDS` | Directory size (data/USB/network) | `OK 120` · `ER INVALID` |
| `#QHR` `#QHS` `#Q3D` | HDR setting / HDR status / 3D status | `OK Auto` / `OK HDR` / `OK 3D` |
| `#QRP` `#QZM` `#QSH` `#QOP` `#QAR` | Repeat / Zoom / Sub-shift / OSD-pos / Aspect | (mode codes; see doc) |

**Key for "did the OPPO play the requested file?"** → `#QPL` (started) + `#QTE`/`#QEL` advancing (progressing) + **`#QFN`** (file name). `#QFN`/`#QFT` apply to **media files** (NAS/USB/data); a physical disc returns `ER INVALID`, so fall back to `#QDT`/`#QTK`. **Caveat:** the ≤25-byte reply truncates long names with `*` (e.g. `Movie 4K U*.iso`) → match by **prefix**, not exact equality.

## Verbose push (`#SVM 2|3` → `@U..`) — unsolicited updates

`#SVM 2` reports major changes; `#SVM 3` adds per-second time codes during playback. Triggered by any source (IP, panel, IR, playback progress).

| Update | Meaning | Example |
|---|---|---|
| `UPW` | Power | `UPW 1` (on) / `UPW 0` (going off) |
| `UPL` | Playback status (4-char) | `UPL PLAY` / `STOP` / `PAUS` / `LOAD` / `DISC` (no disc) / `HOME` / `MCTR` / `OPEN` / `CLOS` / `STPF`/`STPR` / `FFWn`/`FRVn`/`SFWn`/`SRVn` |
| `UVL` | Volume / mute | `UVL 095` / `UVL MUT` |
| `UDT` | Disc type (4-char) | `UDT UHBD` / `BDMV` / `DVDV` / `CDDA` / `DATA` / … |
| `UAT` | Audio type | `UAT DD 01/05 ENG 5.1` |
| `UST` | Subtitle | `UST 02/05 ENG` |
| `UIS` | Input source | `@UIS 0 BD-PLAYER` |
| `U3D` / `UAR` | 3D / aspect-ratio status | `@U3D 3D` / `@UAR 16WW` |
| `UTC` *(mode 3, every second)* | Time code: `Title Chapter Type HH:MM:SS` | `UTC 001 001 C 00:01:23` |
| `UVO` *(mode 3)* | Source/output resolution | `UVO _UHD24_ _UHD24_` |

The add-on already listens for `@UPW 0` / `@UPL <stop>` in `verbose_push` hold mode ([`oppo_tcp_client.py`](../resources/lib/oppo/oppo_tcp_client.py)).

## Notes for add-on use

- All of the above is **silent on the control channel** — nothing is drawn on the TV. The on-screen overlay only appears if you *send* `#OSD` (the remote INFO button) or `#INH` (INFO-hold).
- The HTTP app API on **port 436** (`/getmovieplayinfo`, `/playnormalfile`, `/getfilelist`) is **separate and undocumented** (OPPO MediaControl app / Xnoppo reverse-engineering). `probe_player_status` captures its raw `/getmovieplayinfo` payload only as a *bonus* alongside the documented `#Q..` battery.
- Status-only and read-only: querying never changes playback. Best run outside an active `#SVM 2/3` verbose session, since unsolicited push lines can interleave with query replies on the simple one-recv-per-command model.
