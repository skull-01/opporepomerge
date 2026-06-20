"""Detect which Kodi playback items qualify for OPPO handoff -- the single source of truth.

ONLY disc content goes to the OPPO: disc images (``.iso``) and disc folders (BDMV / VIDEO_TS /
HVDVD_TS). Everything else (MKV, MP4, loose m2ts, ...) stays in Kodi. ``pcf.py`` builds the
playercorefactory routing rules from ``PCF_RULES`` here, and the orchestrator re-checks at play time,
so the XML routing and the runtime classifier can never drift apart.
"""
from __future__ import annotations

import urllib.parse

_DISC_MARKERS = ("/bdmv/", "/video_ts/", "/hvdvd_ts/")

# The playercorefactory <rule> patterns that route a file to the OPPO external player. (kind, pattern)
# where kind is "filetypes" or "filename". One definition shared by pcf.py's XML and is_handoff_target.
PCF_RULES = (
    ("filetypes", "iso"),
    ("filename", "(?i).*/bdmv/.*"),
    ("filename", "(?i).*/video_ts/.*"),
    ("filename", r"(?i).*\.bdmv$"),
    ("filename", r"(?i).*\.iso$"),
)


def is_iso(path: str) -> bool:
    """True for a disc-image file (``.iso``)."""
    return str(path).strip().lower().endswith(".iso")


def is_disc_path(path: str) -> bool:
    """True for a Blu-ray / DVD disc-folder path (BDMV / VIDEO_TS / HVDVD_TS structure)."""
    low = str(path).replace("\\", "/").lower()
    return low.endswith((".bdmv", ".ifo")) or any(m in low for m in _DISC_MARKERS)


def disc_folder(path: str) -> str:
    """The disc folder (the dir that CONTAINS BDMV/VIDEO_TS) from a disc-structure path.

    ``…/Ant-Man (2015)/BDMV/index.bdmv`` -> ``…/Ant-Man (2015)``.
    """
    text = str(path).replace("\\", "/")
    low = text.lower()
    for marker in _DISC_MARKERS:
        idx = low.find(marker)
        if idx >= 0:
            return text[:idx]
    return text


def is_handoff_target(path: str) -> bool:
    """The handoff filter. Route to the OPPO ONLY for disc content: disc images (``.iso``) and disc
    folders (BDMV / VIDEO_TS / HVDVD_TS). Everything else stays in Kodi -- this is the only kind of
    file Kodi should send to the OPPO."""
    text = str(path)
    if text.lower().startswith(("nfs://", "smb://")):
        text = urllib.parse.unquote(text)
    return is_iso(text) or is_disc_path(text)


# Backwards-compatible alias (oppo_http re-exports this for existing importers/tests).
is_oppo_target = is_handoff_target
