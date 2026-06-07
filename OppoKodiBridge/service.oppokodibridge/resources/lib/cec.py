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
