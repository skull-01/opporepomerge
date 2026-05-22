# Build Notes — v2.9.13 Final

Version 2.9.13 Final is a software-verified maintenance release after the v2.9.12 Final line. It refreshes the testing strategy and developer tooling without changing runtime behavior.

## Scope

- Adopts `docs/testing-strategy.md`: a realistic Kodi add-on testing strategy that measures coverage on pure-Python logic modules rather than chasing high percentages on `xbmc*`-coupled UI/glue.
- Lowers the enforced coverage floor from 98% to 50% and omits UI/glue modules (`wizard.py`, `first_run_wizard.py`, `wizard_polish.py`, `installer.py`) from measurement; logic-module coverage remains ~99%.
- Replaces Black with `ruff format` (CI step, development dependencies, and project configuration).
- Adds parallel test execution via `pytest-xdist`; the local full suite runs about 14x faster.
- Fixes the release audit so it no longer force-recompiles the local virtualenv (which was both slow and unsafe under parallel test runs).

## Preserved behavior

- This is a developer-experience and tooling change only. OPPO command-map payloads, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, startup auto-power, TV switching, and AVR sequencing semantics remain unchanged.
- Runtime-only installable ZIP policy remains preserved.
- No new hardware features were added.

## Hardware validation

This is a software-verified release. Real hardware validation was not performed or claimed.
