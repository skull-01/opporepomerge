"""#111: the diagnostics-dashboard HTTP probe targets the OPPO HTTP API port.

The ``_http`` probe in ``default.run_diagnostics_dashboard`` hardcoded port 80,
but the OPPO HTTP control API runs on ``oppo_http_port`` (default 436). These
confirm the probe now connects to 436 by default (and to an explicit override),
never 80. ``socket.socket`` is faked so no real network call is made.
"""

import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
STUBS = ROOT / "tests" / "_stubs"
for _path in (str(STUBS), str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import default


class DiagProbePortTests(unittest.TestCase):
    def _captured_ports(self, **kwargs):
        connects = []

        class _RecordingSocket:
            def __init__(self, *args, **kwargs):
                pass

            def settimeout(self, timeout):
                pass

            def connect(self, address):
                connects.append(address)

            def sendall(self, data):
                pass

            def recv(self, size):
                return b"ok"

            def setsockopt(self, *args):
                pass

            def sendto(self, *args):
                pass

            def close(self):
                pass

        with (
            tempfile.TemporaryDirectory() as td,
            mock.patch.object(socket, "socket", _RecordingSocket),
        ):
            default.run_diagnostics_dashboard(
                addon_data_dir=td, host="10.0.0.5", mac="00:11:22:33:44:55", **kwargs
            )
        return [addr[1] for addr in connects if isinstance(addr, tuple)]

    def test_http_probe_defaults_to_436_not_80(self):
        ports = self._captured_ports()
        self.assertIn(436, ports)
        self.assertNotIn(80, ports)

    def test_http_probe_honors_explicit_port(self):
        ports = self._captured_ports(http_port=8060)
        self.assertIn(8060, ports)
        self.assertNotIn(80, ports)


if __name__ == "__main__":
    unittest.main()
