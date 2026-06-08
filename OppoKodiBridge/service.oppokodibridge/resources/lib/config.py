"""Add-on configuration.

``Config`` is a plain dataclass with no Kodi dependency, so the pure-logic modules and
the test-suite can build one directly. ``from_addon()`` is the only Kodi-aware entry
point: it reads the live add-on settings.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    oppo_ip: str = ""
    oppo_http_port: int = 436
    oppo_http_broadcast: str = "255.255.255.255"
    socket_timeout: float = 4.0
    handoff_enabled: bool = True
    disc_iso_only: bool = True
    use_json_payload: bool = True
    media_type: int = 1
    app_device_type: int = 2
    path_from: str = ""
    path_to: str = ""
    cec_auto_enable: bool = True
    cec_reclaim_on_stop: bool = True
    grab_tv_on_play: bool = True
    fast_tv_switch: bool = True
    oppo_hdmi_phys: str = "1.0.0.0"
    poll_interval: float = 5.0
    idle_confirmations: int = 2

    @property
    def configured(self) -> bool:
        return bool(self.oppo_ip.strip())


def from_addon() -> "Config":
    import xbmcaddon

    addon = xbmcaddon.Addon()

    def s(key: str, default: str = "") -> str:
        try:
            return addon.getSettingString(key) or default
        except Exception:
            return default

    def b(key: str, default: bool) -> bool:
        try:
            return bool(addon.getSettingBool(key))
        except Exception:
            return default

    def i(key: str, default: int) -> int:
        try:
            return int(addon.getSettingInt(key))
        except Exception:
            return default

    return Config(
        oppo_ip=s("oppo_ip").strip(),
        oppo_http_port=i("oppo_http_port", 436),
        socket_timeout=float(i("socket_timeout", 4)),
        handoff_enabled=b("handoff_enabled", True),
        disc_iso_only=b("disc_iso_only", True),
        use_json_payload=b("use_json_payload", True),
        media_type=i("media_type", 1),
        app_device_type=i("app_device_type", 2),
        path_from=s("path_from").strip(),
        path_to=s("path_to").strip(),
        cec_auto_enable=b("cec_auto_enable", True),
        cec_reclaim_on_stop=b("cec_reclaim_on_stop", True),
        grab_tv_on_play=b("grab_tv_on_play", True),
        fast_tv_switch=b("fast_tv_switch", True),
        oppo_hdmi_phys=s("oppo_hdmi_phys") or "1.0.0.0",
        poll_interval=float(i("poll_interval", 5)),
    )
