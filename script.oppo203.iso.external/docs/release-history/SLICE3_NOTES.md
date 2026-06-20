# SLICE3_NOTES.md — v2 MVP Slice 3 implementation

## Scope

Slice 3 wires TCL/Android TV HDMI switching into the External Player flow.

## Build 2 status

Implemented in Build 2:

- `external_player.fast_start()` attempts TV switch-to-OPPO before OPPO startup.
- TV switching is controlled by `tv_switching_enabled`.
- Disabled TV switching is a clean no-op path.
- ADB/TV switching failures are logged as non-fatal.
- `external_player.fast_return()` still sends OPPO stop commands even if TV switch-back fails.
- Session sentinel cleanup remains in `finally` and is tested when startup fails.
- `adb_control.switch_input()` supports `_adb_runner` injection so tests do not call a real `adb` binary.

## Tests

Build 2 tests cover:

- TV switch-to-OPPO runs before OPPO startup.
- TV switching disabled path is a no-op.
- ADB/TV failure does not prevent OPPO startup.
- ADB/TV failure during return does not hide OPPO stop commands.
- External Player startup failure still clears the session sentinel.
- ADB command construction uses injected runner and does not require a real TV.

## Remaining notes

This slice is considered automated-test compliant for the MVP. Physical TCL/Android TV validation remains manual hardware testing.
