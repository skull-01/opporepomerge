"""v2.0 Build 3 Kodi-stub tests.

These tests exercise the local tests/_stubs modules without making those
stubs global for the whole suite. That keeps legacy "no Kodi installed"
checks intact while giving the project a concrete staged path for testing
Kodi-bound code outside Kodi.
"""
import contextlib
import importlib
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUBS = os.path.join(ROOT, "tests", "_stubs")
KODI_MODULES = ("xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs", "xbmcplugin", "xbmcdrm")
TARGET_MODULES = ("default", "service", "resources.lib.installer")


@contextlib.contextmanager
def kodi_stub_context(extra_targets=()):
    from tests._support.lib_buckets import with_canonical
    old_path = list(sys.path)
    names = with_canonical(set(KODI_MODULES) | set(TARGET_MODULES) | set(extra_targets))
    saved = {name: sys.modules.get(name) for name in names}
    try:
        sys.path.insert(0, STUBS)
        sys.path.insert(0, ROOT)
        sys.path.insert(0, os.path.join(ROOT, "resources", "lib"))
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


class TKodiStubModules(unittest.TestCase):
    def test_all_stub_modules_import(self):
        with kodi_stub_context():
            for name in KODI_MODULES:
                module = importlib.import_module(name)
                self.assertIsNotNone(module)

    def test_xbmc_monitor_player_and_log_are_programmable(self):
        with kodi_stub_context():
            import xbmc
            xbmc.reset()
            xbmc.setInfoLabel("System.BuildVersion", "21.0 Omega")
            self.assertEqual(xbmc.getInfoLabel("System.BuildVersion"), "21.0 Omega")
            xbmc.log("hello", xbmc.LOGWARNING)
            self.assertEqual(xbmc.get_logs(), [("hello", xbmc.LOGWARNING)])
            xbmc.Player.configure(playing=True, playing_file="/media/movie.iso")
            player = xbmc.Player()
            self.assertTrue(player.isPlaying())
            self.assertEqual(player.getPlayingFile(), "/media/movie.iso")
            player.stop()
            self.assertFalse(player.isPlaying())
            monitor = xbmc.Monitor()
            self.assertFalse(monitor.abortRequested())
            monitor.requestAbort()
            self.assertTrue(monitor.abortRequested())

    def test_xbmcaddon_settings_and_info_are_programmable(self):
        with kodi_stub_context():
            import xbmcaddon
            xbmcaddon.reset(
                settings={"oppo_ip": "192.0.2.10"},
                info={"profile": "/tmp/profile", "version": "2.0.0.3"},
                localized={31000: "Welcome"},
            )
            addon = xbmcaddon.Addon("script.oppo203.iso.external")
            self.assertEqual(addon.getSetting("oppo_ip"), "192.0.2.10")
            addon.setSetting("oppo_port", 23)
            self.assertEqual(addon.getSetting("oppo_port"), "23")
            self.assertEqual(addon.getAddonInfo("version"), "2.0.0.3")
            self.assertEqual(addon.getLocalizedString(31000), "Welcome")

    def test_xbmcgui_dialog_records_calls(self):
        with kodi_stub_context():
            import xbmcgui
            xbmcgui.reset()
            xbmcgui.push_yesno(True)
            xbmcgui.push_select(2)
            xbmcgui.push_input("typed")
            dialog = xbmcgui.Dialog()
            self.assertTrue(dialog.yesno("Question", "Proceed?"))
            self.assertEqual(dialog.select("Pick", ["a", "b", "c"]), 2)
            self.assertEqual(dialog.input("Name", "default"), "typed")
            dialog.ok("Done", "Saved")
            methods = [call[0] for call in xbmcgui.calls()]
            self.assertEqual(methods, ["yesno", "select", "input", "ok"])

    def test_xbmcvfs_file_and_path_helpers(self):
        with kodi_stub_context():
            import xbmcvfs
            path = xbmcvfs.translatePath("special://profile/addon_data/demo/file.txt")
            self.assertTrue(path.startswith("/tmp/kodi-profile"))
            with xbmcvfs.File(path, "w") as handle:
                handle.write("payload")
            self.assertTrue(xbmcvfs.exists(path))
            with xbmcvfs.File(path, "r") as handle:
                self.assertEqual(handle.read(), "payload")

    def test_installer_imports_with_local_kodi_stubs(self):
        with kodi_stub_context():
            import xbmcaddon
            xbmcaddon.reset(info={"path": ROOT, "profile": "/tmp/profile"})
            installer = importlib.import_module("resources.lib.installer")
            self.assertEqual(installer.ADDON_ID, "script.oppo203.iso.external")
            xml = installer.build_external_player_xml()
            self.assertIn("Oppo203ISO", xml)
            self.assertIn("external_player.py", xml)

    def test_default_and_service_import_with_local_kodi_stubs(self):
        with kodi_stub_context():
            import xbmc
            xbmc.reset()
            xbmc.setInfoLabel("System.BuildVersion", "21.0 (21.0.0)")
            default = importlib.import_module("default")
            service = importlib.import_module("service")
            self.assertTrue(callable(default.main))
            self.assertEqual(service._kodi_major_version(), 21)
            self.assertTrue(service._is_omega_or_newer())
