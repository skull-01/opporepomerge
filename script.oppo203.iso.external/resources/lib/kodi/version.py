"""Single source of truth for the add-on release identity.

Kodi reads the runtime version from addon.xml, so this module is paired with
``tools/sync_version.py`` and release-audit checks that keep the XML metadata,
expected audit version, and Python version source aligned.
"""

from __future__ import annotations

ADDON_ID = "script.oppo203.iso.external"
ADDON_VERSION = "2.9.17"
BUILD_ID = "v2.9.17 Final"
BUILD_NUMBER = 26
RELEASE_LINE = "v2.9.17 player database: five OPPO-clone variants (M9205 V2/V3/V4, M9702 Plus, VenPro V203) added end-to-end plus a cross-area Dolby Vision capability layer (per-player processing guidance + a global TV rule); research-sourced, software-verified, hardware validation not claimed"


def addon_version() -> str:
    """Return the active Kodi add-on version string."""
    return ADDON_VERSION


def build_id() -> str:
    """Return the human-readable active build identifier."""
    return BUILD_ID
