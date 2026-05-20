# Release Notes — v2.9.1 Build 13

Build 13 introduces a local, non-blocking type-check baseline. It adds `tools/type_check.py` and `mypy.ini`, plus selected type hints on public helper surfaces. The type-check path is advisory and does not add a runtime dependency.

No runtime playback/control behavior changed. Hardware validation remains pending and is not claimed.
