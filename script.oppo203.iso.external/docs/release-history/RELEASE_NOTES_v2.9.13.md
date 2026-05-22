# Release Notes — v2.9.13 Final

This release refreshes the project testing strategy and developer tooling for the software-verified Kodi add-on. It contains no runtime behavior change.

## Highlights

- Adopts a realistic Kodi add-on testing strategy (`docs/testing-strategy.md`): test the pure-Python logic that matters instead of chasing high coverage on `xbmc*`-coupled UI/glue.
- Sets the enforced coverage floor to a realistic 50%, measured on logic modules (wizard dialogs and the file installer are omitted from measurement); logic-module coverage remains ~99%.
- Replaces Black with `ruff format` for code formatting.
- Adds parallel test execution via `pytest-xdist` (local full suite runs about 14x faster).
- Fixes the release audit so it no longer recompiles the local virtualenv.
- Refreshes developer documentation and release evidence.

## Runtime behavior

No runtime behavior changed in v2.9.13. OPPO command semantics, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, startup auto-power, TV switching, and AVR sequencing are preserved.

## Hardware validation

This package remains software-verified only. Hardware validation is not performed / not claimed.
