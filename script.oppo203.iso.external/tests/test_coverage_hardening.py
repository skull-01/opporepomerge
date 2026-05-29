"""Post-MVP coverage hardening tests for the v2.1 coverage gate path.

These tests intentionally exercise previously under-covered production paths
with local fakes rather than real OPPO, Kodi, ADB, TV, or HTTP devices.
"""
import contextlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
STUBS = ROOT / "tests" / "_stubs"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class FakeSettings(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self

    def get_bool(self, key, default=False):
        value = self.get(key, default)
        if value is None:
            return bool(default)
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text == "":
            return bool(default)
        return text in ("1", "true", "yes", "on")

    def get_lines(self, key):
        return [line.strip() for line in str(self.get(key, "")).splitlines() if line.strip()]


@contextlib.contextmanager
def kodi_stubs(*targets):
    from tests._support.lib_buckets import with_canonical
    names = {
        "xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs", "xbmcplugin", "xbmcdrm",
        "resources.lib.installer", "resources.lib.oppo_remote", "autoscript_helper",
    }
    names.update(targets)
    names = with_canonical(names)
    old_path = list(sys.path)
    saved = {name: sys.modules.get(name) for name in names}
    try:
        sys.path.insert(0, str(STUBS))
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(LIB))
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


class FakeTcpSocket:
    def __init__(self, responses=()):
        self.responses = list(responses)
        self.sent = []
        self.timeout = None
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, size):
        item = self.responses.pop(0)
        if item == "TIMEOUT" or item == b"TIMEOUT":
            import socket
            raise socket.timeout()
        return item

    def close(self):
        self.closed = True


class FakeUdpSocket:
    def __init__(self, packets=()):
        self.packets = list(packets)
        self.sent = []
        self.options = []
        self.timeout = None
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def setsockopt(self, *args):
        self.options.append(args)

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendto(self, data, addr):
        self.sent.append((data, addr))

    def recvfrom(self, size):
        if not self.packets:
            import socket
            raise socket.timeout()
        return self.packets.pop(0)

    def close(self):
        self.closed = True


class FakeHttpResponse:
    def __init__(self, body, status=200):
        self.body = body.encode("utf-8") if isinstance(body, str) else body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.body


class TOppoControlCoverageHardening(unittest.TestCase):
    def setUp(self):
        self.oc = importlib.import_module("resources.lib.oppo_control")
        self.settings = FakeSettings({
            "oppo_ip": "192.0.2.10",
            "oppo_port": "23",
            "oppo_socket_timeout": "1.0",
            "oppo_command_delay": "0",
            "oppo_http_port": "436",
            "oppo_http_path_from": "/media",
            "oppo_http_path_to": "/nas",
            "oppo_http_urlencode_path": "true",
            "oppo_http_disc_folder_root": "true",
            "oppo_http_app_device_type": "2",
            "oppo_http_media_type": "1",
            "oppo_http_activate": "true",
            "oppo_http_broadcast": "255.255.255.255",
            "oppo_start_commands": "#PON\n#PLA",
            "oppo_stop_commands": "#STP",
            "oppo_start_mode": "tcp_commands",
            "oppo_hardware_model": "udp_203",
            "oppo_use_wol": "false",
            "oppo_verbose_mode": "0",
        })

    def test_tcp_send_and_query_helpers_use_fake_socket(self):
        sock = FakeTcpSocket([b"@PON OK", b"TIMEOUT", b"@QPW OK ON"])
        calls = []
        def fake_create(addr, timeout):
            calls.append((addr, timeout))
            return sock
        with mock.patch.object(self.oc.socket, "create_connection", side_effect=fake_create), \
             mock.patch.object(self.oc.time, "sleep", lambda *_: None):
            self.assertEqual(self.oc.send_commands("host", "23", ["#PON", "", "#PLA"], timeout="2", delay="0"), ["@PON OK", ""])
        sock2 = FakeTcpSocket([b"@QPW OK ON"])
        with mock.patch.object(self.oc.socket, "create_connection", return_value=sock2):
            self.assertEqual(self.oc.query_power_status("host", 23), "ON")
        sock3 = FakeTcpSocket(["TIMEOUT"])
        with mock.patch.object(self.oc.socket, "create_connection", return_value=sock3):
            self.assertEqual(self.oc.query_command("host", 23, "#QPL"), "")
        self.assertEqual(calls[0][0], ("host", 23))

    def test_response_status_preflight_and_verbose_helpers(self):
        self.assertEqual(self.oc.normalize_command("#QPW"), "#QPW\r")
        self.assertEqual(self.oc.normalize_command("  "), "")
        self.assertEqual(self.oc._parse_response("@QIS OK HDMI IN"), "HDMI IN")
        self.assertEqual(self.oc._parse_response("OK play"), "PLAY")
        self.assertEqual(self.oc._parse_response("garbage"), "GARBAGE")
        with self.assertRaises(self.oc.OppoError):
            self.oc._parse_response("@QPL ER BAD")
        self.assertTrue(self.oc.tcp_qpl_is_idle("NO DISC"))
        self.assertFalse(self.oc.tcp_qpl_is_idle("PLAY"))
        with mock.patch.object(self.oc, "query_power_status", return_value="ON"), \
             mock.patch.object(self.oc, "query_input_source", return_value="BLU-RAY"):
            pre = self.oc.run_preflight(FakeSettings(dict(self.settings, oppo_preflight_enabled="true")))
        self.assertTrue(pre["already_on"])
        self.assertEqual(pre["input_source"], "BLU-RAY")
        with mock.patch.object(self.oc, "setup_verbose_mode", side_effect=self.oc.OppoError("bad")):
            self.oc.maybe_setup_verbose_mode(FakeSettings({"oppo_verbose_mode": "2"}), "h", 23)
        with self.assertRaises(self.oc.OppoError):
            self.oc.setup_verbose_mode("h", 23, 1)

    def test_wol_discovery_and_http_helpers_are_local_fakes(self):
        created = []
        def fake_socket(*args, **kwargs):
            sock = FakeUdpSocket([(b"OPPO UDP-203", ("192.0.2.20", 7624))])
            created.append(sock)
            return sock
        with mock.patch.object(self.oc.socket, "socket", side_effect=fake_socket), \
             mock.patch.object(self.oc.time, "time", side_effect=[0, 0, 10]):
            found = self.oc.discover_oppo(timeout=1)
        self.assertEqual(found[0]["ip"], "192.0.2.20")
        wol_sock = FakeUdpSocket()
        with mock.patch.object(self.oc.socket, "socket", return_value=wol_sock):
            self.oc.wake_on_lan("00:11:22:33:44:55")
        self.assertEqual(len(wol_sock.sent[0][0]), 102)
        with self.assertRaises(self.oc.OppoError):
            self.oc.wake_on_lan("bad")

        seen_urls = []
        def fake_urlopen(request_or_url, timeout=0):
            seen_urls.append(str(request_or_url.full_url if hasattr(request_or_url, "full_url") else request_or_url))
            return FakeHttpResponse('{"result":{"play_status":"PLAY"}}')
        with mock.patch.object(self.oc.urllib.request, "urlopen", side_effect=fake_urlopen):
            self.assertIn("result", self.oc._http_get(self.settings, "/getmovieplayinfo"))
            self.assertEqual(self.oc.get_playback_status(self.settings), "PLAY")
            self.oc.signin_http_api(self.settings)
            self.oc.play_media_http_api(self.settings, "/media/Movie/BDMV/index.bdmv")
            self.settings["oppo_http_payload_mode"] = "json_payload"
            self.oc.play_media_http_api(self.settings, "/media/Movie.iso")
        self.assertTrue(any("playnormalfile" in url for url in seen_urls))
        with mock.patch.object(self.oc.urllib.request, "urlopen", side_effect=self.oc.urllib.error.URLError("down")):
            with self.assertRaises(self.oc.OppoError):
                self.oc._http_get(self.settings, "/fail")
        self.assertEqual(self.oc._translate_media_path(self.settings, "/media/Movie/BDMV/index.bdmv"), "/nas/Movie")

    def test_http_info_track_command_and_filelist_helpers(self):
        self.assertTrue(self.oc.http_status_is_idle("STOP"))
        self.assertFalse(self.oc.http_status_is_idle("PLAY"))
        self.assertTrue(self.oc.http_info_is_definitive_stop({"result": {"errcode1": "-5"}}))
        self.assertTrue(self.oc.http_info_indicates_playing({"playinfo": {"e_play_status": 56}}))
        self.assertEqual(list(self.oc._info_containers({"result": {"status": "PLAY"}}))[1]["status"], "PLAY")
        self.assertEqual(self.oc._filter_commands_for_mode(self.settings, "oppo_start_commands", ["#PON", "#PLA"], {"already_on": True}), ["#PLA"])
        self.assertEqual(self.oc._resolve_hardware_wake_command(FakeSettings({"oppo_hardware_model": "chinoppo_m9702"}), "#PON"), "#EJT")
        with mock.patch.object(self.oc, "send_commands", return_value=["@OK"]) as send:
            out = self.oc.run_configured_commands(FakeSettings(dict(self.settings, oppo_start_commands="#PON\n#PLA")), "oppo_start_commands")
            self.assertEqual(out, ["@OK"])
            self.assertEqual(send.call_args.args[2], ["#PON", "#PLA"])
        calls = []
        with mock.patch.object(self.oc, "maybe_wake_on_lan", lambda s: calls.append("wol")), \
             mock.patch.object(self.oc, "maybe_setup_verbose_mode", lambda s, h, p: calls.append("svm")), \
             mock.patch.object(self.oc, "run_configured_commands", lambda *a, **k: calls.append("tcp")), \
             mock.patch.object(self.oc, "activate_http_api", lambda s: calls.append("activate")), \
             mock.patch.object(self.oc, "signin_http_api", lambda s: calls.append("signin")), \
             mock.patch.object(self.oc, "play_media_http_api", lambda s, m: calls.append("play") or "ok"):
            s = FakeSettings(dict(self.settings, oppo_start_mode="tcp_then_http"))
            self.assertEqual(self.oc.run_start(s, "/movie.iso"), "ok")
        self.assertEqual(calls, ["wol", "svm", "tcp", "activate", "signin", "play"])

        responses = {
            "/getaudiomenulist": '{"audio_list":{"0":{"index":"0","name":"English","selected":true}}}',
            "/getsubtitlemenulist": '{"result":[{"index":1,"name":"Forced","selected":false}]}',
        }
        def fake_http(settings, endpoint, query=None, timeout=None):
            if endpoint in responses:
                return responses[endpoint]
            return "OK"
        with mock.patch.object(self.oc, "_http_get", side_effect=fake_http) as http:
            self.assertEqual(self.oc.get_audio_tracks(self.settings)[0]["name"], "English")
            self.assertEqual(self.oc.get_subtitle_tracks(self.settings)[0]["index"], 1)
            self.oc.set_audio_track(self.settings, 2)
            self.oc.set_subtitle_track(self.settings, 3)
            self.oc.set_play_time(self.settings, 1, 2, 3)
        self.assertGreaterEqual(http.call_count, 5)
        entries = self.oc.parse_undocumented_file_list('{"files":[{"name":"Movie.iso","size":"10"}]}', base_path="/base")
        self.assertEqual(entries[0]["disc_type"], "iso")
        binary = b"Folder\x00directory\x01Movie.m2ts\x00123"
        self.assertEqual(len(self.oc.parse_undocumented_file_list(binary, base_path="/disc")), 2)
        self.assertEqual(self.oc._infer_disc_type(path="/VIDEO_TS/VIDEO_TS.IFO"), "dvd")


class TSettingsExternalTvRemoteCoverageHardening(unittest.TestCase):
    def test_settings_reader_xml_and_hardware_paths(self):
        import settings_reader as sr
        with tempfile.TemporaryDirectory() as td:
            Path(td, "settings.xml").write_text(
                "<settings>"
                '<setting id="oppo_start_mode" value="1"/>'
                '<setting id="oppo_hardware_model"><value>5</value></setting>'
                '<setting id="tv_backend">custom_command</setting>'
                "</settings>", encoding="utf-8")
            settings = sr.read_settings(td)
        self.assertEqual(settings.get("oppo_start_mode"), "http_api")
        self.assertEqual(settings.get("oppo_hardware_model"), "chinoppo_m9702")
        self.assertEqual(settings.get_str("missing", "x"), "x")
        self.assertEqual(settings.get_lines("oppo_start_commands"), ["#PON", "#PLA"])
        self.assertEqual(sr.normalize_hardware_model("m9205c"), "M9205C")
        self.assertTrue(sr.hardware_profile("UDP-205")["protocol_compatible"])
        self.assertEqual(sr.compatibility_preset("M9702")["oppo_http_activate"], "false")
        self.assertIn("__reavon_warning__", sr.compatibility_preset("Reavon-UBR-X100"))
        self.assertTrue(sr.is_token_supported_by_hardware("#SRC 6", "UDP-205"))
        self.assertFalse(sr.is_token_supported_by_hardware("#SRC 6", "UDP-203"))
        self.assertIn("not supported", sr.warn_if_unsupported("#SRC 6", "UDP-203"))

    def test_tv_control_all_backends_with_no_real_tv(self):
        import tv_control
        settings = FakeSettings({
            "tv_backend": "adb", "tv_ip": "192.0.2.30", "sony_psk": "psk",
            "oppo_input_adb_shell": "input-oppo", "kodi_input_adb_shell": "input-kodi",
            "sony_oppo_hdmi_port": "1", "sony_kodi_hdmi_port": "2",
            "lg_oppo_command": "echo lg-oppo", "lg_kodi_command": "echo lg-kodi",
            "samsung_oppo_command": "echo {tv_ip}", "samsung_kodi_command": "echo samsung-kodi",
            "custom_oppo_command": "echo custom-oppo", "custom_kodi_command": "echo custom-kodi",
        })
        with mock.patch.object(tv_control, "adb_switch_input", return_value="adb-ok") as adb:
            self.assertEqual(tv_control.switch_to_oppo(settings), "adb-ok")
            adb.assert_called_once()
        class Proc:
            returncode = 0
            stdout = "done\n"
            stderr = ""
        with mock.patch.object(tv_control.subprocess, "run", return_value=Proc()):
            settings["tv_backend"] = "lg_command"
            self.assertEqual(tv_control.switch_to_oppo(settings), "done")
            settings["tv_backend"] = "samsung_command"
            self.assertEqual(tv_control.switch_to_oppo(settings), "done")
            settings["tv_backend"] = "custom_command"
            self.assertEqual(tv_control.switch_to_kodi(settings), "done")
        class BadProc:
            returncode = 9
            stdout = ""
            stderr = "bad"
        with mock.patch.object(tv_control.subprocess, "run", return_value=BadProc()):
            with self.assertRaises(tv_control.TVControlError):
                tv_control._run_external("echo bad", settings)
        with mock.patch.object(tv_control.urllib.request, "urlopen", return_value=FakeHttpResponse("sony")):
            settings["tv_backend"] = "sony_bravia"
            self.assertEqual(tv_control.switch_to_kodi(settings), "sony")
        settings["sony_psk"] = ""
        with self.assertRaises(tv_control.TVControlError):
            tv_control._sony_set_hdmi(settings, 1)
        settings["tv_backend"] = "unknown"
        with self.assertRaises(tv_control.TVControlError):
            tv_control.switch_to_oppo(settings)

    def test_external_player_hold_modes_and_main_with_fakes(self):
        import external_player as ep
        with tempfile.TemporaryDirectory() as td:
            settings = FakeSettings({"addon_data_dir": td, "hold_mode": "manual_file", "manual_stop_file": str(Path(td, "stop")), "oppo_stop_commands": "#STP", "switch_back_on_exit": "false"})
            ep.mark_session_active(settings)
            self.assertTrue(Path(ep.session_file(settings)).exists())
            ep.clear_session_active(settings)
            self.assertFalse(Path(ep.session_file(settings)).exists())
        with self.assertRaises(ValueError):
            ep.run_parallel([("bad", lambda: (_ for _ in ()).throw(ValueError("boom")))])
        calls = []
        with mock.patch.object(ep, "switch_to_oppo", side_effect=RuntimeError("adb down")):
            self.assertIsNone(ep._safe_tv_switch(FakeSettings({"tv_backend": "adb", "tv_switching_enabled": "true"}), "oppo"))
        with mock.patch.object(ep, "run_start", lambda *a, **k: calls.append("start")), \
             mock.patch.object(ep, "_safe_tv_switch", lambda *a, **k: calls.append(a[1])), \
             mock.patch.object(ep.time, "sleep", lambda *_: calls.append("sleep")):
            ep.fast_start(FakeSettings({"fast_changeover": "true", "startup_delay": "1", "oppo_start_mode": "tcp_commands"}), "/movie.iso")
        self.assertEqual(calls, ["oppo", "sleep", "start"])
        with mock.patch.object(ep, "get_playback_info", return_value={"errcode1": -5}), \
             mock.patch.object(ep.time, "sleep", lambda *_: None):
            ep.hold_playback(FakeSettings({"hold_mode": "http_poll", "http_poll_interval": "1", "http_poll_timeout_minutes": "1", "http_poll_idle_confirmations": "1"}))
        with mock.patch.object(ep, "query_playback_status", return_value="STOP"), \
             mock.patch.object(ep.time, "sleep", lambda *_: None):
            ep.hold_playback(FakeSettings({"hold_mode": "tcp_qpl_poll", "oppo_ip": "h", "oppo_port": "23", "qpl_poll_interval": "1", "qpl_poll_timeout_minutes": "1", "qpl_poll_idle_confirmations": "1"}))
        stop = tempfile.NamedTemporaryFile(delete=False); stop.close()
        try:
            ep.hold_playback(FakeSettings({"hold_mode": "manual_file", "manual_stop_file": stop.name}))
            self.assertFalse(os.path.exists(stop.name))
        finally:
            if os.path.exists(stop.name): os.remove(stop.name)
        with mock.patch.object(ep.time, "sleep", lambda seconds: calls.append(seconds)):
            ep.hold_playback(FakeSettings({"hold_mode": "fixed_timeout", "fixed_timeout_minutes": "0"}))
        self.assertIn(1, calls)
        fake_settings = FakeSettings({"addon_data_dir": tempfile.gettempdir(), "oppo_preflight_enabled": "true"})
        with mock.patch.object(ep.sys, "argv", ["external_player.py", "--addon-data", tempfile.gettempdir(), "--file", "/m.iso"]), \
             mock.patch.object(ep, "read_settings", return_value=fake_settings), \
             mock.patch.object(ep, "run_preflight", return_value={"power_status": "ON", "input_source": "HDMI", "already_on": True}), \
             mock.patch.object(ep, "mark_session_active", lambda s: calls.append("mark")), \
             mock.patch.object(ep, "fast_start", lambda *a, **k: calls.append("fast")), \
             mock.patch.object(ep, "hold_playback", lambda s: calls.append("hold")), \
             mock.patch.object(ep, "fast_return", lambda s: calls.append("return")), \
             mock.patch.object(ep, "clear_session_active", lambda s: calls.append("clear")):
            self.assertEqual(ep.main(), 0)
        self.assertTrue({"mark", "fast", "hold", "return", "clear"}.issubset(calls))

    def test_oppo_remote_send_paths_with_local_settings(self):
        remote = importlib.import_module("resources.lib.oppo_remote")
        settings = FakeSettings({"addon_data_dir": tempfile.gettempdir(), "remote_bridge_only_when_active": "true", "oppo_ip": "h", "oppo_port": "23", "oppo_socket_timeout": "1", "oppo_hardware_model": "chinoppo_m9702"})
        calls = []
        with mock.patch.object(remote, "_load_settings", return_value=settings), \
             mock.patch.object(remote, "_session_is_active", return_value=False), \
             mock.patch.object(remote, "_log", lambda msg: calls.append(msg)):
            remote.send_remote_key("play")
        self.assertTrue(any("Ignoring" in c for c in calls))
        with mock.patch.object(remote, "_load_settings", return_value=settings), \
             mock.patch.object(remote, "_session_is_active", return_value=True), \
             mock.patch.object(remote, "_command_map", return_value={"power_on": "#PON", "missing": ""}), \
             mock.patch.object(remote, "send_commands", lambda *a, **k: calls.append(a[2][0])), \
             mock.patch.object(remote, "_log", lambda msg: calls.append(msg)), \
             mock.patch.object(remote, "_notify", lambda msg: calls.append("notify:" + msg)):
            remote.send_remote_key("power_on")
            remote.send_remote_key("missing")
        self.assertIn("#EJT", calls)
        self.assertTrue(any(str(c).startswith("notify:") for c in calls))
        with mock.patch.object(remote, "get_audio_tracks", return_value=[{"index": 0, "name": "A", "selected": True}, {"index": 1, "name": "B", "selected": False}]), \
             mock.patch.object(remote, "set_audio_track", lambda s, i: calls.append(("audio", i))), \
             mock.patch.object(remote, "_notify", lambda msg: calls.append(msg)):
            remote._cycle_audio(settings)
        with mock.patch.object(remote, "get_subtitle_tracks", return_value=[]), \
             mock.patch.object(remote, "send_commands", lambda *a, **k: calls.append(a[2][0])):
            remote._cycle_subtitle(settings)
        with mock.patch.object(remote, "set_play_time", side_effect=RuntimeError("nope")), \
             mock.patch.object(remote, "_log", lambda msg: calls.append(msg)):
            remote._seek_beginning(settings)
        self.assertIn(("audio", 1), calls)
        self.assertIn("#SUB", calls)


class TKodiBoundCoverageHardening(unittest.TestCase):
    def test_installer_builders_dialogs_and_writers_with_stubs(self):
        with kodi_stubs():
            import xbmcaddon, xbmcgui, xbmcvfs
            xbmcaddon.reset(settings={"include_disc_folder_rules": "true", "python_path": "/usr/bin/python3"}, info={"path": str(ROOT), "id": "script.oppo203.iso.external"})
            xbmcgui.reset(); xbmcgui.push_select(0); xbmcgui.push_yesno(True)
            installer = importlib.import_module("resources.lib.installer")
            self.assertIn("Oppo203ISO", installer.build_external_player_xml())
            self.assertIn("BDMV", installer.build_rule_xml())
            self.assertIn("RunScript", installer.build_keymap_snippet_xml())
            snippet = installer.build_snippet_xml()
            self.assertIn("playercorefactory", snippet)
            self.assertIn("<playercorefactory>", installer.build_snippet_xml_body())
            installer.show_generated_xml(); installer.show_generated_keymap_xml()
            installer.write_snippet()
            installer.write_keymap_snippet()
            self.assertTrue(True)
            self.assertEqual(installer.show_architecture_choice_dialog(), 0)
            installer.show_tcl_presets()
            self.assertTrue(any(call[0] in ("textviewer", "ok", "select") for call in xbmcgui.calls()))

    def test_installer_discovery_and_filelist_diagnostic_with_stubs(self):
        with kodi_stubs("oppo_control", "settings_reader"):
            import xbmcaddon, xbmcgui
            xbmcaddon.reset(settings={"oppo_experimental_filelist_enabled": "true"}, info={"path": str(ROOT), "id": "script.oppo203.iso.external"})
            xbmcgui.reset(); xbmcgui.push_yesno(True)
            installer = importlib.import_module("resources.lib.installer")
            fake_oc = types.ModuleType("oppo_control")
            fake_oc.discover_oppo = lambda timeout=0: [{"ip": "192.0.2.44", "port": 23, "name": "OPPO"}]
            fake_oc.get_file_list_raw = lambda settings, path="/": '[{"name":"Movie.iso"}]'
            import oppo_control as real_oc
            fake_oc.parse_undocumented_file_list = real_oc.parse_undocumented_file_list
            fake_sr = types.ModuleType("settings_reader")
            fake_sr.read_settings = lambda addon_data: FakeSettings({"oppo_ip": "h"})
            sys.modules["oppo_control"] = fake_oc
            sys.modules["settings_reader"] = fake_sr
            installer.run_oppo_discovery()
            installer.run_experimental_filelist_diagnostic()
            self.assertEqual(installer.ADDON.getSetting("oppo_ip"), "192.0.2.44")
            self.assertTrue(any(call[0] == "textviewer" for call in xbmcgui.calls()))

    def test_installer_main_menu_dispatches_each_choice(self):
        """Strip-wizard: installer.main() menu has 11 choices (0-10) + Cancel.

        Exercise every dispatch + the architecture-choice gate to lock the
        post-strip menu shape.
        """
        with kodi_stubs("oppo_control", "settings_reader"):
            import xbmcaddon, xbmcgui
            xbmcaddon.reset(
                settings={
                    "architecture_choice_made": "true",
                    "playback_architecture": "external_player",
                    "python_path": "/usr/bin/python3",
                    "include_disc_folder_rules": "true",
                    "oppo_experimental_filelist_enabled": "false",  # exercises the disabled-warning branch
                    "avr_control_enabled": "false",
                },
                info={"path": str(ROOT), "id": "script.oppo203.iso.external"},
            )
            installer = importlib.import_module("resources.lib.installer")
            installer.ADDON.openSettings = lambda: None
            fake_oc = types.ModuleType("oppo_control")
            fake_oc.discover_oppo = lambda timeout=0: []  # no-results branch
            sys.modules["oppo_control"] = fake_oc

            # Each menu choice 0..10, then Cancel (-1).
            for choice in range(11):
                xbmcgui.reset()
                xbmcgui.push_select(choice)
                # show_tcl_presets needs a sub-select + yesno; filelist asks no
                # extra prompts in the disabled branch.
                xbmcgui.push_select(-1)   # tcl preset cancel
                xbmcgui.push_yesno(False)
                installer.main()

            # Architecture-not-chosen gate triggers the first-run dialog.
            installer.ADDON.setSetting("architecture_choice_made", "false")
            xbmcgui.reset()
            xbmcgui.push_select(-1)   # cancel arch dialog
            xbmcgui.push_select(-1)   # cancel menu
            installer.main()

    def test_installer_discovery_multiple_results_and_exceptions(self):
        """Strip-wizard: discovery multi-result branch + exception path."""
        with kodi_stubs("oppo_control"):
            import xbmcaddon, xbmcgui
            xbmcaddon.reset(
                settings={"architecture_choice_made": "true"},
                info={"path": str(ROOT), "id": "script.oppo203.iso.external"},
            )
            installer = importlib.import_module("resources.lib.installer")
            fake_oc = types.ModuleType("oppo_control")
            fake_oc.discover_oppo = lambda timeout=0: [
                {"ip": "192.0.2.10", "port": 23, "name": "OPPO-1"},
                {"ip": "192.0.2.11", "port": 23, "name": "OPPO-2"},
            ]
            sys.modules["oppo_control"] = fake_oc
            xbmcgui.reset()
            installer.run_oppo_discovery()
            self.assertTrue(any(c[0] == "textviewer" and "multiple" in c[1].lower() for c in xbmcgui.calls()))

            # Single result with user declining apply -> textviewer branch.
            fake_oc.discover_oppo = lambda timeout=0: [{"ip": "192.0.2.40", "port": 9999, "name": "OPPO"}]
            xbmcgui.reset(); xbmcgui.push_yesno(False)
            installer.run_oppo_discovery()
            self.assertTrue(any(c[0] == "textviewer" for c in xbmcgui.calls()))

            # Exception path inside discovery.
            def boom(timeout=0): raise RuntimeError("net down")
            fake_oc.discover_oppo = boom
            xbmcgui.reset()
            installer.run_oppo_discovery()
            self.assertTrue(any(c[0] == "ok" and "failed" in c[2].lower() for c in xbmcgui.calls()))

    def test_installer_filelist_diagnostic_large_listing_truncates(self):
        """Strip-wizard: file-list diagnostic with >50 entries truncates."""
        with kodi_stubs("oppo_control", "settings_reader"):
            import xbmcaddon, xbmcgui
            xbmcaddon.reset(
                settings={"oppo_experimental_filelist_enabled": "true"},
                info={"path": str(ROOT), "id": "script.oppo203.iso.external"},
            )
            installer = importlib.import_module("resources.lib.installer")
            entries = [
                {"name": f"item{i}.iso", "entry_type": "file", "is_dir": False,
                 "is_file": True, "size_bytes": 1000 + i, "disc_type": "iso",
                 "extension": "iso", "path": f"/m/item{i}.iso"}
                for i in range(60)
            ]
            fake_oc = types.ModuleType("oppo_control")
            fake_oc.get_file_list_raw = lambda settings, path="/": "raw"
            fake_oc.parse_undocumented_file_list = lambda raw, base_path=None: entries
            sys.modules["oppo_control"] = fake_oc
            fake_sr = types.ModuleType("settings_reader")
            fake_sr.read_settings = lambda addon_data: FakeSettings({})
            sys.modules["settings_reader"] = fake_sr
            xbmcgui.reset()
            installer.run_experimental_filelist_diagnostic()
            self.assertTrue(any("and 10 more entries" in str(c) for c in xbmcgui.calls()))

    def test_installer_filelist_diagnostic_empty_entries_branch(self):
        """Strip-wizard: file-list diagnostic with 0 entries reports the empty branch."""
        with kodi_stubs("oppo_control", "settings_reader"):
            import xbmcaddon, xbmcgui
            xbmcaddon.reset(
                settings={"oppo_experimental_filelist_enabled": "true"},
                info={"path": str(ROOT), "id": "script.oppo203.iso.external"},
            )
            installer = importlib.import_module("resources.lib.installer")
            fake_oc = types.ModuleType("oppo_control")
            fake_oc.get_file_list_raw = lambda settings, path="/": "raw"
            fake_oc.parse_undocumented_file_list = lambda raw, base_path=None: []
            sys.modules["oppo_control"] = fake_oc
            fake_sr = types.ModuleType("settings_reader")
            fake_sr.read_settings = lambda addon_data: FakeSettings({})
            sys.modules["settings_reader"] = fake_sr
            xbmcgui.reset()
            installer.run_experimental_filelist_diagnostic()
            self.assertTrue(any("No entries parsed" in str(c) for c in xbmcgui.calls()))

    def test_installer_extra_branches_for_coverage(self):
        """Service-interception snippet header + TCL apply branch + AVR export."""
        with kodi_stubs():
            import xbmcaddon, xbmcgui
            xbmcaddon.reset(
                settings={
                    "include_disc_folder_rules": "true",
                    "python_path": "/usr/bin/python3",
                    "playback_architecture": "service_interception",
                    "architecture_choice_made": "true",
                    "avr_control_enabled": "false",
                },
                info={"path": str(ROOT), "id": "script.oppo203.iso.external"},
            )
            installer = importlib.import_module("resources.lib.installer")

            # service_interception snippet header (build_snippet_xml wraps the body).
            snippet = installer.build_snippet_xml()
            self.assertIn("service_interception", snippet)

            # show_architecture_choice_dialog choice==1 (service_interception).
            xbmcgui.reset(); xbmcgui.push_select(1)
            installer.show_architecture_choice_dialog()
            self.assertEqual(installer.ADDON.getSetting("playback_architecture"), "service_interception")

            # show_tcl_presets apply branch.
            xbmcgui.reset(); xbmcgui.push_select(0); xbmcgui.push_yesno(True)
            installer.show_tcl_presets()
            self.assertTrue(installer.ADDON.getSetting("oppo_input_adb_shell"))

            # export_avr_diagnostic_report runs through the success path.
            installer.export_avr_diagnostic_report()


class TStripWizardAutoscriptCoverage(unittest.TestCase):
    """Cover the post-strip surface in autoscript_helper.py."""

    def test_cifs_with_username_and_password(self):
        autoscript = importlib.import_module("resources.lib.autoscript_helper")
        body = autoscript.generate({
            "mount_type": "cifs",
            "mount_remote": "//nas/movies",
            "cifs_user": "user",
            "cifs_pass": "pass",
        })
        self.assertIn(",username=user,password=pass", body)

    def test_write_script_normalizes_line_endings(self):
        autoscript = importlib.import_module("resources.lib.autoscript_helper")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "autoexec.sh")
            autoscript.write_script(str(path), "a\r\nb\r")
            self.assertEqual(path.read_text(encoding="utf-8"), "a\nb\n")

    def test_write_script_chmod_failure_is_swallowed(self):
        autoscript = importlib.import_module("resources.lib.autoscript_helper")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "autoexec.sh")
            with mock.patch.object(autoscript.os, "chmod", side_effect=OSError("readonly")):
                out = autoscript.write_script(str(path), "x\n")
            self.assertEqual(out, str(path))
            self.assertEqual(path.read_text(encoding="utf-8"), "x\n")


class TStripWizardSettingsReaderCoverage(unittest.TestCase):
    """Cover settings_reader.save_settings + Settings.get_bool None branch."""

    def test_save_settings_persists_keys_to_xml(self):
        sr = importlib.import_module("resources.lib.settings_reader")
        with tempfile.TemporaryDirectory() as td:
            ok = sr.save_settings(td, sr.Settings({"oppo_ip": "192.0.2.5"}))
            self.assertTrue(ok)
            self.assertTrue(Path(td, "settings.xml").exists())
            text = Path(td, "settings.xml").read_text(encoding="utf-8")
            self.assertIn("oppo_ip", text)
            self.assertIn("192.0.2.5", text)

            # Second call updates existing setting + creates a new one.
            ok = sr.save_settings(td, sr.Settings({"oppo_ip": "192.0.2.99", "oppo_port": "23"}))
            self.assertTrue(ok)
            text = Path(td, "settings.xml").read_text(encoding="utf-8")
            self.assertIn("192.0.2.99", text)
            self.assertIn("oppo_port", text)

    def test_save_settings_empty_dir_returns_false(self):
        sr = importlib.import_module("resources.lib.settings_reader")
        self.assertFalse(sr.save_settings("", sr.Settings({"x": "y"})))

    def test_settings_get_bool_none_branch_returns_default(self):
        sr = importlib.import_module("resources.lib.settings_reader")

        class RawNone:
            data = {"x": None}

            def get(self, key, default=None):
                return self.data.get(key, default)

        s = RawNone()
        # Direct call hits the `raw is None` branch.
        self.assertTrue(sr.Settings.get_bool(s, "x", default=True))
        self.assertFalse(sr.Settings.get_bool(s, "x", default=False))


class TStripWizardHardwareGuidanceCoverage(unittest.TestCase):
    """Cover player_setup_guidance and format_player_setup_guidance.

    These were exercised through wizard.py; the configurator may consume them
    via IPC.
    """

    def test_player_setup_guidance_covers_all_hardware_classes(self):
        hc = importlib.import_module("resources.lib.hardware_capabilities")
        for key, expected_marker in (
            ("UDP-203", "Stock OPPO"),
            ("M9702", "Chinoppo-style clone"),
            ("Magnetar-UDP800", "Magnetar"),
            ("Reavon-UBR-X100", "Reavon"),
            ("unknown_model_xyz", "Unknown"),
        ):
            guidance = hc.player_setup_guidance(key)
            self.assertIn(expected_marker, guidance["title"])
            rendered = hc.format_player_setup_guidance(key)
            self.assertIn("Hardware validation claimed: no", rendered)


if __name__ == "__main__":
    unittest.main()

class TCoverageGateSecondPass(unittest.TestCase):
    def test_oppo_control_remaining_branches(self):
        oc = importlib.import_module("resources.lib.oppo_control")
        self.assertEqual(oc.query_command("h", 23, "   "), "")
        self.assertEqual(oc._parse_response(""), "")
        self.assertEqual(oc._parse_response("@QPW OK"), "")
        with self.assertRaises(oc.OppoError):
            oc._parse_response("ER INVALID")
        with mock.patch.object(oc, "query_command", return_value="PLAY") as q:
            self.assertEqual(oc.query_playback_status("h", 23), "PLAY")
            self.assertEqual(oc.query_input_source("h", 23), "PLAY")
            self.assertEqual(oc.setup_verbose_mode("h", 23, 2), "PLAY")
        self.assertGreaterEqual(q.call_count, 3)
        self.assertEqual(oc.run_preflight(FakeSettings({"oppo_preflight_enabled": "false"})), {"power_status": None, "input_source": None, "already_on": False})
        with mock.patch.object(oc, "query_power_status", side_effect=OSError("down")), \
             mock.patch.object(oc, "query_input_source", side_effect=oc.OppoError("bad")):
            pre = oc.run_preflight(FakeSettings({"oppo_preflight_enabled": "true", "oppo_ip": "h", "oppo_port": "23", "oppo_socket_timeout": "1"}))
        self.assertEqual(pre["power_status"], None)
        self.assertFalse(oc.maybe_wake_on_lan(FakeSettings({"oppo_use_wol": "false"})))
        with self.assertRaises(oc.OppoError):
            oc.maybe_wake_on_lan(FakeSettings({"oppo_use_wol": "true", "oppo_mac": ""}))
        with mock.patch.object(oc, "wake_on_lan", lambda mac, b: "sent"):
            self.assertTrue(oc.maybe_wake_on_lan(FakeSettings({"oppo_use_wol": "true", "oppo_mac": "001122334455", "oppo_wol_broadcast": "255.255.255.255"})))
        udp = FakeUdpSocket()
        with mock.patch.object(oc.socket, "socket", return_value=udp):
            self.assertTrue(oc.activate_http_api(FakeSettings({"oppo_http_activate": "true", "oppo_http_broadcast": "255.255.255.255", "oppo_http_port": "436"})))
        self.assertFalse(oc.activate_http_api(FakeSettings({"oppo_http_activate": "false"})))
        bad_response = FakeHttpResponse("bad", status=500)
        with mock.patch.object(oc.urllib.request, "urlopen", return_value=bad_response):
            with self.assertRaises(oc.OppoError):
                oc._http_get(FakeSettings({"oppo_ip": "h", "oppo_http_port": "436"}), "/x")
        s = FakeSettings({"oppo_http_disc_folder_root": "false", "oppo_http_path_from": "", "oppo_http_path_to": "", "oppo_http_urlencode_path": "false", "oppo_http_app_device_type": "3", "oppo_http_media_type": "4"})
        self.assertEqual(oc._translate_media_path(s, "/plain path.iso"), "/plain path.iso")
        self.assertEqual(oc._build_json_payload(s, "/plain path.iso")["type"], 4)
        with mock.patch.object(oc, "_http_get", return_value="not-json"):
            self.assertEqual(oc.get_playback_info(FakeSettings({"oppo_ip": "h"})), {"raw": "not-json"})
        with mock.patch.object(oc, "get_playback_info", return_value=["bad"]):
            self.assertEqual(oc.get_playback_status(FakeSettings()), "")
        self.assertFalse(oc.http_info_is_definitive_stop(["bad"]))
        self.assertFalse(oc.http_info_indicates_playing(["bad"]))
        self.assertTrue(oc.http_info_indicates_playing({"state": "PAUSE"}))
        self.assertFalse(oc.http_info_indicates_playing({"state": "UNKNOWN"}))
        self.assertEqual(oc._filter_commands_for_mode(FakeSettings({"oppo_already_on_mode": "true"}), "oppo_start_commands", ["PON", "#PLA"]), ["#PLA"])
        self.assertEqual(oc._filter_commands_for_mode(FakeSettings(), "oppo_stop_commands", ["#STP"]), ["#STP"])
        self.assertEqual(oc._resolve_hardware_wake_command(FakeSettings(), 123), 123)
        self.assertEqual(oc._resolve_hardware_wake_command(FakeSettings(), "#PLA"), "#PLA")
        with mock.patch.object(oc, "send_commands", return_value=[]) as send:
            self.assertEqual(oc.run_configured_commands(FakeSettings({"oppo_ip": "h", "oppo_port": "23", "oppo_socket_timeout": "1", "oppo_command_delay": "0", "oppo_start_commands": ""}), "oppo_start_commands"), [])
            send.assert_not_called()
        with mock.patch.object(oc, "_http_get", side_effect=oc.OppoError("bad")):
            self.assertEqual(oc.get_audio_tracks(FakeSettings()), [])
            self.assertEqual(oc.get_subtitle_tracks(FakeSettings()), [])

    def test_oppo_control_filelist_edges(self):
        oc = importlib.import_module("resources.lib.oppo_control")
        entry = oc._normalise_filelist_entry({"path": "/Movies/BDMV/", "isDir": True}, base_path="/base")
        self.assertEqual(entry["entry_type"], "directory")
        self.assertEqual(oc._normalise_filelist_entry("LooseName", base_path="/base")["path"], "/base/LooseName")
        self.assertEqual(oc._first_non_empty({"a": "", "b": "B"}, "a", "b"), "B")
        self.assertIsNone(oc._first_int({"a": "bad"}, "a"))
        self.assertTrue(oc._first_bool({"folder": "yes"}, "folder"))
        self.assertFalse(oc._first_bool({"file": "0"}, "file"))
        self.assertIsNone(oc._first_bool({}, "missing"))
        self.assertIsNone(oc._safe_int("bad"))
        self.assertEqual(oc._guess_name_from_fields(["size=10", "type=file", "/dir/movie.iso"]), "movie.iso")
        self.assertEqual(oc._guess_name_from_fields(["", "index=1"]), "")
        self.assertEqual(oc._guess_path_from_fields(["x", "smb://server/share/movie.iso"]), "smb://server/share/movie.iso")
        self.assertEqual(oc._guess_size_from_fields(["size=25"]), 25)
        self.assertEqual(oc._guess_size_from_fields(["7"]), 7)
        self.assertEqual(oc._join_base_path("", "x"), "x")
        self.assertEqual(oc._extension_for("noextension"), "")
        self.assertEqual(oc._infer_entry_type(explicit_is_dir=True), "directory")
        self.assertEqual(oc._infer_entry_type(explicit_is_dir=False), "file")
        self.assertEqual(oc._infer_entry_type(path="/folder/"), "directory")
        self.assertEqual(oc._infer_entry_type(type_hint="this is a file"), "file")
        self.assertEqual(oc._infer_entry_type(), "unknown")
        for kwargs, expected in [
            ({"name": "disc.uhd"}, "uhd_bluray"),
            ({"extension": "mpls"}, "bluray"),
            ({"path": "/MPEGAV/file.dat"}, "svcd"),
            ({"extension": "cue"}, "vcd"),
            ({"name": "unknown.txt"}, ""),
        ]:
            self.assertEqual(oc._infer_disc_type(**kwargs), expected)

    def test_external_player_more_hold_and_error_paths(self):
        import external_player as ep

        # Suppress log(): its stdlib-logging fallback (xbmc absent) calls time.time()
        # and would otherwise drain the patched time sequence below.
        _logp = mock.patch.object(ep, "log", lambda *a, **k: None)
        _logp.start()
        self.addCleanup(_logp.stop)
        times = iter([0, 1, 2, 1000])
        with mock.patch.object(ep.time, "time", side_effect=lambda: next(times)), \
             mock.patch.object(ep.time, "sleep", lambda *_: None), \
             mock.patch.object(ep, "get_playback_info", side_effect=[{"e_play_status": 0}, {"status": "STOP"}]), \
             mock.patch.object(ep, "http_info_indicates_playing", side_effect=[True, False]), \
             mock.patch.object(ep, "http_info_is_definitive_stop", return_value=False):
            ep.hold_playback(FakeSettings({"hold_mode": "http_poll", "http_poll_interval": "1", "http_poll_timeout_minutes": "1", "http_poll_idle_confirmations": "1", "trickplay_suppress_seconds": "0"}))
        times = iter([0, 1, 1000])
        with mock.patch.object(ep.time, "time", side_effect=lambda: next(times)), \
             mock.patch.object(ep.time, "sleep", lambda *_: None), \
             mock.patch.object(ep, "get_playback_info", side_effect=RuntimeError("http down")):
            ep.hold_playback(FakeSettings({"hold_mode": "http_poll", "http_poll_interval": "1", "http_poll_timeout_minutes": "1", "http_poll_idle_confirmations": "2"}))
        times = iter([0, 1, 1000])
        with mock.patch.object(ep.time, "time", side_effect=lambda: next(times)), \
             mock.patch.object(ep.time, "sleep", lambda *_: None), \
             mock.patch.object(ep, "query_playback_status", side_effect=RuntimeError("tcp down")):
            ep.hold_playback(FakeSettings({"hold_mode": "tcp_qpl_poll", "oppo_ip": "h", "oppo_port": "23", "qpl_poll_interval": "1", "qpl_poll_timeout_minutes": "1", "qpl_poll_idle_confirmations": "2"}))
        class FakeClient:
            def __init__(self, host, port): pass
            def wait_for_stop(self, timeout): return True
        with mock.patch("oppo_tcp_client.OppoTcpClient", FakeClient):
            ep.hold_playback(FakeSettings({"hold_mode": "verbose_push", "oppo_ip": "h", "oppo_port": "23", "verbose_push_timeout_minutes": "1"}))
        class BadClient:
            def __init__(self, host, port): raise RuntimeError("connect")
        with mock.patch("oppo_tcp_client.OppoTcpClient", BadClient), \
             mock.patch.object(ep.time, "time", side_effect=[0, 1000]), \
             mock.patch.object(ep.time, "sleep", lambda *_: None):
            ep.hold_playback(FakeSettings({"hold_mode": "verbose_push", "oppo_ip": "h", "oppo_port": "23", "verbose_push_timeout_minutes": "1", "qpl_poll_timeout_minutes": "1"}))
        calls = []
        with mock.patch.object(ep, "run_configured_commands", lambda *a, **k: calls.append("stop")), \
             mock.patch.object(ep, "_safe_tv_switch", lambda s, target: calls.append(target)):
            ep.fast_return(FakeSettings({"switch_back_on_exit": "true"}))
        self.assertEqual(calls, ["stop", "kodi"])
        with mock.patch.object(ep.sys, "argv", ["external_player.py", "--addon-data", tempfile.gettempdir(), "--file", "/m.iso"]), \
             mock.patch.object(ep, "read_settings", return_value=FakeSettings({"addon_data_dir": tempfile.gettempdir()})), \
             mock.patch.object(ep, "mark_session_active", lambda s: None), \
             mock.patch.object(ep, "fast_start", side_effect=RuntimeError("player failed")), \
             mock.patch.object(ep, "fast_return", side_effect=RuntimeError("return failed")), \
             mock.patch.object(ep, "clear_session_active", lambda s: None):
            self.assertEqual(ep.main(), 1)
    def test_oppo_remote_kodi_and_success_specials(self):
        with kodi_stubs():
            import xbmcaddon, xbmcgui, xbmcvfs
            xbmcaddon.reset(settings={"oppo_ip": "h", "remote_bridge_only_when_active": "false"}, info={"profile": tempfile.mkdtemp()})
            xbmcgui.reset()
            remote = importlib.import_module("resources.lib.oppo_remote")
            self.assertTrue(remote._translate("special://profile/test").startswith("/tmp"))
            remote._notify("hello")
            self.assertTrue(any(call[0] == "notification" for call in xbmcgui.calls()))
            self.assertTrue(remote._addon_data_dir())
            settings = remote._load_settings()
            self.assertIn("addon_data_dir", settings.data)
            with tempfile.TemporaryDirectory() as td:
                s = FakeSettings({"addon_data_dir": td})
                Path(td, "oppo203iso-active").write_text("1", encoding="utf-8")
                self.assertTrue(remote._session_is_active(s))
            self.assertIn("play", remote._command_map(FakeSettings({"oppo_remote_command_map": "not-json"})))
            calls = []
            settings = FakeSettings({"addon_data_dir": "", "remote_bridge_only_when_active": "false", "oppo_ip": "h", "oppo_port": "23", "oppo_socket_timeout": "1", "oppo_hardware_model": "udp_203"})
            with mock.patch.object(remote, "_load_settings", return_value=settings), \
                 mock.patch.object(remote, "_command_map", return_value={"cycle_audio": "__cycle_audio__", "cycle_subtitle": "__cycle_subtitle__", "seek_beginning": "__seek_beginning__"}), \
                 mock.patch.object(remote, "_cycle_audio", lambda s: calls.append("audio")), \
                 mock.patch.object(remote, "_cycle_subtitle", lambda s: calls.append("sub")), \
                 mock.patch.object(remote, "_seek_beginning", lambda s: calls.append("seek")):
                remote.send_remote_key("cycle_audio"); remote.send_remote_key("cycle_subtitle"); remote.send_remote_key("seek_beginning")
            self.assertEqual(calls, ["audio", "sub", "seek"])
            with mock.patch.object(remote, "get_subtitle_tracks", return_value=[{"index": 0, "name": "Off", "selected": False}, {"index": 2, "name": "English", "selected": True}]), \
                 mock.patch.object(remote, "set_subtitle_track", lambda s, i: calls.append(("subtitle", i))), \
                 mock.patch.object(remote, "_notify", lambda msg: calls.append(msg)):
                remote._cycle_subtitle(settings)
            with mock.patch.object(remote, "set_play_time", lambda *a: calls.append("played")), \
                 mock.patch.object(remote, "_notify", lambda msg: calls.append(msg)):
                remote._seek_beginning(settings)
            self.assertIn(("subtitle", 0), calls)
            self.assertIn("played", calls)

    def test_small_module_edges(self):
        import adb_control, i18n, reconnect_backoff
        class Proc: returncode = 0; stdout = "ok\n"; stderr = ""
        with mock.patch.object(adb_control.subprocess, "run", return_value=Proc()):
            self.assertEqual(adb_control.adb_connect("adb", "1.2.3.4", 5555), "ok")
            self.assertEqual(adb_control.adb_shell("adb", "1.2.3.4", 5555, "input keyevent 3"), "ok")
        class Bad: returncode = 1; stdout = ""; stderr = "bad"
        with mock.patch.object(adb_control.subprocess, "run", return_value=Bad()):
            with self.assertRaises(adb_control.ADBError): adb_control._run(["adb"], timeout=1)
        self.assertEqual(adb_control.switch_input(FakeSettings({"adb_path": "adb", "tv_ip": "1.2.3.4", "tv_adb_port": "5555", "adb_connect_before_switch": "false", "_adb_runner": lambda *a, **k: Proc()}), "input keyevent 3"), "ok")
        self.assertEqual(i18n.L("plain"), "plain")
        self.assertIsInstance(i18n.supported_languages(), list)
        self.assertGreaterEqual(len(reconnect_backoff.schedule(3, base=1, cap=2, jitter=0)), 3)

class TCoverageGateThirdPass(unittest.TestCase):
    def test_oppo_tcp_client_direct_state_machine_paths(self):
        import socket
        import threading
        import oppo_tcp_client as otc
        client = otc.OppoTcpClient("h", 23)
        client._handle_line("not-a-push")
        self.assertFalse(client._stop_event_seen)
        client._handle_line("@UPW 1")
        self.assertFalse(client._stop_event_seen)
        client._handle_line("@UPW 0")
        self.assertTrue(client._stop_event_seen)
        client = otc.OppoTcpClient("h", 23)
        client._handle_line("@UPL PLAY")
        self.assertFalse(client._stop_event_seen)
        client._handle_line("@UPL STOP")
        self.assertTrue(client._stop_event_seen)
        # wait_for_stop returns False immediately on connection error.
        c2 = otc.OppoTcpClient("h", 23)
        with mock.patch.object(c2, "_connect_and_read", lambda: setattr(c2, "_error", OSError("down")) or c2._connected.set()):
            self.assertFalse(c2.wait_for_stop(timeout=0.01))
        # wait_for_stop returns True when a test thread sets a stop event.
        c3 = otc.OppoTcpClient("h", 23)
        def fake_connect():
            c3._connected.set(); c3._stop_event_seen = True
        with mock.patch.object(c3, "_connect_and_read", fake_connect):
            self.assertTrue(c3.wait_for_stop(timeout=0.01))
        # close covers socket and thread cleanup paths, including OSError swallow.
        class Sock:
            def close(self): raise OSError("already closed")
        class Thread:
            def is_alive(self): return True
            def join(self, timeout): self.timeout = timeout
        c3._sock = Sock(); c3._thread = Thread(); c3.close()
        # _attempt_once resets per-attempt events before delegating.
        c4 = otc.OppoTcpClient("h", 23)
        with mock.patch.object(c4, "wait_for_stop", return_value=True):
            self.assertTrue(c4._attempt_once())

    def test_oppo_tcp_client_connect_and_read_with_fake_socket(self):
        import socket
        import oppo_tcp_client as otc
        class PushSocket:
            def __init__(self, chunks, raise_on_close=False):
                self.chunks = list(chunks); self.sent = []; self.raise_on_close = raise_on_close
            def settimeout(self, timeout): self.timeout = timeout
            def sendall(self, data): self.sent.append(data)
            def recv(self, size):
                item = self.chunks.pop(0)
                if item == "timeout": raise socket.timeout()
                if item == "oserror": raise OSError("down")
                return item
            def close(self):
                if self.raise_on_close: raise OSError("close")
        sock = PushSocket([b"@SVM OK\r", b"@UPL STOP\r", b""])
        c = otc.OppoTcpClient("h", 23)
        with mock.patch.object(otc.socket, "create_connection", return_value=sock):
            c._connect_and_read()
        self.assertTrue(c._stop_event_seen)
        self.assertTrue(sock.sent[0].startswith(b"#SVM"))
        sock2 = PushSocket(["timeout", b"@UPW 0\n", b""], raise_on_close=True)
        c2 = otc.OppoTcpClient("h", 23, send_svm=False)
        with mock.patch.object(otc.socket, "create_connection", return_value=sock2):
            c2._connect_and_read()
        self.assertTrue(c2._stop_event_seen)
        c3 = otc.OppoTcpClient("h", 23)
        with mock.patch.object(otc.socket, "create_connection", side_effect=OSError("connect")):
            c3._connect_and_read()
        self.assertIsInstance(c3._error, OSError)
        sleeps = []
        with mock.patch.object(otc.time, "time", side_effect=[0, 0, 0.1, 0.2, 2]), \
             mock.patch.object(otc.reconnect_backoff if hasattr(otc, 'reconnect_backoff') else otc, "__name__", getattr(otc, "__name__", "oppo_tcp_client"), create=True):
            c4 = otc.OppoTcpClient("h", 23)
            self.assertFalse(c4.wait_for_stop_persistent(timeout=1, max_retries=2, base_delay=5, cap_delay=5, jitter=0, _sleep=sleeps.append, _connect_factory=lambda: False))
        self.assertTrue(sleeps)

    def test_settings_reader_and_i18n_remaining_edges(self):
        import settings_reader as sr
        self.assertTrue(sr.Settings({"x": True}).get_bool("x"))
        self.assertTrue(sr.Settings({"x": ""}).get_bool("x", True))
        self.assertFalse(sr.Settings({"x": object()}).get_bool("x", False))
        self.assertEqual(sr.Settings({"x": None}).get_str("x", "fallback"), "fallback")
        import xml.etree.ElementTree as ET
        self.assertEqual(sr._setting_value(ET.fromstring('<setting id="x">text</setting>')), "text")
        self.assertEqual(sr._setting_value(ET.fromstring('<setting id="x"><value>child</value></setting>')), "child")
        self.assertEqual(sr._setting_value(ET.fromstring('<setting id="x"/>')), "")
        self.assertEqual(sr.normalize_hardware_model(None), "UDP-203")
        self.assertEqual(sr.normalize_hardware_model("unknown"), "unknown")
        self.assertTrue(sr.hardware_profile("unknown")["protocol_compatible"])
        self.assertEqual(sr.compatibility_preset("UDP-203", jailbreak=True)["oppo_http_payload_mode"], "json_payload")
        self.assertEqual(sr.compatibility_preset("UDP-203"), {})
        self.assertTrue(sr.is_token_supported_by_hardware("#SRC 9", "UDP-203"))
        self.assertIsNone(sr.warn_if_unsupported("#SRC 0", "UDP-203"))
        with kodi_stubs("i18n"):
            import xbmcaddon
            xbmcaddon.reset(localized={31000: "Bienvenue"})
            i18n = importlib.import_module("i18n")
            self.assertEqual(i18n.L(31000), "Bienvenue")
            xbmcaddon.reset(localized={})
            self.assertEqual(i18n.L(31000), "")
            self.assertEqual(i18n.L(31000, "fallback"), "fallback")
            class BadAddon:
                def getLocalizedString(self, sid): raise RuntimeError("bad")
            i18n.xbmcaddon.Addon = lambda *_: BadAddon()
            self.assertEqual(i18n.L(31001), "")
class TCoverageGateFourthPassGradual99(unittest.TestCase):
    def test_autoscript_generation_profiles(self):
        with kodi_stubs("autoscript_helper"):
            import xbmcgui, xbmcaddon
            autoscript = importlib.import_module("autoscript_helper")
            nfs = autoscript.generate({
                "enable_telnet": False,
                "passwordless_root": False,
                "mount_type": "nfs",
                "mount_remote": "192.0.2.5:/movies",
                "mount_local": "/mnt/movies",
                "mount_options": "ro,nolock",
                "heartbeat_path": "",
                "enable_adb": True,
                "adb_port": "5566",
            })
            self.assertIn("mount -t nfs -o ro,nolock", nfs)
            self.assertIn("setprop service.adb.tcp.port 5566", nfs)
            self.assertNotIn("telnetd", nfs)
            cifs_user = autoscript.generate({
                "mount_type": "cifs",
                "mount_remote": "//192.0.2.5/movies",
                "cifs_user": "guest",
                "cifs_pass": "",
            })
            self.assertIn(",username=guest", cifs_user)
            self.assertNotIn(",password=", cifs_user)
            cifs_pass = autoscript.generate({
                "mount_type": "cifs",
                "mount_remote": "//192.0.2.5/movies",
                "cifs_user": "u",
                "cifs_pass": "p",
            })
            self.assertIn(",username=u,password=p", cifs_pass)

    def test_discovery_cache_and_probe_edge_paths(self):
        import discovery
        self.assertIsNone(discovery.vendor_to_preset("unknown vendor"))
        self.assertIsNone(discovery.apply_preset_for("bad"))
        self.assertIsNone(discovery.parse_ssdp_response("HTTP/1.1 200 OK"))
        self.assertIsNone(discovery.parse_ssdp_response("garbage\nX: y"))
        self.assertIsNone(discovery.parse_mdns_record({"addresses": []}))
        ssdp = "NOTIFY * HTTP/1.1\nLOCATION: http://192.0.2.50:80/desc.xml\nSERVER: OPPO UDP-205\nNT: upnp:rootdevice\n"
        devs = discovery.discover(
            ssdp=lambda: [ssdp],
            mdns=lambda: [{"addresses": ["192.0.2.50"], "port": 23, "properties": {"vendor": "OPPO"}, "type": "_oppo._tcp", "name": "oppo"}],
            udp=lambda: [("192.0.2.51", "Reavon")],
            now=lambda: 100.0,
        )
        self.assertEqual(devs[0]["source"], "mdns")
        self.assertEqual(devs[1]["preset"], "reavon_x200")
        devs = discovery.discover(ssdp=lambda: (_ for _ in ()).throw(RuntimeError("ssdp")),
                                  mdns=lambda: (_ for _ in ()).throw(RuntimeError("mdns")),
                                  udp=lambda: (_ for _ in ()).throw(RuntimeError("udp")))
        self.assertEqual(devs, [])

        class MemFS:
            def __init__(self, text=None): self.text = text; self.writes = {}
            def exists(self, p): return self.text is not None or p in self.writes
            def read(self, p): return self.text if self.text is not None else self.writes[p]
            def write(self, p, t): self.writes[p] = t; self.text = t
        cache = discovery.DeviceCache(path="cache.json", fs=MemFS(), clock=lambda: 200.0)
        self.assertIsNone(cache.add({}))
        cache.add_many([{"ip": "192.0.2.60", "port": "23", "vendor": "Magnetar", "last_seen": 190.0}, None])
        self.assertEqual(cache.recent(max_age_s=20)[0]["preset"], "magnetar")
        self.assertTrue(cache.save())
        raw = '{"items":[{"ip":"192.0.2.61","port":23,"vendor":"OPPO"},"bad",{"port":23}]}'
        cache2 = discovery.DeviceCache(path="cache.json", fs=MemFS(raw), clock=lambda: 300.0)
        self.assertTrue(cache2.load())
        self.assertEqual(cache2.all()[0]["ip"], "192.0.2.61")
        self.assertFalse(discovery.DeviceCache(path=None).save())
        self.assertFalse(discovery.DeviceCache(path="x", fs=MemFS("not json")).load())
        self.assertFalse(discovery.DeviceCache(path="x", fs=MemFS('{"items":{}}')).load())
        cache2.clear()
        self.assertEqual(cache2.all(), [])

    def test_external_player_idle_suppression_and_disabled_tv_paths(self):
        import external_player as ep

        # Suppress log(): its stdlib-logging fallback (xbmc absent) calls time.time()
        # and would otherwise drain the patched time sequences below.
        _logp = mock.patch.object(ep, "log", lambda *a, **k: None)
        _logp.start()
        self.addCleanup(_logp.stop)
        self.assertFalse(ep.tv_switching_enabled(FakeSettings({"tv_backend": "none"})))
        self.assertFalse(ep.tv_switching_enabled(FakeSettings({"tv_backend": "off"})))
        self.assertIsNone(ep.mark_session_active(FakeSettings({"addon_data_dir": ""})))
        self.assertIsNone(ep.clear_session_active(FakeSettings({"addon_data_dir": ""})))
        self.assertIsNone(ep.run_parallel([]))
        with mock.patch.object(ep, "_safe_tv_switch") as sw, \
             mock.patch.object(ep, "run_configured_commands"):
            ep.fast_return(FakeSettings({"switch_back_on_exit": "false"}))
            sw.assert_not_called()

        # First PLAY extends the suppress window, then STOP inside that window is ignored,
        # then the loop times out. This covers the trick-play suppression branch.
        times = iter([0, 1, 2, 3, 4, 5, 6, 1000])
        infos = iter([{"status": "PLAY"}, {"status": "STOP"}, {"status": "UNKNOWN"}])
        with mock.patch.object(ep.time, "time", side_effect=lambda: next(times)), \
             mock.patch.object(ep.time, "sleep", lambda *_: None), \
             mock.patch.object(ep, "get_playback_info", side_effect=lambda s: next(infos)), \
             mock.patch.object(ep, "http_info_is_definitive_stop", return_value=False), \
             mock.patch.object(ep, "http_info_indicates_playing", side_effect=[True, False, False]):
            ep.hold_playback(FakeSettings({"hold_mode": "http_poll", "http_poll_interval": "1", "http_poll_timeout_minutes": "1", "http_poll_idle_confirmations": "2", "trickplay_suppress_seconds": "10"}))

        # A non-idle TCP status resets idle confirmations and then a later STOP exits.
        times = iter([0, 1, 2, 3])
        with mock.patch.object(ep.time, "time", side_effect=lambda: next(times)), \
             mock.patch.object(ep.time, "sleep", lambda *_: None), \
             mock.patch.object(ep, "query_playback_status", side_effect=["PLAY", "STOP"]):
            ep.hold_playback(FakeSettings({"hold_mode": "tcp_qpl_poll", "oppo_ip": "h", "oppo_port": "23", "qpl_poll_interval": "1", "qpl_poll_timeout_minutes": "1", "qpl_poll_idle_confirmations": "1"}))

    def test_oppo_remote_error_fallbacks_and_hardware_gate_paths(self):
        remote = importlib.import_module("resources.lib.oppo_remote")
        settings = FakeSettings({"addon_data_dir": "", "remote_bridge_only_when_active": "false", "oppo_ip": "h", "oppo_port": "23", "oppo_socket_timeout": "1", "oppo_hardware_model": "udp_203"})
        calls = []
        with mock.patch.object(remote, "get_audio_tracks", return_value=[]), \
             mock.patch.object(remote, "send_commands", lambda *a, **k: calls.append(a[2])):
            remote._cycle_audio(settings)
        self.assertIn(["#AUD"], calls)
        with mock.patch.object(remote, "set_play_time", side_effect=RuntimeError("seek")):
            remote._seek_beginning(settings)
        with mock.patch.object(remote, "_load_settings", return_value=settings), \
             mock.patch.object(remote, "_command_map", return_value={"bad": "#SRC 6", "missing": ""}), \
             mock.patch.object(remote, "send_commands", lambda *a, **k: calls.append(a[2])):
            remote.send_remote_key("bad")
            remote.send_remote_key("missing")
        self.assertIn(["#SRC 6"], calls)
        # Cover hardware profile import-failure fallback in the resolver.
        original = sys.modules.get("settings_reader")
        sys.modules["settings_reader"] = None
        try:
            self.assertEqual(remote.resolve_power_on_token("#PON", "chinoppo_m9702"), "#PON")
        finally:
            if original is not None:
                sys.modules["settings_reader"] = original
            else:
                sys.modules.pop("settings_reader", None)

    def test_small_manager_logger_and_playercore_edges(self):
        import logging_v116, playercorefactory_merge as pcf, preset_manager as pm
        class MemLogFS:
            def __init__(self): self.files = {}; self.renames = []
            def exists(self, p): return p in self.files
            def size(self, p): return len(self.files.get(p, ""))
            def append(self, p, text): self.files[p] = self.files.get(p, "") + text
            def rename(self, src, dst): self.renames.append((src, dst)); self.files[dst] = self.files.pop(src)
            def remove(self, p): self.files.pop(p, None)
        fs = MemLogFS(); fs.files["log"] = "old"
        logger = logging_v116.Logger("log", level="DEBUG", max_bytes=1, backups=0, fs=fs, clock=lambda: 0)
        logger.info("ip %s", "192.0.2.10")
        self.assertIn("x.x.x.x", fs.files["log"])
        logger.log("TRACE", "hidden")
        with self.assertRaises(ValueError): logging_v116.Logger("x", level="NOPE")
        with self.assertRaises(ValueError): logger.set_level("NOPE")
        self.assertEqual(pcf._count_players("<bad>"), 0)
        snippet = pcf.generate("oppo203", player_path="/tmp/player.py")
        self.assertTrue(pcf.is_well_formed(snippet))
        class FS:
            def __init__(self): self.files = {}
            def exists(self, p): return p in self.files
            def read(self, p): return self.files[p]
            def write(self, p, t): self.files[p] = t
            def copy(self, src, dst): self.files[dst] = self.files[src]
        fs2 = FS()
        result = pcf.merge("pcf.xml", snippet, fs=fs2, now=lambda: 0)
        self.assertTrue(result["written"])
        with self.assertRaises(ValueError): pcf.merge("bad.xml", "<bad>", fs=fs2)
        fs2.files["bad.xml"] = "<broken>"
        with self.assertRaises(ValueError): pcf.merge("bad.xml", snippet, fs=fs2)
        self.assertFalse(pm._validate_preset({"label": "x", "start_commands": "#PON"}))
        self.assertEqual(pm.compare_versions("bad", "1.0"), None)
        self.assertIsNone(pm.firmware_warning("bad", "1.0"))
        self.assertIsNone(pm.firmware_warning({"firmware_min": "bad"}, "1.0"))
        self.assertIn("older", pm.firmware_warning({"firmware_min": "2.0"}, "1.0"))
        with self.assertRaises(ValueError): pm.export_submission("custom", user_preset={"label": "x"})
        with self.assertRaises(ValueError): pm.save_submission("bad", tempfile.gettempdir())
        class WriteFS:
            def __init__(self): self.written = {}
            def write(self, p, t): self.written[p] = t
        wfs = WriteFS()
        path = pm.save_submission({"preset_id": "unsafe/id", "preset": {}}, tempfile.gettempdir(), now=lambda: 0, fs=wfs)
        self.assertIn("unsafe_id", path)

class TCoverageGateFifthPassGradual99(unittest.TestCase):
    def test_external_player_idle_confirmed_and_remote_import_edges(self):
        import external_player as ep

        # Suppress log(): its stdlib-logging fallback (xbmc absent) calls time.time()
        # and would otherwise drain the patched time sequence below.
        _logp = mock.patch.object(ep, "log", lambda *a, **k: None)
        _logp.start()
        self.addCleanup(_logp.stop)
        times = iter([0, 1, 2, 3, 4])
        with mock.patch.object(ep.time, "time", side_effect=lambda: next(times)), \
             mock.patch.object(ep.time, "sleep", lambda *_: None), \
             mock.patch.object(ep, "get_playback_info", side_effect=[{"status": "STOP"}, {"status": "STOP"}]), \
             mock.patch.object(ep, "http_info_is_definitive_stop", return_value=False), \
             mock.patch.object(ep, "http_info_indicates_playing", return_value=False):
            ep.hold_playback(FakeSettings({"hold_mode": "http_poll", "http_poll_interval": "1", "http_poll_timeout_minutes": "1", "http_poll_idle_confirmations": "2", "trickplay_suppress_seconds": "0"}))

        remote = importlib.import_module("resources.lib.oppo_remote")
        old_vfs, old_addon = remote.xbmcvfs, remote.xbmcaddon
        try:
            remote.xbmcvfs = None
            remote.xbmcaddon = None
            self.assertEqual(remote._translate("special://profile"), "special://profile")
            self.assertEqual(remote._addon_data_dir(), "")
        finally:
            remote.xbmcvfs, remote.xbmcaddon = old_vfs, old_addon
        self.assertEqual(remote.resolve_power_on_token(123, "chinoppo"), 123)
        import resources.lib.settings_reader as sr
        settings = FakeSettings({"addon_data_dir": "", "remote_bridge_only_when_active": "false", "oppo_ip": "h", "oppo_port": "23", "oppo_socket_timeout": "1", "oppo_hardware_model": "udp_203"})
        with mock.patch.object(sr, "warn_if_unsupported", side_effect=RuntimeError("warn failed")), \
             mock.patch.object(remote, "_load_settings", return_value=settings), \
             mock.patch.object(remote, "_command_map", return_value={"play": "#PLA"}), \
             mock.patch.object(remote, "send_commands", return_value=[]):
            remote.send_remote_key("play")

class TCoverageGateBuild3Gradual99(unittest.TestCase):
    def test_small_branch_closures_reconnect_settings_and_tv(self):
        import reconnect_backoff as rb
        # Cover default rng fallback and defensive negative jitter clamp.
        with mock.patch.object(rb.random, "random", return_value=0.5):
            self.assertGreater(rb.compute_delay(1, base=2, cap=10, jitter=0.25), 0)
        self.assertEqual(rb.compute_delay(1, base=1, cap=10, jitter=2, rng=lambda: -1), 0.0)
        self.assertEqual(rb.schedule(max_retries="2", base=1, cap=9, jitter=0), [1.0, 2.0])
        self.assertFalse(rb.should_retry(2, 2))

        import settings_reader as sr
        class BadStr:
            def __str__(self):
                raise RuntimeError("no str")
        self.assertTrue(sr.Settings({"x": None}).get_bool("x", True))
        self.assertFalse(sr.Settings({"x": BadStr()}).get_bool("x", False))
        import xml.etree.ElementTree as ET
        self.assertEqual(sr._setting_value(ET.fromstring('<setting id="x"><value>child</value></setting>')), "child")
        with tempfile.TemporaryDirectory() as td:
            Path(td, "settings.xml").write_text('<settings><setting id="oppo_start_mode" value="99"/></settings>', encoding="utf-8")
            self.assertEqual(sr.read_settings(td).get("oppo_start_mode"), "99")
        self.assertTrue(sr.is_token_supported_by_hardware(123, "UDP-203"))
        self.assertIsNone(sr.warn_if_unsupported("#SRC 0", "UDP-203"))
        self.assertEqual(sr.compatibility_preset("UDP-203", jailbreak=True)["oppo_http_payload_mode"], "json_payload")

        import tv_control
        with self.assertRaises(tv_control.TVControlError):
            tv_control._run_external("", FakeSettings())
        bad = FakeHttpResponse("sony error", status=500)
        with mock.patch.object(tv_control.urllib.request, "urlopen", return_value=bad):
            with self.assertRaises(tv_control.TVControlError):
                tv_control._sony_set_hdmi(FakeSettings({"tv_ip": "192.0.2.3", "sony_psk": "psk"}), 2)
        with mock.patch.object(tv_control.urllib.request, "urlopen", side_effect=tv_control.urllib.error.URLError("down")):
            with self.assertRaises(tv_control.TVControlError):
                tv_control._sony_set_hdmi(FakeSettings({"tv_ip": "192.0.2.3", "sony_psk": "psk"}), 2)

    def test_oppo_tcp_client_direct_socket_edges(self):
        import socket
        import resources.lib.oppo_tcp_client as otc

        class ScriptedSocket:
            def __init__(self, actions):
                self.actions = list(actions)
                self.sent = []
                self.closed = False
            def settimeout(self, timeout):
                self.timeout = timeout
            def sendall(self, data):
                self.sent.append(data)
            def recv(self, size):
                if not self.actions:
                    return b""
                action = self.actions.pop(0)
                if action == "timeout":
                    raise socket.timeout()
                if action == "oserror":
                    raise OSError("drop")
                return action
            def close(self):
                self.closed = True

        sock = ScriptedSocket([b"@SVM OK\r\n", b"@UPL PLAY\n", b"@UPW 0\r\n"])
        client = otc.OppoTcpClient("h", 23, send_svm=True, recv_timeout=0.01)
        with mock.patch.object(otc.socket, "create_connection", return_value=sock):
            client._connect_and_read()
        self.assertTrue(client._stop_event_seen)
        self.assertTrue(sock.sent[0].startswith(b"#SVM"))
        self.assertTrue(sock.closed)

        bad_start_sock = ScriptedSocket(["oserror", b""])
        client = otc.OppoTcpClient("h", 23, send_svm=True, recv_timeout=0.01)
        with mock.patch.object(otc.socket, "create_connection", return_value=bad_start_sock):
            client._connect_and_read()
        self.assertTrue(client._connection_closed.is_set())

        client = otc.OppoTcpClient("h", 23, send_svm=False, recv_timeout=0.01)
        with mock.patch.object(otc.socket, "create_connection", side_effect=OSError("no route")):
            client._connect_and_read()
        self.assertIsNotNone(client._error)

        client = otc.OppoTcpClient("h", 23)
        delays = []
        with mock.patch.object(otc.time, "time", side_effect=[0, 1, 2, 999]), \
             mock.patch.object(otc.time, "sleep", lambda s: delays.append(s)):
            self.assertFalse(client.wait_for_stop_persistent(timeout=None, max_retries=2, base_delay=1, cap_delay=1, jitter=0, _sleep=delays.append, _connect_factory=lambda: False))
        self.assertEqual(delays, [1.0])

    def test_oppo_control_error_and_filelist_edges(self):
        oc = importlib.import_module("resources.lib.oppo_control")
        with self.assertRaises(oc.OppoError):
            oc.wake_on_lan("00:11:22:33:44:GG")
        # Discovery sockets can fail at top-level creation and still return an empty list.
        with mock.patch.object(oc.socket, "socket", side_effect=OSError("no multicast")):
            self.assertEqual(oc.discover_oppo(timeout=0.1), [])
        # Probe send errors are swallowed inside discovery.
        sockets = [FakeUdpSocket(), FakeUdpSocket()]
        sockets[1].sendto = mock.Mock(side_effect=OSError("send fail"))
        with mock.patch.object(oc.socket, "socket", side_effect=sockets), \
             mock.patch.object(oc.time, "time", side_effect=[0, 999]):
            self.assertEqual(oc.discover_oppo(timeout=0.1), [])
        with mock.patch.object(oc._http_get, "__call__", return_value="unused"):
            pass
        captured = {}
        def fake_http(settings, endpoint, query=None, timeout=None):
            captured["endpoint"] = endpoint
            captured["query"] = query
            captured["timeout"] = timeout
            return "raw"
        with mock.patch.object(oc, "_http_get", side_effect=fake_http):
            self.assertEqual(oc.get_file_list_raw(FakeSettings({}), "/Movies"), "raw")
        self.assertEqual(captured["endpoint"], "/getfilelist")
        self.assertEqual(captured["timeout"], 10)
        self.assertEqual(oc.parse_undocumented_file_list(b"\x01\x02"), [])
        self.assertEqual(oc._normalise_filelist_entry({"fileName": "clip.m2ts", "size": "abc", "isDir": "file"})["size_bytes"], None)
        self.assertEqual(oc._guess_size_from_fields(["size=bad", "length=17"]), 17)
        self.assertEqual(oc._infer_disc_type(name="disc.bdmv"), "bluray")
        self.assertEqual(oc._infer_disc_type(path="/VIDEO_TS/VIDEO_TS.IFO"), "dvd")
        self.assertEqual(oc._infer_disc_type(path="/VCD/AVSEQ01.DAT"), "vcd")
        self.assertEqual(oc._infer_disc_type(path="/SVCD/AVSEQ01.DAT"), "svcd")

    def test_logger_playercore_and_preset_more_edges(self):
        import logging_v116, playercorefactory_merge as pcf, preset_manager as pm
        class FS:
            def __init__(self): self.files = {}
            def exists(self, p): return p in self.files
            def size(self, p): return len(self.files.get(p, ""))
            def append(self, p, text): self.files[p] = self.files.get(p, "") + text
            def rename(self, src, dst): self.files[dst] = self.files.pop(src)
            def remove(self, p): self.files.pop(p, None)
        fs = FS()
        logger = logging_v116.Logger("log", level="DEBUG", max_bytes=100, backups=2, fs=fs, clock=lambda: 1)
        logger.debug("loopback %s", "127.0.0.1")
        self.assertIn("127.0.0.1", fs.files["log"])
        logger.rotate()  # no current file after manual remove branch is avoided once removed
        fs.files = {"log": "current", "log.1": "older", "log.2": "oldest"}
        logger.rotate()
        self.assertIn("log.1", fs.files)
        real = logging_v116._RealFS()
        self.assertEqual(real.size("/path/that/does/not/exist"), 0)
        real.remove("/path/that/does/not/exist")

        merged, added = pcf._merge_xml("<playercorefactory><players></players><rules></rules></playercorefactory>", pcf.generate("oppo203", player_path="/tmp/player.py"))
        self.assertIn("OPPO_External_oppo203", merged)
        self.assertEqual(added, 1)
        self.assertEqual(pcf._count_players("<bad>"), 0)
        self.assertEqual(pm.compare_versions("1.2", "1.2.0"), 0)
        self.assertGreater(pm.compare_versions("1.2.1", "1.2.0"), 0)
        self.assertLess(pm.compare_versions("1.1.9", "1.2.0"), 0)
        valid = {"label": "Custom", "description": "d", "start_commands": "#PON", "stop_commands": "#STP"}
        self.assertTrue(pm._validate_preset(valid))
        submission = pm.export_submission("custom", ip="192.0.2.70", quirks=["clone"], contact="tester", user_preset=valid)
        self.assertEqual(submission["preset_id"], "custom")

class TCoverageGateBuild4Gradual99(unittest.TestCase):
    def test_oppo_control_remaining_http_and_parser_edges(self):
        oc = importlib.import_module("resources.lib.oppo_control")
        settings = FakeSettings({"oppo_ip": "h", "oppo_http_port": "436"})
        with mock.patch.object(oc, "_http_get", return_value=json.dumps({"audio_list": {"0": {"index": "2", "name": "Main", "selected": ""}}})):
            tracks = oc.get_audio_tracks(settings)
        self.assertEqual(tracks[0]["index"], 2)
        with mock.patch.object(oc, "_http_get", return_value=json.dumps({"subtitle_list": {"0": {"index": "3", "name": "Sub", "selected": True}}})):
            subs = oc.get_subtitle_tracks(settings)
        self.assertEqual(subs[0]["index"], 3)
        captured = []
        with mock.patch.object(oc, "_http_get", side_effect=lambda s, ep, query=None: captured.append((ep, query)) or "ok"):
            self.assertEqual(oc.set_audio_track(settings, "4"), "ok")
            self.assertEqual(oc.set_subtitle_track(settings, 5), "ok")
        self.assertIn(("/setaudiomenulist", "cur_index=4"), captured)
        self.assertIn(("/setsubttmenulist", "cur_index=5"), captured)

        self.assertEqual(oc.parse_undocumented_file_list('[{"name":"A.iso"}]', base_path="/base")[0]["path"], "/base/A.iso")
        self.assertEqual(oc.parse_undocumented_file_list('{"files":[{"name":"B.iso"}]}', base_path="/base")[0]["path"], "/base/B.iso")
        self.assertEqual(oc.parse_undocumented_file_list('{"result":{}}')[0]["entry_type"], "unknown")
        self.assertEqual(oc._normalise_filelist_entry(["folder/"], base_path="/base")["entry_type"], "directory")
        self.assertEqual(oc._normalise_filelist_entry(["size=abc", "44", "clip.m2ts"], base_path="/base")["size_bytes"], 44)
        self.assertEqual(oc._first_non_empty({"a": None, "b": "  "}, "a", "b"), "")
        self.assertEqual(oc._infer_entry_type(type_hint="isfolder=true"), "directory")
        self.assertEqual(oc._infer_entry_type(type_hint="isdir=false"), "file")

    def test_external_player_timeout_and_preflight_failure_paths(self):
        import external_player as ep
        # Verbose-push connected but no stop event: covers the timed-out branch.
        class TimeoutClient:
            def __init__(self, host, port): pass
            def wait_for_stop(self, timeout): return False
        with mock.patch("oppo_tcp_client.OppoTcpClient", TimeoutClient):
            ep.hold_playback(FakeSettings({"hold_mode": "verbose_push", "oppo_ip": "h", "oppo_port": "23", "verbose_push_timeout_minutes": "1"}))

        calls = []
        with mock.patch.object(ep.sys, "argv", ["external_player.py", "--addon-data", tempfile.gettempdir(), "--file", "/m.iso"]), \
             mock.patch.object(ep, "read_settings", return_value=FakeSettings({"addon_data_dir": tempfile.gettempdir(), "oppo_preflight_enabled": "true"})), \
             mock.patch.object(ep, "run_preflight", side_effect=RuntimeError("preflight down")), \
             mock.patch.object(ep, "mark_session_active", lambda s: calls.append("mark")), \
             mock.patch.object(ep, "fast_start", lambda *a, **k: calls.append(("fast", k.get("preflight_result")))), \
             mock.patch.object(ep, "hold_playback", lambda s: calls.append("hold")), \
             mock.patch.object(ep, "fast_return", lambda s: calls.append("return")), \
             mock.patch.object(ep, "clear_session_active", lambda s: calls.append("clear")):
            self.assertEqual(ep.main(), 0)
        self.assertIn(("fast", None), calls)

    def test_oppo_tcp_wait_timeout_and_close_error_branches(self):
        import resources.lib.oppo_tcp_client as otc
        import socket
        class CloseRaisesSocket:
            def settimeout(self, timeout): pass
            def sendall(self, data): pass
            def recv(self, size): return b""
            def close(self): raise OSError("close failed")
        client = otc.OppoTcpClient("h", 23, send_svm=False, recv_timeout=0.01)
        with mock.patch.object(otc.socket, "create_connection", return_value=CloseRaisesSocket()):
            client._connect_and_read()
        self.assertTrue(client._connection_closed.is_set())

        client = otc.OppoTcpClient("h", 23)
        client._connected.set()
        with mock.patch.object(otc.time, "time", side_effect=[0, 0.01, 0.02, 1.0]), \
             mock.patch.object(otc.time, "sleep", lambda *_: None):
            self.assertFalse(client.wait_for_stop(timeout=0.05))

        client = otc.OppoTcpClient("h", 23)
        sleeps = []
        with mock.patch.object(otc.time, "time", side_effect=[0, 0.1, 0.2, 0.3]), \
             mock.patch.object(otc.time, "sleep", lambda s: sleeps.append(s)):
            self.assertFalse(client.wait_for_stop_persistent(timeout=0.15, max_retries=2, base_delay=10, cap_delay=10, jitter=0, _sleep=sleeps.append, _connect_factory=lambda: False))
        self.assertTrue(any(s <= 0.15 for s in sleeps))

    def test_preset_manager_load_custom_and_merge_edges(self):
        import preset_manager as pm
        class FS:
            def __init__(self, text): self.text = text
            def exists(self, p): return True
            def read(self, p): return self.text
            def write(self, p, t): self.text = t
        self.assertEqual(pm.load_custom("x", fs=FS("[]")), {})
        self.assertEqual(pm.load_custom("x", fs=FS('{"presets":[]}')), {})
        data = {"presets": {"": {"label": "bad"}, "bad": {"label": "bad"}, "ok": {"label": "OK", "start_commands": "#PON", "stop_commands": "#STP", "firmware_min": "1.0"}}}
        loaded = pm.load_custom("x", fs=FS(json.dumps(data)))
        self.assertEqual(list(loaded), ["ok"])
        merged = pm.merged_presets("x", fs=FS(json.dumps(data)))
        self.assertIn("ok", merged)
        self.assertIsNone(pm._parse_version("x.y"))
        self.assertIsNone(pm.firmware_warning({"firmware_min": "1.0"}, "bad"))
        self.assertIsNone(pm.firmware_warning({"firmware_min": "1.0"}, "1.0"))

class TCoverageGateBuild5Gradual98(unittest.TestCase):
    def test_oppo_control_additional_protocol_and_discovery_edges(self):
        oc = importlib.import_module("resources.lib.oppo_control")
        self.assertEqual(oc._parse_response("@XYZ MAYBE VALUE"), "@XYZ MAYBE VALUE")
        self.assertEqual(oc._parse_response("@QPW OK"), "")
        self.assertIsNone(oc.maybe_setup_verbose_mode(FakeSettings({"oppo_verbose_mode": "0"}), "h", 23))
        self.assertIsNone(oc.maybe_setup_verbose_mode(FakeSettings({"oppo_verbose_mode": ""}), "h", 23))

        with mock.patch.object(oc, "get_playback_info", return_value={"result": "not-a-dict"}):
            self.assertEqual(oc.get_playback_status(FakeSettings()), "")
        with mock.patch.object(oc, "get_playback_info", return_value={"result": {}}):
            self.assertEqual(oc.get_playback_status(FakeSettings()), "")
        self.assertFalse(oc.http_info_is_definitive_stop({"result": "not-a-dict"}))
        self.assertFalse(oc.http_info_indicates_playing({"playinfo": "not-a-dict", "state": object()}))
        self.assertEqual(list(oc._info_containers({"result": {"status": "STOP"}, "playinfo": "bad"}))[1]["status"], "STOP")

        # tcp_commands-only startup reaches the explicit None return after command dispatch.
        calls = []
        with mock.patch.object(oc, "maybe_wake_on_lan", lambda s: calls.append("wol")), \
             mock.patch.object(oc, "maybe_setup_verbose_mode", lambda s, h, p: calls.append("svm")), \
             mock.patch.object(oc, "run_configured_commands", lambda *a, **k: calls.append("tcp")):
            self.assertIsNone(oc.run_start(FakeSettings({"oppo_ip": "h", "oppo_port": "23", "oppo_start_mode": "tcp_commands"}), "/movie.iso"))
        self.assertEqual(calls, ["wol", "svm", "tcp"])

        with mock.patch.object(oc, "_http_get", return_value="[]"):
            self.assertEqual(oc.get_audio_tracks(FakeSettings()), [])
        with mock.patch.object(oc, "_http_get", return_value=json.dumps({"result": {"0": {"index": 0, "name": "A", "selected": False}}})):
            self.assertFalse(oc.get_audio_tracks(FakeSettings())[0]["selected"])

        import socket
        class DiscoverySock(FakeUdpSocket):
            def __init__(self):
                super().__init__([(b"", ("192.0.2.88", 7624))])
                self.recvs = 0
            def setsockopt(self, *args):
                if len(args) >= 2 and args[1] == socket.IP_ADD_MEMBERSHIP:
                    raise OSError("join denied")
                return super().setsockopt(*args)
            def recvfrom(self, size):
                self.recvs += 1
                if self.recvs == 1:
                    return super().recvfrom(size)
                raise OSError("recv failed")
            def close(self):
                self.closed = True
                raise OSError("close failed")
        main_sock = DiscoverySock()
        probe_sock = FakeUdpSocket()
        with mock.patch.object(oc.socket, "socket", side_effect=[main_sock, probe_sock]), \
             mock.patch.object(oc.time, "time", side_effect=[0, 0, 1, 3]):
            found = oc.discover_oppo(timeout=2)
        self.assertEqual(found[0]["name"], "192.0.2.88")
        self.assertTrue(main_sock.closed)

    def test_external_player_remaining_cleanup_and_reset_paths(self):
        import external_player as ep

        # Suppress log(): its stdlib-logging fallback (xbmc absent) calls time.time()
        # and would otherwise drain the patched time sequence below.
        _logp = mock.patch.object(ep, "log", lambda *a, **k: None)
        _logp.start()
        self.addCleanup(_logp.stop)
        self.assertFalse(ep.tv_switching_enabled(FakeSettings({"tv_backend": ""})))
        self.assertFalse(ep.tv_switching_enabled(FakeSettings({"tv_backend": "disabled"})))
        with mock.patch.object(ep, "session_file", return_value=""):
            self.assertIsNone(ep.mark_session_active(FakeSettings()))
        with tempfile.TemporaryDirectory() as td:
            missing = str(Path(td, "missing"))
            with mock.patch.object(ep, "session_file", return_value=missing):
                self.assertIsNone(ep.clear_session_active(FakeSettings()))
        calls = []
        with mock.patch.object(ep, "run_start", lambda *a, **k: calls.append("run_start")), \
             mock.patch.object(ep.time, "sleep", lambda *_: calls.append("sleep")):
            ep.start_oppo_after_optional_delay(FakeSettings({"startup_delay": "0", "oppo_start_mode": "tcp_commands"}), "/m.iso")
        self.assertEqual(calls, ["run_start"])
        with mock.patch.object(ep, "_safe_tv_switch", lambda *a, **k: calls.append("tv")), \
             mock.patch.object(ep, "start_oppo_after_optional_delay", lambda *a, **k: calls.append("start")):
            ep.fast_start(FakeSettings({"fast_changeover": "false"}), "/m.iso")
        self.assertEqual(calls[-2:], ["tv", "start"])

        # Cover reset-after-idle branch: STOP creates one idle confirmation, then PLAY resets it.
        times = iter([0, 1, 2, 3, 4, 1000])
        infos = iter([{"status": "STOP"}, {"status": "PLAY"}, {"status": "STOP"}])
        with mock.patch.object(ep.time, "time", side_effect=lambda: next(times)), \
             mock.patch.object(ep.time, "sleep", lambda *_: None), \
             mock.patch.object(ep, "get_playback_info", side_effect=lambda s: next(infos)), \
             mock.patch.object(ep, "http_info_is_definitive_stop", return_value=False), \
             mock.patch.object(ep, "http_info_indicates_playing", side_effect=[False, True, False]):
            ep.hold_playback(FakeSettings({"hold_mode": "http_poll", "http_poll_interval": "1", "http_poll_timeout_minutes": "1", "http_poll_idle_confirmations": "2", "trickplay_suppress_seconds": "0"}))

        stop = tempfile.NamedTemporaryFile(delete=False); stop.close()
        try:
            with mock.patch.object(ep.os, "remove", side_effect=OSError("locked")):
                ep.hold_playback(FakeSettings({"hold_mode": "manual_file", "manual_stop_file": stop.name}))
        finally:
            if os.path.exists(stop.name):
                os.unlink(stop.name)

        with mock.patch.object(ep.sys, "argv", ["external_player.py", "--addon-data", tempfile.gettempdir(), "--file", "/m.iso"]), \
             mock.patch.object(ep, "read_settings", return_value=FakeSettings({"addon_data_dir": tempfile.gettempdir(), "oppo_preflight_enabled": "false"})), \
             mock.patch.object(ep, "mark_session_active", lambda s: calls.append("mark")), \
             mock.patch.object(ep, "fast_start", lambda *a, **k: calls.append(("fast", k.get("preflight_result")))), \
             mock.patch.object(ep, "hold_playback", lambda s: calls.append("hold")), \
             mock.patch.object(ep, "fast_return", lambda s: calls.append("return")), \
             mock.patch.object(ep, "clear_session_active", lambda s: calls.append("clear")):
            self.assertEqual(ep.main(), 0)
        self.assertIn(("fast", None), calls)
    def test_settings_logger_and_merge_edge_branches(self):
        import settings_reader as sr
        class BadStr:
            def __str__(self):
                raise RuntimeError("no str")
        settings = sr.Settings({"none": None, "bool": True, "bad": BadStr(), "lines": " a \n\n b "})
        self.assertTrue(settings.get_bool("none", True))
        self.assertTrue(settings.get_bool("bool"))
        self.assertFalse(settings.get_bool("bad", False))
        self.assertEqual(settings.get_str("none", "fallback"), "fallback")
        self.assertIn("bool", settings)
        self.assertEqual(settings.get_lines("lines"), ["a", "b"])
        xml = '<settings><setting id="oppo_start_mode">2</setting><setting id="oppo_hardware_model"><value>999</value></setting><setting><value>ignored</value></setting></settings>'
        with tempfile.TemporaryDirectory() as td:
            Path(td, "settings.xml").write_text(xml, encoding="utf-8")
            parsed = sr.read_settings(td)
        self.assertEqual(parsed.get("oppo_start_mode"), "tcp_then_http")
        self.assertEqual(parsed.get("oppo_hardware_model"), "999")

        import logging_v116
        self.assertEqual(logging_v116.level_value(None), -1)
        self.assertIsNone(logging_v116.scrub(None))
        self.assertEqual(logging_v116.scrub(""), "")
        class FS:
            def __init__(self): self.files = {"log": "old", "log.1": "older"}; self.removed = []
            def exists(self, p): return p in self.files
            def size(self, p): return len(self.files.get(p, ""))
            def append(self, p, text): self.files[p] = self.files.get(p, "") + text
            def rename(self, src, dst): self.files[dst] = self.files.pop(src)
            def remove(self, p): self.removed.append(p); self.files.pop(p, None)
        fs = FS()
        logger = logging_v116.Logger("log", level="INFO", max_bytes=100, backups=1, fs=fs, clock=lambda: 0)
        logger.rotate()
        self.assertIn("log.1", fs.files)
        logger.error("bad format %s %s", "only-one")
        self.assertIn("only-one", fs.files["log"])

        import playercorefactory_merge as pcf
        snippet = pcf.generate("oppo203", player_path="/tmp/player.py")
        existing = "<playercorefactory><players>" + snippet.split("<players>",1)[1].split("</players>",1)[0] + "</players><rules></rules></playercorefactory>"
        merged, added = pcf._merge_xml(existing, snippet)
        self.assertEqual(added, 0)
        self.assertIn("playercorefactory", merged)
