# Build Notes — v2.9.11 Final

Version 2.9.11 Final is a software-verified maintenance release after the v2.9.10 Final line. It restores green CI and makes the add-on cross-platform.

## Scope

- Restore green CI: clear all `ruff` findings and apply the `black` format gate across `resources/`, `default.py`, and `service.py`.
- Stabilize timezone- and shell-dependent tests so the suite passes on Windows, Linux, and macOS.
- Make the runtime cross-platform:
  - build add-on-data paths with forward slashes (`posixpath.join`) instead of OS-native separators;
  - timestamp exported diagnostic/submission filenames in UTC (`gmtime`) for deterministic, timezone-independent names.
- Set the enforced coverage gate to 98% after the repository-wide formatting pass.
- Skip POSIX-only release scripts (bash/python3/sha256sum) on platforms that cannot run them instead of failing.

## Preserved behavior

- OPPO command-map payloads, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, startup auto-power, TV switching, and AVR sequencing semantics remain unchanged.
- Runtime-only installable ZIP policy remains preserved.
- No new hardware features were added.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
