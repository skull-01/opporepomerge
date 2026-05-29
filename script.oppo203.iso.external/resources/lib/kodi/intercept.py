"""Service interception breadth + remote-bridge polish (v1.1.5).

Pure-function classification of paths a Kodi `Player.OnPlay` callback
might see, with a configurable whitelist/blacklist that the service
checks before deciding to redirect playback to the external OPPO.

Public API
----------
- DISC_KIND constants
- classify(path, fs=None)             -> str (DISC_KIND_* / "other")
- is_disc_image(path, fs=None)        -> bool
- should_intercept(path, *, whitelist=None, blacklist=None,
                   fs=None)            -> bool
- normalise_pattern(pattern)           -> str
- pattern_matches(path, pattern)       -> bool

A "disc image" includes:
  - .iso, .img files (case-insensitive)
  - BDMV folder layouts (path ends in /BDMV or contains /BDMV/index.bdmv)
  - VIDEO_TS folder layouts (path ends in /VIDEO_TS or contains
    /VIDEO_TS/VIDEO_TS.IFO)
  - .bdmv files directly (e.g. /path/to/index.bdmv)
  - .m2ts, .mpls (BD playlist) when in a BDMV-shaped tree
  - sibling-MKV: a .mkv whose folder also contains BDMV/ - the user's
    rip workflow.
"""

from __future__ import annotations

import os
import re as _re
from collections.abc import Iterable
from typing import Protocol

try:
    from .disc_classification import (  # type: ignore[attr-defined]
        DISC_STYLE_EXTENSIONS_4K,  # noqa: F401  # re-exported for sibling modules
        UHD_DISC_TAGS,  # noqa: F401  # re-exported for sibling modules
    )
    from .disc_classification import (  # type: ignore[attr-defined]
        LOOSE_VIDEO_EXTENSIONS as EXCLUDED_LOOSE_VIDEO_EXTENSIONS,  # noqa: F401
    )
    from .disc_classification import (
        extension as _disc_extension,
    )
    from .disc_classification import (
        has_uhd_disc_tag as _shared_path_has_uhd_disc_tag,
    )
    from .disc_classification import (
        is_4k_disc_style_source as _shared_is_4k_disc_style_source,
    )
    from .disc_classification import (
        is_bdmv_navigation_path as _shared_is_bdmv_navigation_path,
    )
    from .disc_classification import (
        is_loose_video_path as _shared_is_loose_video_path,
    )
    from .disc_classification import (
        should_intercept_4k_disc_source as _shared_should_intercept_4k_disc_source,
    )
except ImportError:  # pragma: no cover - top-level test import compatibility
    from disc_classification import (  # type: ignore
        DISC_STYLE_EXTENSIONS_4K,  # noqa: F401  # re-exported for sibling modules
        UHD_DISC_TAGS,  # noqa: F401  # re-exported for sibling modules
    )
    from disc_classification import (  # type: ignore[no-redef]
        LOOSE_VIDEO_EXTENSIONS as EXCLUDED_LOOSE_VIDEO_EXTENSIONS,  # noqa: F401
    )
    from disc_classification import (  # type: ignore[no-redef]
        extension as _disc_extension,
    )
    from disc_classification import (  # type: ignore[no-redef]
        has_uhd_disc_tag as _shared_path_has_uhd_disc_tag,
    )
    from disc_classification import (  # type: ignore[no-redef]
        is_4k_disc_style_source as _shared_is_4k_disc_style_source,
    )
    from disc_classification import (  # type: ignore[no-redef]
        is_bdmv_navigation_path as _shared_is_bdmv_navigation_path,
    )
    from disc_classification import (  # type: ignore[no-redef]
        is_loose_video_path as _shared_is_loose_video_path,
    )
    from disc_classification import (  # type: ignore[no-redef]
        should_intercept_4k_disc_source as _shared_should_intercept_4k_disc_source,
    )


DISC_KIND_ISO = "iso"
DISC_KIND_BDMV = "bdmv"
DISC_KIND_VIDEO_TS = "video_ts"
DISC_KIND_M2TS = "m2ts"
DISC_KIND_MPLS = "mpls"
DISC_KIND_MKV_SIBLING = "mkv_sibling"
DISC_KIND_OTHER = "other"


class _FsLike(Protocol):
    def exists(self, p: object) -> bool: ...  # pragma: no cover

    def isdir(self, p: object) -> bool: ...  # pragma: no cover


class _RealFS:
    def exists(self, p: object) -> bool:
        return os.path.exists(str(p))

    def isdir(self, p: object) -> bool:
        return os.path.isdir(str(p))


def _norm(p: object) -> str:
    if p is None:
        return ""
    return str(p).replace("\\", "/")


def _lower(p: object) -> str:
    return _norm(p).lower()


def classify(path: object, fs: _FsLike | None = None) -> str:
    """Return the DISC_KIND_* constant for `path`."""
    if not path:
        return DISC_KIND_OTHER
    fs = fs if fs is not None else _RealFS()
    p = _norm(path)
    pl = p.lower()

    # .iso / .img
    if pl.endswith(".iso") or pl.endswith(".img"):
        return DISC_KIND_ISO
    # /BDMV or /BDMV/ at end -> bdmv folder
    if pl.endswith("/bdmv") or pl.endswith("/bdmv/"):
        return DISC_KIND_BDMV
    # index.bdmv or any .bdmv file
    if pl.endswith(".bdmv"):
        return DISC_KIND_BDMV
    # VIDEO_TS folder
    if pl.endswith("/video_ts") or pl.endswith("/video_ts/"):
        return DISC_KIND_VIDEO_TS
    # VIDEO_TS.IFO inside a VIDEO_TS folder
    if pl.endswith("/video_ts.ifo"):
        return DISC_KIND_VIDEO_TS
    # .m2ts / .mpls when path includes /BDMV/
    if pl.endswith(".m2ts") and "/bdmv/" in pl:
        return DISC_KIND_M2TS
    if pl.endswith(".mpls") and "/bdmv/" in pl:
        return DISC_KIND_MPLS
    # MKV with sibling BDMV/
    if pl.endswith(".mkv"):
        parent = os.path.dirname(p)
        sibling = parent + "/BDMV"
        if fs.isdir(sibling) or fs.exists(sibling):
            return DISC_KIND_MKV_SIBLING
        return DISC_KIND_OTHER
    return DISC_KIND_OTHER


def is_disc_image(path: object, fs: _FsLike | None = None) -> bool:
    """True iff classify(path) is any disc-image kind."""
    return classify(path, fs=fs) != DISC_KIND_OTHER


# ---------------------------------------------------------------------
# v2.5.3 Build 1 / v2.9.1 Build 2: 4K UHD disc-style interception classifier
# ---------------------------------------------------------------------

# Constants and shared helpers now live in resources/lib/disc_classification.py.
# The wrapper functions below preserve the historical public API used by the
# service and tests while removing duplicated classification logic.


def _path_has_uhd_disc_tag(path: object) -> bool:
    return _shared_path_has_uhd_disc_tag(path)


def _extension(path: object) -> str:
    return _disc_extension(path)


def _is_bdmv_navigation_path(path: object) -> bool:
    return _shared_is_bdmv_navigation_path(path)


def is_excluded_loose_video(path: object) -> bool:
    """Return True for loose/raw video containers that must stay in Kodi."""
    return _shared_is_loose_video_path(path)


def is_4k_disc_style_source(path: object) -> bool:
    """Return True when `path` is a supported disc-style handoff target.

    This is intentionally narrow: ISO files and BDMV navigation/playlist files
    are candidates; loose/raw stream files such as .m2ts, .ts, .vob, .mkv,
    and .mp4 are not candidates even when their names contain 4K tags.
    """
    return _shared_is_4k_disc_style_source(path)


def should_intercept_4k_disc_source(path: object) -> bool:
    """Return True only for tagged 4K/UHD/2160p disc-style sources.

    v2.5.3 Build 1 policy:
      * require a 4K/UHD/2160p tag in the file or folder path;
      * allow only disc-style sources (.iso, .bdmv navigation, BDMV/PLAYLIST .mpls);
      * always exclude loose/raw video file types so Kodi remains default player.
    """
    return _shared_should_intercept_4k_disc_source(path)


# ---------------------------------------------------------------------
# Whitelist / blacklist
# ---------------------------------------------------------------------


def normalise_pattern(pattern: object) -> str:
    """Lowercase + forward-slashes; strip surrounding whitespace."""
    if not pattern:
        return ""
    return _norm(pattern).strip().lower()


def pattern_matches(path: object, pattern: object) -> bool:
    """Glob-ish match: substring + simple `*` wildcard support.

    - Empty pattern matches nothing (so accidental empties don't open
      the whole filesystem).
    - `*` is the only special character; it becomes `.*`.
    - Match is case-insensitive and forward-slash-normalised, applied
      to the full path.
    """
    p = _lower(path)
    pat = normalise_pattern(pattern)
    if not pat or not p:
        return False
    if "*" not in pat:
        return pat in p
    regex = "^.*" + ".*".join(_re.escape(part) for part in pat.split("*")) + ".*$"
    return _re.match(regex, p) is not None


def should_intercept(
    path: object,
    *,
    whitelist: Iterable[str] | None = None,
    blacklist: Iterable[str] | None = None,
    fs: _FsLike | None = None,
) -> bool:
    """Return True iff the service should redirect playback for `path`.

    Rules (in order):
      1. Path must be a disc image (else False).
      2. If blacklist matches -> False (blacklist beats whitelist).
      3. If whitelist is provided and non-empty:
           True iff a whitelist pattern matches.
      4. If whitelist is empty/None: True (default-allow).
    """
    if not is_disc_image(path, fs=fs):
        return False
    p = path
    for pat in blacklist or []:
        if pattern_matches(p, pat):
            return False
    wl = [pat for pat in (whitelist or []) if pat and pat.strip()]
    if not wl:
        return True
    for pat in wl:
        if pattern_matches(p, pat):
            return True
    return False
