# Test Layout Policy — v2.9.1 Build 14

Build 14 introduces a transition-safe test layout policy without moving the inherited historical tests.

## Current transition rule

- Existing flat tests under `tests/test_*.py` remain valid and continue to be collected by pytest and unittest.
- Future build-specific tests may use `tests/v<MAJOR>_<MINOR>_<PATCH>/build<N>/test_*.py` once the project is ready for directory-based organization.
- Pytest markers are declared for `version(...)`, `build(...)`, and `legacy_layout`.
- `tools/test_layout.py --check` validates the transition policy.

## Reason for transition instead of mass move

The repository contains long-lived historical regression tests that double as build reconstruction evidence. Build 14 therefore defines the future standard and adds tooling, but avoids a destructive mass rename/move that could break unittest discovery or historical traceability.
