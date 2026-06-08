"""Pure-HTTP handoff to the OPPO/M9205 app API.

Verified live against the operator's M9205 (2026-06-07). The exact sequence the device needs:

  1. wake   -- UDP b"NOTIFY OREMOTE LOGIN" to :7624 starts the :436 app API (it sleeps after boot)
  2. init   -- /getmainfirmwareversion, /getsetupmenu, /signin (appIconType/appIpAddress), /getglobalinfo
  3. login  -- /loginNfsServer for the OPPO's OWN NFS server (read from /getdevicelist)
  4. mount  -- /mountNfsSharedFolder of the FILE'S FOLDER -> the OPPO mounts it at /mnt/nfs1
  5. play   -- /playnormalfile?{...} with path "/mnt/nfs1/<basename>" and the server in extraNetPath

Two hard rules learned on hardware: mount the file's folder and play the bare filename (the OPPO
won't play sub-paths of a mount), and NEVER mount a non-exported folder (it hard-crashes the OPPO).
Mirrors the working emby-chinoppo-bridge; community-reverse-engineered, not an official protocol.
"""
from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, Tuple

MOUNT_TIMEOUT = 25.0
PLAY_TIMEOUT = 15.0
OREMOTE_PORT = 7624

IDLE_STATUSES = {"STOP", "STOPPED", "IDLE", "END", "ENDED", "NO_MEDIA", "NO MEDIA", "HOME"}
PLAY_STATUSES = {
    "PLAY",
    "PLAYING",
    "PAUSE",
    "PAUSED",
    "LOADING",
    "BUFFER",
    "BUFFERING",
    "FFWD",
    "FREV",
    "SFWD",
    "SREV",
}

# The M9205 /getglobalinfo reports playback via these booleans (confirmed on hardware).
_PLAYING_FLAGS = (
    "is_playing",
    "is_video_playing",
    "is_audio_playing",
    "is_bdmv_playing",
    "is_disc_playing",
)


class OppoError(RuntimeError):
    pass


def parse_media_path(media_file: str) -> Tuple[str, str, str]:
    """Split a Kodi/network path into ``(server, folder, filename)``."""
    movie = str(media_file).replace("\\\\", "\\").replace("\\", "/")
    if "://" in movie:
        movie = movie.split("://", 1)[1]
    parts = [p for p in movie.split("/") if p]
    if not parts:
        return ("", "", "")
    server = parts[0]
    filename = parts[-1] if len(parts) > 1 else ""
    folder = "/".join(parts[1:-1]) if len(parts) > 2 else ""
    return (server, folder, filename)


def split_share_relative(media_file: str, path_from: str) -> Tuple[Optional[str], Optional[str]]:
    """``(folder, basename)`` for the file's location WITHIN the share, after stripping ``path_from``.

    ``nfs://192.168.1.177/mnt/Super3/Super3Share/A/B/file.mkv`` with path_from
    ``nfs://192.168.1.177/mnt/Super3/Super3Share`` -> ``("A/B", "file.mkv")``; ``(None, None)`` if the
    prefix doesn't match. Network URLs are URL-decoded so spaces/parens come through literal.
    """
    text = str(media_file)
    if text.lower().startswith(("nfs://", "smb://")):
        text = urllib.parse.unquote(text)
    prefix = (path_from or "").strip().rstrip("/")
    if not prefix or not text.startswith(prefix):
        return (None, None)
    rel = text[len(prefix):].lstrip("/")
    if not rel:
        return (None, None)
    if "/" in rel:
        folder, basename = rel.rsplit("/", 1)
    else:
        folder, basename = "", rel
    return (folder, basename)


def oppo_mount_folder(folder: Optional[str], path_to: str) -> str:
    """The OPPO export folder to mount = the OPPO export root (``path_to``) + the in-share folder."""
    base = (path_to or "").strip().strip("/")
    rel = (folder or "").strip("/")
    if base and rel:
        return base + "/" + rel
    return base or rel


_DISC_MARKERS = ("/bdmv/", "/video_ts/", "/hvdvd_ts/")


def is_disc_path(path: str) -> bool:
    """True for a Blu-ray / DVD disc-folder path (BDMV/VIDEO_TS structure)."""
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


def is_iso(path: str) -> bool:
    """True for a disc-image file (.iso)."""
    return str(path).strip().lower().endswith(".iso")


def is_oppo_target(path: str) -> bool:
    """The handoff filter. Route to the OPPO ONLY for disc content: disc images (.iso) and disc
    folders (BDMV / VIDEO_TS / HVDVD_TS). Everything else (MKV, MP4, loose m2ts, ...) stays in
    Kodi -- this is the only kind of file Kodi will send to the OPPO.
    """
    text = str(path)
    if text.lower().startswith(("nfs://", "smb://")):
        text = urllib.parse.unquote(text)
    return is_iso(text) or is_disc_path(text)


def local_ip_toward(host: str, port: int = 436) -> str:
    """The local source IP the box uses to reach ``host`` — for signin's ``appIpAddress``."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((host, int(port)))
            return sock.getsockname()[0]
        finally:
            sock.close()
    except OSError:
        return "127.0.0.1"


def nfs_server_from_devices(devices: Any) -> Optional[str]:
    """The OPPO's own NFS server name from ``/getdevicelist`` (the address it can reach)."""
    if isinstance(devices, dict):
        for dev in devices.get("devicelist", []) or []:
            if isinstance(dev, dict) and dev.get("sub_type") == "nfs":
                return dev.get("name") or dev.get("path")
    return None


def _containers(info: Any) -> list:
    out: list = []
    if isinstance(info, dict):
        out.append(info)
        for key in ("result", "playinfo", "data"):
            value = info.get(key)
            if isinstance(value, dict):
                out.append(value)
    return out


def status_is_idle(status: object) -> bool:
    s = str(status).strip().upper()
    if s in PLAY_STATUSES:
        return False
    return s == "" or s in IDLE_STATUSES


def info_is_playing(info: Any) -> bool:
    """True when a ``/getglobalinfo`` payload indicates active (or loading) playback."""
    for container in _containers(info):
        for key in _PLAYING_FLAGS:
            flag = container.get(key)
            if isinstance(flag, bool):
                if flag:
                    return True
            elif flag is not None and str(flag).strip().lower() in ("1", "true", "yes", "playing"):
                return True
        for key in ("status", "state", "play_status", "e_play_status", "playStatus"):
            value = container.get(key)
            if value is not None and not status_is_idle(value):
                return True
    return False


class OppoClient:
    """Live HTTP client for one OPPO. All calls raise OppoError on a transport failure."""

    def __init__(self, config: Any) -> None:
        self.cfg = config

    def _base(self) -> str:
        return "http://{}:{}".format(self.cfg.oppo_ip, int(self.cfg.oppo_http_port))

    def _get(self, endpoint: str, timeout: Optional[float] = None) -> str:
        url = self._base() + endpoint
        request_timeout = float(timeout if timeout is not None else self.cfg.socket_timeout)
        try:
            with urllib.request.urlopen(url, timeout=request_timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                status = getattr(response, "status", 200) or 200
                if status >= 400:
                    raise OppoError("OPPO HTTP {} for {}".format(status, url))
                return body
        except OppoError:
            raise
        except OSError as exc:
            raise OppoError("OPPO HTTP request failed for {}: {}".format(url, exc)) from exc

    def _get_json(self, endpoint: str, timeout: Optional[float] = None) -> dict:
        body = self._get(endpoint, timeout=timeout)
        try:
            parsed = json.loads(body)
            return parsed if isinstance(parsed, dict) else {"raw": body}
        except ValueError:
            return {"raw": body}

    def _port_open(self, port: int, timeout: float = 3.0) -> bool:
        try:
            conn = socket.create_connection((self.cfg.oppo_ip, int(port)), timeout=timeout)
            conn.close()
            return True
        except OSError:
            return False

    def send_oremote_notify(self) -> None:
        """The wake packet that starts the :436 app API."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.sendto(b"NOTIFY OREMOTE LOGIN", (self.cfg.oppo_ip, OREMOTE_PORT))
            finally:
                sock.close()
        except OSError:
            pass

    def wake_and_wait(self, attempts: int = 18, interval: float = 3.0) -> bool:
        """Send the OREMOTE notify until the :436 API answers. Returns True if it came up."""
        port = int(self.cfg.oppo_http_port)
        for _ in range(max(1, attempts)):
            self.send_oremote_notify()
            if self._port_open(port):
                return True
            time.sleep(interval)
        return self._port_open(port)

    def get_firmware_version(self) -> str:
        return self._get("/getmainfirmwareversion")

    def get_setup_menu(self) -> str:
        return self._get("/getsetupmenu")

    def signin(self, app_ip: str = "127.0.0.1") -> str:
        payload = urllib.parse.quote('{"appIconType":1,"appIpAddress":"%s"}' % app_ip)
        return self._get("/signin?" + payload, timeout=15)

    def get_device_list(self) -> dict:
        return self._get_json("/getdevicelist")

    def get_global_info(self) -> dict:
        return self._get_json("/getglobalinfo")

    def login_nfs(self, server: str) -> dict:
        return self._get_json("/loginNfsServer?" + urllib.parse.quote('{"serverName":"%s"}' % server))

    def get_nfs_share_list(self) -> str:
        return self._get("/getNfsShareFolderlist", timeout=12)

    def mount_nfs(self, server: str, folder: str) -> dict:
        endpoint = '/mountNfsSharedFolder?{"server":"%s","folder":"%s"}' % (
            server,
            urllib.parse.quote(folder),
        )
        return self._get_json(endpoint, timeout=MOUNT_TIMEOUT)

    def play_file(self, server: str, rel_path: str, index: str = "0", nfs: bool = True) -> dict:
        mount_path = "nfs1" if nfs else "cifs1"
        inner = (
            '"path":"/mnt/%s/%s","index":%s,"type":1,"appDeviceType":2,"extraNetPath":"%s","playMode":0'
            % (mount_path, rel_path, index, server)
        )
        endpoint = "/playnormalfile?{" + urllib.parse.quote(inner) + "}"
        return self._get_json(endpoint, timeout=PLAY_TIMEOUT)

    def stop(self) -> dict:
        """Send STOP (clears a stuck 'bd_is_playing' before loading a new disc)."""
        return self._get_json("/sendremotekey?" + urllib.parse.quote('{"key":"STP"}'))

    def play_bdmv(self, disc_folder_name: str, nfs: bool = True) -> dict:
        """Play a Blu-ray disc FOLDER (one containing BDMV). On this OPPO ``/checkfolderhasBDMV``
        doesn't just check -- it starts the disc. ``disc_folder_name`` is relative to the mount."""
        mount_path = "nfs1" if nfs else "cifs1"
        endpoint = '/checkfolderhasBDMV?{"folderpath":"/mnt/%s/%s"}' % (
            mount_path,
            urllib.parse.quote(disc_folder_name),
        )
        return self._get_json(endpoint, timeout=PLAY_TIMEOUT)

    def is_playing(self) -> bool:
        try:
            return info_is_playing(self.get_global_info())
        except OppoError:
            return False

    def send_tcp_command(self, command: str, timeout: float = 5.0) -> str:
        """Send an OPPO IP-control command on :23 (e.g. #PON / #POF) and return the reply."""
        try:
            conn = socket.create_connection((self.cfg.oppo_ip, 23), timeout=timeout)
        except OSError as exc:
            raise OppoError("OPPO :23 connect failed: {}".format(exc)) from exc
        try:
            conn.sendall((command.strip() + "\r").encode("ascii"))
            time.sleep(0.5)
            conn.settimeout(2.0)
            try:
                return conn.recv(128).decode("ascii", errors="replace")
            except OSError:
                return ""
        finally:
            conn.close()

    def power_cycle(self, delay: float = 5.0) -> None:
        """Standby then power on -- the power-ON fires CEC One-Touch-Play so the TV switches to the
        OPPO (it does NOT assert active source on a play-while-already-on). Verified on a TCL Q9L."""
        self.send_tcp_command("#POF")
        time.sleep(delay)
        self.send_tcp_command("#PON")

    def query_power(self) -> str:
        """OPPO power state over :23 -- '#QPW' replies '@OK ON' / '@OK OFF'."""
        return self.send_tcp_command("#QPW")

    def is_power_on(self) -> bool:
        """True if the OPPO reports it is powered on, so we can switch the TV without a power-cycle."""
        try:
            return "ON" in self.query_power().upper().split()
        except OppoError:
            return False
