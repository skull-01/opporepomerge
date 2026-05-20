# Release Notes — v2.9.1 Build 14

Build 14 adds a transition-safe test naming/layout standardization layer. Existing flat historical tests remain untouched, while future builds now have a documented path convention and pytest marker strategy.

Added development-only tooling/documentation:

- `tools/test_layout.py`
- `docs/test-layout.md`
- pytest markers in `pytest.ini`
- `scripts/verify.sh` layout-check integration

No runtime playback/control behavior changed. Hardware validation was not performed and is not claimed.
