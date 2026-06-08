"""v3 playback handoff -- runs in the playercorefactory EXTERNAL-player process.

Key difference from v2: this runs outside Kodi, so there are NO xbmc / CEC APIs. Everything is
network:
  * switch the TV to the OPPO -- by Broadlink IR if configured (CEC-free), else an interim OPPO
    power-cycle (the OPPO's own One-Touch-Play on power-on);
  * play the file on the OPPO over the HTTP app API (identical to v2);
  * block until the OPPO goes idle;
  * switch the TV back to Kodi -- by Broadlink IR if configured, otherwise rely on Kodi re-asserting
    itself as the active source when this external player exits.

There is deliberately no ``CECActivateSource`` reclaim -- v3 is CEC-free by design.
"""
from __future__ import annotations

import time

from . import ir
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


def _best_effort(fn, label: str):
    try:
        return fn()
    except OppoError as exc:
        log("{} step skipped (non-fatal): {}".format(label, exc))
        return None


def play_on_oppo(config, kodi_file: str, should_abort=None) -> bool:
    """Hand ``kodi_file`` to the OPPO and block until it stops. Returns True if playback was seen."""
    if should_abort is None:
        should_abort = lambda: False

    folder, basename = split_share_relative(kodi_file, config.path_from)
    if not basename:
        log("Cannot map {!r} with path_from={!r}".format(kodi_file, config.path_from))
        return False

    # Disc folders (BDMV / VIDEO_TS): mount the disc folder's parent and play the disc folder via
    # /checkfolderhasBDMV. Single files: mount the file's folder and play the bare basename.
    rel = (folder + "/" + basename) if folder else basename
    is_disc = is_disc_path(rel)
    if is_disc:
        droot = disc_folder(rel)
        mount_rel, play_name = droot.rsplit("/", 1) if "/" in droot else ("", droot)
    else:
        mount_rel, play_name = folder, basename

    client = OppoClient(config)

    # --- switch the TV to the OPPO ---
    if ir.configured(config):
        log("Switching the TV to the OPPO via Broadlink IR")
        ir.switch_to_oppo(config)
    elif config.grab_tv_on_play:
        log("No IR configured; interim switch via OPPO power-cycle (One-Touch-Play)")
        try:
            client.power_cycle()
        except OppoError as exc:
            log("TV grab (power-cycle) failed (non-fatal): {}".format(exc))

    if not client.wake_and_wait():
        log("OPPO app API ({}:{}) did not wake".format(config.oppo_ip, config.oppo_http_port))
        return False

    # Init dance (without it, signin/mount fail on a fresh API session).
    _best_effort(client.get_firmware_version, "firmware")
    _best_effort(client.get_setup_menu, "setup")
    app_ip = local_ip_toward(config.oppo_ip, config.oppo_http_port)
    _best_effort(lambda: client.signin(app_ip), "signin")
    _best_effort(client.get_global_info, "global info")

    # Dual-homed NAS: use the OPPO's own NFS server from its device list, not Kodi's address.
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
        _best_effort(lambda: client.mount_nfs(server, mount_folder), "mount retry")

    if is_disc:
        _best_effort(client.stop, "stop")  # clear any stuck bd_is_playing
        _interruptible_sleep(2.0, should_abort)
        reply = _best_effort(lambda: client.play_bdmv(play_name), "play-bdmv")
    else:
        reply = _best_effort(lambda: client.play_file(server, play_name), "play")
    log("Play reply: {!r}".format(reply))
    if isinstance(reply, dict) and reply.get("success") is False:
        log("OPPO rejected the file: {}".format(reply.get("retInfo") or reply.get("msg") or ""))
        return False

    started = _watch_playback(config, client, should_abort)

    # --- switch the TV back to Kodi ---
    if ir.configured(config):
        log("Switching the TV back to Kodi via Broadlink IR")
        ir.switch_to_kodi(config)
    else:
        log("No IR: relying on Kodi re-asserting active source when this player exits")
    return started


def _watch_playback(config, client, should_abort) -> bool:
    """Two-phase wait, per the design:

      Phase 1 (pre-playback) -- HTTP /getglobalinfo polling until playback STARTS. Verbose mode only
        carries useful info once the OPPO is actually playing, and the NFS mount + buffer can take a
        while, so the latency-tolerant HTTP poll owns the startup window.
      Phase 2 (playing) -- open a fresh verbose ``#SVM 3`` connection and block until ``@UPL STOP``,
        which is pushed the instant playback ends (no poll lag). The connection is terminated on stop.

    Returns True if playback was observed.
    """
    interval = max(2.0, float(config.poll_interval))
    grace = max(int(config.idle_confirmations), 10)  # NFS mount + buffer can be slow to start
    _interruptible_sleep(interval, should_abort)
    idle = 0
    while not should_abort():
        if client.is_playing():
            break
        idle += 1
        if idle >= grace:
            log("OPPO never reported playback after {} HTTP polls; giving up.".format(idle))
            return False
        _interruptible_sleep(interval, should_abort)
    else:
        return False

    log("Playback started; opening verbose (#SVM 3) for instant stop detection.")
    try:
        client.verbose_watch_until_stop(should_abort)
    except OppoError as exc:
        log("verbose watch failed ({}); falling back to HTTP polling".format(exc))
        _http_watch_until_idle(config, client, should_abort)
    return True


def _http_watch_until_idle(config, client, should_abort) -> None:
    """Fallback for phase 2: poll /getglobalinfo until idle for N consecutive reads."""
    interval = max(2.0, float(config.poll_interval))
    needed = max(1, int(config.idle_confirmations))
    idle = 0
    while not should_abort():
        if client.is_playing():
            idle = 0
        else:
            idle += 1
            if idle >= needed:
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
