"""#114: the shipped default ``hold_mode`` detects stop.

The out-of-box default was ``fixed_timeout`` -- a blind 180-minute sleep with
no stop detection (the configurator does not write ``hold_mode``, so this
default governs every unconfigured install). It is now ``tcp_qpl_poll``. These
pin the reader default and its consistency with the ``settings.xml`` enum
default index, so the two cannot drift apart.
"""

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import resources.lib.kodi.settings_reader as sr


class HoldDefaultTests(unittest.TestCase):
    def test_default_hold_mode_detects_stop(self):
        self.assertEqual(sr.DEFAULTS["hold_mode"], "tcp_qpl_poll")

    def test_settings_xml_default_matches_reader_default(self):
        xml_path = ROOT / "resources" / "settings.xml"
        tree = ET.parse(str(xml_path))
        node = next(s for s in tree.iter("setting") if s.get("id") == "hold_mode")
        values = node.get("values").split("|")
        index = int(node.get("default"))
        self.assertEqual(values, sr.ENUM_VALUES["hold_mode"])
        self.assertEqual(values[index], sr.DEFAULTS["hold_mode"])


if __name__ == "__main__":
    unittest.main()
