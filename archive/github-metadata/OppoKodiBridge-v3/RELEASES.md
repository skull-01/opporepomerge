# OppoKodiBridge-v3 — Releases (1)

Archived 2026-06-25. Full machine-readable data in [`releases.json`](releases.json). No releases had binary assets attached; the notes below are the unique content.

## v3.1.0 — v3.1.0 — pure-CEC handoff + ISO fix
published 2026-06-25 · by `skull-01` · [original](https://github.com/skull-01/OppoKodiBridge-v3/releases/tag/v3.1.0)

**OppoKodiBridge v3.1.0 — pure-CEC handoff + ISO fix**

v3 now switches the TV with **legitimate HDMI-CEC** instead of v3.0.0's Broadlink IR blaster: the OPPO grabs its HDMI input via its **own** One-Touch-Play on a `#POF`→`#PON` power-cycle, and Kodi reclaims its input via libCEC `SetActiveSource`. No IR, no CEC injection / bus corruption. (Trade-off: the ~20-24s OPPO power-cycle per handoff.)

**ISO playback fixed.** `oppo_model` now defaults to **M9205** — mount the movie's *own* folder and play the *bare* filename — the NFS layout that lets disc-image `.iso` files loop-mount to `/mnt/iso` and play. (M9207's mount-export-root/play-subpath shape leaves an ISO in a subdirectory where the OPPO won't loop-mount it.) Verified live end-to-end on a UDP-203 clone.

Brings the modular **detector / handoff / cec / monitor / orchestrator** pipeline; **73 off-box tests** pass. The OPPO HTTP API is community-reverse-engineered, not an official protocol.

**Install:** download `service.oppokodibridge.v3-3.1.0.zip` → Kodi → Add-ons → *Install from zip file*.

---
