"""Playback handoff: Kodi -> OPPO, with CEC switching.

``play_on_oppo`` runs the launch sequence (activate -> wake -> signin -> mount -> play),
then blocks polling /getglobalinfo until the OPPO has been idle long enough to call the
session ended, and finally reclaims the TV by CEC. It takes a ``should_abort`` callable so
the Kodi service can cut the watch loop short on shutdown.
"""
from __future__ import annotations

import time

from . import cec
from .kodilog import log
from .oppo_http import OppoClient, OppoError


def _notify(line: str, time_ms: int = 4000) -> None:
    try:
        import xbmcgui

        xbmcgui.Dialog().notification("OppoKodiBridge", line, time=time_ms)
    except Exception:
        log("notify: {}".format(line))


def _best_effort(fn, label: str) -> None:
    try:
        fn()
    except OppoError as exc:
        log("{} step skipped (non-fatal): {}".format(label, exc))


def play_on_oppo(config, kodi_file: str, should_abort=None) -> bool:
    """Hand ``kodi_file`` to the OPPO and block until it stops, then reclaim the TV."""
    if should_abort is None:
        should_abort = lambda: False

    if config.cec_auto_enable:
        cec.ensure_kodi_cec_enabled()

    client = OppoClient(config)
    try:
        client.activate()
        _best_effort(client.wake, "wake")
        client.signin()
        _best_effort(lambda: client.ensure_share_mounted(kodi_file), "mount")
        reply = client.play(kodi_file)
        log("Handoff launched: {!r}".format(reply))
    except OppoError as exc:
        log("Handoff failed: {}".format(exc))
        _notify("Could not reach the OPPO")
        return False

    _notify("Playing on the OPPO")
    _watch_until_idle(config, client, should_abort)

    if config.cec_reclaim_on_stop:
        cec.reclaim_tv()
        _notify("Back to Kodi")
    return True


def _watch_until_idle(config, client, should_abort) -> None:
    """Poll /getglobalinfo until the OPPO has read idle for N consecutive polls."""
    interval = max(2.0, float(config.poll_interval))
    needed = max(1, int(config.idle_confirmations))
    _interruptible_sleep(interval, should_abort)  # let the player actually start
    idle_streak = 0
    seen_playing = False
    while not should_abort():
        if client.is_playing():
            seen_playing = True
            idle_streak = 0
        else:
            idle_streak += 1
            limit = needed if seen_playing else max(needed, 4)
            if idle_streak >= limit:
                log("OPPO idle for {} polls; playback considered ended.".format(idle_streak))
                return
        _interruptible_sleep(interval, should_abort)


def _interruptible_sleep(seconds: float, should_abort) -> None:
    waited = 0.0
    step = 0.5
    while waited < seconds:
        if should_abort():
            return
        time.sleep(min(step, seconds - waited))
        waited += step
