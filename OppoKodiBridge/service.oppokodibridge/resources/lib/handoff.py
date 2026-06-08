"""Playback handoff: Kodi -> OPPO, with CEC switching.

Runs the launch sequence verified live on the operator's M9205: wake the app API, run the init
calls that prime it, log in to the OPPO's own NFS server (resolved from its device list), mount the
file's folder, then play the bare filename from /mnt/nfs1. Playback is confirmed by polling
/getglobalinfo; when it ends, Kodi reclaims the TV by CEC. Takes a ``should_abort`` callable so the
service can cut the watch loop short on shutdown.
"""
from __future__ import annotations

import time

from . import cec
from .kodilog import log
from .oppo_http import (
    OppoClient,
    OppoError,
    disc_folder,
    is_disc_path,
    local_ip_toward,
    nfs_server_from_devices,
    oppo_mount_folder,
    parse_media_path,
    split_share_relative,
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

    folder, basename = split_share_relative(kodi_file, config.path_from)
    if not basename:
        log("Cannot map {!r} with path_from={!r}".format(kodi_file, config.path_from))
        _notify("Path mapping not set for this share")
        return False

    # Disc folders (BDMV / VIDEO_TS): the OPPO plays the disc FOLDER, not the index file. Mount the
    # disc folder's parent and play the disc folder itself via /checkfolderhasBDMV.
    rel = (folder + "/" + basename) if folder else basename
    is_disc = is_disc_path(rel)
    if is_disc:
        droot = disc_folder(rel)
        if "/" in droot:
            mount_rel, play_name = droot.rsplit("/", 1)
        else:
            mount_rel, play_name = "", droot
    else:
        mount_rel, play_name = folder, basename

    client = OppoClient(config)

    # Switch the TV to the OPPO by broadcasting CEC <Active Source> for its HDMI input from the Kodi
    # box -- instant, no OPPO power-cycle (the OPPO doesn't assert active source on a play-while-on).
    if config.grab_tv_on_play:
        log("Switching the TV to the OPPO via CEC route to {}".format(config.oppo_hdmi_phys))
        cec.switch_tv_to_oppo(config.oppo_hdmi_phys)

    if not client.wake_and_wait():
        log("OPPO app API ({}:{}) did not wake".format(config.oppo_ip, config.oppo_http_port))
        _notify("OPPO not responding")
        return False

    # Init dance that primes the device (without it, signin/mount fail on a fresh API session).
    _best_effort(client.get_firmware_version, "firmware")
    _best_effort(client.get_setup_menu, "setup")
    app_ip = local_ip_toward(config.oppo_ip, config.oppo_http_port)
    _best_effort(lambda: client.signin(app_ip), "signin")
    _best_effort(client.get_global_info, "global info")

    # The OPPO may reach the NAS at a different address than Kodi (dual-homed); use its own device.
    server = nfs_server_from_devices(_best_effort(client.get_device_list, "device list"))
    if not server:
        server = parse_media_path(kodi_file)[0]

    _best_effort(lambda: client.login_nfs(server), "login")
    _best_effort(client.get_nfs_share_list, "share list")
    _interruptible_sleep(2.0, should_abort)
    _best_effort(client.get_setup_menu, "setup")

    mount_folder = oppo_mount_folder(mount_rel, config.path_to)
    log("Handoff: server={} disc={} mount={!r} play={!r}".format(server, is_disc, mount_folder, play_name))
    mount = _best_effort(lambda: client.mount_nfs(server, mount_folder), "mount")
    if isinstance(mount, dict) and mount.get("success") is False:
        log("mount failed ({}); re-login and retry".format(mount.get("retInfo") or mount.get("msg")))
        _best_effort(lambda: client.login_nfs(server), "re-login")
        _interruptible_sleep(2.0, should_abort)
        _best_effort(client.get_setup_menu, "setup")
        _best_effort(lambda: client.mount_nfs(server, mount_folder), "mount retry")

    if is_disc:
        _best_effort(client.stop, "stop")  # clear any stuck bd_is_playing
        _interruptible_sleep(2.0, should_abort)
        reply = _best_effort(lambda: client.play_bdmv(play_name), "play-bdmv")
    else:
        reply = _best_effort(lambda: client.play_file(server, play_name), "play")
    log("Play reply: {!r}".format(reply))
    if isinstance(reply, dict) and reply.get("success") is False:
        _notify("OPPO rejected the file: {}".format(reply.get("retInfo") or reply.get("msg") or ""))
        return False

    _notify("Playing on the OPPO")
    started = _watch_until_idle(config, client, should_abort)

    if config.cec_reclaim_on_stop:
        cec.reclaim_tv()
        _notify("Back to Kodi")
    return started


def _watch_until_idle(config, client, should_abort) -> bool:
    """Poll /getglobalinfo until the OPPO has read idle for N consecutive polls.

    Returns True if playback was ever observed.
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
            # NFS mount + buffering can take a while before the first 'playing' read.
            limit = needed if seen_playing else max(needed, 10)
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
