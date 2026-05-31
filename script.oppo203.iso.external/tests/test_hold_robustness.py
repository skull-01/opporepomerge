"""Robustness regressions for ``external_player.hold_playback``.

Exercised with local fakes only -- no real OPPO, network, or Kodi. Pins:

* **#112** -- a ``verbose_push`` connect failure routes to the real ``#QPL``
  poll and ends on idle, instead of silently falling through to the blind
  ``fixed_timeout`` sleep.
* **#115** -- ``manual_file`` is bounded by the ``fixed_timeout`` ceiling, so a
  stop file that never appears cannot pin Kodi forever.
* **#116** -- ``http_poll`` / ``tcp_qpl_poll`` end the hold after
  ``MAX_CONSECUTIVE_POLL_FAILURES`` unreachable polls instead of running to the
  full timeout when the player drops off the network.
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import resources.lib.kodi.external_player as ep


class FakeSettings(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self

    def get_bool(self, key, default=False):
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")


class HoldRobustnessTests(unittest.TestCase):
    def test_verbose_push_connect_failure_polls_qpl_not_fixed_timeout(self):
        # #112: the verbose-push client raises -> the hold must poll #QPL and end
        # on idle. Before the fix it fell through to the blind fixed_timeout
        # sleep and query_playback_status was never called.
        qpl = mock.Mock(return_value="STOP")
        with (
            mock.patch("oppo_tcp_client.OppoTcpClient", side_effect=RuntimeError("no client")),
            mock.patch.object(ep, "query_playback_status", qpl),
            mock.patch.object(ep.time, "sleep", lambda *_: None),
        ):
            ep.hold_playback(
                FakeSettings(
                    {
                        "hold_mode": "verbose_push",
                        "oppo_ip": "10.0.0.5",
                        "oppo_port": "23",
                        "qpl_poll_idle_confirmations": "1",
                        "qpl_poll_interval": "1",
                        "verbose_push_timeout_minutes": "1",
                    }
                )
            )
        self.assertTrue(qpl.called, "verbose_push fallback must poll #QPL")

    def test_manual_file_is_bounded_by_ceiling(self):
        # #115: with no stop file ever appearing, the hold returns at the
        # fixed_timeout ceiling. A fake clock is swapped in for the module's own
        # ``time`` reference (so logging's clock is untouched) and stepped past
        # the deadline, so the test does not actually wait.
        missing_stop = str(ROOT / "build" / "no-such-oppo203-stop-file")
        clock = mock.Mock()
        clock.time = mock.Mock(side_effect=[1000.0, 1000.0, 9000.0])
        clock.sleep = mock.Mock()
        with mock.patch.object(ep, "time", clock):
            ep.hold_playback(
                FakeSettings(
                    {
                        "hold_mode": "manual_file",
                        "manual_stop_file": missing_stop,
                        "fixed_timeout_minutes": "1",
                    }
                )
            )
        # Returned without raising or hanging -> the ceiling was honored.
        self.assertGreaterEqual(clock.time.call_count, 2)

    def test_tcp_qpl_poll_aborts_after_consecutive_failures(self):
        # #116: an unreachable OPPO (connect raises) ends the hold after
        # MAX_CONSECUTIVE_POLL_FAILURES polls, not at the 240-minute timeout.
        qpl = mock.Mock(side_effect=ConnectionRefusedError("refused"))
        with (
            mock.patch.object(ep, "query_playback_status", qpl),
            mock.patch.object(ep.time, "sleep", lambda *_: None),
        ):
            ep.hold_playback(
                FakeSettings(
                    {
                        "hold_mode": "tcp_qpl_poll",
                        "oppo_ip": "10.0.0.5",
                        "oppo_port": "23",
                        "qpl_poll_interval": "1",
                        "qpl_poll_timeout_minutes": "240",
                    }
                )
            )
        self.assertEqual(qpl.call_count, ep.MAX_CONSECUTIVE_POLL_FAILURES)

    def test_http_poll_aborts_after_consecutive_failures(self):
        # #116: same abort for the HTTP polling hold.
        info = mock.Mock(side_effect=OSError("unreachable"))
        with (
            mock.patch.object(ep, "get_playback_info", info),
            mock.patch.object(ep.time, "sleep", lambda *_: None),
        ):
            ep.hold_playback(
                FakeSettings(
                    {
                        "hold_mode": "http_poll",
                        "http_poll_interval": "1",
                        "http_poll_timeout_minutes": "240",
                    }
                )
            )
        self.assertEqual(info.call_count, ep.MAX_CONSECUTIVE_POLL_FAILURES)


if __name__ == "__main__":
    unittest.main()
