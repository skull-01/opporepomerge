# Release Notes — v2.9.11 Final

Version 2.9.11 Final is a software-verified maintenance release. It restores green continuous integration and makes the add-on behave deterministically across Windows, Linux, and macOS.

## What changed

- Lint and format gates (`ruff`, `black`) pass across the runtime sources.
- Add-on-data paths use forward slashes so they are consistent on every platform.
- Exported diagnostic and preset-submission filenames are timestamped in UTC, so they no longer depend on the host machine's timezone.
- Timezone- and shell-dependent tests were stabilized; POSIX-only release scripts skip on platforms that cannot run them.
- The enforced coverage gate is 98% following the repository-wide formatting pass.

## What did not change

No new hardware features were added. OPPO command semantics, service interception, XML routing, NAS behavior, startup power, TV switching, and AVR sequencing remain preserved.

This is a software-verified release. Real hardware validation was not performed or claimed for OPPO/Chinoppo/Magnetar/Reavon/Kodi/NAS/TV/ADB/Roku/LG/Samsung/Sony/Panasonic/Vizio/AVR paths unless separately recorded from real tester results.

Hardware validation remains not performed / not claimed.
