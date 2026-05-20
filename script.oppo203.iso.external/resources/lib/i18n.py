"""Tiny i18n facade with safe fallback for tests/headless (v1.0.6)."""
try:
    import xbmcaddon
except ImportError:
    xbmcaddon = None

ADDON_ID = "script.oppo203.iso.external"

# English source-of-truth fallback (mirrors msgctxt #31xxx in strings.po)
_EN = {
    31000: "Welcome",
    31001: "Configuration mode",
    31002: "Basic - just the essentials",
    31003: "Full - configure every option",
    31010: "Prerequisites",
    31011: "Oppo IP",
    31012: "Oppo port",
    31013: "Reachable",
    31014: "Unreachable",
    31020: "Hardware",
    31021: "Chinoppo preset",
    31022: "Apply Chinoppo #EJT/#PLA preset?",
    31030: "Kodi startup auto-power",
    31031: "Do you want Kodi to automatically power on the OPPO/compatible player when Kodi starts? Choose No if you prefer to keep the player off until playback starts or you power it on manually.",
    31032: "Delay (seconds)",
    31033: "Retries",
    31034: "Wake-on-LAN first?",
    31040: "Architecture auto-test",
    31041: "Run quick auto-test now?",
    31042: "Apply recommendation now?",
    31043: "Architecture set",
    31050: "Wizard complete",
    31051: "Wizard reset",
    31060: "AutoScript generated",
    31061: "AutoScript failed",
}


def L(string_id, default=None):
    """Return localized string, falling back to English source.

    Always safe to call: never raises, never returns None.
    """
    try:
        sid = int(string_id)
    except (TypeError, ValueError, OverflowError):
        return str(default if default is not None else string_id)
    if xbmcaddon is not None:
        try:
            s = xbmcaddon.Addon(ADDON_ID).getLocalizedString(sid)
            if s:
                return s
        except Exception:
            pass
    return _EN.get(sid, default if default is not None else "")


def supported_languages():
    """Return the list of bundled language folders."""
    return [
        "resource.language.en_gb",
        "resource.language.de_de",
        "resource.language.fr_fr",
        "resource.language.es_es",
        "resource.language.it_it",
        "resource.language.nl_nl",
        "resource.language.zh_cn",
    ]
