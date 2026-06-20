"""Pure network logic for the CEC Switcher desktop app (no GUI, unit-testable off-box).

The PC is NOT on the HDMI/CEC bus. Instead of sending CEC itself, this triggers each device to take
CEC ownership ITSELF over the LAN -- the legitimate, spec-clean pattern (each device announces only
its OWN active source; nothing is spoofed):

  * OPPO  -- power-cycle over TCP :23 (#POF -> #PON) so the OPPO's own One-Touch-Play grabs the TV.
             The OPPO only asserts active source on a power-ON transition, so a power-cycle is the
             reliable way to force it (an already-on OPPO told to play does NOT switch).
  * Kodi  -- JSON-RPC Addons.ExecuteAddon -> script.cecreclaim -> CECActivateSource, i.e. Kodi
             re-asserts its own active source.

No CEC frames originate here.
"""
from __future__ import annotations

import base64
import json
import socket
import time
import urllib.request

OPPO_TCP_PORT = 23
KODI_PORT = 8080
KODI_RECLAIM_ADDON = "script.cecreclaim"


# --------------------------------------------------------------------------- OPPO (TCP :23 #XXX)
def _oppo_send(ip: str, command: str, port: int = OPPO_TCP_PORT, timeout: float = 4.0,
               read: bool = True) -> str:
    """Send one ``#XXX`` command (CR-terminated) to the OPPO control port; return the reply line."""
    with socket.create_connection((ip, port), timeout=timeout) as sock:
        sock.sendall((command + "\r").encode("ascii"))
        if not read:
            return ""
        sock.settimeout(timeout)
        try:
            data = sock.recv(64)
        except socket.timeout:
            return ""
        return data.decode("ascii", "replace").strip()


def oppo_query_power(ip: str, port: int = OPPO_TCP_PORT, timeout: float = 4.0) -> str:
    """Return ``'ON'`` / ``'OFF'`` / ``''`` from ``#QPW`` (reply ``@QPW OK ON`` / ``OFF``)."""
    up = _oppo_send(ip, "#QPW", port=port, timeout=timeout).upper()
    if "ON" in up:
        return "ON"
    if "OFF" in up:
        return "OFF"
    return ""


def oppo_take_tv(ip: str, port: int = OPPO_TCP_PORT, gap: float = 3.0, timeout: float = 4.0,
                 sleep=time.sleep) -> str:
    """Force the OPPO's own One-Touch-Play by power-cycling it (#POF -> wait -> #PON).

    If the OPPO is already off the ``#POF`` is a harmless no-op and ``#PON`` alone fires the OTP; if it
    is on, the cycle forces the power-ON transition it needs. Returns a short human status string.
    """
    _oppo_send(ip, "#POF", port=port, timeout=timeout, read=False)
    sleep(gap)
    _oppo_send(ip, "#PON", port=port, timeout=timeout, read=False)
    return "OPPO power-cycled (#POF -> #PON); the TV follows when its HDMI comes up (~20-24s)."


def ping_oppo(ip: str, port: int = OPPO_TCP_PORT, timeout: float = 4.0) -> bool:
    """True if the OPPO control port accepts a connection (we send #QPW and don't care about the reply)."""
    try:
        _oppo_send(ip, "#QPW", port=port, timeout=timeout)
        return True
    except OSError:
        return False


# --------------------------------------------------------------------------- Kodi (JSON-RPC :8080)
def _kodi_rpc(ip: str, method: str, params=None, port: int = KODI_PORT, user: str = "",
              password: str = "", timeout: float = 4.0):
    """POST a JSON-RPC call to ``http://ip:port/jsonrpc``; return its ``result`` (raises on error)."""
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(
        "http://{}:{}/jsonrpc".format(ip, port),
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    if user:
        token = base64.b64encode("{}:{}".format(user, password).encode()).decode()
        req.add_header("Authorization", "Basic " + token)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8", "replace"))
    if "error" in body:
        raise OSError("Kodi JSON-RPC error: {}".format(body["error"]))
    return body.get("result")


def kodi_ping(ip: str, port: int = KODI_PORT, user: str = "", password: str = "",
              timeout: float = 4.0):
    """``JSONRPC.Ping`` -> ``'pong'`` when Kodi's HTTP remote control is reachable."""
    return _kodi_rpc(ip, "JSONRPC.Ping", {}, port=port, user=user, password=password, timeout=timeout)


def kodi_take_tv(ip: str, port: int = KODI_PORT, user: str = "", password: str = "",
                 timeout: float = 4.0, addon: str = KODI_RECLAIM_ADDON):
    """Trigger the ``script.cecreclaim`` helper, which runs ``CECActivateSource`` (Kodi's own source)."""
    return _kodi_rpc(ip, "Addons.ExecuteAddon", {"addonid": addon},
                     port=port, user=user, password=password, timeout=timeout)
