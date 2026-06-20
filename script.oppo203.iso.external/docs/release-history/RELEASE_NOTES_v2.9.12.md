# Release Notes — v2.9.12 Final

Version 2.9.12 Final is a software-verified release that makes first-run setup easier and gives the add-on a proper icon.

## What changed

- The first-run wizard and the add-on menu now generate complete, ready-to-transfer files instead of showing XML snippets to merge by hand:
  - a drop-in `playercorefactory.xml`, and
  - a drop-in remote-bridge keymap.
- The files are written to the add-on-data `generated/` folder, which mirrors Kodi's `userdata` layout, so you copy them straight into place and restart Kodi.
- In external-player mode the wizard writes `playercorefactory.xml` and the keymap; in service-interception mode it writes only the keymap. Generation is non-fatal and never blocks the wizard.
- The add-on now ships a 256x256 icon, so it is no longer blank when installed.

## What did not change

This is an additive setup-tooling change. OPPO command semantics, service interception, XML routing, NAS behavior, startup auto-power, TV switching, and AVR sequencing remain preserved. No new hardware features were added.

This is a software-verified release. Real hardware validation was not performed or claimed for OPPO/Chinoppo/Magnetar/Reavon/Kodi/NAS/TV/ADB/Roku/LG/Samsung/Sony/Panasonic/Vizio/AVR paths unless separately recorded from real tester results.

Hardware validation remains not performed / not claimed.
