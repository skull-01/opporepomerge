"""Shared project constants for script.oppo203.iso.external.

Build 2 of the v2.9.1 cleanup line introduces this small module to avoid
repeating protected invariants across runtime code, tests, and audit helpers.
Only low-risk constants are centralized here; the OPPO command-map data itself
remains in its historical location until the dedicated command-map migration
build.
"""
from __future__ import annotations

OPPO_COMMAND_MAP_SIZE: int = 76
MIN_COVERAGE_PERCENT: int = 99

# XML/service 4K UHD disc-routing invariants.
UHD_DISC_TAGS: tuple[str, ...] = ("4k", "uhd", "2160p")
XML_4K_TAG_FILENAME_PATTERN: str = r".*(4K|4k|UHD|uhd|2160p|2160P).*"
XML_DISC_FILETYPES: tuple[str, ...] = ("iso", "bdmv", "mpls")
XML_LOOSE_VIDEO_FILETYPES: tuple[str, ...] = (
    "mkv", "mp4", "m4v", "mov", "mpg", "mpeg", "avi", "wmv",
    "flv", "webm", "ts", "m2ts", "mts", "m2t", "vob", "ogm",
    "ogv", "divx", "xvid", "3gp", "3g2", "f4v", "rm", "rmvb",
    "asf",
)
LOOSE_VIDEO_EXTENSIONS: tuple[str, ...] = tuple(f".{item}" for item in XML_LOOSE_VIDEO_FILETYPES)
DISC_STYLE_EXTENSIONS_4K: tuple[str, ...] = tuple(f".{item}" for item in XML_DISC_FILETYPES)
