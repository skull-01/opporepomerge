"""v2.9.17 Build 3 — in-add-on add-on-language switcher (ENH-#42, language part).

Covers the language half of ENH-#42:
- `i18n.supported_languages()` now lists all 12 bundled locales (was stale at 7).
- `i18n.language_options()` for the menu (follow-Kodi sentinel + 12 locales).
- `i18n.effective_language()` resolves the `addon_language` setting — the
  "follow Kodi system language" path is exercised with a stubbed
  `xbmc.getLanguage()` per the issue's acceptance criteria.
- `i18n.L()` consults a pinned locale's strings.po first, else the existing
  Kodi/default path (unchanged for the follow-Kodi default).
- `installer.language_menu()` persists the preference and dispatches from
  `installer.main()`.

Bundled non-en_gb strings are currently English placeholders, so a pinned
locale changes the source file consulted, not yet the visible text.
"""

import contextlib
import importlib
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "resources", "lib")
STUBS = os.path.join(ROOT, "tests", "_stubs")
ADDON_ID = "script.oppo203.iso.external"


@contextlib.contextmanager
def kodi_stubs():
    from tests._support.lib_buckets import with_canonical

    names = with_canonical(
        {
            "xbmc",
            "xbmcaddon",
            "xbmcgui",
            "xbmcvfs",
            "xbmcplugin",
            "xbmcdrm",
            "i18n",
            "resources.lib.i18n",
            "resources.lib.installer",
            "installer",
            "settings_reader",
            "resources.lib.settings_reader",
        }
    )
    old_path = list(sys.path)
    saved = {name: sys.modules.get(name) for name in names}
    try:
        for path in (STUBS, ROOT, LIB):
            sys.path.insert(0, path)
        for name in names:
            sys.modules.pop(name, None)
        yield
    finally:
        for name in names:
            sys.modules.pop(name, None)
        for name, module in saved.items():
            if module is not None:
                sys.modules[name] = module
        sys.path[:] = old_path


def _import_i18n(settings=None, localized=None, get_language=None, iso_attr=False):
    """Import a fresh stub-bound i18n; optionally stub xbmc.getLanguage."""
    import xbmc
    import xbmcaddon

    xbmcaddon.reset(
        settings=settings or {}, info={"path": ROOT, "id": ADDON_ID}, localized=localized or {}
    )
    if get_language is not None:
        if iso_attr:
            xbmc.ISO_639_1 = 0
        xbmc.getLanguage = get_language
    return importlib.import_module("i18n")


class TSupportedLanguages(unittest.TestCase):
    def test_lists_all_twelve_bundled_locales(self):
        with kodi_stubs():
            i18n = _import_i18n()
            langs = i18n.supported_languages()
            self.assertEqual(len(langs), 12)
            for code in ("en_gb", "de_de", "fr_fr", "zh_cn", "ja_jp", "ru_ru"):
                self.assertIn("resource.language." + code, langs)

    def test_every_listed_folder_exists_on_disk(self):
        with kodi_stubs():
            i18n = _import_i18n()
            for folder in i18n.supported_languages():
                self.assertTrue(os.path.isdir(os.path.join(ROOT, "resources", "language", folder)))


class TLanguageOptions(unittest.TestCase):
    def test_follow_kodi_first_then_locales(self):
        with kodi_stubs():
            i18n = _import_i18n()
            options = i18n.language_options()
            self.assertEqual(options[0][0], "follow_kodi")
            self.assertEqual(len(options), 13)  # sentinel + 12 locales
            values = [v for v, _ in options]
            self.assertEqual(values[1:], i18n.BUNDLED_LOCALES)


class TEffectiveLanguage(unittest.TestCase):
    def test_follow_kodi_resolves_via_getlanguage_iso(self):
        with kodi_stubs():
            i18n = _import_i18n(get_language=lambda *a, **k: "fr")
            self.assertEqual(i18n.effective_language(), "fr_fr")

    def test_follow_kodi_resolves_via_english_name(self):
        with kodi_stubs():
            i18n = _import_i18n(get_language=lambda *a, **k: "German")
            self.assertEqual(i18n.effective_language(), "de_de")

    def test_follow_kodi_two_letter_prefix_fallback(self):
        with kodi_stubs():
            i18n = _import_i18n(get_language=lambda *a, **k: "fr-FR")
            self.assertEqual(i18n.effective_language(), "fr_fr")

    def test_follow_kodi_iso_attr_path(self):
        with kodi_stubs():
            i18n = _import_i18n(get_language=lambda iso: "de", iso_attr=True)
            self.assertEqual(i18n.effective_language(), "de_de")

    def test_follow_kodi_unknown_language_defaults_en(self):
        with kodi_stubs():
            i18n = _import_i18n(get_language=lambda *a, **k: "xx")
            self.assertEqual(i18n.effective_language(), "en_gb")

    def test_follow_kodi_getlanguage_raises_defaults_en(self):
        def boom(*a, **k):
            raise RuntimeError("no language")

        with kodi_stubs():
            i18n = _import_i18n(get_language=boom)
            self.assertEqual(i18n.effective_language(), "en_gb")

    def test_follow_kodi_missing_getlanguage_defaults_en(self):
        # The xbmc stub has no getLanguage at all.
        with kodi_stubs():
            i18n = _import_i18n()
            self.assertEqual(i18n.effective_language(), "en_gb")

    def test_no_xbmc_module_defaults_en(self):
        with kodi_stubs():
            i18n = _import_i18n()
            i18n.xbmc = None
            self.assertEqual(i18n.effective_language(), "en_gb")

    def test_pinned_locale_returned_as_is(self):
        with kodi_stubs():
            i18n = _import_i18n(settings={"addon_language": "de_de"})
            self.assertEqual(i18n.effective_language(), "de_de")

    def test_pinned_invalid_locale_defaults_en(self):
        with kodi_stubs():
            i18n = _import_i18n(settings={"addon_language": "zz_zz"})
            self.assertEqual(i18n.effective_language(), "en_gb")


class TLocalizedLookup(unittest.TestCase):
    def test_follow_kodi_uses_kodi_string(self):
        with kodi_stubs():
            i18n = _import_i18n(localized={30101: "FromKodi"})
            self.assertEqual(i18n.L(30101), "FromKodi")

    def test_pinned_locale_reads_from_po(self):
        # localized is empty, so a non-empty result proves the .po was consulted.
        with kodi_stubs():
            i18n = _import_i18n(settings={"addon_language": "fr_fr"}, localized={})
            self.assertEqual(i18n.L(30101), "Oppo IP address")

    def test_pinned_locale_missing_id_falls_through(self):
        with kodi_stubs():
            i18n = _import_i18n(settings={"addon_language": "fr_fr"}, localized={31000: "K"})
            self.assertEqual(i18n.L(31000), "K")

    def test_invalid_pin_uses_default_path(self):
        with kodi_stubs():
            i18n = _import_i18n(settings={"addon_language": "zz_zz"}, localized={30101: "K"})
            self.assertEqual(i18n.L(30101), "K")

    def test_invalid_id_returns_default(self):
        with kodi_stubs():
            i18n = _import_i18n()
            self.assertEqual(i18n.L("notanint", "fallback"), "fallback")

    def test_load_po_missing_file_is_empty(self):
        with kodi_stubs():
            i18n = _import_i18n()
            self.assertEqual(i18n._load_po("nonexistent"), {})

    def test_load_po_is_cached(self):
        with kodi_stubs():
            i18n = _import_i18n()
            first = i18n._load_po("fr_fr")
            second = i18n._load_po("fr_fr")
            self.assertIs(first, second)


class TLanguageMenu(unittest.TestCase):
    def _run(self, settings, selects):
        with kodi_stubs():
            import xbmcaddon
            import xbmcgui

            xbmcaddon.reset(settings=settings, info={"path": ROOT, "id": ADDON_ID})
            installer = importlib.import_module("resources.lib.installer")
            xbmcgui.reset()
            for choice in selects:
                xbmcgui.push_select(choice)
            installer.language_menu()
            return {
                "addon_language": installer.ADDON.getSetting("addon_language"),
                "calls": list(xbmcgui.calls()),
            }

    def test_select_follow_kodi_persists_sentinel(self):
        result = self._run({"addon_language": "fr_fr"}, selects=[0])
        self.assertEqual(result["addon_language"], "follow_kodi")
        self.assertTrue(any(c[0] == "ok" and c[1] == "Add-on language" for c in result["calls"]))

    def test_select_locale_persists_code(self):
        # options: 0 follow, 1 en_gb, 2 de_de, 3 es_es, 4 fr_fr
        result = self._run({}, selects=[4])
        self.assertEqual(result["addon_language"], "fr_fr")
        self.assertTrue(any(c[0] == "ok" and "saved" in c[2] for c in result["calls"]))

    def test_current_marker_shown(self):
        with kodi_stubs():
            import xbmcaddon
            import xbmcgui

            xbmcaddon.reset(
                settings={"addon_language": "de_de"}, info={"path": ROOT, "id": ADDON_ID}
            )
            installer = importlib.import_module("resources.lib.installer")
            xbmcgui.reset()
            xbmcgui.push_select(-1)
            installer.language_menu()
            rows = [c for c in xbmcgui.calls() if c[0] == "select"][0][2]
            self.assertTrue(any("(current)" in row for row in rows))

    def test_cancel_does_not_write(self):
        result = self._run({}, selects=[-1])
        self.assertEqual(result["addon_language"], "")

    def test_main_menu_lists_language_entry_and_dispatches(self):
        with kodi_stubs():
            import xbmcaddon
            import xbmcgui

            xbmcaddon.reset(
                settings={"architecture_choice_made": "true"},
                info={"path": ROOT, "id": ADDON_ID},
            )
            installer = importlib.import_module("resources.lib.installer")
            installer.ADDON.openSettings = lambda: None
            xbmcgui.reset()
            xbmcgui.push_select(12)  # "Add-on language"
            xbmcgui.push_select(-1)  # language menu: cancel
            installer.main()
            selects = [c for c in xbmcgui.calls() if c[0] == "select"]
            self.assertTrue(any("Add-on language" in opt for opt in selects[0][2]))
            self.assertTrue(any(c[1] == "Add-on language" for c in selects))


if __name__ == "__main__":
    unittest.main()
