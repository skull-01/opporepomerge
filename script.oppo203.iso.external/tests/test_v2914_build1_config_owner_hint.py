"""v2.9.14 Build 1 — configurator-owns-config in-add-on guidance hint and overwrite warning.

Covers the addon-side parts of ENH-#41 Parts B and C:
- Static lsep label at the top of <category id="connection"> in settings.xml.
- service.Monitor.onSettingsChanged shows a once-per-session generic hint
  notification and warns per key when a CONFIGURATOR_MANAGED_KEYS entry was
  overwritten via Kodi's settings UI.
- Logging/notification only — no add-on state is mutated.
"""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "resources", "lib"))
for _name in ("xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs"):
    sys.modules.pop(_name, None)


def _import_service():
    import service
    return service


def _make_addon(settings):
    addon = mock.MagicMock()
    addon.getSetting.side_effect = lambda k: settings.get(k, "")
    return addon


def _make_xbmcaddon(settings):
    mod = mock.MagicMock()
    mod.Addon.return_value = _make_addon(settings)
    return mod


class _FakeWindow:
    def __init__(self):
        self._props = {}

    def getProperty(self, key):
        return self._props.get(key, "")

    def setProperty(self, key, value):
        self._props[key] = value


def _make_xbmcgui_with_window(window):
    mod = mock.MagicMock()
    mod.Window.return_value = window
    return mod


class TManagedKeysContent(unittest.TestCase):
    def setUp(self):
        self.s = _import_service()

    def test_tuple_of_strings(self):
        self.assertIsInstance(self.s.CONFIGURATOR_MANAGED_KEYS, tuple)
        self.assertGreater(len(self.s.CONFIGURATOR_MANAGED_KEYS), 10)
        for key in self.s.CONFIGURATOR_MANAGED_KEYS:
            self.assertIsInstance(key, str)
            self.assertTrue(key)

    def test_includes_core_ips_and_hardware_model(self):
        for key in (
            "oppo_ip", "tv_ip", "avr_host",
            "oppo_hardware_model", "tv_backend", "avr_backend",
        ):
            self.assertIn(key, self.s.CONFIGURATOR_MANAGED_KEYS)

    def test_includes_command_strings_and_tokens(self):
        for key in (
            "lg_oppo_command", "samsung_kodi_command", "custom_oppo_command",
            "roku_oppo_key", "smartthings_token", "sony_psk",
            "avr_player_input", "oppo_start_commands", "oppo_remote_command_map",
        ):
            self.assertIn(key, self.s.CONFIGURATOR_MANAGED_KEYS)

    def test_excludes_operator_tunable_knobs(self):
        for key in (
            "oppo_socket_timeout", "oppo_command_delay",
            "reconnect_enabled", "reconnect_max_retries",
            "kodi_startup_power_on", "kodi_startup_power_on_delay",
            "fast_changeover", "switch_back_on_exit",
            "fixed_timeout_minutes", "http_poll_interval",
            "oppo_use_wol", "tv_switching_enabled", "avr_control_enabled",
            "oppo_jailbreak_enabled", "oppo_verbose_mode",
        ):
            self.assertNotIn(key, self.s.CONFIGURATOR_MANAGED_KEYS)


class TSnapshotAndDiff(unittest.TestCase):
    def setUp(self):
        self.s = _import_service()

    def test_snapshot_empty_when_xbmcaddon_missing(self):
        with mock.patch.object(self.s, "xbmcaddon", None):
            self.assertEqual(self.s._snapshot_managed_settings(), {})

    def test_snapshot_returns_current_values(self):
        seed = {
            "oppo_ip": "10.0.0.5",
            "tv_ip": "10.0.0.6",
            "oppo_hardware_model": "udp_203",
        }
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon(seed)):
            snap = self.s._snapshot_managed_settings()
        for key in self.s.CONFIGURATOR_MANAGED_KEYS:
            self.assertIn(key, snap)
        self.assertEqual(snap["oppo_ip"], "10.0.0.5")
        self.assertEqual(snap["tv_ip"], "10.0.0.6")

    def test_changed_keys_detects_changes(self):
        baseline = {key: "" for key in self.s.CONFIGURATOR_MANAGED_KEYS}
        baseline["oppo_ip"] = "10.0.0.5"
        baseline["avr_host"] = "10.0.0.7"
        current = dict(baseline)
        current["oppo_ip"] = "10.0.0.9"
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon(current)):
            changed = self.s._changed_managed_keys(baseline)
        self.assertEqual(changed, ["oppo_ip"])

    def test_changed_keys_empty_when_unchanged(self):
        baseline = {"oppo_ip": "10.0.0.5"}
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon(baseline)):
            changed = self.s._changed_managed_keys(baseline)
        self.assertEqual(changed, [])

    def test_changed_keys_ignores_non_managed(self):
        baseline = {key: "" for key in self.s.CONFIGURATOR_MANAGED_KEYS}
        current = dict(baseline)
        current["oppo_socket_timeout"] = "5.0"  # operator-tunable
        current["fast_changeover"] = "false"
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon(current)):
            changed = self.s._changed_managed_keys(baseline)
        self.assertEqual(changed, [])


class TNotificationHelpers(unittest.TestCase):
    def setUp(self):
        self.s = _import_service()

    def test_hint_safe_without_xbmcgui(self):
        with mock.patch.object(self.s, "xbmcgui", None):
            self.assertFalse(self.s._notify_config_hint_once_per_session())

    def test_hint_fires_once_per_session(self):
        window = _FakeWindow()
        fake_gui = _make_xbmcgui_with_window(window)
        with mock.patch.object(self.s, "xbmcgui", fake_gui):
            self.assertTrue(self.s._notify_config_hint_once_per_session())
            self.assertEqual(window.getProperty("oppo203_config_hint_shown"), "1")
            self.assertEqual(fake_gui.Dialog.return_value.notification.call_count, 1)
            self.assertFalse(self.s._notify_config_hint_once_per_session())
            self.assertEqual(fake_gui.Dialog.return_value.notification.call_count, 1)

    def test_warn_noop_on_empty_list(self):
        fake_gui = _make_xbmcgui_with_window(_FakeWindow())
        with mock.patch.object(self.s, "xbmcgui", fake_gui):
            self.s._warn_overwritten_managed_keys([])
        fake_gui.Dialog.return_value.notification.assert_not_called()

    def test_warn_logs_and_notifies_per_key(self):
        fake_gui = _make_xbmcgui_with_window(_FakeWindow())
        with mock.patch.object(self.s, "xbmcgui", fake_gui):
            self.s._warn_overwritten_managed_keys(["oppo_ip", "tv_ip"])
        self.assertEqual(fake_gui.Dialog.return_value.notification.call_count, 2)

    def test_warn_safe_without_xbmcgui(self):
        with mock.patch.object(self.s, "xbmcgui", None):
            self.s._warn_overwritten_managed_keys(["oppo_ip"])


class TMonitor(unittest.TestCase):
    def setUp(self):
        self.s = _import_service()

    def _patched_modules(self, settings):
        return mock.patch.multiple(
            self.s,
            xbmcaddon=_make_xbmcaddon(settings),
            xbmcgui=_make_xbmcgui_with_window(_FakeWindow()),
        )

    def test_init_captures_baseline(self):
        seed = {"oppo_ip": "192.168.1.50", "tv_ip": "192.168.1.60"}
        with self._patched_modules(seed):
            monitor = self.s.Monitor()
            self.assertEqual(monitor._managed_baseline["oppo_ip"], "192.168.1.50")
            self.assertEqual(monitor._managed_baseline["tv_ip"], "192.168.1.60")

    def test_on_settings_changed_fires_hint_and_warn(self):
        live = {"oppo_ip": "192.168.1.50"}
        fake_addon_mod = _make_xbmcaddon(live)
        window = _FakeWindow()
        fake_gui = _make_xbmcgui_with_window(window)
        with mock.patch.object(self.s, "xbmcaddon", fake_addon_mod), \
             mock.patch.object(self.s, "xbmcgui", fake_gui):
            monitor = self.s.Monitor()
            live["oppo_ip"] = "192.168.1.99"
            monitor.onSettingsChanged()
            self.assertEqual(window.getProperty("oppo203_config_hint_shown"), "1")
            self.assertGreaterEqual(
                fake_gui.Dialog.return_value.notification.call_count, 2
            )
            self.assertEqual(monitor._managed_baseline["oppo_ip"], "192.168.1.99")

    def test_on_settings_changed_part_b_only_when_no_managed_change(self):
        live = {"oppo_ip": "192.168.1.50"}
        fake_addon_mod = _make_xbmcaddon(live)
        window = _FakeWindow()
        fake_gui = _make_xbmcgui_with_window(window)
        with mock.patch.object(self.s, "xbmcaddon", fake_addon_mod), \
             mock.patch.object(self.s, "xbmcgui", fake_gui):
            monitor = self.s.Monitor()
            monitor.onSettingsChanged()
            self.assertEqual(fake_gui.Dialog.return_value.notification.call_count, 1)
            self.assertEqual(monitor._managed_baseline["oppo_ip"], "192.168.1.50")

    def test_on_settings_changed_part_b_suppressed_on_repeat(self):
        live = {"oppo_ip": "192.168.1.50"}
        fake_addon_mod = _make_xbmcaddon(live)
        window = _FakeWindow()
        fake_gui = _make_xbmcgui_with_window(window)
        with mock.patch.object(self.s, "xbmcaddon", fake_addon_mod), \
             mock.patch.object(self.s, "xbmcgui", fake_gui):
            monitor = self.s.Monitor()
            live["oppo_ip"] = "192.168.1.99"
            monitor.onSettingsChanged()
            first_count = fake_gui.Dialog.return_value.notification.call_count
            live["tv_ip"] = "192.168.1.77"
            monitor.onSettingsChanged()
            second_count = fake_gui.Dialog.return_value.notification.call_count
            self.assertEqual(second_count - first_count, 1)

    def test_on_settings_changed_swallows_exceptions(self):
        fake_addon_mod = mock.MagicMock()
        fake_addon_mod.Addon.side_effect = RuntimeError("boom")
        with mock.patch.object(self.s, "xbmcaddon", fake_addon_mod), \
             mock.patch.object(self.s, "xbmcgui", None):
            monitor = self.s.Monitor()
            monitor.onSettingsChanged()


class TSettingsXmlAndPo(unittest.TestCase):
    def test_settings_xml_has_lsep_at_top_of_connection(self):
        path = os.path.join(ROOT, "resources", "settings.xml")
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        connection_idx = text.index('<category id="connection"')
        next_category_idx = text.index("<category", connection_idx + 1)
        connection_block = text[connection_idx:next_category_idx]
        self.assertIn('label="30290"', connection_block)
        self.assertIn('type="lsep"', connection_block)
        lsep_idx = connection_block.index("type=\"lsep\"")
        first_real_setting_idx = connection_block.index('id="oppo_ip"')
        self.assertLess(lsep_idx, first_real_setting_idx)

    def test_po_has_all_new_entries(self):
        path = os.path.join(
            ROOT, "resources", "language", "resource.language.en_gb", "strings.po"
        )
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        for ctx in ("#30290", "#30291", "#30292", "#30293"):
            self.assertIn(f'msgctxt "{ctx}"', text)


if __name__ == "__main__":
    unittest.main()
