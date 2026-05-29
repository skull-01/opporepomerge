"""Shared 4K/UHD disc-style classification helpers.

This module centralizes the v2.5.3+ policy that was previously duplicated in
intercept.py, installer.py, and playercorefactory_merge.py.  It intentionally
preserves the existing behavior: filename/path tag matching remains a simple
case-insensitive substring check for 4K, UHD, or 2160p; XML mode remains
filename/path driven; and loose/raw video extensions stay with Kodi.
"""

from __future__ import annotations

import os

try:  # package import during normal use
    from ..oppo.constants import (
        DISC_STYLE_EXTENSIONS_4K,  # noqa: F401  # re-exported via shared-constants hub
        LOOSE_VIDEO_EXTENSIONS,
        UHD_DISC_TAGS,
        XML_4K_TAG_FILENAME_PATTERN,
        XML_DISC_FILETYPES,
        XML_LOOSE_VIDEO_FILETYPES,
    )
except ImportError:  # pragma: no cover - top-level test import compatibility
    from constants import (  # type: ignore
        DISC_STYLE_EXTENSIONS_4K,  # noqa: F401  # re-exported via shared-constants hub
        LOOSE_VIDEO_EXTENSIONS,
        UHD_DISC_TAGS,
        XML_4K_TAG_FILENAME_PATTERN,
        XML_DISC_FILETYPES,
        XML_LOOSE_VIDEO_FILETYPES,
    )


def norm_path(path: object) -> str:
    """Return a forward-slash path string, preserving historical handling."""
    if path is None:
        return ""
    return str(path).replace("\\", "/")


def lower_path(path: object) -> str:
    """Return a normalized lower-case path string."""
    return norm_path(path).lower()


def extension(path: object) -> str:
    """Return the lower-case extension, including the leading dot."""
    return os.path.splitext(lower_path(path))[1]


def has_uhd_disc_tag(path: object) -> bool:
    """Return True if the visible path contains 4K, UHD, or 2160p.

    The implementation intentionally matches the historical substring behavior
    used by intercept.py, avoiding behavior changes in this cleanup build.
    """
    pl = lower_path(path)
    return any(tag in pl for tag in UHD_DISC_TAGS)


def is_bdmv_navigation_path(path: object) -> bool:
    """Return True for supported BDMV navigation/playlist handoff files."""
    pl = lower_path(path)
    if pl.endswith("/bdmv/index.bdmv"):
        return True
    if pl.endswith("/bdmv/movieobject.bdmv"):
        return True
    if pl.endswith(".bdmv") and "/bdmv/" in pl:
        return True
    if pl.endswith(".mpls") and "/bdmv/playlist/" in pl:
        return True
    return False


def is_loose_video_path(path: object) -> bool:
    """Return True for loose/raw video containers that must stay in Kodi."""
    return extension(path) in LOOSE_VIDEO_EXTENSIONS


def is_4k_disc_style_source(path: object) -> bool:
    """Return True when path is a supported disc-style handoff target."""
    if not path:
        return False
    if is_loose_video_path(path):
        return False
    if extension(path) == ".iso":
        return True
    return is_bdmv_navigation_path(path)


def should_intercept_4k_disc_source(path: object) -> bool:
    """Return True only for tagged 4K/UHD/2160p disc-style sources."""
    if not path:
        return False
    if not has_uhd_disc_tag(path):
        return False
    return is_4k_disc_style_source(path)


def xml_4k_tag_filename_pattern() -> str:
    """Return the exact Option 4 filename regex used in playercorefactory XML."""
    return XML_4K_TAG_FILENAME_PATTERN


def xml_disc_filetypes() -> tuple[str, ...]:
    """Return the ordered disc-style filetypes used by Option 4 XML rules."""
    return XML_DISC_FILETYPES


def xml_loose_video_filetypes() -> tuple[str, ...]:
    """Return loose/raw video filetypes excluded from Option 4 XML rules."""
    return XML_LOOSE_VIDEO_FILETYPES
