"""#117: the oppo203iso-active session sentinel self-heals.

A crash or power loss before ``fast_return`` runs leaves the sentinel behind,
which disabled all interception (``service.py``) and stuck the remote-key bridge
(``oppo_remote.py``). A sentinel file older than ``SESSION_MAX_AGE_SECONDS`` is
now treated as inactive. Covers the shared helper plus both delegating readers.
"""

import importlib
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import resources.lib.kodi.settings_reader as sr


class FakeSettings(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self


def _write_sentinel(directory, age_seconds):
    path = Path(directory, "oppo203iso-active")
    path.write_text(str(time.time()), encoding="utf-8")
    when = time.time() - age_seconds
    os.utime(path, (when, when))
    return path


class SessionStalenessTests(unittest.TestCase):
    def test_missing_sentinel_is_inactive(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertFalse(sr.session_is_active(td))

    def test_fresh_sentinel_is_active(self):
        with tempfile.TemporaryDirectory() as td:
            _write_sentinel(td, 5)
            self.assertTrue(sr.session_is_active(td))

    def test_stale_sentinel_is_inactive(self):
        with tempfile.TemporaryDirectory() as td:
            _write_sentinel(td, sr.SESSION_MAX_AGE_SECONDS + 60)
            self.assertFalse(sr.session_is_active(td))

    def test_service_reader_honors_staleness(self):
        import service

        with tempfile.TemporaryDirectory() as td:
            _write_sentinel(td, sr.SESSION_MAX_AGE_SECONDS + 60)
            self.assertFalse(service._session_is_active(FakeSettings({"addon_data_dir": td})))
            _write_sentinel(td, 5)
            self.assertTrue(service._session_is_active(FakeSettings({"addon_data_dir": td})))

    def test_remote_reader_honors_staleness(self):
        remote = importlib.import_module("resources.lib.oppo.oppo_remote")

        with tempfile.TemporaryDirectory() as td:
            _write_sentinel(td, sr.SESSION_MAX_AGE_SECONDS + 60)
            self.assertFalse(remote._session_is_active(FakeSettings({"addon_data_dir": td})))
            _write_sentinel(td, 5)
            self.assertTrue(remote._session_is_active(FakeSettings({"addon_data_dir": td})))


if __name__ == "__main__":
    unittest.main()
