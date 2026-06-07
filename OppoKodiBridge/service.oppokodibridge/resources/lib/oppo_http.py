"""Pure-HTTP handoff to the OPPO/M9205 app API.

This mirrors the API the M9205 actually speaks, as implemented by the working
emby-chinoppo-bridge (`lib/oppo.py`):

  * `/signin?{"appIconType":1,"appIpAddress":"<app-ip>"}`
  * `/loginNfsServer?{"serverName":"<server>"}`
  * `/mountNfsSharedFolder?{"server":"<server>","folder":"<folder>"}` — mounts at `/mnt/nfs1`
  * `/playnormalfile?{...}` with `"path":"/mnt/nfs1/<relative>"` and the server in `"extraNetPath"`

The server is the OPPO's OWN NFS device (from `/getdevicelist`) — the address the OPPO can reach,
which on a dual-homed NAS is not the address Kodi uses. Playback is confirmed by polling
`/getglobalinfo` for `is_video_playing` (etc.). Community-reverse-engineered; not an official OPPO
protocol; verified live against one M9205 on 2026-06-07.
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, Tuple

# The NFS login/mount/play calls can be slow; quick calls use config.socket_timeout.
MOUNT_TIMEOUT = 20.0
PLAY_TIMEOUT = 15.0

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

# The M9205 /getglobalinfo reports playback via these booleans (confirmed on hardware), not a
# single status string: e.g. {"is_video_playing": true, "is_audio_playing": false, ...}.
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
    """Split a Kodi/network path into ``(server, folder, filename)`` like the bridge.

    ``nfs://192.168.1.177/mnt/Super3/Super3Share/A/B/file.mkv`` ->
    ``("192.168.1.177", "mnt/Super3/Super3Share/A/B", "file.mkv")``. The OPPO mounts ``folder`` at
    ``/mnt/nfs1`` and plays ``filename`` from there.
    """
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
        # OSError covers URLError, socket.timeout/TimeoutError, and connection errors — all must
        # become OppoError so the handoff treats them as non-fatal instead of crashing.
        except OSError as exc:
            raise OppoError("OPPO HTTP request failed for {}: {}".format(url, exc)) from exc

    def _get_json(self, endpoint: str, timeout: Optional[float] = None) -> dict:
        body = self._get(endpoint, timeout=timeout)
        try:
            parsed = json.loads(body)
            return parsed if isinstance(parsed, dict) else {"raw": body}
        except ValueError:
            return {"raw": body}

    def signin(self, app_ip: str = "127.0.0.1") -> str:
        payload = urllib.parse.quote('{"appIconType":1,"appIpAddress":"%s"}' % app_ip)
        return self._get("/signin?" + payload)

    def send_remote_key(self, key: str) -> str:
        return self._get("/sendremotekey?" + urllib.parse.quote('{"key":"%s"}' % key))

    def get_device_list(self) -> dict:
        return self._get_json("/getdevicelist")

    def get_global_info(self) -> dict:
        return self._get_json("/getglobalinfo")

    def login_nfs(self, server: str) -> dict:
        return self._get_json("/loginNfsServer?" + urllib.parse.quote('{"serverName":"%s"}' % server))

    def mount_nfs(self, server: str, folder: str) -> dict:
        endpoint = '/mountNfsSharedFolder?{"server":"%s","folder":"%s"}' % (
            server,
            urllib.parse.quote(folder),
        )
        return self._get_json(endpoint, timeout=MOUNT_TIMEOUT)

    def login_smb(self, server: str) -> dict:
        return self._get_json("/loginSambaWithOutID?" + urllib.parse.quote('{"serverName":"%s"}' % server))

    def mount_smb(self, server: str, folder: str, username: str = "", password: str = "") -> dict:
        endpoint = (
            '/mountSharedFolder?{"server":"%s","bWithID":0,"folder":"%s","userName":"%s","password":"%s","bRememberID":0}'
            % (server, urllib.parse.quote(folder), username, password)
        )
        return self._get_json(endpoint, timeout=MOUNT_TIMEOUT)

    def play_file(self, server: str, filename: str, index: str = "0", nfs: bool = True) -> dict:
        mount_path = "nfs1" if nfs else "cifs1"
        inner = (
            '"path":"/mnt/%s/%s","index":%s,"type":1,"appDeviceType":2,"extraNetPath":"%s","playMode":0'
            % (mount_path, filename, index, server)
        )
        endpoint = "/playnormalfile?{" + urllib.parse.quote(inner) + "}"
        return self._get_json(endpoint, timeout=PLAY_TIMEOUT)

    def is_playing(self) -> bool:
        try:
            return info_is_playing(self.get_global_info())
        except OppoError:
            return False
