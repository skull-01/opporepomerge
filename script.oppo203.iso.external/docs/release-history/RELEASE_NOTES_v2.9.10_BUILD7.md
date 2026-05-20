# Release Notes — v2.9.10 Build 7

Build 7 adds a Roku TV ECP backend for optional local TV input switching.

The backend uses default port `8060`, sends HTTP POST to `/keypress/<key>`, and validates Roku input keys through a strict allowlist before URL construction. Roku TV presets are software-only and editable. TV switching failures remain non-fatal.

Hardware validation is not claimed.
