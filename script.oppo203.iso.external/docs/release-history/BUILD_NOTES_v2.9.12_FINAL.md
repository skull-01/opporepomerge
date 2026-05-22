# Build Notes — v2.9.12 Final

Version 2.9.12 Final is a software-verified release after the v2.9.11 Final line. It improves first-run setup with ready-to-transfer file generation and ships an add-on icon.

## Scope

- The first-run wizard and the add-on menu now generate complete, ready-to-transfer files instead of asking the user to merge XML snippets by hand:
  - a drop-in `playercorefactory.xml`, and
  - a drop-in remote-bridge keymap (`keymaps/oppo203iso.xml`).
- Files are written to the add-on-data `generated/` folder, mirroring Kodi's `userdata` layout, so the user copies them straight across.
- The wizard writes `playercorefactory.xml` only in external-player mode and always writes the keymap; generation is non-fatal and never blocks wizard completion.
- The add-on now ships a 256x256 `icon.png` referenced via an `<assets>` block so it is not blank when installed.

## Preserved behavior

- This is an additive setup-tooling change. OPPO command-map payloads, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, startup auto-power, TV switching, and AVR sequencing semantics remain unchanged.
- The legacy snippet helpers remain for backward compatibility.
- Runtime-only installable ZIP policy remains preserved; the icon ships via the existing allowlist.
- No new hardware features were added.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
