"""Tiny i18n facade with safe fallback for tests/headless (v1.0.6).

`L()` resolves a localized string. By default ("follow Kodi system language")
it delegates to Kodi, which renders the add-on's strings in Kodi's GUI
language. When the user pins a specific bundled locale via the in-add-on
language menu (the ``addon_language`` setting), `L()` instead reads that
locale's ``strings.po`` so the choice is applied to add-on-routed strings.

Bundled non-en_gb strings are presently English placeholders, so pinning a
locale changes the source file consulted but not yet the visible text until
translations are populated. The mechanism is in place for when they are.
"""

from __future__ import annotations

import os

try:
    import xbmcaddon
except ImportError:
    xbmcaddon = None

try:
    import xbmc
except ImportError:
    xbmc = None

ADDON_ID = "script.oppo203.iso.external"

# In-add-on language preference: the addon_language setting holds either the
# FOLLOW_KODI sentinel (default) or one of BUNDLED_LOCALES.
LANGUAGE_SETTING = "addon_language"
FOLLOW_KODI = "follow_kodi"
DEFAULT_LOCALE = "en_gb"

# Short locale codes for every bundled resource.language.* folder, menu order.
BUNDLED_LOCALES = [
    "en_gb",
    "de_de",
    "es_es",
    "fr_fr",
    "it_it",
    "nl_nl",
    "zh_cn",
    "ja_jp",
    "ko_kr",
    "pl_pl",
    "pt_br",
    "ru_ru",
]

_DISPLAY_NAMES = {
    "en_gb": "English (en_gb)",
    "de_de": "German (de_de)",
    "es_es": "Spanish (es_es)",
    "fr_fr": "French (fr_fr)",
    "it_it": "Italian (it_it)",
    "nl_nl": "Dutch (nl_nl)",
    "zh_cn": "Chinese Simplified (zh_cn)",
    "ja_jp": "Japanese (ja_jp)",
    "ko_kr": "Korean (ko_kr)",
    "pl_pl": "Polish (pl_pl)",
    "pt_br": "Portuguese Brazil (pt_br)",
    "ru_ru": "Russian (ru_ru)",
}

# Kodi's getLanguage() returns either an ISO 639-1 code ("fr") or an English
# name ("French"); map both (lowercased) to a bundled locale.
_KODI_LANG_MAP = {
    "en": "en_gb",
    "english": "en_gb",
    "de": "de_de",
    "german": "de_de",
    "es": "es_es",
    "spanish": "es_es",
    "fr": "fr_fr",
    "french": "fr_fr",
    "it": "it_it",
    "italian": "it_it",
    "nl": "nl_nl",
    "dutch": "nl_nl",
    "zh": "zh_cn",
    "chinese": "zh_cn",
    "ja": "ja_jp",
    "japanese": "ja_jp",
    "ko": "ko_kr",
    "korean": "ko_kr",
    "pl": "pl_pl",
    "polish": "pl_pl",
    "pt": "pt_br",
    "portuguese": "pt_br",
    "ru": "ru_ru",
    "russian": "ru_ru",
}

# English source-of-truth fallback (populate as new ids are added to strings.po)
_EN: dict[int, str] = {}
_PO_CACHE: dict[str, dict[int, str]] = {}


def supported_languages() -> list[str]:
    """Return the list of bundled language resource folders."""
    return ["resource.language." + code for code in BUNDLED_LOCALES]


def language_options() -> list[tuple[str, str]]:
    """Return [(value, label)] for the in-add-on language menu.

    First entry is the follow-Kodi sentinel; the rest are the bundled locales.
    """
    options = [(FOLLOW_KODI, "Follow Kodi system language")]
    options += [(code, _DISPLAY_NAMES[code]) for code in BUNDLED_LOCALES]
    return options


def _get_setting(key: str) -> str:
    if xbmcaddon is None:
        return ""
    try:
        return xbmcaddon.Addon(ADDON_ID).getSetting(key) or ""
    except Exception:
        return ""


def _kodi_locale() -> str:
    """Resolve Kodi's current UI language to a bundled locale code."""
    if xbmc is None:
        return DEFAULT_LOCALE
    raw = ""
    try:
        iso = getattr(xbmc, "ISO_639_1", None)
        raw = xbmc.getLanguage(iso) if iso is not None else xbmc.getLanguage()
    except Exception:
        raw = ""
    raw = (raw or "").strip().lower()
    if raw in _KODI_LANG_MAP:
        return _KODI_LANG_MAP[raw]
    return _KODI_LANG_MAP.get(raw[:2], DEFAULT_LOCALE)


def effective_language() -> str:
    """Return the active bundled locale code.

    follow_kodi (the default) resolves through Kodi's UI language; a pinned
    locale is returned as-is when bundled, otherwise the default locale.
    """
    setting = _get_setting(LANGUAGE_SETTING).strip()
    if setting and setting != FOLLOW_KODI:
        return setting if setting in BUNDLED_LOCALES else DEFAULT_LOCALE
    return _kodi_locale()


def _override_locale() -> str | None:
    """Return the pinned locale code when one is set, else None (follow Kodi)."""
    setting = _get_setting(LANGUAGE_SETTING).strip()
    if setting and setting != FOLLOW_KODI and setting in BUNDLED_LOCALES:
        return setting
    return None


def _po_path(code: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    language_root = os.path.join(os.path.dirname(os.path.dirname(here)), "language")
    return os.path.join(language_root, "resource.language." + code, "strings.po")


def _load_po(code: str) -> dict[int, str]:
    """Parse a bundled strings.po into {numeric_id: msgstr}, cached per locale."""
    if code in _PO_CACHE:
        return _PO_CACHE[code]
    table: dict[int, str] = {}
    try:
        with open(_po_path(code), encoding="utf-8") as handle:
            current = None
            for raw in handle:
                line = raw.strip()
                if line.startswith("msgctxt"):
                    digits = "".join(ch for ch in line if ch.isdigit())
                    current = int(digits) if digits else None
                elif line.startswith("msgstr") and current is not None:
                    table[current] = line[len("msgstr") :].strip().strip('"')
                    current = None
    except Exception:
        table = {}
    _PO_CACHE[code] = table
    return table


def L(string_id: int, default: str | None = None) -> str:
    """Return localized string, falling back to English source.

    Always safe to call: never raises, never returns None. A pinned
    (non-follow-Kodi) locale is consulted first; otherwise Kodi's GUI-language
    string is used, then the English source table, then the caller default.
    """
    try:
        sid = int(string_id)
    except (TypeError, ValueError, OverflowError):
        return str(default if default is not None else string_id)
    override = _override_locale()
    if override is not None:
        value = _load_po(override).get(sid)
        if value:
            return value
    if xbmcaddon is not None:
        try:
            s: str = xbmcaddon.Addon(ADDON_ID).getLocalizedString(sid)
            if s:
                return s
        except Exception:
            pass
    return _EN.get(sid, default if default is not None else "")
