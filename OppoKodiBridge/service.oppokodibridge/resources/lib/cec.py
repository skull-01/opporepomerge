"""HDMI-CEC helpers (Kodi side).

v2 switches the TV by CEC, not by any TV-control backend:
  * the OPPO asserts itself as the active source when it starts playing (One Touch Play),
    so the TV switches to the OPPO with no command from us;
  * when playback ends, Kodi reclaims the TV with the CECActivateSource builtin.

This module is the Kodi side only. The TV's and the OPPO's CEC toggles are hardware
settings we cannot flip from software, so we show the user the one-time steps.

``input.enablecec`` is the best-effort lever for Kodi's own CEC adapter; the exact id is
build-dependent (Phase-C: confirm on the CoreELEC/Omega box). Every call degrades quietly.
"""
from __future__ import annotations

import json

from .kodilog import log

CEC_ENABLE_SETTING = "input.enablecec"


def _jsonrpc(method: str, params: object = None) -> dict:
    import xbmc

    request = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        request["params"] = params
    return json.loads(xbmc.executeJSONRPC(json.dumps(request)))


def reclaim_tv() -> bool:
    """Assert Kodi as the active CEC source so the TV switches its input back to Kodi."""
    try:
        import xbmc

        xbmc.executebuiltin("CECActivateSource")
        log("Reclaimed the TV (CECActivateSource).")
        return True
    except Exception as exc:  # pragma: no cover - exercised on hardware
        log("reclaim_tv failed: {!r}".format(exc))
        return False


def _phys_to_operand(phys_addr: str) -> str:
    """'1.0.0.0' -> '10:00' (the two CEC operand bytes for a physical address)."""
    parts = (str(phys_addr or "1.0.0.0").split(".") + ["0", "0", "0", "0"])[:4]
    try:
        nib = [int(p) & 0xF for p in parts]
    except ValueError:
        nib = [1, 0, 0, 0]
    return "%02X:%02X" % ((nib[0] << 4) | nib[1], (nib[2] << 4) | nib[3])


def switch_tv_to_oppo(phys_addr: str = "1.0.0.0") -> bool:
    """Switch the TV to the OPPO's HDMI input by broadcasting CEC <Active Source> for its physical
    address from the Kodi box -- instant, no OPPO power-cycle. Uses cec-client (Amlogic aocec)."""
    frame = "tx 4F:82:" + _phys_to_operand(phys_addr) + "\n"
    try:
        import subprocess

        subprocess.run(
            ["/usr/bin/cec-client", "-s", "-d", "1"],
            input=frame.encode("ascii"),
            timeout=15,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log("Routed the TV to the OPPO via CEC (Active Source {}).".format(phys_addr))
        return True
    except Exception as exc:  # pragma: no cover - exercised on hardware
        log("switch_tv_to_oppo failed: {!r}".format(exc))
        return False


def ensure_kodi_cec_enabled() -> bool:
    """Best-effort: turn Kodi's CEC adapter on if a settable flag exists. Never raises."""
    try:
        resp = _jsonrpc("Settings.GetSettingValue", {"setting": CEC_ENABLE_SETTING})
        if isinstance(resp, dict) and "result" in resp:
            value = resp["result"].get("value")
            if value is False:
                _jsonrpc("Settings.SetSettingValue", {"setting": CEC_ENABLE_SETTING, "value": True})
                log("Kodi CEC was off; enabled it.")
            else:
                log("Kodi CEC already enabled.")
            return True
        detail = resp.get("error") if isinstance(resp, dict) else resp
        log("Kodi CEC setting '{}' not readable ({}); leaving as-is.".format(CEC_ENABLE_SETTING, detail))
    except Exception as exc:
        log("ensure_kodi_cec_enabled best-effort failed: {!r}".format(exc))
    return False


def show_setup_guidance(force: bool = False) -> bool:
    """Show the one-time CEC setup steps for the TV and the OPPO. Returns True if shown."""
    try:
        import xbmcaddon
        import xbmcgui

        addon = xbmcaddon.Addon()
        if not force and addon.getSettingBool("cec_guidance_shown"):
            return False
        xbmcgui.Dialog().ok(
            "OppoKodiBridge - enable CEC",
            "For automatic input switching, turn CEC on once on both devices:\n\n"
            "[B]TCL Q9L Pro[/B]: Settings -> System -> CEC / T-Link -> On\n"
            "[B]OPPO / M9205[/B]: Setup -> HDMI -> CEC -> On\n\n"
            "Kodi's own CEC adapter is managed for you. When you play a file the OPPO grabs "
            "the TV; when it stops, Kodi takes the TV back.",
        )
        try:
            addon.setSettingBool("cec_guidance_shown", True)
        except Exception:
            pass
        return True
    except Exception as exc:  # pragma: no cover - exercised on hardware
        log("show_setup_guidance failed: {!r}".format(exc))
        return False
