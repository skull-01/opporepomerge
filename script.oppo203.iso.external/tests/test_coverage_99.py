"""Final pre-merge 99% coverage hardening tests.

These tests cover meaningful defensive and edge paths using local fakes only.
They do not require real Kodi, OPPO, TV, ADB, sockets, or external services.
"""
import io
import os
from contextlib import redirect_stdout
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "tests" / "_stubs"
LIB = ROOT / "resources" / "lib"
for path in (str(STUBS), str(LIB), str(ROOT)):
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


class TestFinal99CoveragePaths(unittest.TestCase):
    def test_adb_and_arch_default_paths(self):
        import adb_control
        import arch_benchmark

        calls = []

        class Proc:
            returncode = 0
            stdout = "ok\n"
            stderr = ""

        def runner(args, **kwargs):
            calls.append(args)
            return Proc()

        settings = FakeSettings({
            "adb_path": "adb",
            "tv_ip": "192.0.2.10",
            "tv_adb_port": "5555",
            "adb_connect_before_switch": "false",
        })
        self.assertEqual(adb_control.switch_input(settings, "input keyevent 3", runner=runner), "ok")
        self.assertEqual(calls, [["adb", "-s", "192.0.2.10:5555", "shell", "input", "keyevent", "3"]])

        result = arch_benchmark.benchmark("external", trials=1, probe=lambda candidate: None)
        self.assertTrue(result["all_ok"])
        self.assertEqual(result["candidate"], "external")

    def test_discovery_and_realfs_edges(self):
        import discovery

        class TruthyBlank:
            def __bool__(self):
                return True
            def __str__(self):
                return ""

        self.assertIsNone(discovery.parse_ssdp_response(TruthyBlank()))
        parsed = discovery.parse_ssdp_response("NOTIFY * HTTP/1.1\nNOT-A-HEADER\nSERVER: OPPO UDP-203\n")
        self.assertIsNone(parsed["ip"])
        self.assertEqual(discovery.discover(ssdp=lambda: ["NOTIFY * HTTP/1.1\nSERVER: OPPO UDP-203\n"], now=1.0), [])

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "cache", "devices.json")
            cache = discovery.DeviceCache(path=path, clock=lambda: 10.0)
            cache.add({"ip": "192.0.2.20", "port": 23, "vendor": "OPPO", "model": "UDP-203"})
            self.assertTrue(cache.save())
            self.assertTrue(os.path.exists(path))
            loaded = discovery.DeviceCache(path=path)
            self.assertTrue(loaded.load())
            self.assertEqual(loaded.all()[0]["ip"], "192.0.2.20")

    def test_logging_realfs_and_rotation_edges(self):
        import logging_v116

        with tempfile.TemporaryDirectory() as td:
            log_path = os.path.join(td, "logs", "kodi.log")
            fs = logging_v116._RealFS()
            self.assertEqual(fs.size(log_path), 0)
            fs.append(log_path, "ip 192.168.1.44\n")
            self.assertIn("192.168.1.44", fs.read(log_path))
            old_dst = log_path + ".1"
            fs.append(old_dst, "old")
            fs.rename(log_path, old_dst)
            self.assertIn("ip", fs.read(old_dst))
            fs.remove(old_dst)
            fs.remove(old_dst)
            self.assertFalse(fs.exists(old_dst))

        class FS:
            def __init__(self): self.files = {}
            def exists(self, p): return p in self.files
            def size(self, p): return len(self.files.get(p, ""))
            def append(self, p, text): self.files[p] = self.files.get(p, "") + text
            def rename(self, src, dst): self.files[dst] = self.files.pop(src)
            def remove(self, p): self.files.pop(p, None)
        fs = FS()
        logger = logging_v116.Logger("missing", fs=fs)
        logger.rotate()
        self.assertEqual(fs.files, {})

    def test_oppo_control_defensive_helpers_and_branches(self):
        import oppo_control as oc

        self.assertEqual(oc._parse_response("@NOP OK"), "")
        with mock.patch.object(oc, "get_playback_info", return_value=[]):
            self.assertEqual(oc.get_playback_status(FakeSettings({})), "")
        with mock.patch.object(oc, "get_playback_info", return_value={"result": "not-a-dict", "playinfo": {"status": "play"}}):
            self.assertEqual(oc.get_playback_status(FakeSettings({})), "PLAY")
        self.assertFalse(oc.http_info_is_definitive_stop({"result": "not-a-dict"}))
        self.assertTrue(oc.http_info_indicates_playing({"result": "not-a-dict", "playinfo": {"e_play_status": "56"}}))
        self.assertFalse(oc.http_info_indicates_playing({"result": "not-a-dict", "playinfo": {"e_play_status": "garbage"}}))

        original = sys.modules.get("settings_reader")
        sys.modules["settings_reader"] = types.SimpleNamespace(hardware_profile=lambda model: (_ for _ in ()).throw(RuntimeError("boom")))
        try:
            self.assertEqual(oc._resolve_hardware_wake_command(FakeSettings({"oppo_hardware_model": "M9702"}), "#PON"), "#PON")
        finally:
            if original is not None:
                sys.modules["settings_reader"] = original
            else:
                sys.modules.pop("settings_reader", None)

        with mock.patch.object(oc, "_http_get", return_value='{"audio_list":{"a":{"index":1,"name":"Main"}}}'):
            self.assertEqual(oc.get_audio_tracks(FakeSettings({}))[0]["name"], "Main")
        self.assertFalse(oc._first_bool({"flag": "file"}, "missing", "flag"))
        self.assertEqual(oc._guess_size_from_fields(["size=bad", "42"]), 42)
        self.assertEqual(oc._infer_entry_type(name="Folder/"), "directory")

    def test_external_player_manual_file_and_main_module(self):
        import external_player as ep

        with tempfile.NamedTemporaryFile(delete=False) as fh:
            stop_file = fh.name
        try:
            ep.hold_playback(FakeSettings({"hold_mode": "manual_file", "manual_stop_file": stop_file}))
            self.assertFalse(os.path.exists(stop_file))
        finally:
            if os.path.exists(stop_file):
                os.remove(stop_file)


    def test_oppo_tcp_client_line_split_and_oserror_paths(self):
        import oppo_tcp_client

        class TimeoutThenOSErrorSock:
            def __init__(self): self.calls = 0; self.closed = False
            def sendall(self, data): pass
            def recv(self, n):
                self.calls += 1
                if self.calls == 1:
                    raise oppo_tcp_client.socket.timeout()
                raise OSError("down")
            def close(self): self.closed = True

        sock = TimeoutThenOSErrorSock()
        sock.settimeout = lambda timeout: None
        client = oppo_tcp_client.OppoTcpClient("127.0.0.1", 23, send_svm=False)
        with mock.patch.object(oppo_tcp_client.socket, "create_connection", return_value=sock):
            self.assertFalse(client.wait_for_stop(timeout=0.2))
        self.assertTrue(sock.closed)

    def test_playercorefactory_preset_and_settings_edges(self):
        import playercorefactory_merge as pcf
        import preset_manager as pm
        import settings_reader as sr

        snippet = pcf.generate("oppo203", player_path="/tmp/player.py")
        existing = "<playercorefactory></playercorefactory>"
        merged, added = pcf._merge_xml(existing, snippet)
        self.assertEqual(added, 1)
        self.assertIn("players", merged)
        self.assertEqual(pcf._count_players("<bad>"), 0)

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "custom.json")
            Path(path).write_text('{"presets":{"mine":{"label":"Mine","start_commands":"#PON","stop_commands":"#STP"}}}', encoding="utf-8")
            self.assertIn("mine", pm.load_custom(path))
            out = os.path.join(td, "nested", "out.json")
            pm._RealFS().write(out, "{}")
            self.assertEqual(Path(out).read_text(encoding="utf-8"), "{}")
        self.assertFalse(pm._validate_preset([]))
        self.assertIsNone(pm.compare_versions("bad", "1.0"))

        s = sr.Settings({})
        s["new_key"] = "value"
        self.assertEqual(s["new_key"], "value")
        self.assertTrue(sr.Settings({"x": None}).get_bool("x", True))
        elem = sr.ET.fromstring("<setting><value>child</value></setting>")
        self.assertEqual(sr._setting_value(elem), "child")

    def test_installer_wizard_and_filelist_branches(self):
        import installer

        fake_gui = installer.xbmcgui
        fake_addon = installer.ADDON
        original_path = list(sys.path)
        try:
            # Discovery: apply port 23 path.
            fake_gui.push_yesno(True)
            with mock.patch.dict(sys.modules, {"oppo_control": types.SimpleNamespace(discover_oppo=lambda timeout=5: [{"ip":"192.0.2.30","port":23,"name":"OPPO","raw":""}])}):
                installer.run_oppo_discovery()
            self.assertEqual(fake_addon.getSetting("oppo_ip"), "192.0.2.30")
            self.assertEqual(fake_addon.getSetting("oppo_port"), "23")

            # File-list diagnostic with lib path already present exercises the no-insert branch.
            lib_path = os.path.join(installer.ADDON.getAddonInfo("path"), "resources", "lib")
            if lib_path not in sys.path:
                sys.path.insert(0, lib_path)
            fake_addon.setSetting("oppo_experimental_filelist_enabled", "true")
            fake_oc = types.SimpleNamespace(
                get_file_list_raw=lambda settings, path="/": "raw",
                parse_undocumented_file_list=lambda raw, base_path=None: [{"name":"Movie.iso","entry_type":"file","is_dir":False,"is_file":True,"size_bytes":123,"disc_type":"iso","extension":"iso","path":"/Movie.iso"}],
            )
            fake_sr = types.SimpleNamespace(read_settings=lambda addon_data: FakeSettings({}))
            with mock.patch.dict(sys.modules, {"oppo_control": fake_oc, "settings_reader": fake_sr}):
                installer.run_experimental_filelist_diagnostic()
            self.assertTrue(any(call[0] == "textviewer" and "Movie.iso" in call[2] for call in fake_gui.calls()))

            # Main wizard failure with architecture already chosen skips fallback dialog.
            fake_addon.setSetting("wizard_completed", "false")
            fake_addon.setSetting("architecture_choice_made", "true")
            failing_w = types.SimpleNamespace(run_wizard=lambda: (_ for _ in ()).throw(RuntimeError("wizard fail")))
            with mock.patch.dict(sys.modules, {"wizard": failing_w}):
                fake_gui.push_select(-1)
                installer.main()
        finally:
            sys.path[:] = original_path

    def test_wizard_import_and_basic_branches(self):
        import wizard

        self.assertEqual(wizard._get(None, "missing", "fallback"), "fallback")
        result = wizard._run_benchmark("127.0.0.1", 23, trials=1, timer=iter([0, 1, 1, 2]).__next__)
        self.assertIn(result["recommendation"], ("external", "service", "tie"))

class TestFinal99AdditionalBranches(unittest.TestCase):
    def test_no_kodi_import_fallbacks(self):
        import builtins
        import importlib.util

        real_import = builtins.__import__
        def fake_import(name, *args, **kwargs):
            if name.startswith("xbmc"):
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        module_specs = [
            ("autoscript_helper_no_kodi", ROOT / "resources" / "lib" / "autoscript_helper.py"),
            ("i18n_no_kodi", ROOT / "resources" / "lib" / "i18n.py"),
            ("resources.lib.oppo_remote_no_kodi", ROOT / "resources" / "lib" / "oppo_remote.py"),
            ("wizard_no_kodi", ROOT / "resources" / "lib" / "wizard.py"),
        ]
        with mock.patch("builtins.__import__", side_effect=fake_import):
            for name, path in module_specs:
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                try:
                    spec.loader.exec_module(module)
                finally:
                    sys.modules.pop(name, None)

    def test_autoscript_cifs_without_credentials_and_wizard_cifs(self):
        import autoscript_helper as ah
        import xbmcgui

        body = ah.generate({"mount_type": "cifs", "mount_remote": "//nas/movies", "cifs_user": ""})
        self.assertIn("mount -t cifs", body)
        self.assertNotIn("username=", body)

        class Addon:
            def __init__(self): self.settings = {}; self.profile = tempfile.mkdtemp()
            def getAddonInfo(self, key): return self.profile if key == "profile" else ""
            def setSetting(self, k, v): self.settings[k] = v

        addon = Addon()
        xbmcgui.reset()
        xbmcgui.push_yesno(False)  # telnet
        xbmcgui.push_yesno(False)  # passwordless root
        xbmcgui.push_select(2)     # CIFS
        xbmcgui.push_input("//nas/movies")
        xbmcgui.push_input("")    # username: no password prompt branch
        xbmcgui.push_input(os.path.join(addon.profile, "heartbeat"))
        xbmcgui.push_yesno(False)  # ADB
        out = ah.run_autoscript_wizard(addon)
        self.assertTrue(os.path.exists(out))

    def test_more_oppo_control_branches(self):
        import oppo_control as oc

        self.assertEqual(oc._parse_response("@XYZ WAITING"), "@XYZ WAITING")
        with mock.patch.object(oc, "get_playback_info", return_value={"result": "bad"}):
            self.assertEqual(oc.get_playback_status(FakeSettings({})), "")
        self.assertFalse(oc.http_info_indicates_playing({"result": "bad"}))
        self.assertTrue(oc.http_info_indicates_playing({"playinfo": {"play_status": 0}}))
        with mock.patch.object(oc, "_http_get", side_effect=ValueError("bad json")):
            self.assertEqual(oc.get_subtitle_tracks(FakeSettings({})), [])
        with mock.patch.object(oc, "_http_get", return_value='{"subtitle_list":{"s":{"index":2,"name":"Sub"}}}'):
            self.assertEqual(oc.get_subtitle_tracks(FakeSettings({}))[0]["name"], "Sub")
        self.assertTrue(oc._first_bool({"flag": "0"}, "flag") is False)
        self.assertEqual(oc._infer_entry_type(path="/Movies/"), "directory")
        self.assertEqual(oc._infer_disc_type(name="movie.iso", extension="iso"), "iso")

        class FakeSock:
            def __init__(self, timeout=False): self.closed = False; self.timeout = timeout
            def setsockopt(self, *a): pass
            def settimeout(self, *a): pass
            def sendto(self, *a): pass
            def recvfrom(self, n): raise oc.socket.timeout()
            def close(self): self.closed = True
        made = []
        def fake_socket(*args):
            s = FakeSock(); made.append(s); return s
        with mock.patch.object(oc.socket, "socket", side_effect=fake_socket), \
             mock.patch.object(oc.time, "time", side_effect=[0, 1]):
            self.assertEqual(oc.discover_oppo(timeout=1), [])
        self.assertTrue(all(s.closed for s in made))

    def test_external_and_tcp_extra_branches(self):
        import external_player as ep
        import oppo_tcp_client

        states = [False, True]
        with mock.patch.object(ep.os.path, "exists", side_effect=lambda path: states.pop(0)), \
             mock.patch.object(ep.os, "remove"), \
             mock.patch.object(ep.time, "sleep") as sleep:
            ep.hold_playback(FakeSettings({"hold_mode": "manual_file", "manual_stop_file": "/tmp/stop"}))
        sleep.assert_called_once_with(2)

        c = oppo_tcp_client.OppoTcpClient("127.0.0.1", 23)
        c._handle_line("@UPL LOADING")
        self.assertFalse(c._stop_event_seen)

    def test_oppo_remote_stock_power_and_i18n_none_branch(self):
        import i18n
        from resources.lib import oppo_remote

        old_xbmcaddon = i18n.xbmcaddon
        i18n.xbmcaddon = None
        try:
            self.assertEqual(i18n.L(31000), "Welcome")
        finally:
            i18n.xbmcaddon = old_xbmcaddon

        with tempfile.TemporaryDirectory() as td:
            Path(td, "oppo203iso-active").write_text("1", encoding="utf-8")
            settings = FakeSettings({
                "addon_data_dir": td,
                "remote_bridge_only_when_active": "true",
                "oppo_remote_command_map": '{"power_on":"#PON"}',
                "oppo_hardware_model": "udp_203",
                "oppo_ip": "127.0.0.1",
                "oppo_port": "23",
                "oppo_socket_timeout": "0.01",
            })
            with mock.patch.object(oppo_remote, "_load_settings", return_value=settings), \
                 mock.patch.object(oppo_remote, "send_commands", return_value=["@OK"]) as send:
                oppo_remote.send_remote_key("power_on")
            self.assertEqual(send.call_args.args[2], ["#PON"])

    def test_playercorefactory_new_player_and_rules_and_settings_child_branch(self):
        import playercorefactory_merge as pcf
        import settings_reader as sr

        snippet = "<playercorefactory><players><player name='New'/></players><rules><rule name='R'/></rules></playercorefactory>"
        merged, added = pcf._merge_xml("<playercorefactory><players></players><rules></rules></playercorefactory>", snippet)
        self.assertEqual(added, 1)
        self.assertIn("rule", merged)
        elem = sr.ET.fromstring("<setting><child /><value>child</value></setting>")
        self.assertEqual(sr._setting_value(elem), "child")

class TestBuild7RawCoverageBranches(unittest.TestCase):
    """Extra branch tests for Build 7 raw line+branch coverage improvement."""

    def test_autoscript_wizard_no_mount_branch(self):
        import autoscript_helper as ah
        import xbmcgui

        class Addon:
            def __init__(self):
                self.profile = tempfile.mkdtemp()
            def getAddonInfo(self, key):
                return self.profile if key == "profile" else ""

        addon = Addon()
        xbmcgui.reset()
        xbmcgui.push_yesno(False)  # telnet
        xbmcgui.push_yesno(False)  # passwordless root
        xbmcgui.push_select(0)     # No mount: covers non-nfs/non-cifs wizard branch
        xbmcgui.push_input(os.path.join(addon.profile, "heartbeat"))
        xbmcgui.push_yesno(False)  # ADB
        out = ah.run_autoscript_wizard(addon)
        body = Path(out).read_text(encoding="utf-8")
        self.assertNotIn("mount -t", body)

    def test_external_player_http_poll_nondict_and_tcp_confirmation_branch(self):
        import external_player as ep

        # log() falls back to stdlib logging (which calls time.time()) when xbmc is
        # absent; suppress it so the patched time.time sequence reaches only the code
        # under test instead of being consumed by the logging fallback.
        _logp = mock.patch.object(ep, "log", lambda *a, **k: None)
        _logp.start()
        self.addCleanup(_logp.stop)

        settings = FakeSettings({
            "hold_mode": "http_poll",
            "http_poll_interval": "1",
            "http_poll_timeout_minutes": "1",
            "http_poll_idle_confirmations": "1",
            "trickplay_suppress_seconds": "0",
        })
        with mock.patch.object(ep, "get_playback_info", return_value=[]), \
             mock.patch.object(ep.time, "time", side_effect=[0, 0, 0]), \
             mock.patch.object(ep.time, "sleep") as sleep:
            ep.hold_playback(settings)
        sleep.assert_not_called()

        tcp_settings = FakeSettings({
            "hold_mode": "tcp_qpl_poll",
            "oppo_ip": "127.0.0.1",
            "oppo_port": "23",
            "oppo_socket_timeout": "0.1",
            "qpl_poll_interval": "1",
            "qpl_poll_timeout_minutes": "1",
            "qpl_poll_idle_confirmations": "2",
        })
        with mock.patch.object(ep, "query_playback_status", side_effect=["STOP", "STOP"]), \
             mock.patch.object(ep.time, "time", side_effect=[0, 0, 0, 0]), \
             mock.patch.object(ep.time, "sleep") as sleep:
            ep.hold_playback(tcp_settings)
        sleep.assert_called_once_with(1)

    def test_installer_discovery_apply_keeps_non_tcp_port_and_inserts_lib_path(self):
        import installer

        fake_gui = installer.xbmcgui
        fake_addon = installer.ADDON
        original_path = list(sys.path)
        try:
            fake_addon.setSetting("oppo_port", "23")
            fake_gui.push_yesno(True)
            with mock.patch.dict(sys.modules, {"oppo_control": types.SimpleNamespace(discover_oppo=lambda timeout=5: [{"ip":"192.0.2.77","port":7624,"name":"OPPO","raw":""}])}):
                installer.run_oppo_discovery()
            self.assertEqual(fake_addon.getSetting("oppo_ip"), "192.0.2.77")
            self.assertEqual(fake_addon.getSetting("oppo_port"), "23")

            fake_addon.setSetting("oppo_experimental_filelist_enabled", "true")
            lib_path = os.path.join(installer.ADDON.getAddonInfo("path"), "resources", "lib")
            sys.path[:] = [p for p in sys.path if p != lib_path]
            fake_oc = types.SimpleNamespace(
                get_file_list_raw=lambda settings, path: b"movie.iso\x00size=5",
                parse_undocumented_file_list=lambda raw, base_path=None: [{"entry_type":"file","name":"movie.iso","size_bytes":5,"extension":"iso","disc_type":"iso","path":"/movie.iso"}],
            )
            fake_sr = types.SimpleNamespace(read_settings=lambda addon_data: FakeSettings({}))
            with mock.patch.dict(sys.modules, {"oppo_control": fake_oc, "settings_reader": fake_sr}):
                installer.run_experimental_filelist_diagnostic()
            self.assertIn(lib_path, sys.path)
        finally:
            sys.path[:] = original_path

    def test_oppo_control_remaining_defensive_branches(self):
        import oppo_control as oc

        self.assertEqual(oc._parse_response("@QPW"), "@QPW")
        self.assertEqual(oc._filter_commands_for_mode(FakeSettings({}), "oppo_stop_commands", ["#STP"]), ["#STP"])
        self.assertEqual(oc._filter_commands_for_mode(FakeSettings({"oppo_already_on_mode": "false"}), "oppo_start_commands", ["#PON", "#PLA"]), ["#PON", "#PLA"])
        self.assertEqual(oc._join_base_path("", "movie.iso"), "movie.iso")
        self.assertEqual(oc._extension_for("folder/movie"), "")
        self.assertEqual(oc._infer_entry_type(type_hint="plain file"), "file")

        class TimeoutSock:
            def __init__(self): self.closed = False
            def setsockopt(self, *args): pass
            def settimeout(self, timeout): pass
            def sendto(self, data, addr): pass
            def recvfrom(self, size): raise oc.socket.timeout()
            def close(self): self.closed = True
        sock = TimeoutSock()
        with mock.patch.object(oc.socket, "socket", return_value=sock), \
             mock.patch.object(oc.time, "time", side_effect=[0, 0]):
            self.assertEqual(oc.discover_oppo(timeout=1), [])
        self.assertTrue(sock.closed)

    def test_oppo_remote_no_xbmc_log_fallback_and_preset_bad_version(self):
        from resources.lib import oppo_remote
        import preset_manager as pm

        old_xbmc = oppo_remote.xbmc
        oppo_remote.xbmc = None
        try:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                oppo_remote._log("fallback")
            self.assertIn("[OPPO203][REMOTE] fallback", buffer.getvalue())
        finally:
            oppo_remote.xbmc = old_xbmc

        self.assertIsNone(pm._parse_version("bad"))

class TestBuild8RawCoverageBranches(unittest.TestCase):
    """Additional meaningful branch tests to raise raw post-99 coverage."""

    def test_external_player_main_module_entrypoint_with_local_fakes(self):
        import runpy

        fake_settings = FakeSettings({
            "addon_data_dir": "",
            "oppo_preflight_enabled": "false",
            "fast_changeover": "false",
            "tv_backend": "none",
            "oppo_start_mode": "tcp_commands",
            "oppo_start_commands": "",
            "oppo_stop_commands": "",
            "hold_mode": "fixed_timeout",
            "fixed_timeout_minutes": "0",
            "switch_back_on_exit": "false",
        })
        fake_oc = types.SimpleNamespace(
            get_playback_info=lambda settings: {},
            get_playback_status=lambda settings: "",
            http_info_is_definitive_stop=lambda info: False,
            http_info_indicates_playing=lambda info: False,
            http_status_is_idle=lambda status: False,
            query_playback_status=lambda *args, **kwargs: "STOP",
            run_configured_commands=lambda *args, **kwargs: [],
            run_preflight=lambda settings: {},
            run_start=lambda *args, **kwargs: None,
            set_play_time=lambda *args, **kwargs: None,
            tcp_qpl_is_idle=lambda status: True,
        )
        fake_sr = types.SimpleNamespace(read_settings=lambda addon_data: fake_settings)
        fake_tv = types.SimpleNamespace(switch_to_kodi=lambda settings: None, switch_to_oppo=lambda settings: None)
        saved = {name: sys.modules.get(name) for name in ("oppo_control", "settings_reader", "tv_control")}
        argv = sys.argv[:]
        try:
            sys.modules["oppo_control"] = fake_oc
            sys.modules["settings_reader"] = fake_sr
            sys.modules["tv_control"] = fake_tv
            sys.argv = ["external_player.py", "--addon-data", tempfile.mkdtemp(), "--file", "/movie.iso"]
            with self.assertRaises(SystemExit) as cm, mock.patch("time.sleep"):
                runpy.run_path(str(ROOT / "resources" / "lib" / "external_player.py"), run_name="__main__")
            self.assertEqual(cm.exception.code, 0)
        finally:
            sys.argv = argv
            for name, module in saved.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module

    def test_intercept_realfs_and_multiple_blacklist_branch(self):
        import intercept

        fs = intercept._RealFS()
        self.assertFalse(fs.exists("/path/that/does/not/exist"))
        self.assertFalse(fs.isdir("/path/that/does/not/exist"))
        self.assertEqual(intercept._norm(None), "")
        self.assertFalse(intercept.should_intercept("/Movie.ISO", blacklist=["not-here", "movie.iso"]))
        self.assertTrue(intercept.should_intercept("/Movie.ISO", whitelist=["", "movie"]))

    def test_logging_rename_ignores_remove_error(self):
        import logging_v116

        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "src.log")
            dst = os.path.join(td, "dst.log")
            Path(src).write_text("new", encoding="utf-8")
            Path(dst).write_text("old", encoding="utf-8")
            fs = logging_v116._RealFS()
            with mock.patch.object(logging_v116.os, "remove", side_effect=OSError("locked")), \
                 mock.patch.object(logging_v116.os, "replace") as replaced:
                fs.rename(src, dst)
            replaced.assert_called_once_with(src, dst)

    def test_oppo_control_remaining_low_level_edges(self):
        import oppo_control as oc

        self.assertEqual(oc._resolve_hardware_wake_command(FakeSettings({}), object()).__class__, object)
        self.assertEqual(oc.run_configured_commands(FakeSettings({"oppo_ip":"127.0.0.1", "oppo_start_commands":""}), "oppo_start_commands"), [])
        self.assertFalse(oc.http_info_is_definitive_stop({"result":"bad", "playinfo":"also-bad"}))
        self.assertFalse(oc.http_info_indicates_playing({"result":"bad", "playinfo":"also-bad"}))
        self.assertTrue(oc.http_info_indicates_playing({"playinfo":{"e_play_status":0}}))
        with mock.patch.object(oc, "_http_get", side_effect=ValueError("bad audio")):
            self.assertEqual(oc.get_audio_tracks(FakeSettings({})), [])
        with mock.patch.object(oc, "_http_get", return_value='{"audio_list":[{"index":3,"name":"List"}]}'):
            self.assertEqual(oc.get_audio_tracks(FakeSettings({}))[0]["index"], 3)
        self.assertEqual(oc._guess_size_from_fields(["size=7", "42"]), 7)
        self.assertIsNone(oc._first_bool({"flag":"maybe"}, "flag"))
        self.assertEqual(oc._infer_entry_type(explicit_is_dir=True), "directory")
        self.assertEqual(oc._infer_entry_type(explicit_is_dir=False), "file")

    def test_oppo_tcp_no_separator_and_playercore_empty_sections(self):
        import oppo_tcp_client
        import playercorefactory_merge as pcf

        class NoSeparatorThenCloseSock:
            def __init__(self): self.calls = 0; self.closed = False
            def settimeout(self, timeout): pass
            def sendall(self, data): pass
            def recv(self, n):
                self.calls += 1
                if self.calls == 1:
                    return b"partial-without-newline"
                return b""
            def close(self): self.closed = True

        sock = NoSeparatorThenCloseSock()
        client = oppo_tcp_client.OppoTcpClient("127.0.0.1", 23, send_svm=False)
        with mock.patch.object(oppo_tcp_client.socket, "create_connection", return_value=sock):
            self.assertFalse(client.wait_for_stop(timeout=0.2))
        self.assertTrue(sock.closed)

        merged, added = pcf._merge_xml(
            "<playercorefactory><players></players><rules></rules></playercorefactory>",
            "<playercorefactory></playercorefactory>",
        )
        self.assertEqual(added, 0)
        self.assertIn("playercorefactory", merged)

    def test_preset_settings_and_wizard_edges(self):
        import preset_manager as pm
        from resources.lib import settings_reader as sr
        import wizard

        self.assertIsNone(pm._parse_version("bad"))
        self.assertTrue(sr.Settings({"x": None}).get_bool("x", True))

        class Addon:
            def __init__(self): self.values = {}
            def setSetting(self, key, value): self.values[key] = value
            def getSetting(self, key): return self.values.get(key, "")

        addon = Addon()
        wizard._set(None, "ignored", "value")
        self.assertEqual(wizard._get(None, "missing", "fallback"), "fallback")

        responses = iter([
            True,   # prerequisites continue
            False,  # jailbreak disabled
            False,  # AutoScript shell handler disabled
            False,  # Quick Start not enabled
            True,   # auto power-on
            True,   # Wake-on-LAN first
            False,  # skip architecture auto-test
            True,   # use External Player
        ])
        inputs = iter(["192.0.2.10", "23", "5", "3", ""])  # IP, port, delay, retries, blank MAC
        with mock.patch.object(wizard, "_addon", return_value=addon), \
             mock.patch.object(wizard, "_choose_mode", return_value="full"), \
             mock.patch.object(wizard, "_probe", return_value=True), \
             mock.patch.object(wizard, "_sel", return_value=0), \
             mock.patch.object(wizard, "_yn", side_effect=lambda *a, **k: next(responses)), \
             mock.patch.object(wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
             mock.patch.object(wizard, "_ok"):
            self.assertTrue(wizard.run_wizard())
        self.assertEqual(addon.values.get("kodi_startup_power_on_use_wol"), "true")
        self.assertNotIn("oppo_mac", addon.values)
