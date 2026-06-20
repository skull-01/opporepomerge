# Build Notes — v2.9.1 Build 11

Build 11 refactors diagnostic logging fallback behavior. Kodi `xbmc.log` remains the preferred runtime sink. When Kodi logging is unavailable, diagnostics now use a Python `logging.StreamHandler` fallback instead of direct per-call `print()` usage in the shared diagnostic logging helper.

No playback, OPPO command-map, XML routing, NAS adapter, startup auto-power, packaging outcome, or hardware-control behavior changed.
