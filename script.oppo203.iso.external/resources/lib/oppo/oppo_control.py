from __future__ import annotations

import json
import socket
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Iterator, Mapping
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:  # pragma: no cover
    from ..kodi.settings_reader import Settings


class OppoError(RuntimeError):
    pass


POWER_ON_COMMANDS = {"#PON", "PON", "POWERON", "POWER_ON"}
HTTP_IDLE_STATUSES = {"STOP", "STOPPED", "IDLE", "END", "ENDED", "NO_MEDIA", "NO MEDIA"}
# v0.9.0: Explicit play-status set for documentation and quick membership tests.
# e_play_status 0 = playing, 56 = also playing (e.g. loading/buffering during trick-play).
# Neither "0" nor "56" is in HTTP_IDLE_STATUSES -- they must NOT end the hold.
HTTP_PLAY_STATUSES = {
    "0",
    "PLAY",
    "PLAYING",
    "PAUSE",
    "PAUSED",
    "FFWD",
    "FREV",
    "SFWD",
    "SREV",
    "LOADING",
    "56",
}

# v0.8.0: TCP QPL responses that indicate idle/stopped playback (safe to end session).
# PLAY, PAUSE, FFWD, FREV, SFWD, SREV, and LOADING must NOT be in this set.
TCP_QPL_IDLE_STATUSES = {
    "STOP",
    "STOPPED",
    "IDLE",
    "NO DISC",
    "NODISC",
    "HOME",
    "MEDIA CENTER",
    "MEDIACENTER",
    "SCREEN SAVER",
    "SCREENSAVER",
    "DISC MENU",
    "DISCMENU",
    "",
}

# Oppo UDP discovery multicast address and port (v0.8.0)
OPPO_DISCOVERY_MCAST_ADDR = "239.255.255.251"
OPPO_DISCOVERY_PORT = 7624


def normalize_command(command: str) -> str:
    command = command.strip()
    if not command:
        return ""
    return command if command.endswith("\r") else command + "\r"


def send_commands(
    host: str,
    port: int | str,
    commands: Iterable[str],
    timeout: float = 3.0,
    delay: float = 1.0,
) -> list[str]:
    responses = []
    with socket.create_connection((host, int(port)), timeout=float(timeout)) as sock:
        sock.settimeout(float(timeout))
        for raw_command in commands:
            command = normalize_command(raw_command)
            if not command:
                continue
            sock.sendall(command.encode("ascii", errors="ignore"))
            try:
                responses.append(sock.recv(4096).decode("ascii", errors="replace").strip())
            except socket.timeout:
                responses.append("")
            time.sleep(float(delay))
    return responses


def query_command(host: str, port: int | str, command: str, timeout: float = 3.0) -> str:
    """Send a single query command and return the parsed value from the response.

    The Oppo UDP-20X protocol returns responses in two forms:
      Official: @CODE OK <value>   (e.g. "@QPW OK ON")
      Legacy:   OK <value>         (e.g. "OK ON")

    Returns the <value> string (uppercased, stripped), or "" on timeout.
    Raises OppoError if the response contains "ER" (error).
    """
    cmd = normalize_command(command)
    if not cmd:
        return ""
    with socket.create_connection((host, int(port)), timeout=float(timeout)) as sock:
        sock.settimeout(float(timeout))
        sock.sendall(cmd.encode("ascii", errors="ignore"))
        try:
            raw = sock.recv(4096).decode("ascii", errors="replace").strip()
        except socket.timeout:
            return ""

    return _parse_response(raw)


def _parse_response(raw: str) -> str:
    """Parse an Oppo response line into the value part."""
    if not raw:
        return ""
    upper = raw.strip().upper()

    # Official format: @CODE OK VALUE  (e.g. "@QPW OK ON")
    if upper.startswith("@"):
        parts = raw.strip().split(None, 3)
        # parts: ['@CODE', 'OK', 'VALUE ...'] or ['@CODE', 'ER', ...]
        if len(parts) >= 2:
            status = parts[1].upper()
            if status == "ER":
                raise OppoError(f"Oppo returned error response: {raw.strip()!r}")
            if status == "OK" and len(parts) >= 3:
                return " ".join(parts[2:]).strip().upper()
            if status == "OK":
                return ""
        return upper

    # Legacy format: OK VALUE  or  ER VALUE
    if upper.startswith("OK"):
        rest = raw.strip()[2:].strip()
        return rest.upper()
    if upper.startswith("ER"):
        raise OppoError(f"Oppo returned error response: {raw.strip()!r}")

    return upper


def query_power_status(host: str, port: int | str, timeout: float = 3.0) -> str:
    """Send #QPW and return 'ON', 'OFF', or '' (timeout)."""
    return query_command(host, port, "#QPW", timeout=timeout)


def query_playback_status(host: str, port: int | str, timeout: float = 3.0) -> str:
    """Send #QPL and return the playback status string such as 'PLAY', 'STOP', etc."""
    return query_command(host, port, "#QPL", timeout=timeout)


def query_input_source(host: str, port: int | str, timeout: float = 3.0) -> str:
    """Send #QIS and return the current input source string."""
    return query_command(host, port, "#QIS", timeout=timeout)


def tcp_qpl_is_idle(status: object) -> bool:
    """Return True if the QPL status indicates the player is idle/stopped."""
    return str(status).strip().upper() in TCP_QPL_IDLE_STATUSES


def setup_verbose_mode(host: str, port: int | str, mode: str | int, timeout: float = 3.0) -> str:
    """Send #SVM <mode> to enable verbose status messages.

    mode 0 = verbose off (default)
    mode 2 = verbose mode 2
    mode 3 = verbose mode 3
    """
    mode_int = int(mode)
    if mode_int not in (0, 2, 3):
        raise OppoError(f"Unsupported verbose mode: {mode_int} (valid: 0, 2, 3)")
    return query_command(host, port, f"#SVM {mode_int}", timeout=timeout)


def maybe_setup_verbose_mode(settings: Settings, host: str, port: int | str) -> None:
    """Apply verbose mode setting if non-zero."""
    mode = settings.get("oppo_verbose_mode", "0").strip()
    if mode in ("0", ""):
        return
    try:
        setup_verbose_mode(host, port, mode)
    except (OppoError, OSError):
        pass  # Non-critical; do not abort startup


# ---------------------------------------------------------------------------
# UDP discovery (v0.8.0)
# ---------------------------------------------------------------------------


def discover_oppo(
    timeout: float = 5.0,
    port: int = OPPO_DISCOVERY_PORT,
    mcast_addr: str = OPPO_DISCOVERY_MCAST_ADDR,
) -> list[dict[str, object]]:
    """Attempt to discover Oppo devices via multicast on 239.255.255.251:7624.

    Returns a list of dicts with keys: ip, port, name, raw.
    Each dict represents one responding device.
    """
    results: list[dict[str, object]] = []
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(float(timeout))
        # Join the multicast group
        mreq = struct.pack("4sL", socket.inet_aton(mcast_addr), socket.INADDR_ANY)
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except OSError:
            pass
        # Send a discovery probe (empty UDP datagram to multicast address)
        probe_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        probe_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        try:
            probe_sock.sendto(b"", (mcast_addr, port))
        except OSError:
            pass
        finally:
            probe_sock.close()

        deadline = time.time() + float(timeout)
        while time.time() < deadline:
            try:
                data, addr = sock.recvfrom(4096)
                raw = data.decode("utf-8", errors="replace").strip()
                name = raw or addr[0]
                results.append({"ip": addr[0], "port": addr[1], "name": name, "raw": raw})
            except socket.timeout:
                break
            except OSError:
                break
    except OSError:
        pass
    finally:
        try:
            if sock is not None:
                sock.close()
        except OSError:
            pass
    return results


# ---------------------------------------------------------------------------
# Preflight helpers (v0.8.0)
# ---------------------------------------------------------------------------


def run_preflight(settings: Settings) -> dict[str, object]:
    """Run optional preflight queries before starting playback.

    If oppo_preflight_enabled is true:
    - Query #QPW; if already ON, skip power-on commands.
    - Query #QIS for informational logging.

    Returns a dict with keys: power_status, input_source, already_on.
    """
    if not settings.get_bool("oppo_preflight_enabled", False):
        return {"power_status": None, "input_source": None, "already_on": False}

    host = settings["oppo_ip"]
    port = int(settings.get("oppo_port", "23"))
    timeout = float(settings.get("oppo_socket_timeout", "3.0"))

    power_status = None
    input_source = None
    already_on = False

    try:
        power_status = query_power_status(host, port, timeout=timeout)
        already_on = power_status == "ON"
    except (OppoError, OSError):
        pass

    try:
        input_source = query_input_source(host, port, timeout=timeout)
    except (OppoError, OSError):
        pass

    return {
        "power_status": power_status,
        "input_source": input_source,
        "already_on": already_on,
    }


# ---------------------------------------------------------------------------
# Existing helpers (unchanged from v0.7.0 except _http_play_json_payload)
# ---------------------------------------------------------------------------


def wake_on_lan(mac_address: str, broadcast: str = "255.255.255.255", port: int | str = 9) -> None:
    mac = mac_address.replace(":", "").replace("-", "").replace(".", "").strip()
    if len(mac) != 12:
        raise OppoError("Oppo MAC address must contain 12 hexadecimal characters.")
    try:
        mac_bytes = bytes.fromhex(mac)
    except ValueError as exc:
        raise OppoError("Oppo MAC address contains non-hexadecimal characters.") from exc

    packet = b"\xff" * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (broadcast, int(port)))


def maybe_wake_on_lan(settings: Settings) -> bool:
    if not settings.get_bool("oppo_use_wol", False):
        return False
    mac = settings.get("oppo_mac", "").strip()
    if not mac:
        raise OppoError("Wake-on-LAN is enabled but oppo_mac is empty.")
    wake_on_lan(mac, settings.get("oppo_wol_broadcast", "255.255.255.255"))
    return True


def _http_base(settings: Settings) -> str:
    return "http://{}:{}".format(settings["oppo_ip"], int(settings.get("oppo_http_port", "436")))


def _http_get(
    settings: Settings, endpoint: str, query: str | None = None, timeout: float | None = None
) -> str:
    url = _http_base(settings) + endpoint
    if query is not None:
        url += "?" + query
    request_timeout = float(
        timeout if timeout is not None else settings.get("oppo_socket_timeout", "3.0")
    )
    try:
        with urllib.request.urlopen(url, timeout=request_timeout) as response:
            body = cast("bytes", response.read()).decode("utf-8", errors="replace")
            if response.status >= 400:
                raise OppoError(f"Oppo HTTP API returned HTTP {response.status}: {body}")
            return body
    except urllib.error.URLError as exc:
        raise OppoError(f"Oppo HTTP API request failed for {url}: {exc}") from exc


def activate_http_api(settings: Settings) -> bool:
    if not settings.get_bool("oppo_http_activate", True):
        return False
    host = settings.get("oppo_http_broadcast", "255.255.255.255")
    port = int(settings.get("oppo_http_port", "436"))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(b"\x55" * 6, (host, port))
    return True


def signin_http_api(settings: Settings) -> str:
    query = urllib.parse.quote('{"user":"","password":""}', safe="")
    return _http_get(settings, "/signin", query=query)


def _translate_media_path(settings: Settings, media_file: str) -> str:
    translated = (
        _disc_folder_root(media_file)
        if settings.get_bool("oppo_http_disc_folder_root", True)
        else media_file
    )
    source = settings.get("oppo_http_path_from", "")
    target = settings.get("oppo_http_path_to", "")
    if source:
        translated = translated.replace(source, target, 1)
    if settings.get_bool("oppo_http_urlencode_path", True):
        return urllib.parse.quote(translated, safe="/:\\")
    return translated


def _disc_folder_root(media_file: str) -> str:
    normalized = media_file.replace("\\", "/")
    lowered = normalized.lower()
    markers = [
        "/bdmv/",
        "/certificate/",
        "/video_ts/",
        "/audio_ts/",
        "/mpegav/",
        "/vcd/",
        "/svcd/",
    ]
    for marker in markers:
        index = lowered.find(marker)
        if index >= 0:
            return normalized[:index]
    return media_file


def _build_json_payload(settings: Settings, media_file: str) -> dict[str, object]:
    """Build the JSON payload for Oppo HTTP /playnormalfile?payload=<urlencoded JSON>.

    Fields per v0.8.0 JSON payload spec:
      path            - translated media path (before URL encoding for the query value)
      index           - always 0
      type            - oppo_http_media_type setting (default 1 = video)
      appDeviceType   - oppo_http_app_device_type setting (default 2 = network)
      extraNetPath    - empty string
      playMode        - always 0
    """
    # Build the translated path without URL encoding (the whole payload gets encoded)
    translated = (
        _disc_folder_root(media_file)
        if settings.get_bool("oppo_http_disc_folder_root", True)
        else media_file
    )
    source = settings.get("oppo_http_path_from", "")
    target = settings.get("oppo_http_path_to", "")
    if source:
        translated = translated.replace(source, target, 1)

    app_device_type = int(settings.get("oppo_http_app_device_type", "2"))
    media_type = int(settings.get("oppo_http_media_type", "1"))

    payload = {
        "path": translated,
        "index": 0,
        "type": media_type,
        "appDeviceType": app_device_type,
        "extraNetPath": "",
        "playMode": 0,
    }
    return payload


def play_media_http_api(settings: Settings, media_file: str) -> str:
    payload_mode = settings.get("oppo_http_payload_mode", "raw_path")

    if payload_mode == "json_payload":
        payload_dict = _build_json_payload(settings, media_file)
        payload_json = json.dumps(payload_dict, ensure_ascii=False)
        encoded_payload = urllib.parse.quote(payload_json, safe="")
        return _http_get(
            settings, "/playnormalfile", query="payload=" + encoded_payload, timeout=10
        )

    # Default: raw_path (original behavior)
    path_query = _translate_media_path(settings, media_file)
    return _http_get(settings, "/playnormalfile", query=path_query, timeout=10)


def get_playback_info(settings: Settings) -> dict[str, Any]:
    body = _http_get(settings, "/getmovieplayinfo")
    try:
        return cast("dict[str, Any]", json.loads(body))
    except ValueError:
        return {"raw": body}


def get_playback_status(settings: Settings) -> str:
    """Return the best available playback status string from getmovieplayinfo.

    Checks top-level and nested 'result'/'playinfo' sub-dicts.  Returns the
    raw string (uppercased) of the first non-None status field found.
    Returns '' when no status field is present.
    """
    info = get_playback_info(settings)
    if not isinstance(info, dict):
        return ""
    for container in _info_containers(info):
        if not isinstance(container, dict):
            continue
        for key in ("e_play_status", "play_status", "status", "state"):
            val = container.get(key)
            if val is not None:
                return str(val).strip().upper()
    return ""


def http_status_is_idle(status: object) -> bool:
    """Return True only when status is a known idle/stopped value.

    v0.9.0: '0' and '56' are valid playing states (e_play_status from
    getmovieplayinfo) and must NOT be treated as idle.  An empty status
    is counted as idle to allow the confirmation counter to fire if the
    device becomes unreachable, but the definitive-stop check via
    http_info_is_definitive_stop() should take priority in callers.
    """
    s = str(status).strip().upper()
    if s in HTTP_PLAY_STATUSES:
        return False
    return s in HTTP_IDLE_STATUSES or s == ""


# ---------------------------------------------------------------------------
# v0.9.0: HTTP info helpers
# ---------------------------------------------------------------------------


def http_info_is_definitive_stop(info: object) -> bool:
    """Return True when the Oppo HTTP response signals an official, clean stop.

    The Oppo returns errcode1 == -5 when playback has ended cleanly.  This
    is distinct from a network error and should bypass the idle-confirmation
    counter to end the hold immediately.

    Inspects top-level dict and nested 'result'/'playinfo' sub-dicts so that
    all known Oppo API response shapes are covered.
    """
    if not isinstance(info, dict):
        return False
    for container in _info_containers(info):
        if isinstance(container, dict):
            errcode = container.get("errcode1")
            if errcode == -5 or str(errcode) == "-5":
                return True
    return False


def http_info_indicates_playing(info: object) -> bool:
    """Return True when the Oppo HTTP response indicates active/non-idle playback.

    Checks e_play_status (numeric 0 or 56 = playing), and play_status / status /
    state strings against HTTP_PLAY_STATUSES.  Inspects top-level dict and
    nested 'result'/'playinfo' sub-dicts.
    """
    if not isinstance(info, dict):
        return False
    for container in _info_containers(info):
        if not isinstance(container, dict):
            continue
        for key in ("e_play_status", "play_status", "status", "state"):
            val = container.get(key)
            if val is None:
                continue
            if str(val).strip().upper() in HTTP_PLAY_STATUSES:
                return True
            # Numeric 0 or 56 (int or str) = playing
            try:
                if int(val) in (0, 56):
                    return True
            except (TypeError, ValueError):
                pass
    return False


def _info_containers(info: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield the top-level info dict plus any nested result/playinfo sub-dicts."""
    yield info
    for nested_key in ("result", "playinfo"):
        nested = info.get(nested_key)
        if isinstance(nested, dict):
            yield nested


# ---------------------------------------------------------------------------
# Pure-HTTP/436 primitives (Xnoppo Elite V3 / emby-chinoppo-bridge model).
#
# Community-reverse-engineered endpoints on the OPPO HTTP API (port 436), adopted
# from the MIT-licensed Xnoppo Elite V3 / emby-chinoppo-bridge control model. These
# are function-only here: nothing in this module calls them yet -- the HTTP launch
# orchestration wires them in a later change. Every transport failure raises
# OppoError so the caller can degrade to a TCP/legacy fallback. The exact endpoint
# paths and query-param names are the Phase-C-validated surface; this is not an
# official OPPO protocol claim and the real-hardware behaviour is not verified in
# software.
# ---------------------------------------------------------------------------


def _http_get_json(
    settings: Settings, endpoint: str, query: str | None = None, timeout: float | None = None
) -> dict[str, Any]:
    """GET a JSON endpoint; return the decoded dict, or ``{"raw": body}`` when the
    body is not valid JSON. Network / HTTP>=400 failures raise OppoError via _http_get."""
    body = _http_get(settings, endpoint, query=query, timeout=timeout)
    try:
        return cast("dict[str, Any]", json.loads(body))
    except ValueError:
        return {"raw": body}


def send_remote_key_http(settings: Settings, key: str) -> str:
    """Send a single OPPO remote key over HTTP (``/sendremotekey?key=<code>``).

    Used to wake the player (``PON``) and drive simple navigation as part of the
    pure-HTTP launch. Returns the raw response body; raises OppoError on failure."""
    code = str(key).strip()
    if not code:
        raise OppoError("send_remote_key_http requires a non-empty key")
    return _http_get(settings, "/sendremotekey", query="key=" + urllib.parse.quote(code, safe=""))


def get_global_info(settings: Settings) -> dict[str, Any]:
    """Return the OPPO ``/getglobalinfo`` response as a dict (player-wide state)."""
    return _http_get_json(settings, "/getglobalinfo")


def global_info_is_playing(info: object) -> bool:
    """Return True when a ``/getglobalinfo`` payload indicates active playback.

    Honours an explicit ``is_playing`` flag (bool, or 1/"true"/"playing") in the
    top-level or nested result/playinfo dicts, then falls back to the shared
    movie-play-status heuristic so loading/trick-play states still count as playing."""
    if isinstance(info, dict):
        for container in _info_containers(info):
            flag = container.get("is_playing")
            if isinstance(flag, bool):
                if flag:
                    return True
            elif flag is not None and str(flag).strip().lower() in ("1", "true", "yes", "playing"):
                return True
    return http_info_indicates_playing(info)


def get_playing_time(settings: Settings) -> dict[str, Any]:
    """Return the OPPO ``/getplayingtime`` response as a dict (elapsed/total)."""
    return _http_get_json(settings, "/getplayingtime")


def get_device_list(settings: Settings) -> dict[str, Any]:
    """Return the OPPO ``/getdevicelist`` response (USB + network devices/shares)."""
    return _http_get_json(settings, "/getdevicelist")


def detect_nfs(settings: Settings) -> bool:
    """Best-effort: report whether the player advertises NFS mounting.

    Reads ``/getdevicelist`` and looks for an NFS-typed device entry or an ``nfs``
    capability flag. Returns False (never raises) when the device list cannot be
    read, so the caller can fall back to SMB."""
    try:
        info = get_device_list(settings)
    except OppoError:
        return False
    if not isinstance(info, dict):
        return False
    for container in _info_containers(info):
        if str(container.get("nfs", "")).strip().lower() in ("1", "true", "yes"):
            return True
        devices = container.get("devices") or container.get("devicelist")
        if isinstance(devices, list):
            for dev in devices:
                if isinstance(dev, dict) and "nfs" in str(dev.get("type", "")).lower():
                    return True
    return False


def login_smb(
    settings: Settings, server: str, user: str = "", password: str = ""
) -> dict[str, Any]:
    """Authenticate to an SMB server (``/login_smb``). Returns the response dict."""
    query = urllib.parse.urlencode({"ip": server, "user": user, "password": password})
    return _http_get_json(settings, "/login_smb", query=query)


def login_nfs(settings: Settings, server: str) -> dict[str, Any]:
    """Register an NFS server (``/login_nfs``). Returns the response dict."""
    query = urllib.parse.urlencode({"ip": server})
    return _http_get_json(settings, "/login_nfs", query=query)


def _share_names(info: object) -> list[str]:
    """Extract a flat list of share names from a ``*sharelist`` response dict."""
    names: list[str] = []
    if not isinstance(info, dict):
        return names
    for container in _info_containers(info):
        shares = container.get("shares") or container.get("sharelist") or container.get("list")
        if isinstance(shares, list):
            for item in shares:
                if isinstance(item, str):
                    names.append(item)
                elif isinstance(item, dict):
                    name = item.get("name") or item.get("share")
                    if isinstance(name, str):
                        names.append(name)
    return names


def list_smb_shares(
    settings: Settings, server: str, user: str = "", password: str = ""
) -> list[str]:
    """List SMB shares exported by ``server`` (``/getsmbsharelist``)."""
    query = urllib.parse.urlencode({"ip": server, "user": user, "password": password})
    return _share_names(_http_get_json(settings, "/getsmbsharelist", query=query))


def list_nfs_shares(settings: Settings, server: str) -> list[str]:
    """List NFS exports offered by ``server`` (``/getnfssharelist``)."""
    query = urllib.parse.urlencode({"ip": server})
    return _share_names(_http_get_json(settings, "/getnfssharelist", query=query))


def mount_smb(
    settings: Settings, server: str, share: str, user: str = "", password: str = ""
) -> dict[str, Any]:
    """Mount an SMB share (``/mount_smb``). The leading slash is stripped from the
    share path and no unmount is issued first (Xnoppo mounts idempotently)."""
    path = str(share).lstrip("/")
    query = urllib.parse.urlencode(
        {"ip": server, "share": path, "user": user, "password": password}
    )
    return _http_get_json(settings, "/mount_smb", query=query)


def mount_nfs(settings: Settings, server: str, export: str) -> dict[str, Any]:
    """Mount an NFS export (``/mount_nfs``). The leading slash is stripped and no
    unmount is issued first."""
    path = str(export).lstrip("/")
    query = urllib.parse.urlencode({"ip": server, "export": path})
    return _http_get_json(settings, "/mount_nfs", query=query)


def check_folder_has_bdmv(settings: Settings, folder: str) -> bool:
    """Ask the player whether ``folder`` contains a BDMV structure
    (``/checkfolderhasBDMV?path=...``); return the boolean verdict.

    Raises OppoError on a transport failure so the caller can fall back to a plain
    ``playnormalfile`` rather than silently mis-routing a disc."""
    query = "path=" + urllib.parse.quote(str(folder), safe="/:\\")
    info = _http_get_json(settings, "/checkfolderhasBDMV", query=query)
    if isinstance(info, dict):
        for container in _info_containers(info):
            for key in ("has_bdmv", "hasBDMV", "result", "bdmv"):
                val = container.get(key)
                if isinstance(val, bool):
                    return val
                if val is not None:
                    token = str(val).strip().lower()
                    if token in ("1", "true", "yes"):
                        return True
                    if token in ("0", "false", "no", ""):
                        return False
    return False


def _filter_commands_for_mode(
    settings: Settings,
    key: str,
    commands: list[str],
    preflight_result: dict[str, object] | None = None,
) -> list[str]:
    if key != "oppo_start_commands":
        return commands
    # Preflight already_on overrides oppo_already_on_mode
    already_on = False
    if preflight_result and preflight_result.get("already_on"):
        already_on = True
    elif settings.get_bool("oppo_already_on_mode", False):
        already_on = True

    if not already_on:
        return commands

    filtered = []
    for command in commands:
        normalized = command.strip().upper().rstrip("\r")
        if normalized in POWER_ON_COMMANDS:
            continue
        filtered.append(command)
    return filtered


def _resolve_hardware_wake_command(settings: Settings, command: str) -> str:
    """Apply v2 MVP send-time wake rewrite to configured start commands."""
    if not isinstance(command, str):
        return command
    if command.strip().upper() not in ("#PON", "#POW"):
        return command
    try:
        from settings_reader import hardware_profile

        profile = hardware_profile(settings.get("oppo_hardware_model", "udp_203"))
        wake = profile.get("wake_command")
        is_clone = bool(profile.get("is_clone"))
    except Exception:
        wake = None
        is_clone = False
    return wake if is_clone and isinstance(wake, str) and wake else command


def run_configured_commands(
    settings: Settings, key: str, preflight_result: dict[str, object] | None = None
) -> list[str]:
    host = settings["oppo_ip"]
    port = int(settings.get("oppo_port", "23"))
    timeout = float(settings.get("oppo_socket_timeout", "3.0"))
    delay = float(settings.get("oppo_command_delay", "0.1"))
    commands = _filter_commands_for_mode(settings, key, settings.get_lines(key), preflight_result)
    commands = [_resolve_hardware_wake_command(settings, command) for command in commands]
    if not commands:
        return []
    return send_commands(host, port, commands, timeout=timeout, delay=delay)


def run_start(
    settings: Settings, media_file: str, preflight_result: dict[str, object] | None = None
) -> str | None:
    maybe_wake_on_lan(settings)

    host = settings["oppo_ip"]
    port = int(settings.get("oppo_port", "23"))

    # Apply verbose mode if configured
    maybe_setup_verbose_mode(settings, host, port)

    mode = settings.get("oppo_start_mode", "tcp_commands")

    if mode in ("tcp_commands", "tcp_then_http"):
        run_configured_commands(settings, "oppo_start_commands", preflight_result=preflight_result)

    if mode in ("http_api", "tcp_then_http"):
        activate_http_api(settings)
        signin_http_api(settings)
        return play_media_http_api(settings, media_file)

    return None


# ---------------------------------------------------------------------------
# Read-only player-status probe (documented #Q.. query battery + HTTP playinfo)
# ---------------------------------------------------------------------------

# Ordered (label, command) pairs from the OPPO UDP-20X RS-232 & IP Control
# Protocol "Query Commands" section. #QFN (media file name) and #QFT (media file
# format) are the documented "what is playing" identity queries; the rest report
# play state, position, and disc/audio/subtitle context. Each reply is
# "@CODE OK <value>" (verbose), "OK <value>" (legacy), or "ER <reason>".
PROBE_QUERY_COMMANDS: tuple[tuple[str, str], ...] = (
    ("power", "#QPW"),
    ("playback_status", "#QPL"),
    ("media_file_name", "#QFN"),
    ("media_file_format", "#QFT"),
    ("track_title", "#QTK"),
    ("chapter", "#QCH"),
    ("track_elapsed", "#QTE"),
    ("track_remaining", "#QTR"),
    ("total_elapsed", "#QEL"),
    ("total_remaining", "#QRE"),
    ("disc_type", "#QDT"),
    ("audio_type", "#QAT"),
    ("subtitle_type", "#QST"),
    ("input_source", "#QIS"),
    ("hdmi_resolution", "#QHD"),
    ("firmware_version", "#QVR"),
)


def _classify_probe_response(command: str, raw: str) -> dict[str, object]:
    """Classify one query reply without raising on ER.

    Preserves the original case of the value, which matters for #QFN media file
    names (query_command/_parse_response would uppercase them). Handles both the
    verbose "@QFN OK <value>" form and the legacy "OK <value>" form.
    """
    text = (raw or "").strip()
    entry: dict[str, object] = {"command": command, "raw": text, "ok": False, "value": ""}
    if not text:
        entry["status"] = "no_response"
        return entry
    body = text
    if body.startswith("@"):
        parts = body.split(None, 1)
        body = parts[1].strip() if len(parts) > 1 else ""
    upper = body.upper()
    if upper.startswith("OK"):
        entry["ok"] = True
        entry["status"] = "ok"
        entry["value"] = body[2:].strip()
    elif upper.startswith("ER"):
        entry["status"] = "error"
        entry["value"] = body[2:].strip()
    else:
        entry["status"] = "unknown"
        entry["value"] = body
    return entry


def _default_http_probe(settings: Settings) -> str:
    """Best-effort raw /getmovieplayinfo body (undocumented HTTP app API)."""
    return _http_get(settings, "/getmovieplayinfo")


def probe_player_status(
    settings: Settings, *, send: Any = None, http: Any = None
) -> dict[str, object]:
    """Read-only diagnostic: query the documented OPPO status commands.

    Sends the PROBE_QUERY_COMMANDS battery over one TCP:23 connection and, on a
    best-effort basis, fetches the raw HTTP /getmovieplayinfo payload. Returns a
    structured, non-throwing result. `send` and `http` are injectable for tests.
    """
    send_fn = send or send_commands
    http_fn = http or _default_http_probe
    host = str(settings.get("oppo_ip", "")).strip()
    port = int(settings.get("oppo_port", "23") or "23")
    timeout = float(settings.get("oppo_socket_timeout", "3.0") or "3.0")
    result: dict[str, object] = {
        "host": host,
        "port": port,
        "ok": False,
        "error": None,
        "fields": {},
    }
    if not host:
        result["error"] = "oppo_ip is not set"
        return result
    commands = [command for _label, command in PROBE_QUERY_COMMANDS]
    try:
        raw_responses = send_fn(host, port, commands, timeout=timeout, delay=0)
    except OSError as exc:
        result["error"] = f"player unreachable over TCP: {exc}"
        return result
    fields: dict[str, object] = {}
    for index, (label, command) in enumerate(PROBE_QUERY_COMMANDS):
        raw = raw_responses[index] if index < len(raw_responses) else ""
        fields[label] = _classify_probe_response(command, raw)
    result["fields"] = fields
    result["ok"] = True
    try:
        result["http_getmovieplayinfo_raw"] = http_fn(settings)
    except Exception as exc:
        result["http_getmovieplayinfo_raw"] = f"<error: {exc}>"
    return result


def format_player_status_probe(result: Mapping[str, object]) -> str:
    """Render a probe result (from probe_player_status) as a readable report."""
    lines = [
        "OPPO player status probe",
        f"host: {result.get('host', '')}:{result.get('port', '')}",
    ]
    error = result.get("error")
    if error:
        lines.append(f"error: {error}")
        return "\n".join(lines) + "\n"
    fields = cast("Mapping[str, Mapping[str, object]]", result.get("fields") or {})
    width = max((len(label) for label in fields), default=0)
    for label, entry in fields.items():
        command = str(entry.get("command", ""))
        status = str(entry.get("status", ""))
        value = str(entry.get("value", ""))
        lines.append(f"  {label.ljust(width)}  {command:<5} {status:<11} {value}")
    http_raw = result.get("http_getmovieplayinfo_raw")
    if http_raw is not None:
        lines.append("")
        lines.append("HTTP /getmovieplayinfo (raw, undocumented app API):")
        lines.append(str(http_raw))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# v0.9.0: Audio/subtitle track HTTP helpers
# ---------------------------------------------------------------------------


def get_audio_tracks(settings: Settings) -> list[dict[str, object]]:
    """Return list of audio track dicts from Oppo HTTP /getaudiomenulist.

    Each entry has at minimum: index (int), name (str), selected (bool).
    Returns empty list on failure.
    """
    try:
        body = _http_get(settings, "/getaudiomenulist")
        data = json.loads(body)
        tracks = data.get("audio_list") or data.get("result") or []
        if isinstance(tracks, dict):
            tracks = list(tracks.values())
        return [_normalise_track(t) for t in tracks if isinstance(t, dict)]
    except (OppoError, ValueError, AttributeError):
        return []


def set_audio_track(settings: Settings, index: int | str) -> str:
    """Select audio track by index via Oppo HTTP /setaudiomenulist.

    index: zero-based integer matching the 'index' field from get_audio_tracks().
    """
    query = urllib.parse.urlencode({"cur_index": int(index)})
    return _http_get(settings, "/setaudiomenulist", query=query)


def get_subtitle_tracks(settings: Settings) -> list[dict[str, object]]:
    """Return list of subtitle track dicts from Oppo HTTP /getsubtitlemenulist.

    Each entry has at minimum: index (int), name (str), selected (bool).
    Returns empty list on failure.
    """
    try:
        body = _http_get(settings, "/getsubtitlemenulist")
        data = json.loads(body)
        tracks = data.get("subtitle_list") or data.get("result") or []
        if isinstance(tracks, dict):
            tracks = list(tracks.values())
        return [_normalise_track(t) for t in tracks if isinstance(t, dict)]
    except (OppoError, ValueError, AttributeError):
        return []


def set_subtitle_track(settings: Settings, index: int | str) -> str:
    """Select subtitle track by index via Oppo HTTP /setsubttmenulist.

    index: zero-based integer matching the 'index' field from get_subtitle_tracks().
    Note: the endpoint name on the Oppo uses 'subtt' (not 'subtitle').
    """
    query = urllib.parse.urlencode({"cur_index": int(index)})
    return _http_get(settings, "/setsubttmenulist", query=query)


def _normalise_track(t: dict[str, Any]) -> dict[str, object]:
    """Normalise a raw track dict from the Oppo API to a consistent shape."""
    return {
        "index": int(t.get("index", 0)),
        "name": str(t.get("name", "")),
        "selected": bool(t.get("selected", False)),
    }


# ---------------------------------------------------------------------------
# v0.9.0: Seek / setplaytime helper
# ---------------------------------------------------------------------------


def set_play_time(settings: Settings, h: int | str, m: int | str, s: int | str) -> str:
    """Seek to the given time position via Oppo HTTP /setplaytime.

    h, m, s: hours, minutes, seconds (integers).
    Note: this call succeeds only while the Oppo is actively playing.
    Use get_playback_status() to confirm play before calling.
    """
    query = urllib.parse.urlencode({"h": int(h), "m": int(m), "s": int(s)})
    return _http_get(settings, "/setplaytime", query=query)


# ---------------------------------------------------------------------------
# v0.9.0: Experimental / undocumented helpers (opt-in only)
# ---------------------------------------------------------------------------


def get_file_list_raw(settings: Settings, path: str = "/") -> str:
    """Call the undocumented /getfilelist endpoint and return the raw response body.

    WARNING: This endpoint is not officially documented and its response format
    varies across Oppo firmware versions.  It may contain binary-encoded data.
    This helper is intentionally NOT called during normal playback.

    Only call this helper when the setting 'oppo_experimental_filelist_enabled'
    is explicitly set to true, or from a diagnostic/development context.

    payload: JSON {"path": <path>, "fileType": 1, "mediaType": 3, "flag": 1}
    """
    payload = json.dumps({"path": str(path), "fileType": 1, "mediaType": 3, "flag": 1})
    query = urllib.parse.urlencode({"payload": payload})
    return _http_get(settings, "/getfilelist", query=query, timeout=10)


def parse_undocumented_file_list(
    raw: object, base_path: str | None = None
) -> list[dict[str, object]]:
    """Attempt to parse an undocumented Oppo /getfilelist response.

    EXPERIMENTAL: This parser handles both JSON (newer firmware) and the
    binary-delimited format seen in reference implementations (Xnoppo), where
    entries are separated by \x01/\x02 bytes and fields by \x00 bytes.

    The binary format is undocumented, fragile across firmware versions, and
    must not be used in production without thorough testing on your specific
    firmware.  This function is provided for diagnostic and research purposes
    only.

    Returns: list of entry dicts.  Every entry includes:
    - name: best-effort display name
    - path: best-effort full path when available or derivable from base_path
    - entry_type: "directory", "file", or "unknown"
    - is_dir / is_file: booleans derived from entry_type
    - size_bytes: integer size when an obvious size field exists, else None
    - extension: lowercase extension without dot, else ""
    - disc_type: best-effort disc/media classification, else ""
    - raw_fields / raw_entry: original decoded fields for diagnostics
    """
    import re as _re

    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="replace")
    else:
        text = str(raw)

    # First try JSON (newer / cleaner firmware response)
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            for key in ("filelist", "file_list", "result", "files"):
                candidates = data.get(key)
                if isinstance(candidates, list):
                    return [_normalise_filelist_entry(e, base_path=base_path) for e in candidates]
        if isinstance(data, list):
            return [_normalise_filelist_entry(e, base_path=base_path) for e in data]
    except ValueError:
        pass

    # Binary/delimiter fallback: split on \x01 or \x02 record separators,
    # then split each record on \x00 to get fields.
    # This format is from the Xnoppo reference; may differ on your firmware.
    if isinstance(raw, bytes):
        raw_bytes = raw
    else:
        raw_bytes = text.encode("utf-8", errors="replace")

    entries: list[dict[str, object]] = []
    chunks = _re.split(b"[\x01\x02]", raw_bytes)
    for chunk in chunks:
        if not chunk:
            continue
        fields = chunk.split(b"\x00")
        decoded_fields = [f.decode("utf-8", errors="replace").strip() for f in fields if f]
        entries.append(
            _normalise_filelist_entry(
                decoded_fields,
                base_path=base_path,
                raw_entry=chunk.decode("utf-8", errors="replace"),
            )
        )
    return [e for e in entries if e["name"]]


def _normalise_filelist_entry(
    entry: object, base_path: str | None = None, raw_entry: str | None = None
) -> dict[str, object]:
    """Return a structured diagnostic entry from JSON, list, or binary fields."""
    raw_fields = []
    source = entry

    if isinstance(entry, dict):
        raw_fields = [f"{k}={v}" for k, v in entry.items()]
        name = _first_non_empty(
            entry, "name", "fileName", "filename", "file_name", "title", "label"
        )
        path = _first_non_empty(entry, "path", "filePath", "filepath", "file_path", "url", "uri")
        type_hint = _first_non_empty(
            entry, "type", "fileType", "file_type", "entryType", "entry_type", "kind"
        )
        size = _first_int(
            entry, "size", "fileSize", "file_size", "length", "bytes", "sizeBytes", "size_bytes"
        )
        explicit_is_dir = _first_bool(
            entry, "isDir", "is_dir", "isFolder", "is_folder", "directory", "folder"
        )
    elif isinstance(entry, (list, tuple)):
        raw_fields = [str(x) for x in entry if str(x).strip()]
        name = _guess_name_from_fields(raw_fields)
        path = _guess_path_from_fields(raw_fields)
        type_hint = " ".join(raw_fields[1:]) if len(raw_fields) > 1 else ""
        size = _guess_size_from_fields(raw_fields[1:])
        explicit_is_dir = None
    else:
        raw_fields = [str(entry)]
        name = str(entry).strip()
        path = ""
        type_hint = ""
        size = None
        explicit_is_dir = None

    if not name and path:
        name = path.rstrip("/\\").split("/")[-1].split("\\")[-1]

    if not path:
        path = _join_base_path(base_path, name) if base_path and name else ""

    extension = _extension_for(name or path)
    entry_type = _infer_entry_type(
        name=name,
        path=path,
        extension=extension,
        type_hint=type_hint,
        explicit_is_dir=explicit_is_dir,
    )
    disc_type = _infer_disc_type(name=name, path=path, extension=extension, raw_fields=raw_fields)

    return {
        "name": name or "",
        "path": path or "",
        "entry_type": entry_type,
        "is_dir": entry_type == "directory",
        "is_file": entry_type == "file",
        "size_bytes": size,
        "extension": extension,
        "disc_type": disc_type,
        "raw_fields": raw_fields,
        "raw_entry": raw_entry if raw_entry is not None else str(source),
    }


def _first_non_empty(mapping: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def _first_int(mapping: Mapping[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = mapping.get(key)
        parsed = _safe_int(value)
        if parsed is not None:
            return parsed
    return None


def _first_bool(mapping: Mapping[str, Any], *keys: str) -> bool | None:
    for key in keys:
        if key not in mapping:
            continue
        value = mapping.get(key)
        if isinstance(value, bool):
            return value
        text_value = str(value).strip().lower()
        if text_value in ("1", "true", "yes", "y", "folder", "dir", "directory"):
            return True
        if text_value in ("0", "false", "no", "n", "file"):
            return False
    return None


def _safe_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _guess_name_from_fields(fields: Iterable[object]) -> str:
    for field in fields:
        text_field = str(field).strip()
        if not text_field:
            continue
        if "=" in text_field and text_field.split("=", 1)[0].lower() in (
            "size",
            "type",
            "flag",
            "index",
        ):
            continue
        return text_field.rstrip("/\\").split("/")[-1].split("\\")[-1] or text_field
    return ""


def _guess_path_from_fields(fields: Iterable[object]) -> str:
    for field in fields:
        text_field = str(field).strip()
        lowered = text_field.lower()
        if lowered.startswith(("/", "\\", "smb://", "nfs://", "http://", "https://")):
            return text_field
    return ""


def _guess_size_from_fields(fields: Iterable[object]) -> int | None:
    labelled_size = None
    numeric_candidates = []
    for field in fields:
        text_field = str(field).strip()
        if "=" in text_field:
            key, value = text_field.split("=", 1)
            if key.strip().lower() in ("size", "filesize", "file_size", "bytes", "length"):
                labelled_size = _safe_int(value)
                if labelled_size is not None:
                    return labelled_size
        parsed = _safe_int(text_field)
        if parsed is not None and parsed >= 0:
            numeric_candidates.append(parsed)
    return numeric_candidates[0] if numeric_candidates else None


def _join_base_path(base_path: object, name: str) -> str:
    base = str(base_path).rstrip("/\\")
    if not base:
        return name
    return base + "/" + str(name).lstrip("/\\")


def _extension_for(value: object) -> str:
    leaf = str(value or "").rstrip("/\\").split("/")[-1].split("\\")[-1]
    if "." not in leaf:
        return ""
    return leaf.rsplit(".", 1)[-1].lower()


def _infer_entry_type(
    name: str = "",
    path: str = "",
    extension: str = "",
    type_hint: str = "",
    explicit_is_dir: bool | None = None,
) -> str:
    if explicit_is_dir is True:
        return "directory"
    if explicit_is_dir is False:
        return "file"

    combined = " ".join(str(x or "") for x in (name, path, type_hint)).lower()
    if any(
        token in combined
        for token in ("directory", "folder", "<dir>", " dir ", "isdir=true", "isfolder=true")
    ):
        return "directory"
    if str(path).endswith(("/", "\\")) or str(name).endswith(("/", "\\")):
        return "directory"
    if extension:
        return "file"
    if any(token in combined for token in ("file", "isdir=false", "isfolder=false")):
        return "file"
    return "unknown"


def _infer_disc_type(
    name: str = "", path: str = "", extension: str = "", raw_fields: list[str] | None = None
) -> str:
    combined = " ".join(
        [str(name or ""), str(path or "")] + [str(f) for f in (raw_fields or [])]
    ).lower()
    ext = (extension or "").lower()
    if "uhbd" in combined or "uhd" in combined or "4k" in combined:
        return "uhd_bluray"
    if "bdmv" in combined or ext in ("bdmv", "mpls", "m2ts"):
        return "bluray"
    if "video_ts" in combined or ext in ("ifo", "vob"):
        return "dvd"
    if "mpegav" in combined or "svcd" in combined:
        return "svcd"
    if "vcd" in combined or ext in ("dat", "cue", "bin"):
        return "vcd"
    if ext == "iso":
        return "iso"
    return ""
