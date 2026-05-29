"""Skin-aware keymap variants (v1.1.5).

Generates valid Kodi keymap XML (e.g. `userdata/keymaps/oppo.xml`)
that overlays the user's active skin so playback-control keys (Play,
Stop, Eject, Info) reach the addon's remote bridge regardless of skin.

Three skin profiles are bundled:

  - estuary    (default since Krypton)
  - confluence (legacy default)
  - arctic     (Arctic Zephyr family)

Each profile shares the same base keymap; the only deltas are the
per-skin window names referenced in <!--<window>--> sections.

Public API
----------
- SKINS                                        -> tuple
- generate(skin)                               -> str (XML)
- is_well_formed(text)                         -> bool
"""

import xml.etree.ElementTree as ET

SKINS = ("estuary", "confluence", "arctic")

# Base keys -> remote action.  These are the addon's bridged actions.
_BINDINGS = (
    # key            action
    ("play", "RunPlugin(plugin://script.oppo203.iso.external/?action=play)"),
    ("stop", "RunPlugin(plugin://script.oppo203.iso.external/?action=stop)"),
    ("eject", "RunPlugin(plugin://script.oppo203.iso.external/?action=eject)"),
    ("info", "RunPlugin(plugin://script.oppo203.iso.external/?action=info)"),
    ("menu", "RunPlugin(plugin://script.oppo203.iso.external/?action=menu)"),
    ("pause", "RunPlugin(plugin://script.oppo203.iso.external/?action=pause)"),
    ("skipnext", "RunPlugin(plugin://script.oppo203.iso.external/?action=next)"),
    ("skipprevious", "RunPlugin(plugin://script.oppo203.iso.external/?action=prev)"),
)

# Window id used for "FullscreenVideo" in each skin.  All three modern
# skins use the same global window name; the per-skin entry exists so
# future skin-specific overrides slot in cleanly.
_SKIN_WINDOWS = {
    "estuary": "FullscreenVideo",
    "confluence": "FullscreenVideo",
    "arctic": "FullscreenVideo",
}


def generate(skin: str) -> str:
    """Return a keymap XML string for the given skin id."""
    if skin not in SKINS:
        raise KeyError("unknown skin: " + str(skin))
    window = _SKIN_WINDOWS[skin]
    parts = []
    parts.append('<?xml version="1.0" encoding="utf-8"?>')
    parts.append("<keymap>")
    parts.append("  <!-- skin profile: " + skin + " -->")
    parts.append("  <global>")
    parts.append("    <keyboard>")
    for key, act in _BINDINGS:
        parts.append("      <" + key + ">" + act + "</" + key + ">")
    parts.append("    </keyboard>")
    parts.append("  </global>")
    parts.append("  <" + window + ">")
    parts.append("    <keyboard>")
    for key, act in _BINDINGS:
        parts.append("      <" + key + ">" + act + "</" + key + ">")
    parts.append("    </keyboard>")
    parts.append("  </" + window + ">")
    parts.append("</keymap>")
    return "\n".join(parts) + "\n"


def is_well_formed(text: str) -> bool:
    if not text or not str(text).strip():
        return False
    try:
        ET.fromstring(text)
        return True
    except ET.ParseError:
        return False
