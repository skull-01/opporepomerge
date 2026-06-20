from __future__ import annotations

import os
import sys
import threading
import time
import traceback
from typing import Any, Callable

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcvfs
except ImportError:
    xbmc = None
    xbmcaddon = None
    xbmcgui = None
    xbmcvfs = None

try:  # ENH-#43: install the legacy flat-name alias finder before bare imports below
    import resources.lib  # noqa: F401
except Exception:
    pass


ADDON_ID = "script.oppo203.iso.external"
LOG_PREFIX = "[OPPO203][SERVICE]"

# Setting keys the Windows configurator owns. Edits to these via Kodi's
# settings UI are warned about, not blocked. Operator-tunable knobs (timeouts,
# retries, bool toggles, playback timings, broadcast addresses, mode enums)
# are intentionally excluded — only protocol-level integration knobs the
# configurator wizard writes belong here.
CONFIGURATOR_MANAGED_KEYS = (
    "oppo_ip",
    "oppo_mac",
    "tv_ip",
    "avr_host",
    "oppo_port",
    "oppo_http_port",
    "tv_adb_port",
    "roku_ecp_port",
    "avr_port",
    "oppo_hardware_model",
    "tv_backend",
    "avr_backend",
    "selected_avr_preset_id",
    "tv_adb_preset",
    "adb_path",
    "oppo_input_adb_shell",
    "kodi_input_adb_shell",
    "lg_oppo_command",
    "lg_kodi_command",
    "samsung_oppo_command",
    "samsung_kodi_command",
    "custom_oppo_command",
    "custom_kodi_command",
    "roku_oppo_key",
    "roku_kodi_key",
    "sony_psk",
    "sony_oppo_hdmi_port",
    "sony_kodi_hdmi_port",
    "smartthings_token",
    "smartthings_device_id",
    "smartthings_oppo_input_id",
    "smartthings_kodi_input_id",
    "avr_player_input",
    "avr_restore_input",
    "avr_sound_mode",
    "sony_avr_psk",
    "sony_avr_api_path",
    "sony_avr_player_input_uri",
    "sony_avr_restore_input_uri",
    "oppo_start_commands",
    "oppo_stop_commands",
    "oppo_remote_command_map",
)

CONFIG_HINT_WINDOW_PROPERTY = "oppo203_config_hint_shown"
CONFIG_HINT_WINDOW_ID = 10000

# v0.8.0: Disc path markers used by service interception to detect disc files
DISC_PATH_MARKERS = [
    "/bdmv/",
    "/video_ts/",
    "/mpegav/",
    "/vcd/",
    "/svcd/",
    "/certificate/",
    "/audio_ts/",
]
DISC_EXTENSIONS = {".iso", ".bdmv", ".mpls", ".m2ts", ".ifo", ".vob", ".dat", ".cue", ".bin"}


def log(message: str, level: int | None = None) -> None:
    if xbmc:
        lvl = level if level is not None else xbmc.LOGINFO
        xbmc.log(f"{LOG_PREFIX} {message}", lvl)
    else:
        print(f"{LOG_PREFIX} {message}", flush=True)


def _translate(path: str) -> str:
    if xbmcvfs:
        translated: str = xbmcvfs.translatePath(path)
        return translated
    return path


def _addon_data_dir() -> str:
    if xbmcaddon:
        addon = xbmcaddon.Addon(ADDON_ID)
        return _translate(addon.getAddonInfo("profile"))
    return ""


def _read_settings() -> Any:
    try:
        addon_data = _addon_data_dir()
        lib_path = None
        if xbmcaddon:
            addon = xbmcaddon.Addon(ADDON_ID)
            if xbmcvfs:
                addon_path = xbmcvfs.translatePath(addon.getAddonInfo("path"))
                lib_path = os.path.join(addon_path, "resources", "lib")

        if lib_path and lib_path not in sys.path:
            sys.path.insert(0, lib_path)

        from settings_reader import Settings, read_settings

        if addon_data:
            settings = read_settings(addon_data)
            settings.data["addon_data_dir"] = addon_data
            return settings
        return Settings({})
    except Exception:
        return None


def _settings_bool(settings: Any, key: str, default: bool = False) -> bool:
    try:
        if hasattr(settings, "get_bool"):
            return bool(settings.get_bool(key, default))
        raw = settings.get(key, default)
    except Exception:
        raw = default
    if isinstance(raw, bool):
        return raw
    try:
        value = str(raw).strip().lower()
    except Exception:
        return bool(default)
    if value == "":
        return bool(default)
    return value in ("1", "true", "yes", "on")


def _is_disc_path(path: str) -> bool:
    """Return True if path looks like a disc image or folder entry."""
    if not path:
        return False
    normalized = path.replace("\\", "/").lower()
    _, ext = os.path.splitext(normalized)
    if ext in DISC_EXTENSIONS:
        return True
    for marker in DISC_PATH_MARKERS:
        if marker in normalized:
            return True
    return False


def _should_intercept_4k_disc_source(path: str) -> bool:
    """Use the v2.5.3 centralized 4K disc-style classifier.

    The import is intentionally dynamic because service.py may be imported by
    tests or Kodi before resources/lib has been placed on sys.path.
    """
    try:
        from intercept import should_intercept_4k_disc_source
    except Exception:
        try:
            from resources.lib.intercept import should_intercept_4k_disc_source
        except Exception as exc:
            log(f"Service interception: 4K classifier unavailable: {exc}")
            return False
    return bool(should_intercept_4k_disc_source(path))


def _session_is_active(settings: Any) -> bool:
    try:
        from resources.lib.kodi.settings_reader import session_is_active
    except ImportError:  # pragma: no cover - bare-name fallback for sys.path importers
        from settings_reader import session_is_active  # type: ignore[no-redef]
    return session_is_active(settings.get("addon_data_dir", ""))


def _run_interception(path: str, settings: Any) -> None:
    """Stop Kodi playback quickly and launch the Oppo/TV flow in background."""
    try:
        # Stop Kodi playback first
        if xbmc:
            player = xbmc.Player()
            if player.isPlaying():
                player.stop()

        log(f"Service interception: tagged 4K disc-style path detected: {path}")

        # Dynamic import so the service does not crash in envs without these modules
        lib_path = settings.get("_lib_path", "")
        if lib_path and lib_path not in sys.path:
            sys.path.insert(0, lib_path)

        from playback_session import run_playback_session

        run_playback_session(settings, path, launch_source="service_interception")

    except Exception as exc:
        log(f"Service interception error: {exc}")
        traceback.print_exc()


class InterceptionPlayer(xbmc.Player if xbmc else object):  # type: ignore[misc]
    """xbmc.Player subclass for service interception mode.

    Test contract (test_all.TOmega):
      attributes: settings, _handled_path, _omega
      method:     _is_iso_or_bdmv(path) -> bool
      method:     onPlayBackStarted() -> defers on Omega, calls _handle_started pre-Omega
      method:     onAVStarted()       -> always calls _handle_started
      method:     _handle_started()   -> override-point; default = run interception thread
      callback exceptions must be swallowed (never propagate to Kodi binding)
    """

    _ISO_EXTS = (".iso",)
    _BDMV_MARKERS = ("/bdmv/", "bdmv\\", "/bdmv\\")  # marker tolerant
    _BDMV_FILE = "index.bdmv"

    def __init__(self, settings: Any) -> None:
        if xbmc:
            try:
                super().__init__()
            except Exception:
                pass
        self.settings = settings
        self._settings = settings  # back-compat
        self._handled_path: str | None = None
        self._active_thread: threading.Thread | None = None
        self._omega = _is_omega_or_newer()

    # Test-required helper
    def _is_iso_or_bdmv(self, path: str) -> bool:
        if not path:
            return False
        p = str(path).replace("\\", "/").lower()
        if p.endswith(".iso"):
            return True
        if "/bdmv/" in p or p.endswith("/bdmv") or "/bdmv/index.bdmv" in p:
            return True
        return False

    # Default handler — production path. Overridden in tests.
    def _handle_started(self) -> None:
        try:
            path = ""
            if xbmc:
                try:
                    path = xbmc.Player().getPlayingFile()
                except Exception:
                    pass
            if not _should_intercept_4k_disc_source(path):
                log(
                    f"Service interception: using Kodi default player; not a tagged 4K disc-style source: {path!r}"
                )
                return
            if _session_is_active(self.settings):
                log("Service interception: session already active, skipping.")
                return
            log(f"Service interception: intercepting tagged 4K disc-style playback: {path!r}")
            thread = threading.Thread(
                target=_run_interception,
                args=(path, self.settings),
                daemon=True,
            )
            self._active_thread = thread
            thread.start()
        except Exception as exc:
            log(f"Service interception _handle_started error: {exc}")

    def onPlayBackStarted(self) -> None:
        # Pre-Omega Kodi (<21) used onPlayBackStarted; Omega+ uses onAVStarted
        if self._omega:
            return  # defer to onAVStarted on Omega
        try:
            self._handle_started()
        except Exception as exc:
            log(f"onPlayBackStarted swallowed exception: {exc}")

    def onAVStarted(self) -> None:
        try:
            self._handle_started()
        except Exception as exc:
            log(f"onAVStarted swallowed exception: {exc}")


def _snapshot_managed_settings() -> dict[str, Any]:
    """Return {key: value} for every CONFIGURATOR_MANAGED_KEYS entry.

    Used at service start to capture the configurator-written baseline so
    later `onSettingsChanged` callbacks can detect overwrites via Kodi's UI.
    Safe in headless tests: returns {} when xbmcaddon is unavailable.
    """
    snapshot: dict[str, Any] = {}
    if not xbmcaddon:
        return snapshot
    try:
        addon = xbmcaddon.Addon(ADDON_ID)
    except Exception:
        return snapshot
    for key in CONFIGURATOR_MANAGED_KEYS:
        try:
            snapshot[key] = addon.getSetting(key)
        except Exception:
            snapshot[key] = ""
    return snapshot


def _changed_managed_keys(baseline: dict[str, Any]) -> list[str]:
    """Return CONFIGURATOR_MANAGED_KEYS whose current value differs from baseline."""
    if not xbmcaddon:
        return []
    try:
        addon = xbmcaddon.Addon(ADDON_ID)
    except Exception:
        return []
    changed: list[str] = []
    for key in CONFIGURATOR_MANAGED_KEYS:
        try:
            current = addon.getSetting(key)
        except Exception:
            continue
        if current != baseline.get(key, ""):
            changed.append(key)
    return changed


def _resolve_localized(string_id: int, default: str) -> str:
    """Resolve a localized string via resources.lib.i18n with a hard fallback."""
    try:
        from i18n import L
    except Exception:
        try:
            from resources.lib.i18n import L
        except Exception:
            return default
    try:
        resolved: str = L(string_id, default)
        return resolved
    except Exception:
        return default


def _notify_config_hint_once_per_session() -> bool:
    """Show the Part B 'use the configurator' hint at most once per Kodi session.

    First call sets a window property on the home window (id 10000); subsequent
    calls in the same Kodi process see the property and skip. The property
    clears on Kodi restart by design. Returns True iff the notification fired.
    """
    if not xbmcgui:
        return False
    try:
        window = xbmcgui.Window(CONFIG_HINT_WINDOW_ID)
        if window.getProperty(CONFIG_HINT_WINDOW_PROPERTY) == "1":
            return False
        window.setProperty(CONFIG_HINT_WINDOW_PROPERTY, "1")
    except Exception:
        return False
    title = _resolve_localized(30293, "OPPO 203 ISO External")
    body = _resolve_localized(
        30291,
        "Most settings are managed by the configurator. Changes here may be overwritten.",
    )
    try:
        xbmcgui.Dialog().notification(title, body, time=8000)
    except Exception:
        return False
    log("Configurator hint: shown once per session on first settings change.")
    return True


def _warn_overwritten_managed_keys(changed_keys: list[str]) -> None:
    """Log + notify a Part C warning for each configurator-managed key that changed."""
    if not changed_keys:
        return
    title = _resolve_localized(30293, "OPPO 203 ISO External")
    template = _resolve_localized(
        30292,
        "Setting '{key}' is managed by the configurator. Re-run the configurator to make this change permanent.",
    )
    warn_level = xbmc.LOGWARNING if xbmc else None
    for key in changed_keys:
        msg = template.replace("{key}", key)
        log(f"Configurator-managed key '{key}' was overwritten via Kodi UI.", warn_level)
        if not xbmcgui:
            continue
        try:
            xbmcgui.Dialog().notification(title, msg, time=6000)
        except Exception:
            pass


class Monitor(xbmc.Monitor if xbmc else object):  # type: ignore[misc]
    """Kodi service monitor.

    Lifecycle (abortRequested/waitForAbort inherited) plus a passive
    `onSettingsChanged` hook that (a) shows a once-per-session generic
    configurator-hint notification, and (b) warns per key when an entry in
    `CONFIGURATOR_MANAGED_KEYS` was overwritten via Kodi's settings UI. The
    hook is logging/notification-only — it never mutates add-on state.
    """

    def __init__(self) -> None:
        if xbmc:
            try:
                super().__init__()
            except Exception:
                pass
        self._managed_baseline = _snapshot_managed_settings()

    def onSettingsChanged(self) -> None:
        try:
            _notify_config_hint_once_per_session()
            changed = _changed_managed_keys(self._managed_baseline)
            if changed:
                _warn_overwritten_managed_keys(changed)
                self._managed_baseline = _snapshot_managed_settings()
        except Exception as exc:
            log(f"onSettingsChanged swallowed exception: {exc}")


def _service_main() -> None:
    log("Service started (v2.5.2 Build 1).")
    settings = _read_settings()
    if settings:
        _spawn_kodi_startup_power_on(settings)
    architecture = "external_player"
    if settings:
        architecture = settings.get("playback_architecture", "external_player")

    log(f"Playback architecture: {architecture}")

    monitor = Monitor()

    if architecture == "service_interception" and xbmc and settings:
        # Resolve lib path once
        try:
            if xbmcaddon:
                addon = xbmcaddon.Addon(ADDON_ID)
                if xbmcvfs:
                    addon_path = xbmcvfs.translatePath(addon.getAddonInfo("path"))
                    settings.data["_lib_path"] = os.path.join(addon_path, "resources", "lib")
        except Exception:
            pass

        # Keep a live reference: Kodi garbage-collects xbmc.Player subclasses that
        # are not held, which would silently stop playback callbacks.
        player = InterceptionPlayer(settings)  # noqa: F841
        log("Service interception player active.")
        while not monitor.abortRequested():
            if monitor.waitForAbort(60):
                break
            time.sleep(0.1)
    else:
        # External player mode: lightweight heartbeat only
        while not monitor.abortRequested():
            if monitor.waitForAbort(60):
                break
            time.sleep(0.1)

    log("Service stopped.")


# === v1.1.9 helpers (added to satisfy test_all.py TPower + TOmega) ===
def _kodi_major_version() -> int:
    try:
        if xbmc is None:
            return 0
        label = xbmc.getInfoLabel("System.BuildVersion")
        if not label:
            return 0
        s = str(label).strip()
        digits = ""
        for ch in s:
            if ch.isdigit():
                digits += ch
            else:
                break
        return int(digits) if digits else 0
    except Exception:
        return 0


def _is_omega_or_newer() -> bool:
    return _kodi_major_version() >= 21


def _safe_call(fn: Callable[..., Any], *a: Any, **kw: Any) -> Any:
    try:
        return fn(*a, **kw)
    except Exception:
        return None


def _kodi_startup_power_on(settings: Any) -> None:
    """Wake the configured OPPO-compatible player on Kodi startup when needed.

    Build 8 / v2.5.1 behavior preserved for v2.5.2: query #QPW before
    wake, skip when already ON, use #PON for stock/safe fallback models, and
    use #EJT for Chinoppo/M9702/IPUK/GIEC/Magnetar-style clone models.  This
    function intentionally never imports or calls a missing legacy token helper.
    """
    try:
        if not _settings_bool(settings, "kodi_startup_power_on", False):
            return
        host = str(settings.get("oppo_ip", "")).strip()
        if not host:
            log("Kodi-startup power-on: oppo_ip is empty; skipping wake.")
            return
        try:
            port = settings.get_int("oppo_port", 23, minimum=1, maximum=65535)
        except Exception:
            port = 23
        try:
            timeout = settings.get_float("oppo_socket_timeout", 3.0, minimum=0.1, maximum=60.0)
        except Exception:
            timeout = 3.0
        try:
            retries = settings.get_int("kodi_startup_power_on_retries", 3, minimum=1, maximum=10)
        except Exception:
            retries = 3
        try:
            delay = settings.get_float(
                "kodi_startup_power_on_delay", 5.0, minimum=0.0, maximum=120.0
            )
        except Exception:
            delay = 5.0

        try:
            import oppo_control
        except Exception:
            from resources.lib import oppo_control  # type: ignore[attr-defined]

        try:
            status = oppo_control.query_power_status(host, port, timeout=timeout)
        except Exception as exc:
            log(f"Kodi-startup power-on: #QPW query failed: {exc}")
            status = ""
        normalized = str(status or "").strip().upper()
        if normalized == "ON":
            log("Kodi-startup power-on: player already ON; wake skipped.")
            return

        if _settings_bool(settings, "kodi_startup_power_on_use_wol", True):
            mac = str(settings.get("oppo_mac", "")).strip()
            if mac:
                try:
                    oppo_control.wake_on_lan(
                        mac, settings.get("oppo_wol_broadcast", "255.255.255.255")
                    )
                    log("Kodi-startup power-on: Wake-on-LAN packet sent.")
                except Exception as exc:
                    log(f"Kodi-startup power-on: Wake-on-LAN failed: {exc}")

        token = _startup_wake_token(settings)
        log(f"Kodi-startup power-on: sending {token} after status={normalized or 'UNKNOWN'}")
        for attempt in range(max(1, int(retries))):
            try:
                oppo_control.send_commands(host, port, [token], timeout=timeout, delay=0)
                return
            except Exception as exc:
                if attempt >= retries - 1:
                    log(f"Kodi-startup power-on: wake failed after {retries} attempt(s): {exc}")
                    return
                time.sleep(float(delay))
    except Exception as exc:
        log(f"_kodi_startup_power_on error: {exc}")


def _startup_wake_token(settings: Any) -> str:
    model = str(settings.get("oppo_hardware_model", "udp_203") or "").lower()
    clone_markers = (
        "chinoppo",
        "m9702",
        "m9201",
        "m9203",
        "m9205c",
        "ipuk",
        "giec",
        "magnetar",
    )
    return "#EJT" if any(marker in model for marker in clone_markers) else "#PON"


def _spawn_kodi_startup_power_on(settings: Any) -> threading.Thread | None:
    if not _settings_bool(settings, "kodi_startup_power_on", False):
        return None
    t = threading.Thread(target=_kodi_startup_power_on, args=(settings,), daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    _service_main()
