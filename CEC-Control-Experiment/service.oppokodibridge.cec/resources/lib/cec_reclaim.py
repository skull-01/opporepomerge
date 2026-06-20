"""Single-shot Kodi CEC-reclaim signalling between the external player and the in-Kodi service.

NEVER-REASSERT INVARIANT (the operator's design rule): the reclaim fires EXACTLY ONCE per stop event.
The external player (which has no Kodi APIs) drops a one-shot request file when its handoff ends; the
in-Kodi service consumes it ONCE, calls ``CECActivateSource``, and it is gone. There is deliberately
NO standing monitor that re-asserts active source -- that would override a manual input change and make
the TV un-leaveable (CEC is open-loop: we cannot tell "the TV missed my frame" from "the user switched
away"). A manual input change must STICK.
"""
from __future__ import annotations

import os

RECLAIM_FLAG = "kodi_reclaim_request"


def _flag(data_dir: str) -> str:
    return os.path.join(data_dir, RECLAIM_FLAG)


def request(data_dir: str) -> bool:
    """Drop a one-shot reclaim request. Called ONCE, when the external player's handoff ends."""
    try:
        os.makedirs(data_dir, exist_ok=True)
        open(_flag(data_dir), "w", encoding="utf-8").close()
        return True
    except OSError:
        return False


def consume(data_dir: str, fire) -> bool:
    """If a reclaim request is pending, fire it ONCE and clear it; return whether it fired.

    The flag is removed BEFORE ``fire`` runs, so a failure in ``fire`` can never cause a re-fire loop.
    ``fire`` is the single CEC assertion (e.g. ``xbmc.executebuiltin('CECActivateSource')``). This is
    the only place the service asserts active source -- it never re-asserts on its own.
    """
    path = _flag(data_dir)
    if not os.path.exists(path):
        return False
    try:
        os.remove(path)
    except OSError:
        return False
    fire()
    return True
