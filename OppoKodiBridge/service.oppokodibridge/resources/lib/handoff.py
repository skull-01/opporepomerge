"""Playback handoff: Kodi -> OPPO, with CEC switching.

Mirrors the working emby-chinoppo-bridge launch sequence: sign in, resolve the OPPO's own NFS
server from its device list (the address it can reach), log in, mount the file's folder at
``/mnt/nfs1``, then play the file from there. Playback is confirmed by polling ``/getglobalinfo``;
when it ends, Kodi reclaims the TV by CEC. Takes a ``should_abort`` callable so the service can cut
the watch loop short on shutdown.
"""
from __future__ import annotations

import time

from . import cec
from .kodilog import log
from .oppo_http import (
    OppoClient,
    OppoError,
    local_ip_toward,
    nfs_server_from_devices,
    parse_media_path,
)


def _notify(line: str, time_ms: int = 4000) -> None:
    try:
        import xbmcgui

        xbmcgui.Dialog().notification("OppoKodiBridge", line, time=time_ms)
    except Exception:
        log("notify: {}".format(line))


def _best_effort(fn, label: str):
    try:
        return fn()
    except OppoError as exc:
        log("{} step skipped (non-fatal): {}".format(label, exc))
        return None


def play_on_oppo(config, kodi_file: str, should_abort=None) -> bool:
    """Hand ``kodi_file`` to the OPPO and block until it stops, then reclaim the TV."""
    if should_abort is None:
        should_abort = lambda: False

    if config.cec_auto_enable:
        cec.ensure_kodi_cec_enabled()

    server, folder, filename = parse_media_path(kodi_file)
    if not filename:
        log("Could not parse a playable file from: {}".format(kodi_file))
        _notify("Couldn't read the file path")
        return False

    client = OppoClient(config)
    try:
        app_ip = local_ip_toward(config.oppo_ip, config.oppo_http_port)
        _best_effort(lambda: client.signin(app_ip), "signin")

        # The OPPO may reach the NAS at a different address than Kodi (dual-homed); prefer the
        # OPPO's own NFS device from getdevicelist.
        devices = _best_effort(client.get_device_list, "device list")
        oppo_server = nfs_server_from_devices(devices) if devices else None
        if oppo_server:
            server = oppo_server
        log("Handoff: server={} folder={!r} file={!r}".format(server, folder, filename))

        _best_effort(lambda: client.login_nfs(server), "login")
        mount = _best_effort(lambda: client.mount_nfs(server, folder.lstrip("/")), "mount")
        if isinstance(mount, dict) and mount.get("success") is False:
            log("mount reported failure: {}".format(mount.get("retInfo") or mount.get("msg")))

        reply = client.play_file(server, filename, "0", nfs=True)
        log("Play reply: {!r}".format(reply))
        if isinstance(reply, dict) and reply.get("success") is False:
            _notify("OPPO rejected the file: {}".format(reply.get("retInfo") or reply.get("msg") or ""))
            return False
    except OppoError as exc:
        log("Handoff failed: {}".format(exc))
        _notify("Could not reach the OPPO")
        return False

    _notify("Playing on the OPPO")
    started = _watch_until_idle(config, client, should_abort)

    if config.cec_reclaim_on_stop:
        cec.reclaim_tv()
        _notify("Back to Kodi")
    return started


def _watch_until_idle(config, client, should_abort) -> bool:
    """Poll /getglobalinfo until the OPPO has read idle for N consecutive polls.

    Returns True if playback was ever observed (so the caller knows the handoff actually played).
    """
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
            # Before we ever see it play, allow more polls (NFS mount + buffering can take a while).
            limit = needed if seen_playing else max(needed, 8)
            if idle_streak >= limit:
                if not seen_playing:
                    log("OPPO never reported playback; giving up after {} polls.".format(idle_streak))
                else:
                    log("OPPO idle for {} polls; playback considered ended.".format(idle_streak))
                return seen_playing
        _interruptible_sleep(interval, should_abort)
    return seen_playing


def _interruptible_sleep(seconds: float, should_abort) -> None:
    waited = 0.0
    step = 0.5
    while waited < seconds:
        if should_abort():
            return
        time.sleep(min(step, seconds - waited))
        waited += step
