"""Ready-to-transfer playercorefactory.xml + keymap file generation.

The installer menu writes complete, drop-in files to an addon-data 'generated'
folder (mirroring Kodi's userdata layout) instead of showing snippets the user
must merge by hand. These tests cover the new builders and the silent/announced
writers using the local Kodi stubs only -- no real Kodi, OPPO, or filesystem
target.
"""

from __future__ import annotations

import importlib
import os
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "tests" / "_stubs"
LIB = ROOT / "resources" / "lib"
for path in (str(STUBS), str(LIB), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)


class TestTransferFileGeneration(unittest.TestCase):
    def setUp(self):
        # Other test files swap the xbmcaddon/xbmcgui stub module identity, so
        # re-import installer here and drive settings through installer.ADDON /
        # installer.xbmcgui directly -- the exact stubs installer reads from.
        sys.modules.pop("installer", None)
        self.installer = importlib.import_module("installer")
        self.xbmcgui = self.installer.xbmcgui
        self.xbmcgui.reset()
        for key, value in {
            "python_path": "/usr/bin/python3",
            "include_disc_folder_rules": "true",
            "playback_architecture": "external_player",
        }.items():
            self.installer.ADDON.setSetting(key, value)

    # --- builders -----------------------------------------------------------
    def test_playercorefactory_file_is_a_clean_drop_in_document(self):
        xml = self.installer.build_playercorefactory_file_xml()
        ET.fromstring(xml)  # well-formed
        self.assertIn("Oppo203ISO", xml)
        self.assertIn("copy this file", xml)
        # No "merge into your existing element" instructions in a drop-in file.
        self.assertNotIn("Add this inside", xml)

    def test_playercorefactory_file_notes_optional_in_service_mode(self):
        self.installer.ADDON.setSetting("playback_architecture", "service_interception")
        xml = self.installer.build_playercorefactory_file_xml()
        ET.fromstring(xml)
        self.assertIn("service_interception", xml)

    def test_keymap_file_is_clean_and_keeps_bindings(self):
        xml = self.installer.build_keymap_file_xml()
        ET.fromstring(xml)
        self.assertIn("RunScript", xml)
        self.assertNotIn("Manual merge instructions", xml)
        # The snippet variant still carries its manual-merge header for back-compat.
        self.assertIn("Manual merge instructions", self.installer.build_keymap_snippet_xml())

    def test_generated_paths_mirror_userdata_layout(self):
        generated_dir, pcf_path, keymap_path = self.installer._generated_paths()
        self.assertTrue(pcf_path.endswith(os.path.join("generated", "playercorefactory.xml")))
        self.assertTrue(
            keymap_path.endswith(os.path.join("generated", "keymaps", "oppo203iso.xml"))
        )
        self.assertTrue(pcf_path.startswith(generated_dir))

    # --- writers ------------------------------------------------------------
    def test_write_playercorefactory_external_announces_naming_and_path(self):
        path = self.installer.write_playercorefactory_file(announce=True)
        self.assertTrue(os.path.exists(path))
        headings = [c[1] for c in self.xbmcgui.calls() if c[0] == "ok"]
        self.assertIn("4K XML naming requirement", headings)
        self.assertTrue(any("written to" in c[2] for c in self.xbmcgui.calls() if c[0] == "ok"))

    def test_write_playercorefactory_service_mode_skips_naming_warning(self):
        self.installer.ADDON.setSetting("playback_architecture", "service_interception")
        self.installer.write_playercorefactory_file(announce=True)
        headings = [c[1] for c in self.xbmcgui.calls() if c[0] == "ok"]
        self.assertNotIn("4K XML naming requirement", headings)

    def test_write_keymap_file_announces_path(self):
        path = self.installer.write_keymap_file(announce=True)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(
            any("userdata/keymaps" in c[2] for c in self.xbmcgui.calls() if c[0] == "ok")
        )

    def test_generate_transfer_files_silent_writes_both(self):
        paths = self.installer.generate_transfer_files(announce=False)
        self.assertEqual(set(paths), {"playercorefactory", "keymap"})
        self.assertTrue(all(os.path.exists(p) for p in paths.values()))
        self.assertEqual(self.xbmcgui.calls(), [])

    def test_generate_transfer_files_can_select_subset(self):
        paths = self.installer.generate_transfer_files(
            include_playercorefactory=False, include_keymap=True, announce=False
        )
        self.assertEqual(set(paths), {"keymap"})


if __name__ == "__main__":
    unittest.main()
