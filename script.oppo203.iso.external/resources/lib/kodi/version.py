"""Single source of truth for the add-on release identity.

Kodi reads the runtime version from addon.xml, so this module is paired with
``tools/sync_version.py`` and release-audit checks that keep the XML metadata,
expected audit version, and Python version source aligned.
"""

from __future__ import annotations

ADDON_ID = "script.oppo203.iso.external"
ADDON_VERSION = "2.9.16"
BUILD_ID = "v2.9.16 Final"
BUILD_NUMBER = 25
RELEASE_LINE = "v2.9.16 maintenance/hardening: AVR http_handoff eligibility + HTTP path translation, SVM3/eISCP transport hardening, configurator-owned settings schema guards, honest Pure-HTTP launch failures, distinct Samsung HDMI defaults, and property-test coercion-crash fixes"


def addon_version() -> str:
    """Return the active Kodi add-on version string."""
    return ADDON_VERSION


def build_id() -> str:
    """Return the human-readable active build identifier."""
    return BUILD_ID
