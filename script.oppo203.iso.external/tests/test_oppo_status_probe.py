"""OPPO player-status probe (read-only #Q.. query battery + HTTP playinfo).

Covers oppo_control.probe_player_status (documented query battery, reply
classification incl. #QFN media-file-name case preservation, missing-host and
unreachable handling, the injectable HTTP playinfo field, and the default send
path against a loopback fake OPPO server), oppo_control.format_player_status_probe
rendering, and the installer.run_player_status_probe menu wiring + dispatch.
"""

import contextlib
import importlib
import os
import socket
import sys
import unittest

import oppo_control

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "resources", "lib")
STUBS = os.path.join(ROOT, "tests", "_stubs")
ADDON_ID = "script.oppo203.iso.external"

LABELS = [label for label, _cmd in oppo_control.PROBE_QUERY_COMMANDS]


def _fake_send(responses):
    def send(host, port, commands, timeout=3.0, delay=0):
        return list(responses)

    return send


class TRecvLine(unittest.TestCase):
    """M2: _recv_line reassembles a reply split across recv() segments."""

    class _Sock:
        def __init__(self, chunks):
            self._chunks = list(chunks)

        def recv(self, _n):
            if not self._chunks:
                raise socket.timeout()
            return self._chunks.pop(0)

    def test_reassembles_split_response(self):
        sock = self._Sock([b"@QP", b"W OK ON\r"])
        self.assertEqual(oppo_control._recv_line(sock), "@QPW OK ON")

    def test_returns_first_line_only(self):
        sock = self._Sock([b"@A OK\r@B OK\r"])
        self.assertEqual(oppo_control._recv_line(sock), "@A OK")

    def test_timeout_returns_accumulated(self):
        sock = self._Sock([b"partial"])  # next recv() raises socket.timeout
        self.assertEqual(oppo_control._recv_line(sock), "partial")

    def test_close_returns_accumulated(self):
        sock = self._Sock([b""])  # immediate close
        self.assertEqual(oppo_control._recv_line(sock), "")


class TProbeClassification(unittest.TestCase):
    def test_all_documented_fields_present_and_ordered(self):
        responses = ["OK 0"] * len(oppo_control.PROBE_QUERY_COMMANDS)
        result = oppo_control.probe_player_status(
            {"oppo_ip": "192.0.2.5"}, send=_fake_send(responses), http=lambda s: "{}"
        )
        self.assertTrue(result["ok"])
        self.assertEqual(list(result["fields"].keys()), LABELS)
        self.assertIn("media_file_name", result["fields"])

    def test_reply_forms_are_classified(self):
        responses = ["OK 0"] * len(oppo_control.PROBE_QUERY_COMMANDS)
        responses[0] = "@QPW OK ON"  # verbose OK
        responses[1] = "OK PLAY"  # legacy OK
        responses[2] = "@QFN OK Movie 4K U*.iso"  # #QFN, mixed case
        responses[3] = "@QFT ER INVALID"  # ER reason
        responses[4] = ""  # no response
        responses[5] = "@QCH"  # verbose, no body -> unknown
        responses[6] = "GARBAGE"  # unknown
        result = oppo_control.probe_player_status(
            {"oppo_ip": "192.0.2.5"}, send=_fake_send(responses), http=lambda s: "{}"
        )
        f = result["fields"]
        self.assertTrue(f["power"]["ok"])
        self.assertEqual(f["power"]["value"], "ON")
        self.assertEqual(f["playback_status"]["value"], "PLAY")
        self.assertEqual(f["media_file_name"]["value"], "Movie 4K U*.iso")
        self.assertTrue(f["media_file_name"]["ok"])
        self.assertEqual(f["media_file_format"]["status"], "error")
        self.assertFalse(f["media_file_format"]["ok"])
        self.assertEqual(f["media_file_format"]["value"], "INVALID")
        self.assertEqual(f["track_title"]["status"], "no_response")
        self.assertEqual(f["chapter"]["status"], "unknown")
        self.assertEqual(f["track_elapsed"]["status"], "unknown")
        self.assertEqual(f["track_elapsed"]["value"], "GARBAGE")

    def test_qfn_value_is_not_uppercased(self):
        responses = [""] * len(oppo_control.PROBE_QUERY_COMMANDS)
        responses[2] = "@QFN OK Rocky Mou*.wav"
        result = oppo_control.probe_player_status(
            {"oppo_ip": "192.0.2.5"}, send=_fake_send(responses), http=lambda s: "{}"
        )
        self.assertEqual(result["fields"]["media_file_name"]["value"], "Rocky Mou*.wav")


class TProbeErrors(unittest.TestCase):
    def test_missing_oppo_ip_returns_error(self):
        result = oppo_control.probe_player_status({}, send=_fake_send([]), http=lambda s: "{}")
        self.assertFalse(result["ok"])
        self.assertIn("oppo_ip", str(result["error"]))
        self.assertEqual(result["fields"], {})

    def test_unreachable_tcp_is_nonfatal(self):
        def boom(*a, **k):
            raise OSError("no route to host")

        result = oppo_control.probe_player_status(
            {"oppo_ip": "192.0.2.5"}, send=boom, http=lambda s: "{}"
        )
        self.assertFalse(result["ok"])
        self.assertIn("unreachable", str(result["error"]))

    def test_short_response_list_fills_no_response(self):
        result = oppo_control.probe_player_status(
            {"oppo_ip": "192.0.2.5"}, send=_fake_send([]), http=lambda s: "{}"
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["fields"]["power"]["status"], "no_response")


class TProbeHttp(unittest.TestCase):
    def test_injected_http_payload_is_captured(self):
        responses = ["OK 0"] * len(oppo_control.PROBE_QUERY_COMMANDS)
        result = oppo_control.probe_player_status(
            {"oppo_ip": "192.0.2.5"},
            send=_fake_send(responses),
            http=lambda s: '{"e_play_status":0}',
        )
        self.assertEqual(result["http_getmovieplayinfo_raw"], '{"e_play_status":0}')

    def test_http_error_is_captured_not_raised(self):
        responses = ["OK 0"] * len(oppo_control.PROBE_QUERY_COMMANDS)

        def boom(_s):
            raise RuntimeError("refused")

        result = oppo_control.probe_player_status(
            {"oppo_ip": "192.0.2.5"}, send=_fake_send(responses), http=boom
        )
        self.assertTrue(str(result["http_getmovieplayinfo_raw"]).startswith("<error:"))


class TProbeIntegration(unittest.TestCase):
    def test_default_send_against_fake_server(self):
        from tests._support.fake_oppo_server import FakeOppoServer

        responses = {
            "#QPW": "@QPW OK ON",
            "#QPL": "@QPL OK PLAY",
            "#QFN": "@QFN OK Movie 4K U*.iso",
            "#QFT": "@QFT OK ISO",
        }
        with FakeOppoServer(responses=responses) as server:
            settings = {
                "oppo_ip": server.host,
                "oppo_port": str(server.port),
                "oppo_socket_timeout": "1.0",
                "oppo_http_port": "1",  # nothing listening -> fast refuse
            }
            result = oppo_control.probe_player_status(settings)
        self.assertTrue(result["ok"])
        self.assertEqual(result["fields"]["playback_status"]["value"], "PLAY")
        self.assertEqual(result["fields"]["media_file_name"]["value"], "Movie 4K U*.iso")
        # default HTTP path ran and failed fast -> captured, never raised
        self.assertTrue(str(result["http_getmovieplayinfo_raw"]).startswith("<error:"))


class TFormatReport(unittest.TestCase):
    def test_error_result_renders_error_line(self):
        text = oppo_control.format_player_status_probe(
            {
                "host": "1.2.3.4",
                "port": 23,
                "ok": False,
                "error": "oppo_ip is not set",
                "fields": {},
            }
        )
        self.assertIn("host: 1.2.3.4:23", text)
        self.assertIn("error: oppo_ip is not set", text)

    def test_success_with_http_renders_fields_and_payload(self):
        result = {
            "host": "1.2.3.4",
            "port": 23,
            "ok": True,
            "error": None,
            "fields": {
                "playback_status": {
                    "command": "#QPL",
                    "status": "ok",
                    "value": "PLAY",
                    "ok": True,
                },
                "media_file_name": {
                    "command": "#QFN",
                    "status": "ok",
                    "value": "Movie 4K U*.iso",
                    "ok": True,
                },
            },
            "http_getmovieplayinfo_raw": '{"e_play_status":0}',
        }
        text = oppo_control.format_player_status_probe(result)
        self.assertIn("#QFN", text)
        self.assertIn("Movie 4K U*.iso", text)
        self.assertIn("HTTP /getmovieplayinfo", text)
        self.assertIn('{"e_play_status":0}', text)

    def test_success_without_http_omits_payload_section(self):
        result = {
            "host": "1.2.3.4",
            "port": 23,
            "ok": True,
            "error": None,
            "fields": {"power": {"command": "#QPW", "status": "ok", "value": "ON", "ok": True}},
        }
        text = oppo_control.format_player_status_probe(result)
        self.assertNotIn("HTTP /getmovieplayinfo", text)


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
            "oppo_control",
            "resources.lib.oppo.oppo_control",
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


class TProbeMenu(unittest.TestCase):
    def test_main_menu_lists_probe_entry_and_dispatches(self):
        with kodi_stubs():
            import xbmcaddon
            import xbmcgui

            xbmcaddon.reset(
                settings={"architecture_choice_made": "true"},
                info={"path": ROOT, "id": ADDON_ID},
            )
            installer = importlib.import_module("resources.lib.installer")
            xbmcgui.reset()
            xbmcgui.push_select(13)  # "Probe OPPO player status (diagnostic)"
            installer.main()

            calls = xbmcgui.calls()
            selects = [c for c in calls if c[0] == "select"]
            self.assertTrue(any("Probe OPPO player status" in opt for opt in selects[0][2]))
            textviewers = [c for c in calls if c[0] == "textviewer"]
            self.assertTrue(any(c[1] == "OPPO player status probe" for c in textviewers))


if __name__ == "__main__":
    unittest.main()
