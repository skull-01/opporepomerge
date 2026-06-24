"""v2.9.17 Build 1 — configurator-owns-config in-add-on guidance hint and overwrite warning.

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


def _make_rw_addon(settings):
    """Addon stub backed by a live dict: setSetting mutates it, getSetting reads it.

    Used to exercise the model-default auto-apply path (no-op avoidance,
    re-entrancy guard) which the read-only _make_addon cannot.
    """
    addon = mock.MagicMock()
    addon.getSetting.side_effect = lambda k: settings.get(k, "")
    addon.setSetting.side_effect = lambda k, v: settings.__setitem__(k, v)
    return addon


def _make_xbmcaddon_rw(settings):
    mod = mock.MagicMock()
    mod.Addon.return_value = _make_rw_addon(settings)
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
            "oppo_ip",
            "tv_ip",
            "avr_host",
            "oppo_hardware_model",
            "tv_backend",
            "avr_backend",
        ):
            self.assertIn(key, self.s.CONFIGURATOR_MANAGED_KEYS)

    def test_includes_command_strings_and_tokens(self):
        for key in (
            "lg_oppo_command",
            "samsung_kodi_command",
            "custom_oppo_command",
            "roku_oppo_key",
            "smartthings_token",
            "sony_psk",
            "avr_player_input",
            "oppo_start_commands",
            "oppo_remote_command_map",
        ):
            self.assertIn(key, self.s.CONFIGURATOR_MANAGED_KEYS)

    def test_excludes_operator_tunable_knobs(self):
        for key in (
            "oppo_socket_timeout",
            "oppo_command_delay",
            "reconnect_enabled",
            "reconnect_max_retries",
            "kodi_startup_power_on",
            "kodi_startup_power_on_delay",
            "fast_changeover",
            "switch_back_on_exit",
            "fixed_timeout_minutes",
            "http_poll_interval",
            "oppo_use_wol",
            "tv_switching_enabled",
            "avr_control_enabled",
            "oppo_jailbreak_enabled",
            "oppo_verbose_mode",
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
        baseline = dict.fromkeys(self.s.CONFIGURATOR_MANAGED_KEYS, "")
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
        baseline = dict.fromkeys(self.s.CONFIGURATOR_MANAGED_KEYS, "")
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
        with (
            mock.patch.object(self.s, "xbmcaddon", fake_addon_mod),
            mock.patch.object(self.s, "xbmcgui", fake_gui),
        ):
            monitor = self.s.Monitor()
            live["oppo_ip"] = "192.168.1.99"
            monitor.onSettingsChanged()
            self.assertEqual(window.getProperty("oppo203_config_hint_shown"), "1")
            self.assertGreaterEqual(fake_gui.Dialog.return_value.notification.call_count, 2)
            self.assertEqual(monitor._managed_baseline["oppo_ip"], "192.168.1.99")

    def test_on_settings_changed_part_b_only_when_no_managed_change(self):
        live = {"oppo_ip": "192.168.1.50"}
        fake_addon_mod = _make_xbmcaddon(live)
        window = _FakeWindow()
        fake_gui = _make_xbmcgui_with_window(window)
        with (
            mock.patch.object(self.s, "xbmcaddon", fake_addon_mod),
            mock.patch.object(self.s, "xbmcgui", fake_gui),
        ):
            monitor = self.s.Monitor()
            monitor.onSettingsChanged()
            self.assertEqual(fake_gui.Dialog.return_value.notification.call_count, 1)
            self.assertEqual(monitor._managed_baseline["oppo_ip"], "192.168.1.50")

    def test_on_settings_changed_part_b_suppressed_on_repeat(self):
        live = {"oppo_ip": "192.168.1.50"}
        fake_addon_mod = _make_xbmcaddon(live)
        window = _FakeWindow()
        fake_gui = _make_xbmcgui_with_window(window)
        with (
            mock.patch.object(self.s, "xbmcaddon", fake_addon_mod),
            mock.patch.object(self.s, "xbmcgui", fake_gui),
        ):
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
        with (
            mock.patch.object(self.s, "xbmcaddon", fake_addon_mod),
            mock.patch.object(self.s, "xbmcgui", None),
        ):
            monitor = self.s.Monitor()
            monitor.onSettingsChanged()


class TApplyFullModelDefaultsOnDropdownChange(unittest.TestCase):
    """Selecting a model in oppo_hardware_model auto-applies its full bundle."""

    def setUp(self):
        self.s = _import_service()

    def _stock_seed(self):
        # Enum settings (oppo_start_mode, oppo_http_payload_mode) are stored as
        # their INDEX string in Kodi, like a real install -- "0" == tcp_commands
        # / raw_path. String/bool keys hold their literal value.
        return {
            "oppo_hardware_model": "udp_203",
            "oppo_start_commands": "#PON\n#PLA",
            "oppo_stop_commands": "#STP",
            "oppo_start_mode": "0",
            "oppo_http_activate": "true",
            "oppo_http_payload_mode": "0",
        }

    def _fire_model_change(self, live, new_model):
        fake_addon = _make_xbmcaddon_rw(live)
        fake_gui = _make_xbmcgui_with_window(_FakeWindow())
        with (
            mock.patch.object(self.s, "xbmcaddon", fake_addon),
            mock.patch.object(self.s, "xbmcgui", fake_gui),
        ):
            monitor = self.s.Monitor()
            live["oppo_hardware_model"] = new_model
            monitor.onSettingsChanged()
        return monitor

    def test_model_change_to_m9205_applies_power_bundle(self):
        live = self._stock_seed()
        monitor = self._fire_model_change(live, "chinoppo_m9205")
        self.assertEqual(live["oppo_start_commands"], "#PON\n#PLA")
        self.assertEqual(live["oppo_stop_commands"], "#STP\n#POF")  # #POF release
        self.assertEqual(live["oppo_http_activate"], "false")
        self.assertEqual(live["oppo_start_mode"], "0")  # tcp_commands (index, no-op)
        self.assertFalse(monitor._applying_model_defaults)  # guard reset

    def test_model_change_to_m9702_plus_applies_generic_clone_bundle(self):
        live = self._stock_seed()
        self._fire_model_change(live, "chinoppo_m9702_plus")
        self.assertEqual(live["oppo_start_commands"], "#EJT\n#PLA")
        self.assertEqual(live["oppo_stop_commands"], "#STP")  # NO #POF for M9702-Plus
        self.assertEqual(live["oppo_http_activate"], "false")

    def test_model_change_back_to_stock_restores_http_and_pon(self):
        live = {
            "oppo_hardware_model": "chinoppo_m9205",
            "oppo_start_commands": "#PON\n#PLA",
            "oppo_stop_commands": "#STP\n#POF",
            "oppo_start_mode": "0",
            "oppo_http_activate": "false",
            "oppo_http_payload_mode": "0",
        }
        self._fire_model_change(live, "udp_203")
        self.assertEqual(live["oppo_http_activate"], "true")
        self.assertEqual(live["oppo_start_commands"], "#PON\n#PLA")
        self.assertEqual(live["oppo_stop_commands"], "#STP")  # #POF cleared

    def test_reavon_model_applies_no_bundle(self):
        live = self._stock_seed()
        before = dict(live)
        self._fire_model_change(live, "reavon_ubrx200")
        for key in ("oppo_start_commands", "oppo_stop_commands", "oppo_http_activate"):
            self.assertEqual(live[key], before[key])  # do-not-mutate Reavon

    def test_non_model_change_applies_no_bundle(self):
        live = self._stock_seed()
        live["oppo_ip"] = "192.168.1.50"
        before = dict(live)
        fake_addon = _make_xbmcaddon_rw(live)
        fake_gui = _make_xbmcgui_with_window(_FakeWindow())
        with (
            mock.patch.object(self.s, "xbmcaddon", fake_addon),
            mock.patch.object(self.s, "xbmcgui", fake_gui),
        ):
            monitor = self.s.Monitor()
            live["oppo_ip"] = "192.168.1.99"  # not the model dropdown
            monitor.onSettingsChanged()
        self.assertEqual(live["oppo_start_commands"], before["oppo_start_commands"])
        self.assertEqual(live["oppo_stop_commands"], before["oppo_stop_commands"])
        self.assertEqual(live["oppo_http_activate"], before["oppo_http_activate"])

    def test_reentrancy_guard_blocks_self_refire(self):
        live = self._stock_seed()
        calls = {"n": 0}
        real_apply = self.s._apply_model_defaults

        def counting_apply(model):
            calls["n"] += 1
            return real_apply(model)

        fake_addon = _make_xbmcaddon_rw(live)
        fake_gui = _make_xbmcgui_with_window(_FakeWindow())
        with (
            mock.patch.object(self.s, "xbmcaddon", fake_addon),
            mock.patch.object(self.s, "xbmcgui", fake_gui),
            mock.patch.object(self.s, "_apply_model_defaults", counting_apply),
        ):
            monitor = self.s.Monitor()
            live["oppo_hardware_model"] = "chinoppo_m9205"
            monitor.onSettingsChanged()
            # Simulate the self-induced re-fire that our own writes would trigger
            # in real Kodi: while the guard is set the callback must be a no-op.
            monitor._applying_model_defaults = True
            monitor.onSettingsChanged()
            monitor._applying_model_defaults = False
        self.assertEqual(calls["n"], 1)  # applied exactly once, not recursively

    def test_apply_model_defaults_unit_paths(self):
        # Warning-only models write nothing and return [].
        live = self._stock_seed()
        before = dict(live)
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon_rw(live)):
            self.assertEqual(self.s._apply_model_defaults("reavon_ubrx200"), [])
            self.assertEqual(self.s._apply_model_defaults("magnetar_udp900"), [])
        self.assertEqual(live, before)

        # No-op avoidance: settings already equal the model bundle -> no writes.
        # Enum keys are stored as their index ("0"), matching the encoded form.
        matched = {
            "oppo_start_commands": "#EJT\n#PLA",
            "oppo_stop_commands": "#STP",
            "oppo_start_mode": "0",
            "oppo_http_activate": "false",
            "oppo_http_payload_mode": "0",
        }
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon_rw(matched)):
            self.assertEqual(self.s._apply_model_defaults("chinoppo_m9702"), [])

        # Returns the keys it actually changed.
        live2 = self._stock_seed()
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon_rw(live2)):
            written = self.s._apply_model_defaults("chinoppo_m9205")
        self.assertIn("oppo_stop_commands", written)
        self.assertIn("oppo_http_activate", written)

        # Safe when xbmcaddon is unavailable.
        with mock.patch.object(self.s, "xbmcaddon", None):
            self.assertEqual(self.s._apply_model_defaults("chinoppo_m9205"), [])

    def test_apply_model_defaults_decodes_enum_index_model(self):
        # Kodi's getSetting returns the enum INDEX, not the value string. Index 13
        # is chinoppo_m9205 -> the M9205 power bundle must apply (not stock).
        import settings_reader as sr

        self.assertEqual(sr.ENUM_VALUES["oppo_hardware_model"][13], "chinoppo_m9205")
        live = self._stock_seed()
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon_rw(live)):
            written = self.s._apply_model_defaults("13")  # index, as real Kodi sends
        self.assertIn("oppo_stop_commands", written)
        self.assertEqual(live["oppo_stop_commands"], "#STP\n#POF")  # M9205, not stock
        self.assertEqual(live["oppo_http_activate"], "false")

    def test_apply_model_defaults_writes_enum_values_as_index(self):
        # An enum bundle value ("tcp_commands"/"raw_path") must be written as its
        # INDEX string, since Kodi stores values=-style enums by index.
        live = self._stock_seed()
        live["oppo_start_mode"] = "1"  # http_api -> must be reset to tcp_commands "0"
        live["oppo_http_payload_mode"] = "1"  # json_payload -> reset to raw_path "0"
        with mock.patch.object(self.s, "xbmcaddon", _make_xbmcaddon_rw(live)):
            written = self.s._apply_model_defaults("chinoppo_m9205")
        self.assertEqual(live["oppo_start_mode"], "0")  # index, not "tcp_commands"
        self.assertEqual(live["oppo_http_payload_mode"], "0")
        self.assertIn("oppo_start_mode", written)


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
        lsep_idx = connection_block.index('type="lsep"')
        first_real_setting_idx = connection_block.index('id="oppo_ip"')
        self.assertLess(lsep_idx, first_real_setting_idx)

    def test_po_has_all_new_entries(self):
        path = os.path.join(ROOT, "resources", "language", "resource.language.en_gb", "strings.po")
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        for ctx in ("#30290", "#30291", "#30292", "#30293"):
            self.assertIn(f'msgctxt "{ctx}"', text)


if __name__ == "__main__":
    unittest.main()
