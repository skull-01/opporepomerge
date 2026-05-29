"""Tiny i18n facade with safe fallback for tests/headless (v1.0.6)."""

try:
    import xbmcaddon
except ImportError:
    xbmcaddon = None

ADDON_ID = "script.oppo203.iso.external"

# English source-of-truth fallback (populate as new ids are added to strings.po)
_EN: dict[int, str] = {}


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
