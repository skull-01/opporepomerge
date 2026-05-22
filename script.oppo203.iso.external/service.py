import os
import sys
import threading
import time
import traceback

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


ADDON_ID = "script.oppo203.iso.external"
LOG_PREFIX = "[OPPO203][SERVICE]"

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


def log(message, level=None):
    if xbmc:
        lvl = level if level is not None else xbmc.LOGINFO
        xbmc.log(f"{LOG_PREFIX} {message}", lvl)
    else:
        print(f"{LOG_PREFIX} {message}", flush=True)


def _translate(path):
    if xbmcvfs:
        return xbmcvfs.translatePath(path)
    return path


def _addon_data_dir():
    if xbmcaddon:
        addon = xbmcaddon.Addon(ADDON_ID)
        return _translate(addon.getAddonInfo("profile"))
    return ""


def _read_settings():
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


def _settings_bool(settings, key, default=False):
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


def _is_disc_path(path):
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


def _should_intercept_4k_disc_source(path):
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


def _session_is_active(settings):
    path = os.path.join(settings.get("addon_data_dir", ""), "oppo203iso-active")
    return bool(path and os.path.exists(path))


def _run_interception(path, settings):
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

        from external_player import (
            clear_session_active,
            fast_return,
            fast_start,
            hold_playback,
            mark_session_active,
        )

        mark_session_active(settings)
        try:
            fast_start(settings, path)
            hold_playback(settings)
        finally:
            try:
                fast_return(settings)
            except Exception:
                pass
            clear_session_active(settings)

    except Exception as exc:
        log(f"Service interception error: {exc}")
        traceback.print_exc()


class InterceptionPlayer(xbmc.Player if xbmc else object):
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

    def __init__(self, settings):
        if xbmc:
            try:
                super().__init__()
            except Exception:
                pass
        self.settings = settings
        self._settings = settings  # back-compat
        self._handled_path = None
        self._active_thread = None
        self._omega = _is_omega_or_newer()

    # Test-required helper
    def _is_iso_or_bdmv(self, path):
        if not path:
            return False
        p = str(path).replace("\\", "/").lower()
        if p.endswith(".iso"):
            return True
        if "/bdmv/" in p or p.endswith("/bdmv") or "/bdmv/index.bdmv" in p:
            return True
        return False

    # Default handler — production path. Overridden in tests.
    def _handle_started(self):
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

    def onPlayBackStarted(self):
        # Pre-Omega Kodi (<21) used onPlayBackStarted; Omega+ uses onAVStarted
        if self._omega:
            return  # defer to onAVStarted on Omega
        try:
            self._handle_started()
        except Exception as exc:
            log(f"onPlayBackStarted swallowed exception: {exc}")

    def onAVStarted(self):
        try:
            self._handle_started()
        except Exception as exc:
            log(f"onAVStarted swallowed exception: {exc}")


class Monitor(xbmc.Monitor if xbmc else object):
    """Kodi service monitor.

    v2.2.0 Build 1 begins the v1.1.9 + v0.9.14 superset merge by
    restoring the v0.9.14 compatibility watcher: when the hardware model or
    jailbreak flag changes in Kodi settings, re-apply the safe compatibility
    preset and log warnings for support traces.
    """

    def __init__(self):
        try:
            super().__init__()
        except Exception:
            pass
        self._last_model = None
        self._last_jailbreak = None
        self._last_autoscript_shell = None
        try:
            settings = _read_settings()
            if settings is not None:
                self._last_model = settings.get("oppo_hardware_model", "UDP-203")
                self._last_jailbreak = _settings_bool(settings, "oppo_jailbreak_enabled", False)
                self._last_autoscript_shell = _settings_bool(
                    settings, "oppo_autoscript_shell_handler", False
                )
        except Exception:
            pass

    def onSettingsChanged(self):
        try:
            settings = _read_settings()
            if settings is None:
                return
            new_model = settings.get("oppo_hardware_model", "UDP-203")
            new_jailbreak = _settings_bool(settings, "oppo_jailbreak_enabled", False)
            new_autoscript_shell = _settings_bool(settings, "oppo_autoscript_shell_handler", False)
            if (
                new_model == self._last_model
                and new_jailbreak == self._last_jailbreak
                and new_autoscript_shell == self._last_autoscript_shell
            ):
                return
            try:
                from first_run_wizard import (
                    collect_compatibility_warnings,
                    log_compatibility_warnings,
                    reapply_preset_on_model_change,
                )
            except Exception as exc:
                log(f"v0.9.14 model-change watcher: import failed: {exc!r}")
                return
            applied, warnings = reapply_preset_on_model_change(
                settings,
                self._last_model,
                new_model,
                jailbreak=new_jailbreak,
                _log=log,
            )
            warnings = list(warnings)
            for warning in collect_compatibility_warnings(
                settings,
                model=new_model,
                jailbreak=new_jailbreak,
                uses_autoscript_shell=new_autoscript_shell,
            ):
                if warning not in warnings:
                    warnings.append(warning)
            log_compatibility_warnings(warnings, _log=log)
            saved = False
            if applied:
                try:
                    from settings_reader import save_settings

                    addon_data_dir = settings.get("addon_data_dir", "")
                    if addon_data_dir:
                        saved = bool(save_settings(addon_data_dir, settings))
                except Exception as exc:
                    log(f"v0.9.14 model-change watcher: save failed: {exc!r}")
            log(
                f"v0.9.14 model-change: {self._last_model} -> {new_model} "
                f"applied={len(applied)} warnings={len(warnings)} "
                f"autoscript_shell={new_autoscript_shell} saved={saved}"
            )
            self._last_model = new_model
            self._last_jailbreak = new_jailbreak
            self._last_autoscript_shell = new_autoscript_shell
        except Exception as exc:
            log(f"v0.9.14 model-change watcher exception: {exc!r}")


def _service_main():
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
def _kodi_major_version():
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


def _is_omega_or_newer():
    return _kodi_major_version() >= 21


def _safe_call(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except Exception:
        return None


def _kodi_startup_power_on(settings):
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
            from resources.lib import oppo_control

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


def _startup_wake_token(settings):
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


def _spawn_kodi_startup_power_on(settings):
    if not _settings_bool(settings, "kodi_startup_power_on", False):
        return None
    t = threading.Thread(target=_kodi_startup_power_on, args=(settings,), daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    _service_main()
