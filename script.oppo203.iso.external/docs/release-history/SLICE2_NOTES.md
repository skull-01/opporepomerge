# SLICE2_NOTES.md — v2 MVP Slice 2 verification

## Scope

Slice 2 covers the M9702 / Chinoppo wake-rewrite core for the v2 MVP.

## Build 2 status

Verified and corrected in Build 2:

- `HARDWARE_COMPAT` contains the 12 canonical hardware entries.
- M9702 and other Chinoppo-style clone entries are marked `is_clone=True` and use `wake_command="#EJT"`.
- `oppo_remote.resolve_power_on_token()` rewrites `#PON` and `#POW` to `#EJT` only for clone profiles.
- `oppo_control._resolve_hardware_wake_command()` applies the same clone-only rule to configured start commands.
- Stock UDP-203 / UDP-205 keep `#PON` and `#POW` exactly.
- Unknown hardware keeps the original command as safe default behavior.
- Reavon remains warning-only and does not receive automatic command-map mutation.

## Tests

Build 2 tests cover:

- M9702 `#PON` / `#POW` rewrite to `#EJT`.
- Stock UDP-203 `#PON` pass-through.
- Stock UDP-203 `#POW` pass-through.
- Unknown model pass-through.
- Configured start commands applying clone-only rewrite.

## Remaining notes

This slice is considered MVP-compliant for Build 2. Hardware validation on a real M9702 is still a manual test item.
