"""Single source of truth for the add-on release identity.

Kodi reads the runtime version from addon.xml, so this module is paired with
``tools/sync_version.py`` and release-audit checks that keep the XML metadata,
expected audit version, and Python version source aligned.
"""

from __future__ import annotations

ADDON_ID = "script.oppo203.iso.external"
ADDON_VERSION = "2.9.12"
BUILD_ID = "v2.9.12 Final"
BUILD_NUMBER = 21
RELEASE_LINE = "v2.9.12 ready-to-transfer setup file generation and add-on icon"


def addon_version() -> str:
    """Return the active Kodi add-on version string."""
    return ADDON_VERSION


def build_id() -> str:
    """Return the human-readable active build identifier."""
    return BUILD_ID
