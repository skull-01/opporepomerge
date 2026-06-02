# Release Notes — v2.9.15 Final

This release adopts the Xnoppo Elite V3 pure-HTTP/436 control model into the software-verified Kodi add-on: a seventh playback preset that launches, monitors, mounts, and commands the player entirely over HTTP, plus checkfolderhasBDMV-first disc navigation and selectable HDMI switching.

## Highlights

- **Seventh playback preset `http_handoff_http`** — an asymmetric cell on top of the six-option matrix. The new `http` monitor confirms playback by polling `/getglobalinfo` and `/getplayingtime`, and exists only for the `http_handoff` routing; `normalize_architecture` clamps any other `(routing, "http")` pair to that routing's legacy preset.
- **Pure-HTTP launch orchestration** — the `http_handoff` launch wakes the player (`sendremotekey`), signs in, best-effort mounts the network share (SMB/NFS parsed from the media path), plays, auto-heals a dropped ISO once, and confirms over `/getglobalinfo`. Every step beyond the proven activate→signin→play is best-effort and capability-gated, so older/stock players degrade to today's behaviour.
- **checkfolderhasBDMV-first disc navigation** — `resolve_disc_play_path` confirms a BDMV folder over HTTP (when the player is capable) before handing it over, and is fallback-safe to the existing `_disc_folder_root` behaviour.
- **Selectable confirm-gated HDMI switching** — `hdmi_switch_mode=immediate` (default) keeps today's frozen TV-first order; `delayed` starts the player first and waits `play_delay_hdmi` (≥6s for ISO/BDMV) before switching the TV, with an `av_delay_hdmi` stagger.
- **Pure HTTP is the new default for new installs**; existing installs keep the preset they already have.

## Runtime behavior

Runtime behavior changed in v2.9.15. The playback dispatch gains a seventh preset and an HTTP playback monitor; the `http_handoff` launch is enriched with the pure-HTTP orchestration; disc navigation can confirm BDMV over HTTP; and HDMI switching is selectable. These additions are best-effort and capability-gated — the six prior presets and their TV/AVR sequencing stay byte-identical, the default HDMI mode (`immediate`) is unchanged, and an existing install keeps the preset derived from its current settings unless the configurator writes a new one. The core protected behaviors are preserved: 4K/UHD disc-style interception only, loose/raw files stay with Kodi, conservative `playercorefactory.xml` routing, the canonical OPPO command map with no forbidden tokens, NAS/AutoScript behavior, startup auto-power, TV switching, and AVR sequencing.

## Hardware validation

This package remains software-verified only. The pure-HTTP/436 mount, monitor, command, BDMV, and HDMI-timing paths are community-reverse-engineered (Xnoppo Elite V3 / emby-chinoppo-bridge) and firmware-dependent; hardware validation is not performed / not claimed.
