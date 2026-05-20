# Release Notes — v2.9.1 Build 4

Build 4 is a release-audit maintainability cleanup. It introduces `release-evidence/<build>/MANIFEST.txt` discovery so future builds can add release evidence by manifest instead of only appending to a large inline Python list.

The legacy evidence list remains in place as a transition fallback. Runtime playback and hardware-control behavior are unchanged.

Hardware validation is not claimed.
