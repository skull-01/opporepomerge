import json
import os

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

from .oppo_control import (
    get_audio_tracks,
    get_subtitle_tracks,
    send_commands,
    set_audio_track,
    set_play_time,
    set_subtitle_track,
)
from .settings_reader import DEFAULTS, Settings, read_settings
try:
    from .command_map import load_default_command_map
except ImportError:  # pragma: no cover - top-level test/import compatibility
    from command_map import load_default_command_map
try:
    from .diagnostic_logging import format_log_message, log_to_xbmc
except ImportError:  # pragma: no cover - top-level test/import compatibility
    from diagnostic_logging import format_log_message, log_to_xbmc


ADDON_ID = "script.oppo203.iso.external"
DEFAULT_COMMAND_MAP = load_default_command_map()


def _translate(path):
    if xbmcvfs:
        return xbmcvfs.translatePath(path)
    return path


def _notify(message):
    if xbmcgui:
        xbmcgui.Dialog().notification("Oppo UDP-203", message, "", 1500, False)


def _log(message):
    if xbmc:
        xbmc.log(format_log_message("remote", message), xbmc.LOGINFO)
    else:
        log_to_xbmc(None, "remote", message)


def _addon_data_dir():
    if xbmcaddon:
        addon = xbmcaddon.Addon(ADDON_ID)
        return _translate(addon.getAddonInfo("profile"))
    return ""


def _load_settings():
    addon_data = _addon_data_dir()
    settings = read_settings(addon_data) if addon_data else Settings({})
    settings.data["addon_data_dir"] = addon_data
    return settings


def _session_is_active(settings):
    path = os.path.join(settings.get("addon_data_dir", ""), "oppo203iso-active")
    return bool(path and os.path.exists(path))


def _command_map(settings):
    raw = settings.get("oppo_remote_command_map", DEFAULTS["oppo_remote_command_map"])
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = {}
    merged = dict(DEFAULT_COMMAND_MAP)
    merged.update({k: v for k, v in parsed.items() if isinstance(k, str) and isinstance(v, str)})
    return merged


def send_remote_key(key):
    settings = _load_settings()
    normalized_key = key.strip().lower()

    if settings.get_bool("remote_bridge_only_when_active", True) and not _session_is_active(settings):
        _log(f"Ignoring remote key {normalized_key}: Oppo ISO session is not active.")
        return

    command = _command_map(settings).get(normalized_key)

    if command:
        try:
            from .settings_reader import warn_if_unsupported
            warn = warn_if_unsupported(command, settings.get("oppo_hardware_model", "udp_203"))
            if warn:
                _log("[hardware-gate] " + warn)
        except Exception:
            pass

    if command and normalized_key in ("power_on", "power_toggle"):
        rewritten = resolve_power_on_token(command, settings.get("oppo_hardware_model", "udp_203"))
        if rewritten != command:
            _log(f"[wake-rewrite] {command} -> {rewritten} for model {settings.get('oppo_hardware_model', 'udp_203')}")
            command = rewritten

    if not command:
        _notify(f"No Oppo command for {normalized_key}")
        _log(f"No Oppo command configured for {normalized_key}")
        return

    # v0.9.0: Handle special command values
    if command == "__cycle_audio__":
        _cycle_audio(settings)
        return

    if command == "__cycle_subtitle__":
        _cycle_subtitle(settings)
        return

    if command == "__seek_beginning__":
        _seek_beginning(settings)
        return

    host = settings["oppo_ip"]
    port = int(settings.get("oppo_port", "23"))
    timeout = float(settings.get("oppo_socket_timeout", "3.0"))
    send_commands(host, port, [command], timeout=timeout, delay=0)
    _log(f"Forwarded Kodi remote key {normalized_key} to Oppo command {command}.")


# ---------------------------------------------------------------------------
# v0.9.0: Special command handlers
# ---------------------------------------------------------------------------

def _cycle_audio(settings):
    """Cycle to the next audio track via the Oppo HTTP API.

    Reads the current audio track list, finds the selected track, and selects
    the next one (wrapping around).  Falls back to the #AUD TCP command if the
    HTTP list is unavailable.
    """
    try:
        tracks = get_audio_tracks(settings)
        if not tracks:
            raise ValueError("No audio tracks returned")
        selected_idx = next(
            (i for i, t in enumerate(tracks) if t.get("selected")), 0
        )
        next_idx = (selected_idx + 1) % len(tracks)
        next_track = tracks[next_idx]
        set_audio_track(settings, next_track["index"])
        _log(f"Cycled audio to track {next_track['index']}: {next_track['name']}.")
        _notify(f"Audio: {next_track['name']}")
    except Exception as exc:
        _log(f"HTTP cycle_audio failed ({exc}); falling back to #AUD TCP command.")
        host = settings["oppo_ip"]
        port = int(settings.get("oppo_port", "23"))
        timeout = float(settings.get("oppo_socket_timeout", "3.0"))
        send_commands(host, port, ["#AUD"], timeout=timeout, delay=0)


def _cycle_subtitle(settings):
    """Cycle to the next subtitle track via the Oppo HTTP API.

    Reads the current subtitle track list, finds the selected track, and selects
    the next one (wrapping around).  Falls back to the #SUB TCP command if the
    HTTP list is unavailable.
    """
    try:
        tracks = get_subtitle_tracks(settings)
        if not tracks:
            raise ValueError("No subtitle tracks returned")
        selected_idx = next(
            (i for i, t in enumerate(tracks) if t.get("selected")), 0
        )
        next_idx = (selected_idx + 1) % len(tracks)
        next_track = tracks[next_idx]
        set_subtitle_track(settings, next_track["index"])
        _log(f"Cycled subtitle to track {next_track['index']}: {next_track['name']}.")
        _notify(f"Subtitle: {next_track['name']}")
    except Exception as exc:
        _log(f"HTTP cycle_subtitle failed ({exc}); falling back to #SUB TCP command.")
        host = settings["oppo_ip"]
        port = int(settings.get("oppo_port", "23"))
        timeout = float(settings.get("oppo_socket_timeout", "3.0"))
        send_commands(host, port, ["#SUB"], timeout=timeout, delay=0)


def _seek_beginning(settings):
    """Seek to the beginning of the current title via Oppo HTTP /setplaytime."""
    try:
        set_play_time(settings, 0, 0, 0)
        _log("Sought to beginning via HTTP setplaytime.")
        _notify("Seek: beginning")
    except Exception as exc:
        _log(f"seek_beginning failed: {exc}")


def resolve_power_on_token(token, hardware_model):
    """Rewrite OPPO power wake tokens for Chinoppo-style hardware.

    Stock OPPO UDP-203/205 keeps #PON/#POW. Chinoppo/M9702-style
    hardware uses #EJT as the wake action. Unknown hardware keeps the
    original token as a safe default.
    """
    if not isinstance(token, str):
        return token
    if token.strip().upper() not in ("#PON", "#POW"):
        return token
    try:
        from .settings_reader import hardware_profile
        profile = hardware_profile(hardware_model)
        wake = profile.get("wake_command")
        is_clone = bool(profile.get("is_clone"))
    except Exception:
        wake = None
        is_clone = False
    # Stock OPPO keeps the exact requested power command. Only Chinoppo-style
    # clones use #EJT as the safe wake action. This preserves #POW for stock
    # OPPO while still rewriting M9702/clone #PON and #POW to #EJT.
    return wake if is_clone and isinstance(wake, str) and wake else token
