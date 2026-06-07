"""Pure-HTTP handoff to the OPPO/M9205 app API.

A clean, minimal port of the v1 add-on's reverse-engineered HTTP layer, stripped to
exactly what the M9205 V1 needs: activate -> wake -> signin -> (mount NFS/SMB) -> play,
plus /getglobalinfo polling to know when playback ends.

The free functions carry no Kodi or network dependency and are unit-tested off-box.
``OppoClient`` wraps the live HTTP/UDP calls (stdlib only). The API is
community-reverse-engineered, not an official OPPO protocol, and is not hardware-validated.
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, Tuple

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


class OppoError(RuntimeError):
    pass


def parse_network_share(media_file: str) -> Optional[Tuple[str, str, str]]:
    """Return ``(scheme, server, share)`` for an ``smb://``/``nfs://`` URL, else None.

    ``share`` is the first path segment after the host, matching the player's mount call.
    """
    text = str(media_file).replace("\\", "/")
    for scheme in ("smb", "nfs"):
        prefix = scheme + "://"
        if text.lower().startswith(prefix):
            parts = text[len(prefix):].split("/", 2)
            if len(parts) >= 2 and parts[0] and parts[1]:
                return scheme, parts[0], parts[1]
    return None


def apply_path_rewrite(media_file: str, path_from: str, path_to: str) -> str:
    """Rewrite the Kodi-visible mount prefix to the OPPO-visible one, anchored at the start."""
    if path_from and media_file.startswith(path_from):
        return path_to + media_file[len(path_from):]
    return media_file


def translate_play_path(media_file: str, path_from: str, path_to: str) -> str:
    """Map a Kodi media path to the path the OPPO plays.

    Kodi hands network files to us percent-encoded (``nfs://host/a%20b``); the OPPO's player
    wants the literal path. So URL-decode network URLs first, then apply the prefix rewrite.
    Local paths are left byte-for-byte (no decode) so a literal ``%`` in a filename survives.
    """
    text = str(media_file)
    if text.lower().startswith(("nfs://", "smb://")):
        text = urllib.parse.unquote(text)
    return apply_path_rewrite(text, path_from, path_to)


def build_play_payload(path: str, media_type: int = 1, app_device_type: int = 2) -> dict:
    """The JSON body for ``/playnormalfile?payload=<urlencoded JSON>`` (M9205 json mode)."""
    return {
        "path": path,
        "index": 0,
        "type": int(media_type),
        "appDeviceType": int(app_device_type),
        "extraNetPath": "",
        "playMode": 0,
    }


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
        flag = container.get("is_playing")
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
    """Live HTTP/UDP client for one OPPO. All calls are best-effort; failures raise OppoError."""

    def __init__(self, config: Any) -> None:
        self.cfg = config

    def _base(self) -> str:
        return "http://{}:{}".format(self.cfg.oppo_ip, int(self.cfg.oppo_http_port))

    def _get(self, endpoint: str, query: Optional[str] = None, timeout: Optional[float] = None) -> str:
        url = self._base() + endpoint
        if query is not None:
            url += "?" + query
        request_timeout = float(timeout if timeout is not None else self.cfg.socket_timeout)
        try:
            with urllib.request.urlopen(url, timeout=request_timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                if getattr(response, "status", 200) and response.status >= 400:
                    raise OppoError("OPPO HTTP {} for {}: {}".format(response.status, url, body))
                return body
        except urllib.error.URLError as exc:
            raise OppoError("OPPO HTTP request failed for {}: {}".format(url, exc)) from exc

    def _get_json(self, endpoint: str, query: Optional[str] = None, timeout: Optional[float] = None) -> dict:
        body = self._get(endpoint, query=query, timeout=timeout)
        try:
            return json.loads(body)
        except ValueError:
            return {"raw": body}

    def activate(self) -> None:
        """Wake the app API: a UDP broadcast of six 0x55 bytes to the HTTP port."""
        host = self.cfg.oppo_http_broadcast
        port = int(self.cfg.oppo_http_port)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(b"\x55" * 6, (host, port))

    def wake(self) -> str:
        return self._get("/sendremotekey", query="key=PON")

    def signin(self) -> str:
        return self._get("/signin", query=urllib.parse.quote('{"user":"","password":""}', safe=""))

    def login_nfs(self, server: str) -> dict:
        return self._get_json("/login_nfs", query=urllib.parse.urlencode({"ip": server}))

    def mount_nfs(self, server: str, export: str) -> dict:
        query = urllib.parse.urlencode({"ip": server, "export": str(export).lstrip("/")})
        return self._get_json("/mount_nfs", query=query)

    def login_smb(self, server: str, user: str = "", password: str = "") -> dict:
        query = urllib.parse.urlencode({"ip": server, "user": user, "password": password})
        return self._get_json("/login_smb", query=query)

    def mount_smb(self, server: str, share: str, user: str = "", password: str = "") -> dict:
        query = urllib.parse.urlencode(
            {"ip": server, "share": str(share).lstrip("/"), "user": user, "password": password}
        )
        return self._get_json("/mount_smb", query=query)

    def ensure_share_mounted(self, media_file: str) -> None:
        parsed = parse_network_share(media_file)
        if parsed is None:
            return
        scheme, server, share = parsed
        if scheme == "nfs":
            self.login_nfs(server)
            self.mount_nfs(server, share)
        else:
            self.login_smb(server)
            self.mount_smb(server, share)

    def play(self, media_file: str) -> str:
        translated = translate_play_path(media_file, self.cfg.path_from, self.cfg.path_to)
        if self.cfg.use_json_payload:
            payload = build_play_payload(translated, self.cfg.media_type, self.cfg.app_device_type)
            encoded = urllib.parse.quote(json.dumps(payload, ensure_ascii=False), safe="")
            return self._get("/playnormalfile", query="payload=" + encoded, timeout=10)
        path_query = urllib.parse.quote(translated, safe="/:")
        return self._get("/playnormalfile", query="path=" + path_query, timeout=10)

    def get_global_info(self) -> dict:
        return self._get_json("/getglobalinfo")

    def is_playing(self) -> bool:
        try:
            return info_is_playing(self.get_global_info())
        except OppoError:
            return False
