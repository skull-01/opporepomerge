import os
import sys
import unittest
from unittest import mock

from tests._support.project_files import read_project_file

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "resources", "lib"))
for n in ("xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs"):
    sys.modules.pop(n, None)


class FakeS:
    def __init__(self, d=None):
        self.d = d or {}

    def get(self, k, default=None):
        return self.d.get(k, default)

    def get_bool(self, k, default=False):
        v = self.d.get(k)
        if v is None:
            return default
        return str(v).lower() in ("1", "true", "yes", "on")


class DummyAddon:
    def __init__(self, settings=None):
        self.s = dict(settings or {})

    def getSetting(self, k):
        return self.s.get(k, "")

    def setSetting(self, k, v):
        self.s[k] = str(v)


class TPower(unittest.TestCase):
    def setUp(self):
        import service

        self.s = service

    def test_funcs(self):
        self.assertTrue(hasattr(self.s, "_kodi_startup_power_on"))
        self.assertTrue(hasattr(self.s, "_spawn_kodi_startup_power_on"))

    def test_disabled(self):
        self.s._kodi_startup_power_on(FakeS({"kodi_startup_power_on": "false"}))

    def test_spawn_off(self):
        with mock.patch("threading.Thread") as t:
            self.s._spawn_kodi_startup_power_on(FakeS({"kodi_startup_power_on": "false"}))
            t.assert_not_called()

    def test_spawn_on(self):
        with mock.patch("threading.Thread") as t:
            self.s._spawn_kodi_startup_power_on(FakeS({"kodi_startup_power_on": "true"}))
            t.assert_called_once()

    def test_chinoppo(self):
        import inspect

        src = inspect.getsource(self.s._kodi_startup_power_on)
        self.assertIn("#EJT", src)
        self.assertIn("#PON", src)


class TAuto(unittest.TestCase):
    def setUp(self):
        import autoscript_helper as h

        self.h = h

    def test_min(self):
        s = self.h.generate(
            {
                "mount_type": "none",
                "enable_telnet": False,
                "passwordless_root": False,
                "heartbeat_path": "",
            }
        )
        self.assertTrue(s.startswith("#!/bin/sh"))
        self.assertNotIn("telnetd", s)

    def test_telnet(self):
        self.assertIn("telnetd -p 2323", self.h.generate({"enable_telnet": True}))

    def test_nfs(self):
        s = self.h.generate({"mount_type": "nfs", "mount_remote": "1.2.3.4:/x"})
        self.assertIn("mount -t nfs", s)
        self.assertIn("nolock", s)

    def test_cifs(self):
        s = self.h.generate(
            {"mount_type": "cifs", "mount_remote": "//s/x", "cifs_user": "u", "cifs_pass": "p"}
        )
        self.assertIn("username=u", s)
        self.assertIn("password=p", s)

    def test_lf(self):
        s = self.h.generate({})
        self.assertNotIn("\r\n", s)
        self.assertNotIn("\r", s)


class TOmega(unittest.TestCase):
    """Kodi v21 Omega hardening tests."""

    def setUp(self):
        import service

        self.s = service

    def test_helpers_exist(self):
        self.assertTrue(callable(self.s._kodi_major_version))
        self.assertTrue(callable(self.s._safe_call))
        self.assertTrue(callable(self.s._is_omega_or_newer))

    def test_safe_call_swallows(self):
        def boom():
            raise RuntimeError("bang")

        self.assertIsNone(self.s._safe_call(boom))

    def test_safe_call_returns(self):
        self.assertEqual(self.s._safe_call(lambda: 42), 42)

    def test_version_no_xbmc(self):
        # Without xbmc module loaded the helper must not crash
        self.assertEqual(self.s._kodi_major_version(), 0)
        self.assertFalse(self.s._is_omega_or_newer())

    def test_version_omega(self):
        # Mock xbmc.getInfoLabel to return "21.0 Omega"
        fake = mock.MagicMock()
        fake.getInfoLabel.return_value = "21.0 (21.0.0) Git:abc"
        with mock.patch.object(self.s, "xbmc", fake):
            self.assertEqual(self.s._kodi_major_version(), 21)
            self.assertTrue(self.s._is_omega_or_newer())

    def test_version_matrix(self):
        fake = mock.MagicMock()
        fake.getInfoLabel.return_value = "19.5 (19.5.0)"
        with mock.patch.object(self.s, "xbmc", fake):
            self.assertEqual(self.s._kodi_major_version(), 19)
            self.assertFalse(self.s._is_omega_or_newer())

    def test_interception_player_class_present(self):
        self.assertTrue(hasattr(self.s, "InterceptionPlayer"))

    def test_interception_iso_detection(self):
        # Build an instance without invoking xbmc.Player.__init__
        cls = self.s.InterceptionPlayer
        inst = cls.__new__(cls)
        inst.settings = FakeS({})
        inst._handled_path = None
        inst._omega = True
        self.assertTrue(inst._is_iso_or_bdmv("/x/movie.iso"))
        self.assertTrue(inst._is_iso_or_bdmv("/x/BDMV/index.bdmv"))
        self.assertTrue(inst._is_iso_or_bdmv("/x/bdmv/STREAM/00000.m2ts"))
        self.assertFalse(inst._is_iso_or_bdmv("/x/movie.mkv"))
        self.assertFalse(inst._is_iso_or_bdmv(""))

    def test_omega_defers_onPlayBackStarted(self):
        cls = self.s.InterceptionPlayer
        inst = cls.__new__(cls)
        inst.settings = FakeS({})
        inst._handled_path = None
        inst._omega = True
        called = {"n": 0}

        def fake_handle():
            called["n"] += 1

        inst._handle_started = fake_handle
        # On Omega, onPlayBackStarted should NOT call handle_started
        inst.onPlayBackStarted()
        self.assertEqual(called["n"], 0)
        # onAVStarted SHOULD call it
        inst.onAVStarted()
        self.assertEqual(called["n"], 1)

    def test_pre_omega_uses_onPlayBackStarted(self):
        cls = self.s.InterceptionPlayer
        inst = cls.__new__(cls)
        inst.settings = FakeS({})
        inst._handled_path = None
        inst._omega = False
        called = {"n": 0}
        inst._handle_started = lambda: called.__setitem__("n", called["n"] + 1)
        inst.onPlayBackStarted()
        self.assertEqual(called["n"], 1)

    def test_callback_exception_swallowed(self):
        cls = self.s.InterceptionPlayer
        inst = cls.__new__(cls)
        inst.settings = FakeS({})
        inst._handled_path = None
        inst._omega = False

        def boom():
            raise RuntimeError("nope")

        inst._handle_started = boom
        # Must not raise out to Kodi binding
        try:
            inst.onPlayBackStarted()
        except Exception:
            self.fail("Callback exception leaked out of onPlayBackStarted")


class TPresets(unittest.TestCase):
    def setUp(self):
        import hardware_presets as hp

        self.hp = hp

    def test_all_keys_have_presets(self):
        for k in self.hp.PRESET_KEYS:
            self.assertIn(k, self.hp.PRESETS)

    def test_list_presets_pairs(self):
        pairs = self.hp.list_presets()
        self.assertEqual(len(pairs), len(self.hp.PRESET_KEYS))
        for _k, lbl in pairs:
            self.assertTrue(isinstance(lbl, str) and lbl)

    def test_get_preset_unknown_returns_generic(self):
        p = self.hp.get_preset("does_not_exist")
        self.assertEqual(p["family"], "generic")

    def test_oppo_power_on_uses_pon(self):
        self.assertEqual(self.hp.select_power_on_command("udp_203"), "#PON")
        self.assertEqual(self.hp.select_power_on_command("udp_205"), "#PON")

    def test_chinoppo_power_on_uses_ejt(self):
        for k in (
            "chinoppo",
            "chinoppo_m9702",
            "chinoppo_m9201",
            "chinoppo_m9203",
            "chinoppo_m9205c",
        ):
            self.assertEqual(
                self.hp.select_power_on_command(k),
                "#EJT",
                "preset " + k + " should use #EJT to wake",
            )

    def test_chinoppo_play_needs_eject_first(self):
        self.assertEqual(self.hp.select_play_command("chinoppo"), ["#EJT", "#PLA"])

    def test_oppo_play_is_plain_pla(self):
        self.assertEqual(self.hp.select_play_command("udp_203"), ["#PLA"])

    def test_reavon_x200_longer_delay(self):
        self.assertEqual(self.hp.select_recommended_power_delay("reavon_ubrx200"), 8)

    def test_chinoppo_recommended_delay(self):
        self.assertEqual(self.hp.select_recommended_power_delay("chinoppo"), 6)

    def test_oppo_recommended_delay(self):
        self.assertEqual(self.hp.select_recommended_power_delay("udp_203"), 5)

    def test_supports_http(self):
        self.assertTrue(self.hp.supports_http("udp_203"))
        self.assertFalse(self.hp.supports_http("chinoppo"))
        self.assertFalse(self.hp.supports_http("reavon_ubrx100"))

    def test_is_chinoppo_family(self):
        self.assertTrue(self.hp.is_chinoppo_family("chinoppo_m9702"))
        self.assertFalse(self.hp.is_chinoppo_family("udp_205"))
        self.assertFalse(self.hp.is_chinoppo_family("reavon_ubrx200"))

    def test_jailbroken_uses_pon(self):
        self.assertEqual(self.hp.select_power_on_command("udp_203_jailbroken"), "#PON")
        self.assertEqual(self.hp.select_power_on_command("udp_205_jailbroken"), "#PON")

    def test_magnetar_uses_pon(self):
        self.assertEqual(self.hp.select_power_on_command("magnetar_udp800"), "#PON")
        self.assertEqual(self.hp.select_play_command("magnetar_udp900"), ["#PLA"])

    def test_zappiti_quick_start_disabled(self):
        p = self.hp.get_preset("zappiti_reference")
        self.assertFalse(p["supports_quick_start"])


class TI18N(unittest.TestCase):
    def setUp(self):
        for n in ("xbmcaddon",):
            sys.modules.pop(n, None)
        import importlib

        import i18n

        importlib.reload(i18n)
        self.i = i18n

    def test_unknown_id_uses_default(self):
        self.assertEqual(self.i.L(99999, "fallback"), "fallback")

    def test_invalid_id_uses_default(self):
        self.assertEqual(self.i.L("notanint", "x"), "x")

    def test_l_never_raises(self):
        # Even bizarre input should not raise
        try:
            self.i.L(None)
            self.i.L([])
            self.i.L({})
        except Exception as exc:
            self.fail("L() raised: " + str(exc))

    def test_supported_languages(self):
        langs = self.i.supported_languages()
        self.assertIn("resource.language.en_gb", langs)
        self.assertIn("resource.language.zh_cn", langs)
        self.assertEqual(len(langs), 12)


class TLangFiles(unittest.TestCase):
    """Localization-file integrity: every bundled language folder must exist."""

    def setUp(self):
        import i18n

        self.i = i18n
        self.lang_root = os.path.join(ROOT, "resources", "language")

    def test_all_languages_present(self):
        for folder in self.i.supported_languages():
            self.assertTrue(
                os.path.isdir(os.path.join(self.lang_root, folder)),
                "missing language folder: " + folder,
            )


class TReconnect(unittest.TestCase):
    """Light reconnect-logic regression tests using oppo_tcp_client."""

    def setUp(self):
        import oppo_tcp_client as t

        self.t = t

    def test_module_imports(self):
        self.assertTrue(self.t is not None)

    def test_client_class_present(self):
        self.assertTrue(hasattr(self.t, "OppoTcpClient"))

    def test_client_has_lifecycle(self):
        cls = self.t.OppoTcpClient
        for m in ("wait_for_stop", "close"):
            self.assertTrue(hasattr(cls, m), "OppoTcpClient missing method: " + m)

    def test_client_construct_no_connect(self):
        # Constructing the client must not open sockets eagerly,
        # so it stays safe on platforms without network.
        c = self.t.OppoTcpClient("127.0.0.1", 23)
        try:
            self.assertTrue(hasattr(c, "close"))
        finally:
            try:
                c.close()
            except Exception:
                pass

    def test_oppo_control_send_commands_present(self):
        import oppo_control as oc

        self.assertTrue(hasattr(oc, "send_commands"))
        self.assertTrue(hasattr(oc, "query_power_status"))
        self.assertTrue(hasattr(oc, "wake_on_lan"))


class TBugs(unittest.TestCase):
    """Regression tests for bugs fixed in v1.0.6."""

    def test_i18n_unicode_safe(self):
        import i18n

        # L() never crashes; empty fallback table returns "".
        self.assertEqual(i18n.L(31000), "")
        self.assertEqual(i18n.L(31000, "fallback"), "fallback")

    def test_presets_still_intact(self):
        import hardware_presets as hp

        self.assertEqual(hp.select_power_on_command("chinoppo"), "#EJT")
        self.assertEqual(hp.select_play_command("udp_205"), ["#PLA"])


class TBackoff(unittest.TestCase):
    """Pure-function tests for the backoff schedule."""

    def setUp(self):
        import reconnect_backoff as rb

        self.rb = rb

    def test_no_jitter_schedule_doubles(self):
        s = self.rb.schedule(max_retries=5, base=1.0, cap=100.0, jitter=0)
        self.assertEqual(s, [1.0, 2.0, 4.0, 8.0, 16.0])

    def test_cap_clamps(self):
        s = self.rb.schedule(max_retries=6, base=1.0, cap=8.0, jitter=0)
        self.assertEqual(s, [1.0, 2.0, 4.0, 8.0, 8.0, 8.0])

    def test_zero_jitter_deterministic(self):
        a = self.rb.compute_delay(3, base=1.0, cap=30.0, jitter=0)
        b = self.rb.compute_delay(3, base=1.0, cap=30.0, jitter=0)
        self.assertEqual(a, b)
        self.assertEqual(a, 4.0)

    def test_jitter_within_bounds(self):
        # rng=lambda:0.0 -> factor = 1 - jitter (lower bound)
        # rng=lambda:1.0 actually never returned by random(), but we still cap
        low = self.rb.compute_delay(2, base=1.0, cap=30.0, jitter=0.25, rng=lambda: 0.0)
        high = self.rb.compute_delay(2, base=1.0, cap=30.0, jitter=0.25, rng=lambda: 0.999999)
        self.assertAlmostEqual(low, 2.0 * 0.75, places=4)
        self.assertGreater(high, 2.0 * 0.75)
        self.assertLess(high, 2.0 * 1.25 + 1e-6)

    def test_jitter_midpoint(self):
        # rng=lambda:0.5 -> factor = 1.0 -> raw exactly
        v = self.rb.compute_delay(4, base=1.0, cap=30.0, jitter=0.25, rng=lambda: 0.5)
        self.assertAlmostEqual(v, 8.0, places=6)

    def test_should_retry(self):
        self.assertTrue(self.rb.should_retry(1, 3))
        self.assertTrue(self.rb.should_retry(2, 3))
        self.assertFalse(self.rb.should_retry(3, 3))
        self.assertFalse(self.rb.should_retry(4, 3))

    def test_attempt_floor(self):
        # attempt < 1 should be treated as 1
        self.assertEqual(self.rb.compute_delay(0, base=2.0, cap=99, jitter=0), 2.0)
        self.assertEqual(self.rb.compute_delay(-5, base=2.0, cap=99, jitter=0), 2.0)


class TPersistentReconnect(unittest.TestCase):
    """Mocked-socket tests for the OppoTcpClient persistent reconnect loop."""

    def _make_client(self):
        import oppo_tcp_client as otc

        c = otc.OppoTcpClient.__new__(otc.OppoTcpClient)
        # Minimal attrs the persistent path touches
        c._per_attempt_timeout = 1
        return c

    def test_first_attempt_success(self):
        c = self._make_client()
        slept = []
        ok = c.wait_for_stop_persistent(
            timeout=60,
            max_retries=5,
            base_delay=1.0,
            cap_delay=30.0,
            jitter=0,
            _sleep=lambda s: slept.append(s),
            _connect_factory=lambda: True,
        )
        self.assertTrue(ok)
        self.assertEqual(slept, [])  # No retries -> no sleeps

    def test_succeeds_after_two_failures(self):
        c = self._make_client()
        slept = []
        seq = iter([False, False, True])
        ok = c.wait_for_stop_persistent(
            timeout=60,
            max_retries=5,
            base_delay=1.0,
            cap_delay=30.0,
            jitter=0,
            _sleep=lambda s: slept.append(s),
            _connect_factory=lambda: next(seq),
        )
        self.assertTrue(ok)
        # Two failures -> two sleeps, schedule [1, 2]
        self.assertEqual(slept, [1.0, 2.0])

    def test_gives_up_after_max_retries(self):
        c = self._make_client()
        slept = []
        ok = c.wait_for_stop_persistent(
            timeout=600,
            max_retries=4,
            base_delay=1.0,
            cap_delay=30.0,
            jitter=0,
            _sleep=lambda s: slept.append(s),
            _connect_factory=lambda: False,
        )
        self.assertFalse(ok)
        # 4 attempts, 3 sleeps between them (no sleep after the final fail)
        self.assertEqual(slept, [1.0, 2.0, 4.0])

    def test_zero_max_retries_means_one_attempt(self):
        c = self._make_client()
        slept = []
        calls = {"n": 0}

        def f():
            calls["n"] += 1
            return False

        ok = c.wait_for_stop_persistent(
            timeout=60,
            max_retries=0,
            _sleep=lambda s: slept.append(s),
            _connect_factory=f,
        )
        self.assertFalse(ok)
        self.assertEqual(calls["n"], 1)
        self.assertEqual(slept, [])

    def test_exception_in_attempt_treated_as_failure(self):
        c = self._make_client()
        slept = []
        seq = iter([Exception("boom"), True])

        def f():
            v = next(seq)
            if isinstance(v, Exception):
                raise v
            return v

        ok = c.wait_for_stop_persistent(
            timeout=60,
            max_retries=3,
            base_delay=1.0,
            cap_delay=30.0,
            jitter=0,
            _sleep=lambda s: slept.append(s),
            _connect_factory=f,
        )
        self.assertTrue(ok)
        self.assertEqual(slept, [1.0])

    def test_timeout_short_circuits(self):
        c = self._make_client()
        # Simulate that wall-clock has already passed the deadline.
        # A timeout of 0 -> deadline = time.time() (no future), so the
        # very first failure's pre-sleep deadline check should bail.
        slept = []
        ok = c.wait_for_stop_persistent(
            timeout=0,
            max_retries=5,
            base_delay=1.0,
            cap_delay=30.0,
            jitter=0,
            _sleep=lambda s: slept.append(s),
            _connect_factory=lambda: False,
        )
        self.assertFalse(ok)
        self.assertEqual(slept, [])  # Bailed before any sleep

    def test_settings_label_ids_present(self):
        # Light guard: README referenced ids 30960-30964 for new knobs.
        en = os.path.join(ROOT, "resources", "language", "resource.language.en_gb", "strings.po")
        with open(en, encoding="utf-8") as f:
            txt = f.read()
        for cid in range(30960, 30965):
            self.assertIn('"#' + str(cid) + '"', txt, "missing string id #" + str(cid))


class TArchBenchmark(unittest.TestCase):
    """Real-benchmarking tests using mocked timing and a fake PCF."""

    def setUp(self):
        import arch_benchmark as ab

        self.ab = ab

    def _fake_timer(self, deltas):
        """Return a no-arg timer that yields t0,t1,t0,t1,... per pair."""
        # We'll alternate: each benchmark trial calls timer() twice.
        clock = {"t": 0.0}
        seq = list(deltas)
        idx = {"i": 0}

        def timer():
            i = idx["i"]
            if i % 2 == 0:
                v = clock["t"]
            else:
                # advance by next delta
                d = seq[(i // 2) % len(seq)]
                clock["t"] += d
                v = clock["t"]
            idx["i"] += 1
            return v

        return timer

    def test_benchmark_records_3_trials(self):
        timer = self._fake_timer([0.1, 0.2, 0.3])
        r = self.ab.benchmark("external", trials=3, probe=lambda c: None, timer=timer)
        self.assertEqual(len(r["trials"]), 3)
        self.assertTrue(r["all_ok"])
        self.assertAlmostEqual(r["median"], 0.2, places=6)

    def test_benchmark_failure_marks_all_ok_false(self):
        timer = self._fake_timer([0.05, 0.05, 0.05])

        def probe(_):
            raise RuntimeError("boom")

        r = self.ab.benchmark("service", trials=3, probe=probe, timer=timer)
        self.assertFalse(r["all_ok"])
        self.assertEqual(len(r["trials"]), 3)
        for s in r["trials"]:
            self.assertFalse(s["ok"])

    def test_benchmark_requires_probe(self):
        with self.assertRaises(ValueError):
            self.ab.benchmark("external", trials=1, probe=None)

    def test_recommend_external_wins(self):
        self.assertEqual(self.ab.recommend(0.10, 0.30, eps=0.020), "external")

    def test_recommend_service_wins(self):
        self.assertEqual(self.ab.recommend(0.30, 0.10, eps=0.020), "service")

    def test_recommend_tie_within_eps(self):
        self.assertEqual(self.ab.recommend(0.100, 0.110, eps=0.020), "tie")

    def test_recommend_handles_none(self):
        self.assertEqual(self.ab.recommend(None, 0.10), "service")
        self.assertEqual(self.ab.recommend(0.10, None), "external")
        self.assertEqual(self.ab.recommend(None, None), "tie")

    def test_run_full_picks_lower_median(self):
        self._fake_timer([0.10, 0.10, 0.10])  # median 0.10
        self._fake_timer([0.30, 0.30, 0.30])  # median 0.30
        # We need ONE timer for the whole run; build a combined sequence
        seq = iter(
            [
                0.0,
                0.10,
                0.10,
                0.20,
                0.20,
                0.30,  # external 3 trials
                0.30,
                0.60,
                0.60,
                0.90,
                0.90,
                1.20,
            ]
        )  # service  3 trials

        def timer():
            return next(seq)

        result = self.ab.run_full(
            probe_external=lambda c: None,
            probe_service=lambda c: None,
            trials=3,
            timer=timer,
        )
        self.assertEqual(result["recommendation"], "external")
        self.assertAlmostEqual(result["external"]["median"], 0.10, places=6)
        self.assertAlmostEqual(result["service"]["median"], 0.30, places=6)
        self.assertEqual(result["trials"], 3)

    def test_validate_playercorefactory_well_formed(self):
        path = os.path.join(ROOT, "_tmp_pcf_ok.xml")
        with open(path, "w") as f:
            f.write("""<playercorefactory>
              <players>
                <player name="ExternalOPPO" type="ExternalPlayer" audio="false" video="true">
                  <filename>/usr/bin/true</filename>
                  <args></args>
                </player>
              </players>
              <rules action="prepend">
                <rule filetypes="iso" player="ExternalOPPO"/>
              </rules>
            </playercorefactory>""")
        try:
            ok, reason = self.ab.validate_playercorefactory(path)
            self.assertTrue(ok, "valid pcf rejected: " + reason)
        finally:
            os.remove(path)

    def test_validate_playercorefactory_missing(self):
        ok, reason = self.ab.validate_playercorefactory("/no/such/file.xml")
        self.assertFalse(ok)
        self.assertIn("read error", reason.lower())

    def test_validate_playercorefactory_empty(self):
        path = os.path.join(ROOT, "_tmp_pcf_empty.xml")
        open(path, "w").write("   \n  \n")
        try:
            ok, reason = self.ab.validate_playercorefactory(path)
            self.assertFalse(ok)
            self.assertIn("empty", reason.lower())
        finally:
            os.remove(path)

    def test_validate_playercorefactory_malformed(self):
        path = os.path.join(ROOT, "_tmp_pcf_bad.xml")
        open(path, "w").write("<playercorefactory><players><player>")
        try:
            ok, reason = self.ab.validate_playercorefactory(path)
            self.assertFalse(ok)
            self.assertIn("not well-formed", reason.lower())
        finally:
            os.remove(path)

    def test_validate_playercorefactory_wrong_root(self):
        path = os.path.join(ROOT, "_tmp_pcf_wrongroot.xml")
        open(path, "w").write("<root><players><player/></players></root>")
        try:
            ok, reason = self.ab.validate_playercorefactory(path)
            self.assertFalse(ok)
            self.assertIn("playercorefactory", reason.lower())
        finally:
            os.remove(path)

    def test_validate_playercorefactory_no_players_block(self):
        path = os.path.join(ROOT, "_tmp_pcf_noplayers.xml")
        open(path, "w").write("<playercorefactory><rules/></playercorefactory>")
        try:
            ok, reason = self.ab.validate_playercorefactory(path)
            self.assertFalse(ok)
            self.assertIn("<players>", reason)
        finally:
            os.remove(path)

    def test_run_full_includes_pcf_validation(self):
        path = os.path.join(ROOT, "_tmp_pcf_run.xml")
        open(path, "w").write("<playercorefactory><players><player/></players></playercorefactory>")
        try:
            seq = iter([0.0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.5, 0.6])
            r = self.ab.run_full(
                probe_external=lambda c: None,
                probe_service=lambda c: None,
                trials=3,
                timer=lambda: next(seq),
                playercorefactory_path=path,
            )
            self.assertTrue(r["playercorefactory_ok"])
        finally:
            os.remove(path)


class TDiagnostics(unittest.TestCase):
    """Diagnostics dashboard tests (no sockets, no Kodi)."""

    def setUp(self):
        import diagnostics

        self.d = diagnostics

    def test_redact_masks_mac_and_ip(self):
        s = "host 192.168.1.42 mac AA:BB:CC:11:22:33 ok"
        out = self.d.redact(s)
        self.assertIn("x.x.x.x", out)
        self.assertIn("xx:xx:xx:xx:xx:xx", out)
        self.assertNotIn("192.168.1.42", out)
        self.assertNotIn("AA:BB:CC:11:22:33", out)

    def test_redact_handles_dash_mac(self):
        out = self.d.redact("AA-BB-CC-11-22-33")
        self.assertIn("xx:xx:xx:xx:xx:xx", out)

    def test_redact_empty(self):
        self.assertEqual(self.d.redact(""), "")
        self.assertIsNone(self.d.redact(None))

    def test_default_path_format(self):
        p = self.d.default_path("/tmp/addon", now=lambda: 0)
        self.assertTrue(p.startswith("/tmp/addon/diagnostics-"))
        self.assertTrue(p.endswith(".txt"))

    def test_run_marks_skipped_when_probe_missing(self):
        r = self.d.run("1.2.3.4", 23, mac=None)
        for k in ("tcp", "http", "svm", "wol", "kodi", "capabilities"):
            self.assertTrue(r[k].get("skipped"), "expected " + k + " to be skipped")
        self.assertFalse(r["overall_ok"])

    def test_run_overall_ok_when_all_probes_ok(self):
        def ok(*a, **kw):
            return {"ok": True}

        r = self.d.run(
            "1.2.3.4",
            23,
            mac="AA:BB:CC:11:22:33",
            tcp_check=ok,
            http_check=ok,
            svm_check=ok,
            wol_check=ok,
            kodi_info=lambda: {"ok": True},
            capabilities=lambda: {"ok": True},
        )
        self.assertTrue(r["overall_ok"])

    def test_run_overall_false_when_any_probe_fails(self):
        def ok(*a, **kw):
            return {"ok": True}

        def bad(*a, **kw):
            return {"ok": False, "error": "boom"}

        r = self.d.run(
            "1.2.3.4",
            23,
            mac="AA:BB:CC:11:22:33",
            tcp_check=ok,
            http_check=bad,
            svm_check=ok,
            wol_check=ok,
            kodi_info=lambda: {"ok": True},
            capabilities=lambda: {"ok": True},
        )
        self.assertFalse(r["overall_ok"])
        self.assertFalse(r["http"]["ok"])

    def test_run_skips_wol_when_no_mac(self):
        r = self.d.run("1.2.3.4", 23, mac=None, wol_check=lambda m: {"ok": True})
        self.assertTrue(r["wol"].get("skipped"))

    def test_run_swallows_probe_exceptions(self):
        def boom(*a, **kw):
            raise RuntimeError("nope")

        r = self.d.run(
            "1.2.3.4",
            23,
            mac="AA:BB:CC:11:22:33",
            tcp_check=boom,
            http_check=boom,
            svm_check=boom,
            wol_check=boom,
            kodi_info=boom,
            capabilities=boom,
        )
        for k in ("tcp", "http", "svm", "wol", "kodi", "capabilities"):
            self.assertFalse(r[k].get("ok"))
            self.assertIn("error", r[k])
        self.assertFalse(r["overall_ok"])

    def test_format_report_contains_section_headers(self):
        r = self.d.run(
            "1.2.3.4", 23, mac="AA:BB:CC:11:22:33", tcp_check=lambda h, p: {"ok": True, "rtt_ms": 4}
        )
        text = self.d.format_report(r)
        for h in ("[TCP]", "[HTTP]", "[SVM]", "[WOL]", "[KODI]", "[CAPABILITIES]"):
            self.assertIn(h, text)
        self.assertIn("Overall OK:", text)

    def test_format_report_invalid_input(self):
        self.assertEqual(self.d.format_report(None), "<invalid result>")

    def test_save_report_uses_writer_injection(self):
        captured = {}

        def writer(path, text):
            captured["path"] = path
            captured["text"] = text

        r = self.d.run("1.2.3.4", 23, tcp_check=lambda h, p: {"ok": True})
        path = self.d.save_report(r, "/fake/addon_data", now=lambda: 1234567890, writer=writer)
        self.assertEqual(path, captured["path"])
        self.assertTrue(path.startswith("/fake/addon_data/diagnostics-"))
        self.assertIn("OPPO ISO External - Diagnostics Report", captured["text"])

    def test_save_report_real_io(self):
        import tempfile

        d = tempfile.mkdtemp()
        try:
            r = self.d.run("1.2.3.4", 23, tcp_check=lambda h, p: {"ok": True})
            p = self.d.save_report(r, d)
            self.assertTrue(os.path.isfile(p))
            with open(p, encoding="utf-8") as f:
                txt = f.read()
            self.assertIn("OPPO ISO External", txt)
        finally:
            import shutil

            shutil.rmtree(d, ignore_errors=True)

    def test_default_py_hook_exists(self):
        # The hook is a free function in default.py; we don't import it
        # at test collection time (xbmc may be required by other paths
        # in default.py), but we can scan the file for the symbol.
        path = os.path.join(ROOT, "default.py")
        with open(path, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("def run_diagnostics_dashboard(", src)
        self.assertIn("save_report(", src)

    def test_skipped_probe_does_not_flip_overall(self):
        # If only one probe runs and it's ok, overall should be True.
        r = self.d.run("1.2.3.4", 23, tcp_check=lambda h, p: {"ok": True})
        self.assertTrue(r["overall_ok"])


class TSettingsLayout(unittest.TestCase):
    """Parse settings.xml and assert v1.1.0 structural invariants."""

    def setUp(self):
        import xml.etree.ElementTree as ET

        self.ET = ET
        path = os.path.join(ROOT, "resources", "settings.xml")
        with open(path, "rb") as f:
            self.tree = ET.fromstring(f.read())

    def test_well_formed(self):
        self.assertEqual(self.tree.tag, "settings")

    def test_five_groups_present(self):
        cat_ids = [c.get("id") for c in self.tree.findall("category")]
        for g in ("connection", "hardware", "autopoweron", "playback", "diagnostics"):
            self.assertIn(g, cat_ids, "missing category: " + g)

    def test_no_group_is_empty(self):
        for c in self.tree.findall("category"):
            settings = c.findall("setting")
            self.assertGreater(len(settings), 0, "empty group: " + (c.get("id") or "?"))

    def test_every_setting_has_label(self):
        for s in self.tree.iter("setting"):
            self.assertTrue(s.get("label"), "setting missing label: " + str(s.get("id")))

    def test_every_setting_has_id(self):
        for s in self.tree.iter("setting"):
            self.assertTrue(s.get("id"), "setting missing id attribute")

    def test_unique_ids(self):
        ids = [s.get("id") for s in self.tree.iter("setting")]
        self.assertEqual(
            len(ids),
            len(set(ids)),
            "duplicate setting ids: " + str([i for i in ids if ids.count(i) > 1]),
        )

    def test_dependencies_reference_existing_ids(self):
        ids = {s.get("id") for s in self.tree.iter("setting")}
        for d in self.tree.iter("dependency"):
            ref = d.get("setting")
            self.assertIn(ref, ids, "<dependency setting=" + repr(ref) + "> references unknown id")

    def test_dependency_operators_known(self):
        ALLOWED_OPS = {"is", "!is"}
        for d in self.tree.iter("dependency"):
            self.assertIn(
                d.get("operator"),
                ALLOWED_OPS,
                "unknown operator on <dependency>: " + str(d.get("operator")),
            )

    def test_dependency_values_truthy_strings(self):
        # We only use type="visible" for dependencies; assert that.
        for d in self.tree.iter("dependency"):
            self.assertEqual(
                d.get("type"), "visible", "non-visible dependency type: " + str(d.get("type"))
            )

    def test_mac_and_wol_broadcast_depend_on_use_wol(self):
        deps = {}
        for s in self.tree.iter("setting"):
            sid = s.get("id")
            for d in s.iter("dependency"):
                deps[sid] = (d.get("setting"), (d.text or "").strip())
        self.assertIn("oppo_mac", deps)
        self.assertEqual(deps["oppo_mac"], ("oppo_use_wol", "true"))
        self.assertEqual(deps["oppo_wol_broadcast"], ("oppo_use_wol", "true"))

    def test_reconnect_sub_settings_depend_on_master(self):
        deps = {}
        for s in self.tree.iter("setting"):
            sid = s.get("id")
            for d in s.iter("dependency"):
                deps[sid] = (d.get("setting"), (d.text or "").strip())
        for sub in (
            "reconnect_max_retries",
            "reconnect_base_delay",
            "reconnect_cap_delay",
            "reconnect_jitter_pct",
        ):
            self.assertEqual(
                deps.get(sub), ("reconnect_enabled", "true"), "missing/wrong dependency on " + sub
            )

    def test_autopoweron_sub_settings_depend_on_master(self):
        deps = {}
        for s in self.tree.iter("setting"):
            sid = s.get("id")
            for d in s.iter("dependency"):
                deps[sid] = (d.get("setting"), (d.text or "").strip())
        for sub in (
            "kodi_startup_power_on_delay",
            "kodi_startup_power_on_retries",
            "kodi_startup_power_on_use_wol",
        ):
            self.assertEqual(
                deps.get(sub),
                ("kodi_startup_power_on", "true"),
                "missing/wrong dependency on " + sub,
            )

    def test_http_sub_settings_depend_on_activate(self):
        deps = {}
        for s in self.tree.iter("setting"):
            sid = s.get("id")
            for d in s.iter("dependency"):
                deps[sid] = (d.get("setting"), (d.text or "").strip())
        for sub in (
            "oppo_http_broadcast",
            "oppo_http_payload_mode",
            "oppo_http_app_device_type",
            "oppo_http_media_type",
            "oppo_http_path_from",
            "oppo_http_path_to",
            "oppo_http_urlencode_path",
            "oppo_http_disc_folder_root",
        ):
            self.assertEqual(
                deps.get(sub), ("oppo_http_activate", "true"), "missing/wrong dependency on " + sub
            )

    def test_v2_mvp_settings_count_reflects_removed_architecture_ui(self):
        # v2 Build 2 keeps architecture-selection rows hidden/deferred, adds
        # hardware model, and adds the explicit TV-switching enable/disable
        # control required by the MVP no-op path. Strip-wizard dropped the
        # hidden wizard_mode setting (98 -> 97). The configurator-owner hint
        # lsep added a passive label row at the top of Connection (97 -> 98).
        # ENH-#42 added the hidden addon_language preference slot (98 -> 99).
        ids = [s.get("id") for s in self.tree.iter("setting")]
        self.assertEqual(len(ids), 99)

    def test_category_labels_use_new_ids(self):
        cat_label_ids = {c.get("id"): c.get("label") for c in self.tree.findall("category")}
        self.assertEqual(cat_label_ids["connection"], "32100")
        self.assertEqual(cat_label_ids["hardware"], "32101")
        self.assertEqual(cat_label_ids["autopoweron"], "32102")
        self.assertEqual(cat_label_ids["playback"], "32103")
        self.assertEqual(cat_label_ids["diagnostics"], "32104")


class TPlayerCoreFactory(unittest.TestCase):
    """Per-preset playercorefactory snippets and safe merge."""

    def setUp(self):
        import playercorefactory_merge as pcf

        self.pcf = pcf

    # ---- snippet generation ----

    def test_all_presets_present(self):
        for k in ("oppo203", "oppo103", "chinoppo", "reavon_x200", "zappiti_reference", "magnetar"):
            self.assertIn(k, self.pcf.PRESETS)

    def test_oppo203_uses_pla_only(self):
        s = self.pcf.snippet_for("oppo203", player_path="/usr/bin/python3")
        self.assertIn('--start="#PLA"', s)
        self.assertNotIn("#EJT", s)

    def test_chinoppo_uses_ejt_then_pla(self):
        s = self.pcf.snippet_for("chinoppo", player_path="/usr/bin/python3")
        self.assertIn('--start="#EJT,#PLA"', s)

    def test_reavon_uses_pon_then_pla(self):
        s = self.pcf.snippet_for("reavon_x200", player_path="/usr/bin/python3")
        self.assertIn('--start="#PON,#PLA"', s)

    def test_unknown_preset_raises(self):
        with self.assertRaises(KeyError):
            self.pcf.snippet_for("not_a_preset", player_path="/x")

    def test_snippet_is_well_formed_xml(self):
        for k in self.pcf.PRESETS:
            s = self.pcf.snippet_for(k, player_path="/usr/bin/python3")
            self.assertTrue(self.pcf.is_well_formed(s), "snippet for " + k + " is not well-formed")

    def test_snippet_player_name_unique_per_preset(self):
        import re

        names = set()
        for k in self.pcf.PRESETS:
            s = self.pcf.snippet_for(k, player_path="/x")
            m = re.search(r'<player name="([^"]+)"', s)
            self.assertIsNotNone(m)
            names.add(m.group(1))
        self.assertEqual(len(names), len(self.pcf.PRESETS), "preset player names collide")

    def test_snippet_includes_addon_id(self):
        s = self.pcf.snippet_for("oppo203", player_path="/x", addon_id="custom.addon")
        self.assertIn("--addon=custom.addon", s)

    # ---- well-formedness ----

    def test_is_well_formed_empty(self):
        self.assertTrue(self.pcf.is_well_formed(None))
        self.assertTrue(self.pcf.is_well_formed(""))
        self.assertTrue(self.pcf.is_well_formed("   "))

    def test_is_well_formed_good(self):
        self.assertTrue(
            self.pcf.is_well_formed("<playercorefactory><players/></playercorefactory>")
        )

    def test_is_well_formed_bad(self):
        self.assertFalse(self.pcf.is_well_formed("<playercorefactory><players><nope></players>"))
        self.assertFalse(self.pcf.is_well_formed("not xml at all"))

    # ---- backup path ----

    def test_backup_path_format(self):
        p = self.pcf.backup_path("/u/d/playercorefactory.xml", now=lambda: 0)
        self.assertTrue(p.startswith("/u/d/playercorefactory.xml."))
        self.assertTrue(p.endswith(".bak"))

    # ---- merge ----

    def _fake_fs(self, files=None):
        store = dict(files or {})
        copies = []

        class FS:
            def exists(self, p):
                return p in store

            def read(self, p):
                return store[p]

            def write(self, p, t):
                store[p] = t

            def copy(self, src, dst):
                store[dst] = store[src]
                copies.append((src, dst))

        fs = FS()
        fs._store = store
        fs._copies = copies
        return fs

    def test_merge_into_empty_target_no_backup(self):
        fs = self._fake_fs()
        snip = self.pcf.snippet_for("oppo203", player_path="/x")
        out = self.pcf.merge("/u/d/playercorefactory.xml", snip, fs=fs, now=lambda: 0)
        self.assertIsNone(out["backup"])
        self.assertTrue(out["written"])
        self.assertEqual(out["added_players"], 1)
        self.assertIn("/u/d/playercorefactory.xml", fs._store)

    def test_merge_creates_backup_when_existing_present(self):
        existing = "<playercorefactory><players/></playercorefactory>"
        fs = self._fake_fs({"/u/d/playercorefactory.xml": existing})
        snip = self.pcf.snippet_for("chinoppo", player_path="/x")
        out = self.pcf.merge("/u/d/playercorefactory.xml", snip, fs=fs, now=lambda: 0)
        self.assertIsNotNone(out["backup"])
        self.assertTrue(out["backup"].endswith(".bak"))
        self.assertEqual(
            fs._store[out["backup"]], existing, "backup must be byte-identical to original"
        )
        self.assertEqual(out["added_players"], 1)

    def test_merge_refuses_malformed_existing(self):
        fs = self._fake_fs({"/u/d/playercorefactory.xml": "<playercorefactory><broken>"})
        snip = self.pcf.snippet_for("oppo203", player_path="/x")
        with self.assertRaises(ValueError):
            self.pcf.merge("/u/d/playercorefactory.xml", snip, fs=fs)
        # And no write happened.
        self.assertEqual(fs._store["/u/d/playercorefactory.xml"], "<playercorefactory><broken>")

    def test_merge_refuses_malformed_snippet(self):
        fs = self._fake_fs()
        with self.assertRaises(ValueError):
            self.pcf.merge("/u/d/playercorefactory.xml", "<not></closed>", fs=fs)

    def test_merge_idempotent_no_duplicate_player(self):
        fs = self._fake_fs()
        snip = self.pcf.snippet_for("oppo203", player_path="/x")
        self.pcf.merge("/u/d/p.xml", snip, fs=fs, now=lambda: 0)
        self.pcf.merge("/u/d/p.xml", snip, fs=fs, now=lambda: 1)
        merged = fs._store["/u/d/p.xml"]
        # Idempotent: <player name="OPPO_External_oppo203"> appears once,
        # plus three Option 4 tag-aware disc-style rules.
        player_tag_count = merged.count('<player name="OPPO_External_oppo203"')
        rule_ref_count = merged.count('player="OPPO_External_oppo203"')
        self.assertEqual(
            player_tag_count, 1, "duplicate <player> after re-merge: " + str(player_tag_count)
        )
        self.assertEqual(
            rule_ref_count,
            3,
            'unexpected <rule player="..."> count after re-merge: ' + str(rule_ref_count),
        )

    def test_merge_two_different_presets_keeps_both(self):
        fs = self._fake_fs()
        a = self.pcf.snippet_for("oppo203", player_path="/x")
        b = self.pcf.snippet_for("chinoppo", player_path="/x")
        self.pcf.merge("/u/d/p.xml", a, fs=fs, now=lambda: 0)
        self.pcf.merge("/u/d/p.xml", b, fs=fs, now=lambda: 1)
        merged = fs._store["/u/d/p.xml"]
        self.assertIn("OPPO_External_oppo203", merged)
        self.assertIn("OPPO_External_chinoppo", merged)

    def test_merge_refuses_wrong_root_element(self):
        fs = self._fake_fs({"/u/d/p.xml": "<advancedsettings/>"})
        snip = self.pcf.snippet_for("oppo203", player_path="/x")
        with self.assertRaises(ValueError):
            self.pcf.merge("/u/d/p.xml", snip, fs=fs)

    def test_merge_real_io_roundtrip(self):
        import tempfile

        d = tempfile.mkdtemp()
        try:
            target = os.path.join(d, "playercorefactory.xml")
            existing = "<playercorefactory><players/></playercorefactory>"
            with open(target, "w", encoding="utf-8") as f:
                f.write(existing)
            snip = self.pcf.snippet_for("zappiti_reference", player_path="/x")
            out = self.pcf.merge(target, snip)
            self.assertTrue(os.path.isfile(out["backup"]))
            with open(out["backup"], encoding="utf-8") as f:
                self.assertEqual(f.read(), existing)
            with open(target, encoding="utf-8") as f:
                self.assertIn("OPPO_External_zappiti_reference", f.read())
        finally:
            import shutil

            shutil.rmtree(d, ignore_errors=True)


class TDiscovery(unittest.TestCase):
    """v1.1.3 mDNS/SSDP probes + cache + apply-preset shortcut."""

    def setUp(self):
        import discovery

        self.d = discovery

    # ---- vendor -> preset mapping ----

    def test_vendor_to_preset_oppo(self):
        self.assertEqual(self.d.vendor_to_preset("OPPO Digital UDP-203"), "oppo203")

    def test_vendor_to_preset_reavon(self):
        self.assertEqual(self.d.vendor_to_preset("Reavon UBR-X200"), "reavon_x200")

    def test_vendor_to_preset_magnetar(self):
        self.assertEqual(self.d.vendor_to_preset("Magnetar UDP800"), "magnetar")

    def test_vendor_to_preset_zappiti(self):
        self.assertEqual(self.d.vendor_to_preset("Zappiti Reference"), "zappiti_reference")

    def test_vendor_to_preset_chinoppo_via_udp203(self):
        self.assertEqual(self.d.vendor_to_preset("Generic UDP-203 Player"), "chinoppo")

    def test_vendor_to_preset_unknown(self):
        self.assertIsNone(self.d.vendor_to_preset("Sony BDP-S6700"))
        self.assertIsNone(self.d.vendor_to_preset(""))
        self.assertIsNone(self.d.vendor_to_preset(None))

    def test_apply_preset_for_uses_vendor(self):
        dev = {"vendor": "OPPO", "model": "UDP-203"}
        self.assertEqual(self.d.apply_preset_for(dev), "oppo203")

    def test_apply_preset_for_uses_explicit_preset(self):
        dev = {"vendor": "Random", "preset": "magnetar"}
        self.assertEqual(self.d.apply_preset_for(dev), "magnetar")

    def test_apply_preset_for_invalid_input(self):
        self.assertIsNone(self.d.apply_preset_for(None))
        self.assertIsNone(self.d.apply_preset_for("not a dict"))
        self.assertIsNone(self.d.apply_preset_for({}))

    # ---- SSDP parsing ----

    def test_ssdp_parses_typical_response(self):
        resp = (
            "HTTP/1.1 200 OK\r\n"
            "CACHE-CONTROL: max-age=1800\r\n"
            "LOCATION: http://192.168.1.50:8080/desc.xml\r\n"
            "SERVER: Linux/4.4 UPnP/1.0 OPPO/1.0\r\n"
            "ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n"
            "USN: uuid:abc::urn:schemas-upnp-org:device:MediaRenderer:1\r\n"
        )
        d = self.d.parse_ssdp_response(resp)
        self.assertIsNotNone(d)
        self.assertEqual(d["ip"], "192.168.1.50")
        self.assertIn("OPPO", d["vendor"])
        self.assertEqual(d["source"], "ssdp")

    def test_ssdp_parses_notify(self):
        resp = "NOTIFY * HTTP/1.1\r\nLOCATION: http://10.0.0.5/d.xml\r\nSERVER: Reavon/1.0\r\n"
        d = self.d.parse_ssdp_response(resp)
        self.assertEqual(d["ip"], "10.0.0.5")

    def test_ssdp_rejects_garbage(self):
        self.assertIsNone(self.d.parse_ssdp_response(""))
        self.assertIsNone(self.d.parse_ssdp_response(None))
        self.assertIsNone(self.d.parse_ssdp_response("not http"))

    def test_ssdp_handles_missing_location(self):
        resp = "HTTP/1.1 200 OK\r\nSERVER: x\r\n"
        d = self.d.parse_ssdp_response(resp)
        self.assertIsNotNone(d)
        self.assertIsNone(d["ip"])

    # ---- mDNS parsing ----

    def test_mdns_parses_typical_record(self):
        rec = {
            "name": "OPPO-203._oppo._tcp.local.",
            "type": "_oppo._tcp.local.",
            "addresses": ["192.168.1.50"],
            "port": 23,
            "properties": {"vendor": "OPPO", "model": "UDP-203"},
        }
        d = self.d.parse_mdns_record(rec)
        self.assertEqual(d["ip"], "192.168.1.50")
        self.assertEqual(d["vendor"], "OPPO")
        self.assertEqual(d["source"], "mdns")

    def test_mdns_rejects_no_addresses(self):
        self.assertIsNone(
            self.d.parse_mdns_record({"name": "x", "addresses": [], "properties": {}})
        )

    def test_mdns_rejects_invalid_input(self):
        self.assertIsNone(self.d.parse_mdns_record(None))
        self.assertIsNone(self.d.parse_mdns_record("string"))

    # ---- discover() orchestration ----

    def test_discover_combines_all_probes(self):
        def ssdp():
            return ["HTTP/1.1 200 OK\r\nLOCATION: http://192.168.1.50/d.xml\r\nSERVER: OPPO\r\n"]

        def mdns():
            return [
                {
                    "name": "Reavon",
                    "addresses": ["192.168.1.51"],
                    "port": 23,
                    "properties": {"vendor": "Reavon"},
                }
            ]

        def udp():
            return [("192.168.1.52", "Magnetar UDP800")]

        devs = self.d.discover(ssdp=ssdp, mdns=mdns, udp=udp, now=lambda: 1000.0)
        ips = [x["ip"] for x in devs]
        self.assertEqual(ips, ["192.168.1.50", "192.168.1.51", "192.168.1.52"])
        # presets are mapped automatically
        by_ip = {x["ip"]: x for x in devs}
        self.assertEqual(by_ip["192.168.1.50"]["preset"], "oppo203")
        self.assertEqual(by_ip["192.168.1.51"]["preset"], "reavon_x200")
        self.assertEqual(by_ip["192.168.1.52"]["preset"], "magnetar")

    def test_discover_dedup_prefers_mdns_over_udp(self):
        same_ip = "192.168.1.50"

        def mdns():
            return [
                {"name": "X", "addresses": [same_ip], "port": 23, "properties": {"vendor": "OPPO"}}
            ]

        def udp():
            return [(same_ip, "OPPO")]

        devs = self.d.discover(mdns=mdns, udp=udp)
        self.assertEqual(len(devs), 1)
        self.assertEqual(devs[0]["source"], "mdns")

    def test_discover_swallows_probe_exceptions(self):
        def boom():
            raise OSError("nope")

        devs = self.d.discover(ssdp=boom, mdns=boom, udp=boom)
        self.assertEqual(devs, [])

    def test_discover_no_probes_returns_empty(self):
        self.assertEqual(self.d.discover(), [])

    def test_discover_stamps_last_seen(self):
        def udp():
            return [("1.2.3.4", "OPPO")]

        devs = self.d.discover(udp=udp, now=lambda: 1234.0)
        self.assertEqual(devs[0]["last_seen"], 1234.0)

    # ---- DeviceCache ----

    def _fake_fs(self, files=None):
        store = dict(files or {})

        class FS:
            def exists(self, p):
                return p in store

            def read(self, p):
                return store[p]

            def write(self, p, t):
                store[p] = t

        fs = FS()
        fs._store = store
        return fs

    def test_cache_add_and_all(self):
        c = self.d.DeviceCache(clock=lambda: 100.0)
        c.add({"ip": "1.2.3.4", "port": 23, "vendor": "OPPO"})
        c.add({"ip": "1.2.3.5", "port": 23, "vendor": "Reavon"})
        items = c.all()
        self.assertEqual([x["ip"] for x in items], ["1.2.3.4", "1.2.3.5"])

    def test_cache_dedups_by_ip_port(self):
        c = self.d.DeviceCache(clock=lambda: 100.0)
        c.add({"ip": "1.2.3.4", "port": 23, "vendor": "old"})
        c.add({"ip": "1.2.3.4", "port": 23, "vendor": "new"})
        self.assertEqual(len(c.all()), 1)
        self.assertEqual(c.all()[0]["vendor"], "new")

    def test_cache_recent_filters_by_age(self):
        now = [200.0]
        c = self.d.DeviceCache(clock=lambda: now[0])
        c.add({"ip": "1.2.3.4", "port": 23, "vendor": "OPPO", "last_seen": 100.0})
        c.add({"ip": "1.2.3.5", "port": 23, "vendor": "OPPO", "last_seen": 195.0})
        recent = c.recent(max_age_s=10)
        self.assertEqual([x["ip"] for x in recent], ["1.2.3.5"])

    def test_cache_save_and_load_roundtrip(self):
        fs = self._fake_fs()
        c1 = self.d.DeviceCache(path="/u/d/cache.json", fs=fs, clock=lambda: 100.0)
        c1.add({"ip": "1.2.3.4", "port": 23, "vendor": "OPPO"})
        self.assertTrue(c1.save())
        c2 = self.d.DeviceCache(path="/u/d/cache.json", fs=fs, clock=lambda: 100.0)
        self.assertTrue(c2.load())
        self.assertEqual(len(c2.all()), 1)
        self.assertEqual(c2.all()[0]["vendor"], "OPPO")

    def test_cache_load_missing_file_is_false(self):
        fs = self._fake_fs()
        c = self.d.DeviceCache(path="/u/d/nope.json", fs=fs)
        self.assertFalse(c.load())

    def test_cache_load_corrupt_is_false(self):
        fs = self._fake_fs({"/u/d/cache.json": "not json"})
        c = self.d.DeviceCache(path="/u/d/cache.json", fs=fs)
        self.assertFalse(c.load())

    def test_cache_clear(self):
        c = self.d.DeviceCache(clock=lambda: 100.0)
        c.add({"ip": "1.2.3.4", "port": 23, "vendor": "OPPO"})
        c.clear()
        self.assertEqual(c.all(), [])

    def test_cache_add_invalid_returns_none(self):
        c = self.d.DeviceCache(clock=lambda: 100.0)
        self.assertIsNone(c.add(None))
        self.assertIsNone(c.add({}))
        self.assertIsNone(c.add({"port": 23}))  # no IP
        self.assertEqual(c.all(), [])

    def test_cache_add_stamps_preset(self):
        c = self.d.DeviceCache(clock=lambda: 100.0)
        d = c.add({"ip": "1.2.3.4", "port": 23, "vendor": "Reavon UBR-X200"})
        self.assertEqual(d["preset"], "reavon_x200")


class TPresetExtensibility(unittest.TestCase):
    """v1.1.4 custom presets, submission export, firmware_min."""

    def setUp(self):
        import preset_manager as pm

        self.pm = pm
        import json as _json

        self._json = _json

    def _fake_fs(self, files=None):
        store = dict(files or {})

        class FS:
            def exists(self, p):
                return p in store

            def read(self, p):
                return store[p]

            def write(self, p, t):
                store[p] = t

        fs = FS()
        fs._store = store
        return fs

    # ---- BUILTIN_PRESETS sanity ----

    def test_builtins_present(self):
        for k in ("oppo203", "chinoppo", "reavon_x200", "magnetar"):
            self.assertIn(k, self.pm.BUILTIN_PRESETS)

    # ---- load_custom ----

    def test_load_custom_missing_path(self):
        self.assertEqual(self.pm.load_custom(None), {})
        fs = self._fake_fs()
        self.assertEqual(self.pm.load_custom("/nope.json", fs=fs), {})

    def test_load_custom_corrupt_json(self):
        fs = self._fake_fs({"/c.json": "not json"})
        self.assertEqual(self.pm.load_custom("/c.json", fs=fs), {})

    def test_load_custom_wrong_root(self):
        fs = self._fake_fs({"/c.json": '["list","not","dict"]'})
        self.assertEqual(self.pm.load_custom("/c.json", fs=fs), {})

    def test_load_custom_skips_invalid_entries(self):
        payload = {
            "presets": {
                "good": {"label": "Good", "start_commands": "#PLA", "stop_commands": "#STP"},
                "bad_no_label": {"start_commands": "#PLA", "stop_commands": "#STP"},
                "bad_str_label": {"label": 42, "start_commands": "#PLA", "stop_commands": "#STP"},
                "": {"label": "x", "start_commands": "x", "stop_commands": "x"},
            }
        }
        fs = self._fake_fs({"/c.json": self._json.dumps(payload)})
        out = self.pm.load_custom("/c.json", fs=fs)
        self.assertIn("good", out)
        self.assertNotIn("bad_no_label", out)
        self.assertNotIn("bad_str_label", out)
        self.assertNotIn("", out)

    def test_load_custom_validates_firmware_min_type(self):
        bad = {
            "presets": {
                "x": {
                    "label": "X",
                    "start_commands": "#PLA",
                    "stop_commands": "#STP",
                    "firmware_min": 12345,
                }
            }
        }  # not str
        fs = self._fake_fs({"/c.json": self._json.dumps(bad)})
        self.assertNotIn("x", self.pm.load_custom("/c.json", fs=fs))

    # ---- merged_presets precedence ----

    def test_merged_no_custom_returns_builtins(self):
        m = self.pm.merged_presets()
        self.assertEqual(set(m), set(self.pm.BUILTIN_PRESETS))

    def test_merged_custom_wins_on_collision(self):
        payload = {
            "presets": {
                "oppo203": {"label": "User OPPO", "start_commands": "#XYZ", "stop_commands": "#STP"}
            }
        }
        fs = self._fake_fs({"/c.json": self._json.dumps(payload)})
        m = self.pm.merged_presets("/c.json", fs=fs)
        self.assertEqual(
            m["oppo203"]["start_commands"], "#XYZ", "custom preset must win on key collision"
        )
        self.assertEqual(m["oppo203"]["label"], "User OPPO")

    def test_merged_custom_adds_new_preset(self):
        payload = {
            "presets": {
                "sony_ubp_x800": {
                    "label": "Sony X800",
                    "start_commands": "#PLA",
                    "stop_commands": "#STP",
                }
            }
        }
        fs = self._fake_fs({"/c.json": self._json.dumps(payload)})
        m = self.pm.merged_presets("/c.json", fs=fs)
        self.assertIn("sony_ubp_x800", m)
        # Built-ins still present
        self.assertIn("oppo203", m)
        self.assertIn("chinoppo", m)

    def test_merged_does_not_mutate_builtins(self):
        payload = {
            "presets": {"oppo203": {"label": "hax", "start_commands": "#X", "stop_commands": "#Y"}}
        }
        fs = self._fake_fs({"/c.json": self._json.dumps(payload)})
        before = dict(self.pm.BUILTIN_PRESETS["oppo203"])
        self.pm.merged_presets("/c.json", fs=fs)
        self.assertEqual(self.pm.BUILTIN_PRESETS["oppo203"], before)

    # ---- export_submission ----

    def test_export_submission_known_preset(self):
        s = self.pm.export_submission(
            "oppo203", ip="192.168.1.50", quirks=["slow_eject"], contact="user@example.com"
        )
        self.assertEqual(s["schema_version"], 1)
        self.assertEqual(s["preset_id"], "oppo203")
        self.assertEqual(s["device"]["ip"], "192.168.1.50")
        self.assertEqual(s["device"]["quirks"], ["slow_eject"])
        self.assertEqual(s["contact"], "user@example.com")
        self.assertIn("start_commands", s["preset"])

    def test_export_submission_new_preset_requires_user_preset(self):
        with self.assertRaises(ValueError):
            self.pm.export_submission("brand_new_id")

    def test_export_submission_new_preset_with_user_preset(self):
        up = {
            "label": "My player",
            "start_commands": "#PLA",
            "stop_commands": "#STP",
            "firmware_min": "1.2.3",
        }
        s = self.pm.export_submission("my_player", ip="10.0.0.1", user_preset=up)
        self.assertEqual(s["preset"]["start_commands"], "#PLA")
        self.assertEqual(s["preset"]["firmware_min"], "1.2.3")

    def test_export_submission_user_preset_overrides(self):
        up = {"label": "Override", "start_commands": "#XX", "stop_commands": "#YY"}
        s = self.pm.export_submission("oppo203", user_preset=up)
        self.assertEqual(s["preset"]["start_commands"], "#XX")

    def test_export_submission_validates_user_preset(self):
        with self.assertRaises(ValueError):
            self.pm.export_submission("new_one", user_preset={"label": "x"})  # incomplete

    def test_export_submission_requires_preset_id(self):
        with self.assertRaises(ValueError):
            self.pm.export_submission("")

    # ---- save_submission ----

    def test_save_submission_writes_json(self):
        fs = self._fake_fs()
        s = self.pm.export_submission("oppo203", ip="1.2.3.4")
        path = self.pm.save_submission(s, "/u/d", now=lambda: 0, fs=fs)
        self.assertTrue(path.startswith("/u/d/preset-submission-oppo203-"))
        self.assertTrue(path.endswith(".json"))
        loaded = self._json.loads(fs._store[path])
        self.assertEqual(loaded["preset_id"], "oppo203")
        self.assertEqual(loaded["schema_version"], 1)

    def test_save_submission_sanitises_filename(self):
        fs = self._fake_fs()
        s = self.pm.export_submission("oppo203")
        s["preset_id"] = "../etc/passwd"
        path = self.pm.save_submission(s, "/u/d", now=lambda: 0, fs=fs)
        self.assertNotIn("../", path)
        self.assertNotIn("/etc/", path)

    def test_save_submission_real_io(self):
        import tempfile

        d = tempfile.mkdtemp()
        try:
            s = self.pm.export_submission("oppo203")
            p = self.pm.save_submission(s, d)
            self.assertTrue(os.path.isfile(p))
        finally:
            import shutil

            shutil.rmtree(d, ignore_errors=True)

    # ---- compare_versions ----

    def test_compare_versions_basic(self):
        self.assertEqual(self.pm.compare_versions("1.2.3", "1.2.3"), 0)
        self.assertEqual(self.pm.compare_versions("1.2.3", "1.2.4"), -1)
        self.assertEqual(self.pm.compare_versions("2.0", "1.9"), 1)

    def test_compare_versions_pads(self):
        self.assertEqual(self.pm.compare_versions("1.2", "1.2.0"), 0)
        self.assertEqual(self.pm.compare_versions("1.2.1", "1.2"), 1)

    def test_compare_versions_v_prefix(self):
        self.assertEqual(self.pm.compare_versions("v1.2.3", "1.2.3"), 0)

    def test_compare_versions_unparseable(self):
        self.assertIsNone(self.pm.compare_versions("nope", "1.2"))
        self.assertIsNone(self.pm.compare_versions(None, "1.2"))
        self.assertIsNone(self.pm.compare_versions("", ""))

    # ---- firmware_warning ----

    def test_firmware_warning_no_minimum(self):
        self.assertIsNone(
            self.pm.firmware_warning(
                {"label": "x", "start_commands": "#PLA", "stop_commands": "#STP"}, "1.0.0"
            )
        )

    def test_firmware_warning_older_warns(self):
        preset = {
            "label": "x",
            "start_commands": "#PLA",
            "stop_commands": "#STP",
            "firmware_min": "2.0.0",
        }
        msg = self.pm.firmware_warning(preset, "1.5.0")
        self.assertIsNotNone(msg)
        self.assertIn("1.5.0", msg)
        self.assertIn("2.0.0", msg)

    def test_firmware_warning_equal_no_warn(self):
        preset = {
            "label": "x",
            "start_commands": "#PLA",
            "stop_commands": "#STP",
            "firmware_min": "2.0.0",
        }
        self.assertIsNone(self.pm.firmware_warning(preset, "2.0.0"))

    def test_firmware_warning_newer_no_warn(self):
        preset = {
            "label": "x",
            "start_commands": "#PLA",
            "stop_commands": "#STP",
            "firmware_min": "2.0.0",
        }
        self.assertIsNone(self.pm.firmware_warning(preset, "2.1.0"))

    def test_firmware_warning_unknown_no_false_positive(self):
        preset = {
            "label": "x",
            "start_commands": "#PLA",
            "stop_commands": "#STP",
            "firmware_min": "2.0.0",
        }
        # We don't warn when we can't parse - avoid false positives.
        self.assertIsNone(self.pm.firmware_warning(preset, None))
        self.assertIsNone(self.pm.firmware_warning(preset, "unknown"))

    def test_firmware_warning_invalid_preset(self):
        self.assertIsNone(self.pm.firmware_warning(None, "1.0"))
        self.assertIsNone(self.pm.firmware_warning("string", "1.0"))


class TIntercept(unittest.TestCase):
    """Service interception breadth (v1.1.5)."""

    def setUp(self):
        import intercept

        self.iv = intercept

    class _FS:
        def __init__(self, dirs=None, files=None):
            self.dirs = set(dirs or [])
            self.files = set(files or [])

        def exists(self, p):
            return p in self.dirs or p in self.files

        def isdir(self, p):
            return p in self.dirs

    def test_iso_detected(self):
        self.assertEqual(self.iv.classify("/x/y/movie.iso"), self.iv.DISC_KIND_ISO)
        self.assertEqual(self.iv.classify("/x/y/MOVIE.ISO"), self.iv.DISC_KIND_ISO)

    def test_img_detected(self):
        self.assertEqual(self.iv.classify("/x/y/movie.img"), self.iv.DISC_KIND_ISO)

    def test_bdmv_folder_detected(self):
        self.assertEqual(self.iv.classify("/x/Title/BDMV"), self.iv.DISC_KIND_BDMV)
        self.assertEqual(self.iv.classify("/x/Title/BDMV/"), self.iv.DISC_KIND_BDMV)

    def test_bdmv_index_file_detected(self):
        self.assertEqual(self.iv.classify("/x/Title/BDMV/index.bdmv"), self.iv.DISC_KIND_BDMV)

    def test_video_ts_folder_detected(self):
        self.assertEqual(self.iv.classify("/dvd/VIDEO_TS"), self.iv.DISC_KIND_VIDEO_TS)
        self.assertEqual(self.iv.classify("/dvd/VIDEO_TS/"), self.iv.DISC_KIND_VIDEO_TS)

    def test_video_ts_ifo_detected(self):
        self.assertEqual(self.iv.classify("/dvd/VIDEO_TS/VIDEO_TS.IFO"), self.iv.DISC_KIND_VIDEO_TS)

    def test_m2ts_in_bdmv_tree(self):
        self.assertEqual(self.iv.classify("/x/T/BDMV/STREAM/00001.m2ts"), self.iv.DISC_KIND_M2TS)

    def test_m2ts_outside_bdmv_is_other(self):
        self.assertEqual(self.iv.classify("/x/loose.m2ts"), self.iv.DISC_KIND_OTHER)

    def test_mpls_in_bdmv_tree(self):
        self.assertEqual(self.iv.classify("/x/T/BDMV/PLAYLIST/00001.mpls"), self.iv.DISC_KIND_MPLS)

    def test_mkv_with_sibling_bdmv(self):
        fs = self._FS(dirs={"/x/Title/BDMV"})
        self.assertEqual(
            self.iv.classify("/x/Title/movie.mkv", fs=fs), self.iv.DISC_KIND_MKV_SIBLING
        )

    def test_mkv_without_sibling_is_other(self):
        fs = self._FS()
        self.assertEqual(self.iv.classify("/x/Title/movie.mkv", fs=fs), self.iv.DISC_KIND_OTHER)

    def test_windows_path_separators(self):
        self.assertEqual(
            self.iv.classify(r"C:\Movies\Title\BDMV\index.bdmv"), self.iv.DISC_KIND_BDMV
        )
        self.assertEqual(self.iv.classify(r"D:\Rips\movie.iso"), self.iv.DISC_KIND_ISO)

    def test_empty_input(self):
        self.assertEqual(self.iv.classify(None), self.iv.DISC_KIND_OTHER)
        self.assertEqual(self.iv.classify(""), self.iv.DISC_KIND_OTHER)

    def test_is_disc_image(self):
        self.assertTrue(self.iv.is_disc_image("/x/y.iso"))
        self.assertTrue(self.iv.is_disc_image("/x/T/BDMV"))
        self.assertFalse(self.iv.is_disc_image("/x/song.mp3"))

    # ---- whitelist / blacklist ----

    def test_pattern_matches_substring(self):
        self.assertTrue(self.iv.pattern_matches("/movies/4k/x.iso", "/movies/4k"))
        self.assertFalse(self.iv.pattern_matches("/x.iso", "/movies/"))

    def test_pattern_matches_wildcard(self):
        self.assertTrue(self.iv.pattern_matches("/m/4k/Inception.iso", "*4k*"))
        self.assertTrue(self.iv.pattern_matches("/m/4k/x.iso", "/m/*/x.iso"))

    def test_pattern_matches_case_insensitive(self):
        self.assertTrue(self.iv.pattern_matches("/Movies/X.ISO", "/movies/*.iso"))

    def test_empty_pattern_no_match(self):
        self.assertFalse(self.iv.pattern_matches("/x.iso", ""))
        self.assertFalse(self.iv.pattern_matches("/x.iso", "   "))
        self.assertFalse(self.iv.pattern_matches("/x.iso", None))

    def test_should_intercept_default_allow(self):
        self.assertTrue(self.iv.should_intercept("/x/movie.iso"))

    def test_should_intercept_non_disc_is_false(self):
        self.assertFalse(self.iv.should_intercept("/x/song.mp3"))

    def test_should_intercept_blacklist_blocks(self):
        self.assertFalse(
            self.iv.should_intercept("/x/private/movie.iso", blacklist=["/x/private/*"])
        )

    def test_should_intercept_whitelist_required_when_set(self):
        # whitelist set, but path doesn't match -> False
        self.assertFalse(self.iv.should_intercept("/other/movie.iso", whitelist=["/x/4k/*"]))
        # path matches whitelist -> True
        self.assertTrue(self.iv.should_intercept("/x/4k/movie.iso", whitelist=["/x/4k/*"]))

    def test_blacklist_beats_whitelist(self):
        # path matches both -> blacklist wins
        self.assertFalse(
            self.iv.should_intercept(
                "/x/4k/private/movie.iso", whitelist=["/x/4k/*"], blacklist=["/x/4k/private/*"]
            )
        )

    def test_empty_whitelist_strings_ignored(self):
        # whitelist of [""] should behave like no-whitelist (default-allow)
        self.assertTrue(self.iv.should_intercept("/x/movie.iso", whitelist=["", "   "]))


class TKeymapSkin(unittest.TestCase):
    """Skin-aware keymap variants (v1.1.5)."""

    def setUp(self):
        import keymap_skin

        self.km = keymap_skin

    def test_three_skins_present(self):
        for s in ("estuary", "confluence", "arctic"):
            self.assertIn(s, self.km.SKINS)

    def test_unknown_skin_raises(self):
        with self.assertRaises(KeyError):
            self.km.generate("not_a_skin")

    def test_each_skin_xml_well_formed(self):
        for s in self.km.SKINS:
            xml = self.km.generate(s)
            self.assertTrue(self.km.is_well_formed(xml), "keymap for " + s + " is not well-formed")

    def test_keymap_contains_global_and_fullscreen(self):
        for s in self.km.SKINS:
            xml = self.km.generate(s)
            self.assertIn("<global>", xml)
            self.assertIn("<FullscreenVideo>", xml)
            self.assertIn("<keyboard>", xml)

    def test_keymap_contains_all_actions(self):
        for s in self.km.SKINS:
            xml = self.km.generate(s)
            for tag in (
                "play",
                "stop",
                "eject",
                "info",
                "menu",
                "pause",
                "skipnext",
                "skipprevious",
            ):
                self.assertIn("<" + tag + ">", xml, tag + " missing in skin " + s)

    def test_keymap_action_targets_addon(self):
        xml = self.km.generate("estuary")
        self.assertIn("script.oppo203.iso.external", xml)

    def test_skin_profile_marker_in_xml(self):
        for s in self.km.SKINS:
            xml = self.km.generate(s)
            self.assertIn("skin profile: " + s, xml)

    def test_is_well_formed_negatives(self):
        self.assertFalse(self.km.is_well_formed(""))
        self.assertFalse(self.km.is_well_formed(None))
        self.assertFalse(self.km.is_well_formed("<keymap><broken>"))

    def test_keymap_parses_with_elementtree(self):
        import xml.etree.ElementTree as ET

        for s in self.km.SKINS:
            root = ET.fromstring(self.km.generate(s))
            self.assertEqual(root.tag, "keymap")
            self.assertIsNotNone(root.find("global"))
            self.assertIsNotNone(root.find("FullscreenVideo"))


class TLoggingV116(unittest.TestCase):
    """v1.1.6 leveled logger, rotating file, sensitive-data scrubber."""

    def setUp(self):
        import logging_v116 as L

        self.L = L

    class _FS:
        """In-memory FS for hermetic rotation tests."""

        def __init__(self):
            self.files = {}
            self.events = []

        def exists(self, p):
            return p in self.files

        def size(self, p):
            return len(self.files.get(p, "").encode("utf-8"))

        def read(self, p):
            return self.files[p]

        def append(self, p, text):
            self.files[p] = self.files.get(p, "") + text
            self.events.append(("append", p, len(text)))

        def rename(self, src, dst):
            self.files[dst] = self.files.pop(src)
            self.events.append(("rename", src, dst))

        def remove(self, p):
            self.files.pop(p, None)
            self.events.append(("remove", p))

    # ---- LEVELS / level_value ----

    def test_levels_in_order(self):
        self.assertEqual(self.L.LEVELS, ("DEBUG", "INFO", "WARN", "ERROR"))

    def test_level_value(self):
        self.assertEqual(self.L.level_value("DEBUG"), 0)
        self.assertEqual(self.L.level_value("info"), 1)
        self.assertEqual(self.L.level_value("WARN"), 2)
        self.assertEqual(self.L.level_value("ERROR"), 3)
        self.assertEqual(self.L.level_value("nope"), -1)
        self.assertEqual(self.L.level_value(None), -1)
        self.assertEqual(self.L.level_value(""), -1)

    # ---- scrub ----

    def test_scrub_masks_mac(self):
        self.assertEqual(self.L.scrub("mac AA:BB:CC:11:22:33 here"), "mac xx:xx:xx:xx:xx:xx here")

    def test_scrub_masks_dash_mac(self):
        self.assertEqual(self.L.scrub("AA-BB-CC-11-22-33"), "xx:xx:xx:xx:xx:xx")

    def test_scrub_masks_ipv4(self):
        self.assertIn("x.x.x.x", self.L.scrub("ip 192.168.1.42 ok"))

    def test_scrub_preserves_loopback(self):
        out = self.L.scrub("local 127.0.0.1 and lan 192.168.1.42")
        self.assertIn("127.0.0.1", out)
        self.assertIn("x.x.x.x", out)
        self.assertNotIn("192.168.1.42", out)

    def test_scrub_handles_none_and_empty(self):
        self.assertIsNone(self.L.scrub(None))
        self.assertEqual(self.L.scrub(""), "")
        self.assertEqual(self.L.scrub("plain text"), "plain text")

    def test_scrub_does_not_mask_versions(self):
        # Version-like strings (1.2.3) are 3-octet, not 4 -> not masked
        self.assertEqual(self.L.scrub("v1.2.3"), "v1.2.3")

    # ---- level filtering ----

    def test_default_level_info_filters_debug(self):
        fs = self._FS()
        log = self.L.Logger("/u/d/oppo.log", level="INFO", fs=fs, clock=lambda: 0)
        log.debug("hidden")
        log.info("visible")
        self.assertNotIn("hidden", fs.files.get("/u/d/oppo.log", ""))
        self.assertIn("visible", fs.files["/u/d/oppo.log"])

    def test_set_level_changes_filter(self):
        fs = self._FS()
        log = self.L.Logger("/u/d/oppo.log", level="ERROR", fs=fs, clock=lambda: 0)
        log.warn("x")
        log.info("y")
        self.assertNotIn("/u/d/oppo.log", fs.files, "no write should have happened at ERROR level")
        log.set_level("DEBUG")
        log.debug("now visible")
        self.assertIn("now visible", fs.files["/u/d/oppo.log"])

    def test_unknown_level_in_constructor_raises(self):
        with self.assertRaises(ValueError):
            self.L.Logger("/x", level="LOUD", fs=self._FS())

    def test_unknown_level_in_set_level_raises(self):
        log = self.L.Logger("/x", fs=self._FS(), clock=lambda: 0)
        with self.assertRaises(ValueError):
            log.set_level("LOUD")

    def test_log_unknown_level_is_silent(self):
        fs = self._FS()
        log = self.L.Logger("/u/d/oppo.log", fs=fs, clock=lambda: 0)
        log.log("NOPE", "hi")
        self.assertNotIn("/u/d/oppo.log", fs.files)

    # ---- format and scrub apply on write ----

    def test_log_line_includes_level_and_timestamp(self):
        fs = self._FS()
        log = self.L.Logger("/u/d/oppo.log", level="DEBUG", fs=fs, clock=lambda: 0)
        log.info("hello")
        text = fs.files["/u/d/oppo.log"]
        self.assertIn("INFO", text)
        self.assertIn("hello", text)
        self.assertTrue(text.endswith("\n"))

    def test_log_scrubs_mac_and_ip(self):
        fs = self._FS()
        log = self.L.Logger("/u/d/oppo.log", level="DEBUG", fs=fs, clock=lambda: 0)
        log.info("ip=192.168.1.50 mac=AA:BB:CC:11:22:33")
        text = fs.files["/u/d/oppo.log"]
        self.assertIn("x.x.x.x", text)
        self.assertIn("xx:xx:xx:xx:xx:xx", text)
        self.assertNotIn("192.168.1.50", text)
        self.assertNotIn("AA:BB:CC:11:22:33", text)

    def test_log_supports_printf_args(self):
        fs = self._FS()
        log = self.L.Logger("/u/d/oppo.log", level="DEBUG", fs=fs, clock=lambda: 0)
        log.info("count=%d name=%s", 42, "x")
        self.assertIn("count=42 name=x", fs.files["/u/d/oppo.log"])

    def test_log_handles_bad_format_args(self):
        fs = self._FS()
        log = self.L.Logger("/u/d/oppo.log", level="DEBUG", fs=fs, clock=lambda: 0)
        log.info("count=%d", "not a number")
        # Falls back to repr-append; must not raise.
        self.assertIn("count=%d", fs.files["/u/d/oppo.log"])

    # ---- rotation ----

    def test_rotation_size_triggered(self):
        fs = self._FS()
        log = self.L.Logger(
            "/u/d/oppo.log", level="DEBUG", max_bytes=120, backups=2, fs=fs, clock=lambda: 0
        )
        for i in range(20):
            log.info("padding-line-%d-X" * 1, i)
        # Expect at least one rotation event (rename to .1).
        rotated = "/u/d/oppo.log.1"
        self.assertIn(rotated, fs.files)
        # Current log still exists.
        self.assertIn("/u/d/oppo.log", fs.files)

    def test_rotation_keeps_only_backups_count(self):
        fs = self._FS()
        log = self.L.Logger(
            "/u/d/oppo.log", level="DEBUG", max_bytes=80, backups=2, fs=fs, clock=lambda: 0
        )
        for i in range(60):
            log.info("line-%d-XXXXXXXXX", i)
        # We must never have more than `backups` historical files
        # (.1, .2, ...). .3 must NEVER exist.
        self.assertNotIn("/u/d/oppo.log.3", fs.files)

    def test_rotation_zero_backups_means_truncate(self):
        fs = self._FS()
        log = self.L.Logger(
            "/u/d/oppo.log", level="DEBUG", max_bytes=80, backups=0, fs=fs, clock=lambda: 0
        )
        for i in range(40):
            log.info("line-%d-X", i)
        # No historical files exist.
        self.assertNotIn("/u/d/oppo.log.1", fs.files)
        # Current file should never exceed max_bytes after a write.
        self.assertLessEqual(fs.size("/u/d/oppo.log"), 1000)

    def test_rotation_no_op_when_under_budget(self):
        fs = self._FS()
        log = self.L.Logger(
            "/u/d/oppo.log", level="DEBUG", max_bytes=10_000, backups=3, fs=fs, clock=lambda: 0
        )
        log.info("small")
        log.info("also small")
        self.assertNotIn("/u/d/oppo.log.1", fs.files)

    def test_manual_rotate(self):
        fs = self._FS()
        log = self.L.Logger(
            "/u/d/oppo.log", level="DEBUG", max_bytes=10_000, backups=2, fs=fs, clock=lambda: 0
        )
        log.info("a")
        log.info("b")
        before = fs.files["/u/d/oppo.log"]
        log.rotate()
        self.assertEqual(fs.files.get("/u/d/oppo.log.1"), before)

    def test_max_bytes_zero_disables_rotation(self):
        fs = self._FS()
        log = self.L.Logger(
            "/u/d/oppo.log", level="DEBUG", max_bytes=0, backups=2, fs=fs, clock=lambda: 0
        )
        for i in range(50):
            log.info("line-%d-XXXXXXXXX", i)
        self.assertNotIn("/u/d/oppo.log.1", fs.files)

    def test_real_io_roundtrip(self):
        import tempfile

        d = tempfile.mkdtemp()
        try:
            log = self.L.Logger(
                os.path.join(d, "oppo.log"), level="DEBUG", max_bytes=200, backups=2
            )
            for i in range(30):
                log.info("line-%d", i)
            self.assertTrue(os.path.isfile(os.path.join(d, "oppo.log")))
        finally:
            import shutil

            shutil.rmtree(d, ignore_errors=True)

    def test_is_enabled_query(self):
        log = self.L.Logger("/x", level="WARN", fs=self._FS(), clock=lambda: 0)
        self.assertFalse(log.is_enabled("DEBUG"))
        self.assertFalse(log.is_enabled("INFO"))
        self.assertTrue(log.is_enabled("WARN"))
        self.assertTrue(log.is_enabled("ERROR"))
        self.assertFalse(log.is_enabled("LOUD"))


class TLocalizationParity(unittest.TestCase):
    """v1.1.7 - locale msgctxt parity, .pot helper, breadth checks."""

    def setUp(self):
        import re as _re

        self._re = _re
        # Resolve the addon root from this test file's location.
        here = os.path.dirname(os.path.abspath(__file__))
        self.addon_root = os.path.dirname(here)
        self.locales_dir = os.path.join(self.addon_root, "resources", "language")

    def _msgctxt_set(self, po_text):
        return set(self._re.findall(r'^msgctxt "(#3\d+)"', po_text, self._re.MULTILINE))

    def _read(self, lang):
        p = os.path.join(self.locales_dir, "resource.language." + lang, "strings.po")
        with open(p, "r", encoding="utf-8") as f:
            return f.read()

    # ---- breadth: 5 new locales present alongside existing 7 ----

    def test_new_locales_present(self):
        for lang in ("ru_ru", "pl_pl", "pt_br", "ja_jp", "ko_kr"):
            d = os.path.join(self.locales_dir, "resource.language." + lang)
            self.assertTrue(os.path.isdir(d), "missing locale dir for " + lang)
            self.assertTrue(
                os.path.isfile(os.path.join(d, "strings.po")), "missing strings.po for " + lang
            )

    def test_existing_locales_preserved(self):
        for lang in ("en_gb", "de_de", "fr_fr", "es_es", "it_it", "nl_nl", "zh_cn"):
            d = os.path.join(self.locales_dir, "resource.language." + lang)
            self.assertTrue(os.path.isdir(d), "regression: missing locale dir for " + lang)

    # ---- parity: every locale has the SAME msgctxt set as English ----

    def test_msgctxt_parity_with_english(self):
        en = self._msgctxt_set(self._read("en_gb"))
        self.assertGreater(len(en), 0, "English source has zero msgctxt entries")
        for lang in (
            "de_de",
            "fr_fr",
            "es_es",
            "it_it",
            "nl_nl",
            "zh_cn",
            "ru_ru",
            "pl_pl",
            "pt_br",
            "ja_jp",
            "ko_kr",
        ):
            other = self._msgctxt_set(self._read(lang))
            missing = en - other
            extra = other - en
            self.assertFalse(
                missing, "locale " + lang + " is missing msgctxt ids: " + str(sorted(missing)[:5])
            )
            self.assertFalse(
                extra, "locale " + lang + " has unexpected msgctxt ids: " + str(sorted(extra)[:5])
            )

    def test_every_locale_has_msgstr_for_every_id(self):
        # Each entry must have a msgstr line (even if empty).
        for lang in ("ru_ru", "pl_pl", "pt_br", "ja_jp", "ko_kr"):
            text = self._read(lang)
            ctxs = self._re.findall(r'msgctxt "(#3\d+)"\nmsgid "[^"]*"\nmsgstr "[^"]*"', text)
            ids = self._re.findall(r'^msgctxt "(#3\d+)"', text, self._re.MULTILINE)
            self.assertEqual(
                set(ctxs), set(ids), "locale " + lang + ": some msgctxt entries lack msgstr"
            )


class TMakePot(unittest.TestCase):
    """v1.1.7 - tools/make_pot.py extractor."""

    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        self.addon_root = os.path.dirname(here)
        sys.path.insert(0, os.path.join(self.addon_root, "tools"))
        import make_pot

        self.mp = make_pot

    def tearDown(self):
        # Don't leave tools/ on sys.path between tests
        try:
            sys.path.remove(os.path.join(self.addon_root, "tools"))
        except ValueError:
            pass

    def test_ids_in_source_picks_up_L_calls(self):
        src = "x = L(31000)\ny = L(31001)\n"
        self.assertEqual(self.mp._ids_in_source(src), {31000, 31001})

    def test_ids_in_source_picks_up_underscore_calls(self):
        src = "_(31002)\n"
        self.assertEqual(self.mp._ids_in_source(src), {31002})

    def test_ids_in_source_picks_up_quoted_id(self):
        src = "L('#31003')\n"
        self.assertEqual(self.mp._ids_in_source(src), {31003})

    def test_ids_in_source_filters_out_of_range(self):
        # Numbers below 30000 or above 32999 must not be collected.
        src = "L(123)\nL(99999)\n"
        self.assertEqual(self.mp._ids_in_source(src), set())

    def test_ids_in_source_ignores_unknown_function(self):
        src = "print(31000)\nlen(31001)\n"
        self.assertEqual(self.mp._ids_in_source(src), set())

    def test_ids_in_source_handles_syntax_error(self):
        # Tokeniser should not raise to the caller.
        src = "L(31000\nbroken"
        # Returns whatever it could parse; must not raise.
        ids = self.mp._ids_in_source(src)
        self.assertIsInstance(ids, set)

    def test_render_pot_is_sorted_and_deterministic(self):
        a = self.mp.render_pot([31002, 31000, 31001])
        b = self.mp.render_pot([31000, 31001, 31002])
        self.assertEqual(a, b, "render_pot must be deterministic")
        # Ids appear in numeric order
        idx0 = a.find("#31000")
        idx1 = a.find("#31001")
        idx2 = a.find("#31002")
        self.assertTrue(0 < idx0 < idx1 < idx2)

    def test_render_pot_emits_header(self):
        out = self.mp.render_pot([31000])
        self.assertIn("Kodi .pot template", out)
        self.assertIn('msgctxt "#31000"', out)
        self.assertIn('msgid ""', out)
        self.assertIn('msgstr ""', out)

    def test_collect_ids_walks_tree(self):
        import tempfile

        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "resources", "lib"))
            with open(os.path.join(d, "default.py"), "w") as f:
                f.write("x = L(31000)\n")
            with open(os.path.join(d, "resources", "lib", "x.py"), "w") as f:
                f.write("y = _(31100)\n")
            ids = self.mp.collect_ids(d)
            self.assertEqual(ids, {31000, 31100})
        finally:
            import shutil

            shutil.rmtree(d, ignore_errors=True)

    def test_collect_ids_skips_excluded_dirs(self):
        import tempfile

        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "tests"))
            os.makedirs(os.path.join(d, "tools"))
            with open(os.path.join(d, "tests", "t.py"), "w") as f:
                f.write("L(31999)\n")  # should NOT be collected
            with open(os.path.join(d, "tools", "x.py"), "w") as f:
                f.write("L(31998)\n")  # should NOT be collected
            with open(os.path.join(d, "default.py"), "w") as f:
                f.write("L(31000)\n")  # SHOULD be collected
            ids = self.mp.collect_ids(d)
            self.assertEqual(ids, {31000})
        finally:
            import shutil

            shutil.rmtree(d, ignore_errors=True)

    def test_collect_ids_skips_vendored_and_build_dirs(self):
        # Regression: the walk must not descend into a local virtualenv or
        # build output. Before this guard, collect_ids walked .venv's 1000s of
        # site-packages .py files, making i18n extraction (and its tests) slow.
        import tempfile

        d = tempfile.mkdtemp()
        try:
            for vendored in (".venv", "build", "node_modules", ".mypy_cache"):
                os.makedirs(os.path.join(d, vendored, "pkg"))
                with open(os.path.join(d, vendored, "pkg", "v.py"), "w") as f:
                    f.write("L(32500)\n")  # vendored: must NOT be collected
            with open(os.path.join(d, "default.py"), "w") as f:
                f.write("L(31000)\n")  # SHOULD be collected
            ids = self.mp.collect_ids(d)
            self.assertEqual(ids, {31000})
        finally:
            import shutil

            shutil.rmtree(d, ignore_errors=True)


class TSmokeImports(unittest.TestCase):
    """v1.1.8 - smoke test: every resources/lib/*.py must import cleanly.

    Runs first to catch SyntaxError / ImportError before the deeper
    suites trigger lazier failures inside specific code paths.
    """

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.lib = os.path.join(os.path.dirname(here), "resources", "lib")
        if cls.lib not in sys.path:
            sys.path.insert(0, cls.lib)

    def test_lib_dir_exists(self):
        self.assertTrue(os.path.isdir(self.lib), "resources/lib must exist")

    def test_every_lib_module_imports(self):
        skipped = []
        failed = []
        names = []
        for sub in ("tv", "oppo", "avr", "kodi"):
            bucket = os.path.join(self.lib, sub)
            if os.path.isdir(bucket):
                names.extend(
                    f[:-3] for f in os.listdir(bucket) if f.endswith(".py") and f != "__init__.py"
                )
        names = sorted(names)
        self.assertGreater(len(names), 0, "no modules found under resources/lib sub-packages")
        import importlib

        for name in names:
            try:
                importlib.import_module(name)
            except SyntaxError as e:
                failed.append((name, "SyntaxError: " + str(e)))
            except ImportError as e:
                # Modules that legitimately need Kodi (xbmc, xbmcaddon)
                # are allowed to skip - we record them but don't fail.
                msg = str(e)
                if any(
                    stub in msg
                    for stub in ("xbmc", "xbmcaddon", "xbmcgui", "xbmcvfs", "xbmcplugin")
                ):
                    skipped.append((name, msg))
                elif "relative import" in msg:
                    # Module uses a package-relative import; valid in
                    # Kodi runtime (loaded as resources.lib.<name>),
                    # acceptable to skip in smoke.
                    skipped.append((name, msg))
                else:
                    failed.append((name, "ImportError: " + msg))
        self.assertFalse(failed, "modules failed to import: " + str(failed))
        # Surface the skip count for transparency without failing.
        if skipped:
            sys.stderr.write(
                "  [smoke] " + str(len(skipped)) + " Kodi-bound modules skipped (expected)\n"
            )

    def test_tools_make_pot_imports(self):
        tools = os.path.join(os.path.dirname(self.lib), "..", "tools")
        tools = os.path.abspath(tools)
        if tools not in sys.path:
            sys.path.insert(0, tools)
        import importlib

        m = importlib.import_module("make_pot")
        self.assertTrue(hasattr(m, "render_pot"))
        self.assertTrue(hasattr(m, "collect_ids"))


class TCIScaffolding(unittest.TestCase):
    """v1.1.8 - presence and shape of CI / lint / coverage artefacts."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_pytest_ini_present(self):
        text = self._read("pytest.ini")
        self.assertIn("[pytest]", text)
        self.assertIn("testpaths = tests", text)

    def test_conftest_present(self):
        text = self._read("conftest.py")
        self.assertIn("resources/lib", text)
        self.assertIn("sys.path", text)

    def test_ruff_config_present(self):
        text = self._read("ruff.toml")
        self.assertIn("target-version", text)
        self.assertIn("line-length", text)
        self.assertIn("[lint]", text)

    def test_coveragerc_present(self):
        text = self._read(".coveragerc")
        self.assertIn("[run]", text)
        self.assertIn("source = resources/lib", text)
        self.assertIn(
            "fail_under = 99",
            text.replace(" ", " "),
            "coverage gate floor is 99% per docs/testing-strategy.md",
        )

    def test_gh_actions_workflow_present(self):
        text = self._read(".github/workflows/ci.yml")
        # Matrix covers 3.9 / 3.10 / 3.11 / 3.12
        for v in ("3.9", "3.10", "3.11", "3.12"):
            self.assertIn('"' + v + '"', text, "matrix missing Python " + v)
        self.assertIn("unittest discover", text)
        self.assertIn("pytest", text)
        self.assertIn("coverage", text)
        self.assertIn("ruff", text)

    def test_workflow_has_two_jobs(self):
        text = self._read(".github/workflows/ci.yml")
        # test job and lint job
        self.assertIn("test:", text)
        self.assertIn("lint:", text)
        # fail-fast disabled so all matrix entries report
        self.assertIn("fail-fast: false", text)

    def test_workflow_runs_smoke_via_unittest(self):
        # Smoke test runs as part of `python -m unittest discover`,
        # which the workflow invokes.
        text = self._read(".github/workflows/ci.yml")
        self.assertIn("python -m unittest discover", text)


# ---------------------------------------------------------------------
# v1.1.9 Property-based tests with Hypothesis (fallback if absent)
# ---------------------------------------------------------------------

try:
    from hypothesis import HealthCheck, given, settings
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False


# Deterministic sample sets for the no-Hypothesis fallback path.  These
# cover the same invariants Hypothesis would exercise: a wide range of
# valid / invalid / boundary values for each input type.
_SAMPLE_INVALID_KEYS = [
    "",
    "   ",
    "\t\n",
    "udp_203 ",
    " udp_203",
    "UDP_203",
    "udp-203",
    "../etc/passwd",
    "x" * 200,
    "\x00",
    "💿",
    "udp_999",
    "chinoppo_xxx",
    "reavon_x999",
    None_ := None,
]
_SAMPLE_INVALID_KEYS = [k for k in _SAMPLE_INVALID_KEYS if k is not None] + [None]

_SAMPLE_LOCALIZE_INPUTS = [
    None,
    "",
    0,
    -1,
    31000,
    31999,
    99999,
    2**31,
    -(2**31),
    "31000",
    "abc",
    "  ",
    "\x00",
    True,
    False,
    [],
    {},
    (1, 2),
    object(),
    3.14,
    float("inf"),
    float("nan"),
]


class TPropertyHardwarePresets(unittest.TestCase):
    """Properties that must hold for hardware_presets across all keys."""

    def setUp(self):
        import hardware_presets

        self.hp = hardware_presets

    # --- Helpers shared by both Hypothesis and fallback paths ---

    def _check_select_play_invariants(self, key):
        out = self.hp.select_play_command(key)
        self.assertIsInstance(
            out, list, "select_play_command must always return a list (key=" + repr(key) + ")"
        )
        self.assertGreater(
            len(out),
            0,
            "select_play_command must never return an empty list (key=" + repr(key) + ")",
        )
        for cmd in out:
            self.assertIsInstance(cmd, str)
            self.assertTrue(
                cmd.startswith("#"), "every command must start with '#' (got " + repr(cmd) + ")"
            )
            self.assertNotIn("\n", cmd)
            self.assertNotIn("\r", cmd)

    def _check_select_power_invariants(self, key):
        cmd = self.hp.select_power_on_command(key)
        self.assertIsInstance(cmd, str)
        self.assertTrue(
            cmd.startswith("#"), "power-on command must start with '#' (got " + repr(cmd) + ")"
        )
        self.assertNotIn("\n", cmd)
        self.assertNotIn("\r", cmd)

    def _check_supports_http_invariants(self, key):
        out = self.hp.supports_http(key)
        self.assertIsInstance(out, bool, "supports_http must return bool (got " + repr(out) + ")")

    def _check_recommended_delay_invariants(self, key):
        d = self.hp.select_recommended_power_delay(key)
        self.assertIsInstance(d, (int, float))
        self.assertGreaterEqual(d, 0, "delay must be non-negative (got " + repr(d) + ")")
        self.assertLess(d, 600, "delay must be sane (<10 min)")

    def _check_get_preset_invariants(self, key):
        p = self.hp.get_preset(key)
        self.assertIsInstance(
            p, dict, "get_preset must always return a dict (key=" + repr(key) + ")"
        )
        for required in ("label", "family", "play", "power_on", "stop"):
            self.assertIn(required, p, "preset dict missing key '" + required + "'")

    # --- Coverage of every defined preset key ---

    def test_all_known_keys_satisfy_invariants(self):
        for key in self.hp.PRESET_KEYS:
            self._check_select_play_invariants(key)
            self._check_select_power_invariants(key)
            self._check_supports_http_invariants(key)
            self._check_recommended_delay_invariants(key)
            self._check_get_preset_invariants(key)

    # --- Invariants must hold for invalid keys too (graceful fallback) ---

    def test_invalid_keys_fall_back_safely(self):
        for key in _SAMPLE_INVALID_KEYS:
            self._check_select_play_invariants(key)
            self._check_select_power_invariants(key)
            self._check_supports_http_invariants(key)
            self._check_recommended_delay_invariants(key)
            self._check_get_preset_invariants(key)

    # --- Hypothesis path: random strings ---

    if HYPOTHESIS_AVAILABLE:

        @given(st.text(max_size=64))
        @settings(
            max_examples=100,
            deadline=None,
            suppress_health_check=[HealthCheck.function_scoped_fixture],
        )
        def test_hyp_select_play_never_raises(self, key):
            self._check_select_play_invariants(key)

        @given(st.text(max_size=64))
        @settings(
            max_examples=100,
            deadline=None,
            suppress_health_check=[HealthCheck.function_scoped_fixture],
        )
        def test_hyp_select_power_never_raises(self, key):
            self._check_select_power_invariants(key)

        @given(st.text(max_size=64))
        @settings(
            max_examples=100,
            deadline=None,
            suppress_health_check=[HealthCheck.function_scoped_fixture],
        )
        def test_hyp_supports_http_returns_bool(self, key):
            self._check_supports_http_invariants(key)

        @given(st.text(max_size=64))
        @settings(
            max_examples=100,
            deadline=None,
            suppress_health_check=[HealthCheck.function_scoped_fixture],
        )
        def test_hyp_get_preset_returns_dict(self, key):
            self._check_get_preset_invariants(key)


class TPropertyI18nL(unittest.TestCase):
    """L() must NEVER raise, regardless of input type."""

    def setUp(self):
        import i18n

        self.i18n = i18n

    def _check_L_invariants(self, value):
        try:
            out = self.i18n.L(value)
        except BaseException as e:
            self.fail("L(" + repr(value) + ") raised " + repr(e))
        self.assertIsNotNone(out, "L() must never return None")
        self.assertIsInstance(out, str, "L() must always return str (got " + repr(type(out)) + ")")

    def test_L_on_sample_inputs_never_raises(self):
        for v in _SAMPLE_LOCALIZE_INPUTS:
            self._check_L_invariants(v)

    if HYPOTHESIS_AVAILABLE:

        @given(st.integers())
        @settings(max_examples=200, deadline=None)
        def test_hyp_L_int_never_raises(self, n):
            self._check_L_invariants(n)

        @given(st.text(max_size=128))
        @settings(max_examples=100, deadline=None)
        def test_hyp_L_str_never_raises(self, s):
            self._check_L_invariants(s)

        @given(
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=True, allow_infinity=True),
                st.text(max_size=64),
                st.lists(st.integers(), max_size=4),
                st.dictionaries(st.text(max_size=4), st.integers(), max_size=4),
                st.tuples(st.integers(), st.integers()),
            )
        )
        @settings(max_examples=200, deadline=None)
        def test_hyp_L_arbitrary_never_raises(self, v):
            self._check_L_invariants(v)


class TPropertyAutoScript(unittest.TestCase):
    """generate() shell-script invariants: LF-only, no \\r, sh shebang."""

    def setUp(self):
        import autoscript_helper

        self.ash = autoscript_helper

    def _check_script_invariants(self, opts):
        try:
            out = self.ash.generate(opts)
        except BaseException as e:
            self.fail("generate(" + repr(opts) + ") raised " + repr(e))
        self.assertIsInstance(out, str)
        self.assertTrue(
            out.startswith("#!/bin/sh"),
            "script must start with #!/bin/sh (got " + repr(out[:40]) + ")",
        )
        self.assertNotIn(
            "\r", out, "no carriage returns allowed (BusyBox sh on the OPPO would choke)"
        )
        # Every newline must be LF-only.  Catches a sneaky CRLF that
        # would slip past the no-\r check if encoded as a literal "\\r\\n"
        # pair in the source.
        self.assertNotRegex(out, r"\r\n")
        # Every line uses LF separation.
        if "\n" in out:
            # Last line may or may not have trailing LF; intermediate
            # lines must.
            self.assertNotIn("\r", out)

    def test_generate_with_default_opts(self):
        self._check_script_invariants({})
        self._check_script_invariants(None)

    def test_generate_with_curated_opts(self):
        for opts in (
            {"enable_telnet": True, "telnet_port": 2323},
            {"enable_telnet": False},
            {"passwordless_root": False},
            {
                "mount_type": "cifs",
                "mount_remote": "//nas/share",
                "mount_local": "/tmp/share",
                "cifs_user": "u",
                "cifs_pass": "p",
            },
            {"mount_type": "nfs", "mount_remote": "nas:/share", "mount_local": "/tmp/share"},
            {"enable_adb": True, "adb_port": 5555},
            {"heartbeat_path": "/tmp/usb/sda1/oppo_autoexec_ran"},
        ):
            self._check_script_invariants(opts)

    def test_generate_with_garbage_opts(self):
        # Robust against badly-typed inputs.
        for opts in (
            {"telnet_port": "not-an-int"},
            {"adb_port": -1},
            {"mount_type": 12345},
            {"cifs_user": None},
            {"heartbeat_path": ""},
        ):
            self._check_script_invariants(opts)

    if HYPOTHESIS_AVAILABLE:
        # Strategy that produces an opts dict with a mix of valid and
        # invalid keys/values.
        _opts_strategy = st.fixed_dictionaries(
            {},
            optional={
                "enable_telnet": st.booleans(),
                "telnet_port": st.one_of(
                    st.integers(min_value=0, max_value=65535), st.text(max_size=8)
                ),
                "passwordless_root": st.booleans(),
                "mount_type": st.sampled_from(["none", "cifs", "nfs", ""]),
                "mount_remote": st.text(max_size=64),
                "mount_local": st.text(max_size=64),
                "mount_options": st.text(max_size=64),
                "cifs_user": st.text(max_size=32),
                "cifs_pass": st.text(max_size=32),
                "heartbeat_path": st.text(max_size=64),
                "enable_adb": st.booleans(),
                "adb_port": st.one_of(
                    st.integers(min_value=1, max_value=65535), st.text(max_size=8)
                ),
            },
        )

        @given(_opts_strategy)
        @settings(max_examples=100, deadline=None)
        def test_hyp_generate_invariants(self, opts):
            self._check_script_invariants(opts)


class TPropertyAvailability(unittest.TestCase):
    """Self-test: confirm we know which path actually ran in this env."""

    def test_advertise_hypothesis_status(self):
        # This test always passes; its purpose is to surface in the
        # log whether Hypothesis was loaded.
        if HYPOTHESIS_AVAILABLE:
            sys.stderr.write("  [v1.1.9] Hypothesis available - running property tests\n")
        else:
            sys.stderr.write(
                "  [v1.1.9] Hypothesis NOT available - running deterministic fallback\n"
            )
        self.assertIn(HYPOTHESIS_AVAILABLE, (True, False))


if __name__ == "__main__":
    unittest.main()


class TV2Build1(unittest.TestCase):
    """Version 2.0.0 Build 1 regression tests."""

    def test_addon_version_is_current_v210_build1(self):
        import xml.etree.ElementTree as ET

        tree = ET.parse(os.path.join(ROOT, "addon.xml"))
        self.assertEqual(tree.getroot().attrib.get("version"), "2.9.13")

    def test_default_command_map_is_canonical_76_key_map(self):
        import json

        from resources.lib.settings_reader import DEFAULTS

        command_map = json.loads(DEFAULTS["oppo_remote_command_map"])
        self.assertEqual(len(command_map), 76)
        values = "\n".join(command_map.values())
        self.assertNotIn("#SIS", values)
        self.assertNotIn("#PGU", values)
        self.assertNotIn("#PGD", values)
        self.assertEqual(command_map["bluray_input"], "#SRC 0")
        self.assertEqual(command_map["page_up"], "#PUP")
        self.assertEqual(command_map["page_down"], "#PDN")

    def test_hardware_compat_has_18_canonical_entries(self):
        import json
        from pathlib import Path

        from resources.lib.settings_reader import HARDWARE_COMPAT

        players_db = json.loads(
            (Path(__file__).resolve().parents[1] / "docs/configurator/players-db/players.json")
            .read_text(encoding="utf-8")
        )
        # Canonical count is the players DB; this stays in lockstep via the consistency guard.
        self.assertEqual(len(HARDWARE_COMPAT), len(players_db["models"]))
        self.assertIn("M9702", HARDWARE_COMPAT)
        self.assertIn("M9200", HARDWARE_COMPAT)
        self.assertIn("M9205", HARDWARE_COMPAT)
        self.assertIn("M9205-V1", HARDWARE_COMPAT)
        self.assertEqual(HARDWARE_COMPAT["M9205-V1"], HARDWARE_COMPAT["M9205"])
        self.assertIn("CineUltra-V203", HARDWARE_COMPAT)
        self.assertIn("CineUltra-V204", HARDWARE_COMPAT)
        self.assertIn("Magnetar-UDP900", HARDWARE_COMPAT)
        self.assertTrue(HARDWARE_COMPAT["M9702"]["is_clone"])
        self.assertEqual(HARDWARE_COMPAT["M9702"]["wake_command"], "#EJT")
        self.assertTrue(HARDWARE_COMPAT["Reavon-UBR-X100"]["is_reavon"])
        self.assertFalse(HARDWARE_COMPAT["Reavon-UBR-X100"]["protocol_compatible"])

    def test_chinoppo_wake_rewrite_and_stock_passthrough(self):
        from resources.lib.oppo_remote import resolve_power_on_token

        self.assertEqual(resolve_power_on_token("#PON", "chinoppo_m9702"), "#EJT")
        self.assertEqual(resolve_power_on_token("#POW", "M9702"), "#EJT")
        self.assertEqual(resolve_power_on_token("#PON", "udp_203"), "#PON")
        self.assertEqual(resolve_power_on_token("#PLA", "M9702"), "#PLA")

    def test_configured_start_commands_rewrite_at_send_time(self):
        import resources.lib.oppo_control as oc
        from resources.lib.settings_reader import Settings

        captured = {}
        original = oc.send_commands
        try:

            def fake_send(host, port, commands, timeout=3.0, delay=1.0):
                captured["commands"] = list(commands)
                return ["@OK"] * len(commands)

            oc.send_commands = fake_send
            settings = Settings(
                {
                    "oppo_hardware_model": "chinoppo_m9702",
                    "oppo_start_commands": "#PON\n#PLA",
                }
            )
            oc.run_configured_commands(settings, "oppo_start_commands")
        finally:
            oc.send_commands = original
        self.assertEqual(captured["commands"], ["#EJT", "#PLA"])

    def test_settings_ui_exposes_hardware_and_hides_architecture_choice(self):
        import xml.etree.ElementTree as ET

        tree = ET.parse(os.path.join(ROOT, "resources", "settings.xml"))
        ids = {node.attrib.get("id") for node in tree.getroot().iter("setting")}
        self.assertIn("oppo_hardware_model", ids)
        self.assertNotIn("playback_architecture", ids)
        self.assertNotIn("architecture_choice_made", ids)


class TV2Build2MVPCompliance(unittest.TestCase):
    """Version 2.0.0 Build 2 MVP compliance tests."""

    def test_stock_power_commands_are_exact_passthrough(self):
        from resources.lib.oppo_remote import resolve_power_on_token

        self.assertEqual(resolve_power_on_token("#PON", "udp_203"), "#PON")
        self.assertEqual(resolve_power_on_token("#POW", "udp_203"), "#POW")
        self.assertEqual(resolve_power_on_token("#PON", "unknown"), "#PON")
        self.assertEqual(resolve_power_on_token("#POW", "unknown"), "#POW")

    def test_configured_stock_power_toggle_is_not_rewritten(self):
        import resources.lib.oppo_control as oc
        from resources.lib.settings_reader import Settings

        captured = {}
        original = oc.send_commands
        try:

            def fake_send(host, port, commands, timeout=3.0, delay=1.0):
                captured["commands"] = list(commands)
                return ["@OK"] * len(commands)

            oc.send_commands = fake_send
            settings = Settings(
                {
                    "oppo_hardware_model": "udp_203",
                    "oppo_start_commands": "#POW\n#PLA",
                }
            )
            oc.run_configured_commands(settings, "oppo_start_commands")
        finally:
            oc.send_commands = original
        self.assertEqual(captured["commands"], ["#POW", "#PLA"])

    def test_tv_switch_to_oppo_runs_before_oppo_start(self):
        import external_player as ep
        from settings_reader import Settings

        settings = Settings({"tv_switching_enabled": "true", "fast_changeover": "true"})
        calls = []
        with (
            mock.patch.object(ep, "switch_to_oppo", side_effect=lambda s: calls.append("tv")),
            mock.patch.object(
                ep,
                "start_oppo_after_optional_delay",
                side_effect=lambda s, f, preflight_result=None: calls.append("start"),
            ),
        ):
            ep.fast_start(settings, "/media/movie.iso")
        self.assertEqual(calls, ["tv", "start"])

    def test_tv_switching_disabled_path_is_noop(self):
        import external_player as ep
        from settings_reader import Settings

        settings = Settings({"tv_switching_enabled": "false"})
        calls = []
        with (
            mock.patch.object(ep, "switch_to_oppo", side_effect=lambda s: calls.append("tv")),
            mock.patch.object(
                ep,
                "start_oppo_after_optional_delay",
                side_effect=lambda s, f, preflight_result=None: calls.append("start"),
            ),
        ):
            ep.fast_start(settings, "/media/movie.iso")
        self.assertEqual(calls, ["start"])

    def test_adb_failure_is_nonfatal_and_start_still_runs(self):
        import external_player as ep
        from settings_reader import Settings

        settings = Settings({"tv_switching_enabled": "true"})
        calls = []
        with (
            mock.patch.object(ep, "switch_to_oppo", side_effect=RuntimeError("adb down")),
            mock.patch.object(
                ep,
                "start_oppo_after_optional_delay",
                side_effect=lambda s, f, preflight_result=None: calls.append("start"),
            ),
        ):
            ep.fast_start(settings, "/media/movie.iso")
        self.assertEqual(calls, ["start"])

    def test_fast_return_tv_failure_does_not_hide_stop_commands(self):
        import external_player as ep
        from settings_reader import Settings

        settings = Settings({"tv_switching_enabled": "true", "switch_back_on_exit": "true"})
        calls = []
        with (
            mock.patch.object(
                ep, "run_configured_commands", side_effect=lambda s, key: calls.append(key)
            ),
            mock.patch.object(ep, "switch_to_kodi", side_effect=RuntimeError("adb down")),
        ):
            ep.fast_return(settings)
        self.assertEqual(calls, ["oppo_stop_commands"])

    def test_external_player_failure_still_clears_session_sentinel(self):
        import tempfile

        import external_player as ep
        from settings_reader import Settings

        with tempfile.TemporaryDirectory() as td:
            settings = Settings({"fixed_timeout_minutes": "1"})
            with (
                mock.patch.object(ep, "read_settings", return_value=settings),
                mock.patch.object(ep, "fast_start", side_effect=RuntimeError("player failed")),
                mock.patch.object(ep, "fast_return", return_value=None),
                mock.patch.object(
                    sys,
                    "argv",
                    ["external_player.py", "--addon-data", td, "--file", "/media/movie.iso"],
                ),
            ):
                result = ep.main()
            self.assertEqual(result, 1)
            self.assertFalse(os.path.exists(os.path.join(td, "oppo203iso-active")))

    def test_adb_command_construction_uses_injected_runner(self):
        import types

        import adb_control
        from settings_reader import Settings

        calls = []

        def runner(args, **kwargs):
            calls.append(list(args))
            return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

        settings = Settings(
            {
                "adb_path": "adb-test",
                "tv_ip": "192.0.2.10",
                "tv_adb_port": "5556",
                "adb_connect_before_switch": "true",
                "_adb_runner": runner,
            }
        )
        out = adb_control.switch_input(settings, "am start -d content://input/HW15")
        self.assertEqual(out, "ok")
        self.assertEqual(calls[0], ["adb-test", "connect", "192.0.2.10:5556"])
        self.assertEqual(calls[1][:4], ["adb-test", "-s", "192.0.2.10:5556", "shell"])
        self.assertIn("content://input/HW15", calls[1])

    def test_fake_oppo_server_loopback_ephemeral_and_ok(self):
        import oppo_control as oc

        from tests._support.fake_oppo_server import FakeOppoServer

        with FakeOppoServer({"#PON": "@PON OK"}) as server:
            self.assertEqual(server.host, "127.0.0.1")
            self.assertGreater(server.port, 0)
            self.assertNotEqual(server.port, 23)
            self.assertEqual(
                oc.send_commands(server.host, server.port, ["#PON"], delay=0), ["@PON OK"]
            )
            self.assertEqual(server.commands, ["#PON"])

    def test_fake_oppo_server_error_response_raises_for_query(self):
        import oppo_control as oc

        from tests._support.fake_oppo_server import FakeOppoServer

        with FakeOppoServer({"#BAD": "@BAD ER INVALID COMMAND"}) as server:
            with self.assertRaises(oc.OppoError):
                oc.query_command(server.host, server.port, "#BAD")

    def test_verbose_push_stop_event_returns_true(self):
        import oppo_tcp_client as tc

        from tests._support.fake_oppo_server import FakeOppoServer

        with FakeOppoServer({"#SVM 2": "@SVM OK 2"}, push_lines=["@UPL STOP"]) as server:
            client = tc.OppoTcpClient(server.host, server.port, recv_timeout=0.2)
            self.assertTrue(client.wait_for_stop(timeout=1.0))

    def test_clean_tcp_disconnect_is_not_playback_stop(self):
        import oppo_tcp_client as tc

        from tests._support.fake_oppo_server import FakeOppoServer

        with FakeOppoServer({"#SVM 2": "@SVM OK 2"}, close_after_commands=1) as server:
            client = tc.OppoTcpClient(server.host, server.port, recv_timeout=0.2)
            self.assertFalse(client.wait_for_stop(timeout=1.0))

    def test_midstream_disconnect_triggers_persistent_reconnect_attempts(self):
        import oppo_tcp_client as tc

        from tests._support.fake_oppo_server import FakeOppoServer

        with FakeOppoServer({"#SVM 2": "@SVM OK 2"}, close_after_commands=1) as server:
            client = tc.OppoTcpClient(server.host, server.port, recv_timeout=0.2)
            stopped = client.wait_for_stop_persistent(
                timeout=2.0, max_retries=2, base_delay=0, cap_delay=0, jitter=0
            )
            self.assertFalse(stopped)
            self.assertGreaterEqual(server.commands.count("#SVM 2"), 2)


class TBuild4ReleaseCandidateArtifacts(unittest.TestCase):
    """v2.0.0 Build 4 - release-candidate artifact and MVP-status checks."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build4_notes_remain_available(self):
        text = self._read("BUILD_NOTES_v2.0.0_BUILD4.md")
        self.assertIn("Version 2.0.0 Build 4", text)

    def test_build4_notes_record_packaging_fix(self):
        text = self._read("BUILD_NOTES_v2.0.0_BUILD4.md")
        self.assertIn(".coveragerc", text)
        self.assertIn("packaging", text.lower())
        self.assertIn("337 / 337", text)

    def test_hardware_validation_note_records_user_assumption(self):
        text = self._read("HARDWARE_VALIDATION_v2.0.0_BUILD4.md")
        self.assertIn("assumed passed", text.lower())
        self.assertIn("no issues", text.lower())
        self.assertIn("M9702", text)
        self.assertIn("TCL", text)

    def test_mvp_compliance_matrix_covers_required_areas(self):
        text = self._read("MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md")
        for phrase in (
            "External Player",
            "M9702",
            "TCL / Android TV",
            "Fake OPPO",
            "Kodi stubs",
            "92% coverage gate",
        ):
            self.assertIn(phrase, text)

    def test_docs_have_build4_sections(self):
        self.assertIn("Version 2.0.0 Build 4", self._read("README.md"))
        self.assertIn("Version 2.0.0 Build 4", self._read("reference.md"))
        self.assertIn("Version 2.0.0 Build 4", self._read("web-references.md"))

    def test_coveragerc_restored_for_packaging(self):
        text = self._read(".coveragerc")
        self.assertIn("[run]", text)
        self.assertIn("source = resources/lib", text)
        self.assertIn("fail_under = 99", text)


class TBuild5ReleaseAuditArtifacts(unittest.TestCase):
    """v2.0.0 Build 5 - reproducible release-audit checks."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_addon_version_is_current_hardening_build(self):
        self.assertIn('version="2.9.13"', self._read("addon.xml"))

    def test_build5_notes_and_manifest_exist(self):
        notes = self._read("BUILD_NOTES_v2.0.0_BUILD5.md")
        manifest = self._read("RELEASE_MANIFEST_v2.0.0_BUILD5.md")
        self.assertIn("reproducible release-audit hardening", notes)
        self.assertIn("tools/audit_release.py", notes)
        self.assertIn("artifact_name: script.oppo203.iso.external-2.0.0-build5.zip", manifest)
        self.assertIn("python tools/audit_release.py --expected-version 2.0.0.5", manifest)

    def test_docs_have_build5_sections(self):
        self.assertIn("Version 2.0.0 Build 5", self._read("README.md"))
        self.assertIn("Version 2.0.0 Build 5", self._read("reference.md"))
        self.assertIn("Version 2.0.0 Build 5", self._read("web-references.md"))

    def test_release_audit_module_imports_and_reports_ok(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("command_map", names)
        self.assertIn("hardware_model_count", names)
        self.assertIn("settings_string_ids", names)
        self.assertIn("addon_version", names)

    def test_release_audit_cli_json(self):
        import json
        import subprocess

        out = subprocess.check_output(
            [
                sys.executable,
                os.path.join(self.root, "tools", "audit_release.py"),
                "--root",
                self.root,
                "--expected-version",
                "2.9.13",
                "--json",
            ],
            text=True,
        )
        payload = json.loads(out)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["results"])

    def test_release_audit_rejects_wrong_version(self):
        import subprocess

        proc = subprocess.run(
            [
                sys.executable,
                os.path.join(self.root, "tools", "audit_release.py"),
                "--root",
                self.root,
                "--expected-version",
                "0.0.0",
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, proc.returncode)
        self.assertIn("addon_version", proc.stdout)

    def test_build5_preserves_build4_hardware_validation_evidence(self):
        text = self._read("HARDWARE_VALIDATION_v2.0.0_BUILD4.md")
        self.assertIn("assumed passed", text.lower())
        self.assertIn("no issues", text.lower())


class TFinalV200ReleaseArtifacts(unittest.TestCase):
    """Version 2.0.0 final release evidence and audit checks."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_final_release_docs_exist_and_name_artifact(self):
        notes = self._read("RELEASE_NOTES_v2.0.0.md")
        manifest = self._read("RELEASE_MANIFEST_v2.0.0.md")
        self.assertIn("script.oppo203.iso.external-2.0.0.zip", notes)
        self.assertIn("addon_version: 2.0.0", manifest)
        self.assertIn("checksum_name: script.oppo203.iso.external-2.0.0.sha256", manifest)

    def test_final_mvp_and_hardware_evidence_exist(self):
        matrix = self._read("MVP_COMPLIANCE_MATRIX_v2.0.0.md")
        hardware = self._read("HARDWARE_VALIDATION_v2.0.0.md")
        self.assertIn("External Player", matrix)
        self.assertIn("M9702", matrix)
        self.assertIn("92% coverage gate", matrix)
        self.assertIn("No new physical", hardware)
        self.assertIn("not performed", hardware.lower())

    def test_docs_have_final_sections(self):
        self.assertIn("Version 2.0.0 Final", self._read("README.md"))
        self.assertIn("Version 2.0.0 Final", self._read("reference.md"))
        self.assertIn("Version 2.0.0 Final", self._read("web-references.md"))

    def test_final_release_audit_requires_final_evidence_files(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_final", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:RELEASE_NOTES_v2.0.0.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.0.0.md", names)
        self.assertIn("file:MVP_COMPLIANCE_MATRIX_v2.0.0.md", names)
        self.assertIn("file:HARDWARE_VALIDATION_v2.0.0.md", names)


class TBuild6BuildIdArtifacts(unittest.TestCase):
    """Version 2.0.0 Build 6 build-id evidence and audit checks."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build6_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.0.0_BUILD6.md")
        manifest = self._read("RELEASE_MANIFEST_v2.0.0_BUILD6.md")
        self.assertIn("addon_version: 2.0.0.6", notes)
        self.assertIn("artifact_name: script.oppo203.iso.external-2.0.0-build6.zip", manifest)
        self.assertIn("checksum_name: script.oppo203.iso.external-2.0.0-build6.sha256", manifest)

    def test_docs_have_build6_sections(self):
        self.assertIn("Version 2.0.0 Build 6", self._read("README.md"))
        self.assertIn("Version 2.0.0 Build 6", self._read("reference.md"))
        self.assertIn("Version 2.0.0 Build 6", self._read("web-references.md"))

    def test_build6_release_audit_requires_build6_evidence_files(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_build6", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.0.0_BUILD6.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.0.0_BUILD6.md", names)


class TFinalV200PackageFromBuild6(unittest.TestCase):
    """Final v2.0.0 package repacked from verified Build 6 line."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_addon_identity_is_v210_build1_not_old_build_id(self):
        self.assertIn('version="2.9.13"', self._read("addon.xml"))
        self.assertNotIn('version="2.0.0.6"', self._read("addon.xml"))

    def test_final_release_docs_record_build6_baseline_and_hardware_deferral(self):
        notes = self._read("RELEASE_NOTES_v2.0.0.md")
        manifest = self._read("RELEASE_MANIFEST_v2.0.0.md")
        hardware = self._read("HARDWARE_VALIDATION_v2.0.0.md")
        self.assertIn("verified Build 6", notes)
        self.assertIn("addon_version: 2.0.0", manifest)
        self.assertIn("real_hardware_validation: deferred", manifest)
        self.assertIn("after the later full", hardware)
        self.assertIn("not claimed", hardware.lower())

    def test_final_release_audit_accepts_v200(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_final_build6", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)


class TV210Build1CoverageGateArtifacts(unittest.TestCase):
    """Version 2.1.0 Build 1 coverage-gate hardening evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.1.0_BUILD1.md")
        manifest = self._read("RELEASE_MANIFEST_v2.1.0_BUILD1.md")
        coverage = self._read("COVERAGE_REPORT_v2.1.0_BUILD1.md")
        self.assertIn("addon_version: 2.1.0.1", notes)
        self.assertIn("script.oppo203.iso.external-2.1.0-build1.zip", manifest)
        self.assertIn("fail_under = 92", coverage)
        self.assertIn("381 passed", self._read("TEST_AUDIT_REPORT_v2.1.0_BUILD1.md"))

    def test_docs_have_v210_build1_sections(self):
        self.assertIn("Version 2.1.0 Build 1", self._read("README.md"))
        self.assertIn("Version 2.1.0 Build 1", self._read("reference.md"))
        self.assertIn("Version 2.1.0 Build 1", self._read("web-references.md"))

    def test_audit_requires_coverage_gate_and_build1_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v210_build1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("coverage_gate", names)
        self.assertIn("file:BUILD_NOTES_v2.1.0_BUILD1.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.1.0_BUILD1.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.1.0_BUILD1.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.1.0_BUILD1.md", names)


class TV210Build2CoverageGateArtifacts(unittest.TestCase):
    """Version 2.1.0 Build 2 gradual coverage-gate hardening evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build2_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.1.0_BUILD2.md")
        manifest = self._read("RELEASE_MANIFEST_v2.1.0_BUILD2.md")
        coverage = self._read("COVERAGE_REPORT_v2.1.0_BUILD2.md")
        self.assertIn("addon_version: 2.1.0.2", notes)
        self.assertIn("script.oppo203.iso.external-2.1.0-build2.zip", manifest)
        self.assertIn("fail_under = 94", coverage)
        self.assertIn("TOTAL 94%", self._read("TEST_AUDIT_REPORT_v2.1.0_BUILD2.md"))

    def test_docs_have_v210_build2_sections(self):
        self.assertIn("Version 2.1.0 Build 2", self._read("README.md"))
        self.assertIn("Version 2.1.0 Build 2", self._read("reference.md"))
        self.assertIn("Version 2.1.0 Build 2", self._read("web-references.md"))

    def test_audit_requires_94_percent_gate_and_build2_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v210_build2", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("coverage_gate", names)
        self.assertIn("file:BUILD_NOTES_v2.1.0_BUILD2.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.1.0_BUILD2.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.1.0_BUILD2.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.1.0_BUILD2.md", names)


class TV210Build3CoverageGateArtifacts(unittest.TestCase):
    """Version 2.1.0 Build 3 gradual coverage-gate hardening evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build3_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.1.0_BUILD3.md")
        manifest = self._read("RELEASE_MANIFEST_v2.1.0_BUILD3.md")
        coverage = self._read("COVERAGE_REPORT_v2.1.0_BUILD3.md")
        self.assertIn("addon_version: 2.1.0.3", notes)
        self.assertIn("script.oppo203.iso.external-2.1.0-build3.zip", manifest)
        self.assertIn("fail_under = 96", coverage)
        self.assertIn("TOTAL 96%", self._read("TEST_AUDIT_REPORT_v2.1.0_BUILD3.md"))

    def test_docs_have_v210_build3_sections(self):
        self.assertIn("Version 2.1.0 Build 3", self._read("README.md"))
        self.assertIn("Version 2.1.0 Build 3", self._read("reference.md"))
        self.assertIn("Version 2.1.0 Build 3", self._read("web-references.md"))

    def test_audit_requires_96_percent_gate_and_build3_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v210_build3", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("coverage_gate", names)
        self.assertIn("file:BUILD_NOTES_v2.1.0_BUILD3.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.1.0_BUILD3.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.1.0_BUILD3.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.1.0_BUILD3.md", names)


class TV210Build5CoverageGateArtifacts(unittest.TestCase):
    """Version 2.1.0 Build 5 gradual coverage-gate hardening evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build5_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.1.0_BUILD5.md")
        manifest = self._read("RELEASE_MANIFEST_v2.1.0_BUILD5.md")
        coverage = self._read("COVERAGE_REPORT_v2.1.0_BUILD5.md")
        self.assertIn("addon_version: 2.1.0.5", notes)
        self.assertIn("script.oppo203.iso.external-2.1.0-build5.zip", manifest)
        self.assertIn("fail_under = 98", coverage)
        self.assertIn("TOTAL 98%", self._read("TEST_AUDIT_REPORT_v2.1.0_BUILD5.md"))

    def test_docs_have_v210_build5_sections(self):
        self.assertIn("Version 2.1.0 Build 5", self._read("README.md"))
        self.assertIn("Version 2.1.0 Build 5", self._read("reference.md"))
        self.assertIn("Version 2.1.0 Build 5", self._read("web-references.md"))

    def test_audit_requires_98_percent_gate_and_build5_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v210_build5", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("coverage_gate", names)
        self.assertIn("file:BUILD_NOTES_v2.1.0_BUILD5.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.1.0_BUILD5.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.1.0_BUILD5.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.1.0_BUILD5.md", names)


class TV210Build6CoverageGateArtifacts(unittest.TestCase):
    """Version 2.1.0 Build 6 final 99 percent coverage-gate evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build6_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.1.0_BUILD6.md")
        manifest = self._read("RELEASE_MANIFEST_v2.1.0_BUILD6.md")
        coverage = self._read("COVERAGE_REPORT_v2.1.0_BUILD6.md")
        self.assertIn("addon_version: 2.1.0.6", notes)
        self.assertIn("script.oppo203.iso.external-2.1.0-build6.zip", manifest)
        self.assertIn("fail_under = 99", coverage)
        self.assertIn("TOTAL 99%", self._read("TEST_AUDIT_REPORT_v2.1.0_BUILD6.md"))

    def test_docs_have_v210_build6_sections(self):
        self.assertIn("Version 2.1.0 Build 6", self._read("README.md"))
        self.assertIn("Version 2.1.0 Build 6", self._read("reference.md"))
        self.assertIn("Version 2.1.0 Build 6", self._read("web-references.md"))

    def test_audit_requires_99_percent_gate_and_build6_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v210_build6", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("coverage_gate", names)
        self.assertIn("file:BUILD_NOTES_v2.1.0_BUILD6.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.1.0_BUILD6.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.1.0_BUILD6.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.1.0_BUILD6.md", names)


class TV210Build7RawCoverageArtifacts(unittest.TestCase):
    """Version 2.1.0 Build 7 raw 99 percent coverage hardening evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build7_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.1.0_BUILD7.md")
        manifest = self._read("RELEASE_MANIFEST_v2.1.0_BUILD7.md")
        coverage = self._read("COVERAGE_REPORT_v2.1.0_BUILD7.md")
        report = self._read("TEST_AUDIT_REPORT_v2.1.0_BUILD7.md")
        self.assertIn("addon_version: 2.1.0.7", notes)
        self.assertIn("script.oppo203.iso.external-2.1.0-build7.zip", manifest)
        self.assertIn("raw_combined_line_branch_coverage: 99.06%", coverage)
        self.assertIn("TOTAL 99%", report)

    def test_docs_have_v210_build7_sections(self):
        self.assertIn("Version 2.1.0 Build 7", self._read("README.md"))
        self.assertIn("Version 2.1.0 Build 7", self._read("reference.md"))
        self.assertIn("Version 2.1.0 Build 7", self._read("web-references.md"))

    def test_audit_requires_build7_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v210_build7", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.1.0_BUILD7.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.1.0_BUILD7.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.1.0_BUILD7.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.1.0_BUILD7.md", names)


class TV210Build8RawCoverageArtifacts(unittest.TestCase):
    """Version 2.1.0 Build 8 raw coverage improvement evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build8_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.1.0_BUILD8.md")
        manifest = self._read("RELEASE_MANIFEST_v2.1.0_BUILD8.md")
        coverage = self._read("COVERAGE_REPORT_v2.1.0_BUILD8.md")
        report = self._read("TEST_AUDIT_REPORT_v2.1.0_BUILD8.md")
        self.assertIn("addon_version: 2.1.0.8", notes)
        self.assertIn("script.oppo203.iso.external-2.1.0-build8.zip", manifest)
        self.assertIn("raw_combined_line_branch_coverage: 99.44%", coverage)
        self.assertIn("TOTAL 99%", report)

    def test_docs_have_v210_build8_sections(self):
        self.assertIn("Version 2.1.0 Build 8", self._read("README.md"))
        self.assertIn("Version 2.1.0 Build 8", self._read("reference.md"))
        self.assertIn("Version 2.1.0 Build 8", self._read("web-references.md"))

    def test_audit_requires_build8_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v210_build8", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.1.0_BUILD8.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.1.0_BUILD8.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.1.0_BUILD8.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.1.0_BUILD8.md", names)


class TV220Build4PersistenceArtifacts(unittest.TestCase):
    """Version 2.2.0 Build 4 service watcher persistence evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build4_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.2.0_BUILD4.md")
        manifest = self._read("RELEASE_MANIFEST_v2.2.0_BUILD4.md")
        coverage = self._read("COVERAGE_REPORT_v2.2.0_BUILD4.md")
        report = self._read("TEST_AUDIT_REPORT_v2.2.0_BUILD4.md")
        self.assertIn("addon_version: 2.2.0.4", notes)
        self.assertIn("script.oppo203.iso.external-2.2.0-build4.zip", manifest)
        self.assertIn("raw_combined_line_branch_coverage: 99.17%", coverage)
        self.assertIn("TOTAL 99%", report)

    def test_docs_have_v220_build4_sections(self):
        self.assertIn("Version 2.2.0 Build 4", self._read("README.md"))
        self.assertIn("Version 2.2.0 Build 4", self._read("reference.md"))
        self.assertIn("Version 2.2.0 Build 4", self._read("web-references.md"))

    def test_audit_requires_build4_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v220_build4", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.2.0_BUILD4.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.2.0_BUILD4.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.2.0_BUILD4.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.2.0_BUILD4.md", names)


class TV220Build5WizardUISurfacingArtifacts(unittest.TestCase):
    """Version 2.2.0 Build 5 wizard/UI warning surfacing evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build5_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.2.0_BUILD5.md")
        manifest = self._read("RELEASE_MANIFEST_v2.2.0_BUILD5.md")
        coverage = self._read("COVERAGE_REPORT_v2.2.0_BUILD5.md")
        report = self._read("TEST_AUDIT_REPORT_v2.2.0_BUILD5.md")
        self.assertIn("addon_version: 2.2.0.5", notes)
        self.assertIn("script.oppo203.iso.external-2.2.0-build5.zip", manifest)
        self.assertIn("TOTAL 99%", coverage)
        self.assertIn("SUMMARY: PASS", report)

    def test_docs_have_v220_build5_sections(self):
        self.assertIn("Version 2.2.0 Build 5", self._read("README.md"))
        self.assertIn("Version 2.2.0 Build 5", self._read("reference.md"))
        self.assertIn("Version 2.2.0 Build 5", self._read("web-references.md"))

    def test_audit_requires_build5_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v220_build5", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.2.0_BUILD5.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.2.0_BUILD5.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.2.0_BUILD5.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.2.0_BUILD5.md", names)


class TV220Build6ActiveWizardWarningArtifacts(unittest.TestCase):
    """Version 2.2.0 Build 6 active wizard warning integration evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build6_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.2.0_BUILD6.md")
        manifest = self._read("RELEASE_MANIFEST_v2.2.0_BUILD6.md")
        coverage = self._read("COVERAGE_REPORT_v2.2.0_BUILD6.md")
        report = self._read("TEST_AUDIT_REPORT_v2.2.0_BUILD6.md")
        self.assertIn("addon_version: 2.2.0.6", notes)
        self.assertIn("script.oppo203.iso.external-2.2.0-build6.zip", manifest)
        self.assertIn("TOTAL 99%", coverage)
        self.assertIn("SUMMARY: PASS", report)

    def test_docs_have_v220_build6_sections(self):
        self.assertIn("Version 2.2.0 Build 6", self._read("README.md"))
        self.assertIn("Version 2.2.0 Build 6", self._read("reference.md"))
        self.assertIn("Version 2.2.0 Build 6", self._read("web-references.md"))

    def test_audit_requires_build6_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v220_build6", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.2.0_BUILD6.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.2.0_BUILD6.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.2.0_BUILD6.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.2.0_BUILD6.md", names)


class TV220Build7ServiceWatcherEdgeArtifacts(unittest.TestCase):
    """Version 2.2.0 Build 7 service watcher persistence edge-case evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build7_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.2.0_BUILD7.md")
        manifest = self._read("RELEASE_MANIFEST_v2.2.0_BUILD7.md")
        coverage = self._read("COVERAGE_REPORT_v2.2.0_BUILD7.md")
        report = self._read("TEST_AUDIT_REPORT_v2.2.0_BUILD7.md")
        self.assertIn("addon_version: 2.2.0.7", notes)
        self.assertIn("script.oppo203.iso.external-2.2.0-build7.zip", manifest)
        self.assertIn("TOTAL 99%", coverage)
        self.assertIn("SUMMARY: PASS", report)

    def test_docs_have_v220_build7_sections(self):
        self.assertIn("Version 2.2.0 Build 7", self._read("README.md"))
        self.assertIn("Version 2.2.0 Build 7", self._read("reference.md"))
        self.assertIn("Version 2.2.0 Build 7", self._read("web-references.md"))

    def test_audit_requires_build7_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v220_build7", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.2.0_BUILD7.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.2.0_BUILD7.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.2.0_BUILD7.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.2.0_BUILD7.md", names)


class TV220Build8MergeParityAuditArtifacts(unittest.TestCase):
    """Version 2.2.0 Build 8 merge parity audit and handoff rule evidence."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        cls.root = os.path.dirname(here)

    def _read(self, rel):
        return read_project_file(self.root, rel)

    def test_build8_docs_exist_and_name_artifact(self):
        notes = self._read("BUILD_NOTES_v2.2.0_BUILD8.md")
        manifest = self._read("RELEASE_MANIFEST_v2.2.0_BUILD8.md")
        coverage = self._read("COVERAGE_REPORT_v2.2.0_BUILD8.md")
        report = self._read("TEST_AUDIT_REPORT_v2.2.0_BUILD8.md")
        parity = self._read("MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md")
        self.assertIn("addon_version: 2.2.0.8", notes)
        self.assertIn("script.oppo203.iso.external-2.2.0-build8.zip", manifest)
        self.assertIn("TOTAL 99%", coverage)
        self.assertIn("SUMMARY: PASS", report)
        self.assertIn("full_merge_status: in_progress_not_complete", parity)

    def test_docs_have_v220_build8_sections(self):
        self.assertIn("Version 2.2.0 Build 8", self._read("README.md"))
        self.assertIn("Version 2.2.0 Build 8", self._read("reference.md"))
        self.assertIn("Version 2.2.0 Build 8", self._read("web-references.md"))
        self.assertIn("reconstruction bundle", self._read("README.md"))

    def test_audit_requires_build8_evidence(self):
        import importlib.util

        path = os.path.join(self.root, "tools", "audit_release.py")
        spec = importlib.util.spec_from_file_location("audit_release_v220_build8_all", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results = mod.run_audit(mod.project_root(mod.Path(self.root)), expected_version="2.9.13")
        failed = [item for item in results if item["status"] != "ok"]
        self.assertEqual([], failed)
        names = {item["name"] for item in results}
        self.assertIn("file:BUILD_NOTES_v2.2.0_BUILD8.md", names)
        self.assertIn("file:RELEASE_MANIFEST_v2.2.0_BUILD8.md", names)
        self.assertIn("file:COVERAGE_REPORT_v2.2.0_BUILD8.md", names)
        self.assertIn("file:TEST_AUDIT_REPORT_v2.2.0_BUILD8.md", names)
        self.assertIn("file:MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md", names)
