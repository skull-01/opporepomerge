"""v2.9.16 Build 2 — in-add-on network settings menu (ENH-#42, IP editor part).

Covers the addon-side network/IP viewer-editor added to installer.main():
- New "Network settings (TV / OPPO / AVR / Kodi)" menu entry + dispatch.
- Backend-aware editable field list (TV/AVR rows follow the selected backend),
  including enum-index normalization (a setting stored as "1" -> "sony_bravia").
- Edit flow: write-back, invalid-port rejection, unchanged/empty no-op, the
  read-only Kodi-box-address row, and the "managed by the configurator" marker.

Every editable field here is in service.CONFIGURATOR_MANAGED_KEYS, so an
override is announced as temporary; the menu never mutates config silently.
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


def _field_keys(**settings):
    base = {"oppo_ip": "192.168.1.50", "oppo_port": "23", "tv_ip": "192.168.1.60"}
    base.update(settings)
    with kodi_stubs():
        import xbmcaddon

        xbmcaddon.reset(settings=base, info={"path": ROOT, "id": ADDON_ID})
        installer = importlib.import_module("resources.lib.installer")
        return [key for key, _label, _kind in installer._network_fields()]


def _run_menu(settings, selects, inputs=()):
    with kodi_stubs():
        import xbmcaddon
        import xbmcgui

        base = {
            "oppo_ip": "192.168.1.50",
            "oppo_port": "23",
            "tv_ip": "192.168.1.60",
            "tv_backend": "adb",
        }
        base.update(settings)
        xbmcaddon.reset(settings=base, info={"path": ROOT, "id": ADDON_ID})
        installer = importlib.import_module("resources.lib.installer")
        xbmcgui.reset()
        for choice in selects:
            xbmcgui.push_select(choice)
        for value in inputs:
            xbmcgui.push_input(value)
        installer.network_settings_menu()
        return {
            "settings": {key: installer.ADDON.getSetting(key) for key in base},
            "calls": list(xbmcgui.calls()),
        }


def _ok_headings(calls):
    return [c[1] for c in calls if c[0] == "ok"]


# adb layout rows: 0 marker, 1 oppo_ip, 2 oppo_port, 3 tv_ip, 4 tv_adb_port,
# 5 adb_path, 6 kodi_host(info), 7 Back.
ROW_OPPO_IP = 1
ROW_OPPO_PORT = 2
ROW_KODI_INFO = 6
ROW_BACK = 7
ROW_MARKER = 0


class TMenuEntry(unittest.TestCase):
    def test_main_menu_lists_network_entry_and_dispatches(self):
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
            xbmcgui.push_select(11)  # "Network settings ..." in main()
            xbmcgui.push_select(-1)  # network menu: cancel/back
            installer.main()

            selects = [c for c in xbmcgui.calls() if c[0] == "select"]
            main_options = selects[0][2]
            self.assertTrue(any("Network settings" in opt for opt in main_options))
            self.assertTrue(
                any(c[1] == "Network settings (TV / OPPO / AVR / Kodi)" for c in selects)
            )

    def test_menu_rows_show_marker_and_current_values(self):
        result = _run_menu({}, selects=[ROW_BACK])
        select_calls = [c for c in result["calls"] if c[0] == "select"]
        rows = select_calls[0][2]
        self.assertIn("[Managed by the configurator] - select for details", rows)
        self.assertTrue(any(row.startswith("OPPO IP: 192.168.1.50") for row in rows))
        self.assertTrue(any(row.startswith("TV IP: 192.168.1.60") for row in rows))
        self.assertEqual(rows[-1], "Back")


class TFieldList(unittest.TestCase):
    def test_core_fields_and_kodi_info_always_present(self):
        keys = _field_keys(tv_backend="lg_command")
        for key in ("oppo_ip", "oppo_port", "tv_ip", "kodi_host"):
            self.assertIn(key, keys)
        # lg/samsung/custom are command-based: no extra host field beyond tv_ip.
        self.assertNotIn("tv_adb_port", keys)
        self.assertNotIn("sony_psk", keys)

    def test_adb_backend_shows_adb_fields(self):
        keys = _field_keys(tv_backend="adb")
        self.assertIn("tv_adb_port", keys)
        self.assertIn("adb_path", keys)
        self.assertNotIn("sony_psk", keys)

    def test_sony_bravia_backend_shows_psk(self):
        keys = _field_keys(tv_backend="sony_bravia")
        self.assertIn("sony_psk", keys)
        self.assertNotIn("tv_adb_port", keys)

    def test_roku_backend_shows_ecp_port(self):
        self.assertIn("roku_ecp_port", _field_keys(tv_backend="roku_ecp"))

    def test_smartthings_backend_shows_token_and_device(self):
        keys = _field_keys(tv_backend="smartthings")
        self.assertIn("smartthings_token", keys)
        self.assertIn("smartthings_device_id", keys)

    def test_enum_stored_as_index_is_normalized(self):
        # tv_backend "1" -> "sony_bravia" via settings_reader.ENUM_VALUES.
        self.assertIn("sony_psk", _field_keys(tv_backend="1"))

    def test_enum_index_out_of_range_falls_through(self):
        keys = _field_keys(tv_backend="99")
        for key in ("tv_adb_port", "sony_psk", "roku_ecp_port", "smartthings_token"):
            self.assertNotIn(key, keys)

    def test_avr_enabled_shows_host_and_port(self):
        keys = _field_keys(avr_control_enabled="true")
        self.assertIn("avr_host", keys)
        self.assertIn("avr_port", keys)

    def test_avr_backend_set_shows_host_even_if_flag_off(self):
        keys = _field_keys(avr_control_enabled="false", avr_backend="denon_marantz")
        self.assertIn("avr_host", keys)

    def test_avr_sony_audio_shows_psk(self):
        self.assertIn("sony_avr_psk", _field_keys(avr_backend="sony_audio_api"))

    def test_avr_disabled_hides_avr_fields(self):
        keys = _field_keys(avr_control_enabled="false", avr_backend="disabled")
        self.assertNotIn("avr_host", keys)
        self.assertNotIn("sony_avr_psk", keys)


class TEditFlow(unittest.TestCase):
    def test_edit_oppo_ip_writes_and_warns(self):
        result = _run_menu({}, selects=[ROW_OPPO_IP, ROW_BACK], inputs=["192.0.2.5"])
        self.assertEqual(result["settings"]["oppo_ip"], "192.0.2.5")
        updated = [c for c in result["calls"] if c[0] == "ok" and c[1] == "Setting updated"]
        self.assertTrue(updated)
        self.assertIn("configurator", updated[0][2].lower())

    def test_valid_port_is_written(self):
        result = _run_menu({}, selects=[ROW_OPPO_PORT, ROW_BACK], inputs=["24"])
        self.assertEqual(result["settings"]["oppo_port"], "24")

    def test_invalid_port_is_rejected(self):
        result = _run_menu({}, selects=[ROW_OPPO_PORT, ROW_BACK], inputs=["not-a-port"])
        self.assertEqual(result["settings"]["oppo_port"], "23")
        self.assertIn("Invalid port", _ok_headings(result["calls"]))

    def test_unchanged_value_is_a_noop(self):
        result = _run_menu({}, selects=[ROW_OPPO_IP, ROW_BACK], inputs=["192.168.1.50"])
        self.assertEqual(result["settings"]["oppo_ip"], "192.168.1.50")
        self.assertNotIn("Setting updated", _ok_headings(result["calls"]))

    def test_empty_input_does_not_clear_setting(self):
        result = _run_menu({}, selects=[ROW_OPPO_IP, ROW_BACK], inputs=[""])
        self.assertEqual(result["settings"]["oppo_ip"], "192.168.1.50")
        self.assertNotIn("Setting updated", _ok_headings(result["calls"]))

    def test_marker_row_shows_managed_note(self):
        result = _run_menu({}, selects=[ROW_MARKER, ROW_BACK])
        self.assertIn("Managed by the configurator", _ok_headings(result["calls"]))

    def test_kodi_info_row_is_read_only(self):
        result = _run_menu({}, selects=[ROW_KODI_INFO, ROW_BACK])
        self.assertIn("Kodi box address", _ok_headings(result["calls"]))
        self.assertNotIn("Setting updated", _ok_headings(result["calls"]))

    def test_cancel_returns_immediately(self):
        result = _run_menu({}, selects=[-1])
        self.assertEqual(result["settings"]["oppo_ip"], "192.168.1.50")
        self.assertNotIn("Setting updated", _ok_headings(result["calls"]))


if __name__ == "__main__":
    unittest.main()
