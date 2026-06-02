"""HDMI switch sequencing policy for the OPPO handoff (Xnoppo V3).

Selectable timing for the TV input switch relative to player start:

* ``immediate`` (default) -- today's TV-first order: switch the TV, then start the player.
  Byte-identical to the frozen behaviour.
* ``delayed`` -- start the player first, wait ``compute_play_delay()`` seconds (>= 6 for
  ISO/BDMV, which take longer to mount and output video) before switching the TV, with an
  optional ``av_delay_hdmi`` stagger afterwards. This avoids switching the TV to a player that
  is still black/loading.

This module is the pure policy (mode + delays); the wiring lives in
``external_player._sequence_switch_and_play`` so the ordering is exercised there while the
arithmetic stays trivially testable here.
"""

from __future__ import annotations

from typing import Any

HDMI_SWITCH_MODES = ("immediate", "delayed")
# Disc-style sources need longer before the TV is switched: an ISO/BDMV mounts then spins up.
DISC_MIN_DELAY_SECONDS = 6


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def switch_mode(settings: Any) -> str:
    """Return the configured HDMI switch mode, defaulting to (and clamping unknowns to) immediate."""
    mode = str(settings.get("hdmi_switch_mode", "immediate")).strip().lower()
    return mode if mode in HDMI_SWITCH_MODES else "immediate"


def _is_disc_source(media_file: str) -> bool:
    try:
        from .disc_classification import extension, is_bdmv_navigation_path
    except ImportError:  # pragma: no cover - bare-name fallback (run as __main__)
        from disc_classification import extension, is_bdmv_navigation_path  # type: ignore[no-redef]

    return extension(media_file) == ".iso" or is_bdmv_navigation_path(media_file)


def compute_play_delay(media_file: str, play_delay_hdmi: Any) -> int:
    """Seconds to wait after starting the player before switching the TV (delayed mode).

    Disc-style sources (ISO/BDMV) are floored at ``DISC_MIN_DELAY_SECONDS``; everything else
    uses the configured base delay (>= 0)."""
    base = max(0, _coerce_int(play_delay_hdmi, 2))
    if _is_disc_source(media_file):
        return max(base, DISC_MIN_DELAY_SECONDS)
    return base


def av_stagger(settings: Any) -> int:
    """Extra seconds to wait after the TV switch before downstream (AVR) input changes settle."""
    return max(0, _coerce_int(settings.get("av_delay_hdmi", "0"), 0))
