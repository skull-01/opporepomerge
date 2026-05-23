"""Restore the 99% coverage gate: cover the enumerated gaps that opened up
while the floor policy was at 50% and the UI/glue modules were omitted.

Local fakes only - no real Kodi, OPPO, TV, AVR, sockets, or HTTP.
"""
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "tests" / "_stubs"
LIB = ROOT / "resources" / "lib"
for _p in (str(STUBS), str(LIB), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# --- avr_diagnostics helpers --------------------------------------------------

def test_avr_diagnostics_settings_and_truthy_fallbacks():
    import avr_diagnostics as d

    class Bare:  # neither .data nor .items()
        pass

    assert d._settings_dict(Bare()) == {}            # line 59
    assert d._truthy("", default=True) is True        # line 67 (empty -> default)
    assert d._truthy("   ", default=False) is False


def test_avr_diagnostics_controller_unavailable_paths():
    import avr_diagnostics as d

    settings = {
        "avr_control_enabled": "true",
        "avr_backend": "denon_marantz",
        "avr_host": "10.0.0.5",
        "avr_player_input": "BD",
    }
    with mock.patch.object(d.avr_control, "controller_factory", return_value=None):
        q = d.run_query_only_test(settings, "power", controller=None)   # lines 327-329
        assert q["ok"] is False
        a = d.run_explicit_test_action(
            settings, "power_on", explicit_user_action=True, controller=None
        )  # line 367
        assert a["ok"] is False


def test_settings_dict_fallback_in_avr_sequence_and_tv_diagnostics():
    import avr_sequence
    import tv_diagnostics

    class Bare:  # neither .data nor .items()
        pass

    assert avr_sequence._settings_dict(Bare()) == {}     # avr_sequence line 61
    assert tv_diagnostics._settings_dict(Bare()) == {}    # tv_diagnostics line 80


# --- avr_sony_audio edges -----------------------------------------------------

def test_avr_sony_audio_url_and_parse_edges():
    import avr_sony_audio as s

    try:
        s.build_sony_audio_url("")          # line 177
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    ok, message, warnings = s._parse_response('{"foo": "bar"}', {})   # line 249
    assert ok is False
    assert "unexpected_response" in (message + " ".join(warnings))


def test_avr_sony_audio_default_post_uses_urlopen():
    import avr_sony_audio as s

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return b'{"result": []}'

    with mock.patch.object(s.request, "urlopen", return_value=FakeResponse()) as urlopen:
        out = s._default_post("http://host/api", b"{}", {"X": "y"}, 1.0)  # lines 223-225
        assert out == b'{"result": []}'
        assert urlopen.called


# --- hardware_capabilities class helpers --------------------------------------

def test_hardware_capabilities_class_helpers_execute():
    import hardware_capabilities as hc

    for key in ("udp_203", "chinoppo", "experimental_clone", ""):
        # Execute both class-predicate returns (lines 114, 118) and the NAS
        # autoscript predicate (lines 152-153); values depend on the registry,
        # we only assert they are booleans.
        assert isinstance(hc.is_chinoppo_style_clone(key), bool)
        assert isinstance(hc.is_experimental_clone(key), bool)
        assert isinstance(hc.requires_autoscript_for_nas_direct_playback(key), bool)


# --- wizard._probe ------------------------------------------------------------

def test_wizard_probe_success_and_failure():
    import wizard

    class FakeConn:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    with mock.patch.object(wizard.socket, "create_connection", return_value=FakeConn()):
        assert wizard._probe("host", 23) is True        # line 223
    with mock.patch.object(wizard.socket, "create_connection", side_effect=OSError):
        assert wizard._probe("host", 23) is False


def test_wizard_avr_support_metadata_flat_import_fallback():
    # Imported flat, the `from .avr_diagnostics import ...` relative import in
    # avr_wizard_support_metadata() fails and the bare-import fallback runs
    # (wizard.py lines 719-720).
    import wizard

    data = wizard.avr_wizard_support_metadata()
    assert isinstance(data, dict)
    assert "options" in data


# --- first_run_wizard._ui_call ------------------------------------------------

def test_first_run_wizard_ui_call_paths():
    import first_run_wizard as frw

    assert frw._ui_call(None, "show") is False          # line 206 (ui is None)

    class FallbackRaises:
        def show(self, *args):
            # multi-arg call raises TypeError; single-arg fallback raises too
            raise TypeError("needs one arg") if len(args) != 1 else RuntimeError("boom")

    assert frw._ui_call(FallbackRaises(), "show", "title", "msg") is False  # lines 219-220

    seen = []

    class FallbackSucceeds:
        def show(self, *args):
            if len(args) != 1:
                raise TypeError
            seen.append(args[0])

    assert frw._ui_call(FallbackSucceeds(), "show", "title", "msg") is True
    assert seen == ["msg"]


# --- installer.export_avr_diagnostic_report -----------------------------------

def test_installer_export_avr_diagnostic_report_success_and_failure():
    import importlib

    import avr_diagnostics
    installer = importlib.import_module("installer")

    with mock.patch.object(installer, "_paths", return_value=("", "/tmp", "")), \
            mock.patch.object(installer.ADDON, "getSetting", return_value=""), \
            mock.patch.object(
                avr_diagnostics, "export_avr_diagnostic_report",
                return_value="/tmp/avr_report.txt",
            ):
        assert installer.export_avr_diagnostic_report() == "/tmp/avr_report.txt"  # 726-742

    with mock.patch.object(installer, "_paths", return_value=("", "/tmp", "")), \
            mock.patch.object(installer.ADDON, "getSetting", return_value=""), \
            mock.patch.object(
                avr_diagnostics, "export_avr_diagnostic_report",
                side_effect=RuntimeError("boom"),
            ):
        assert installer.export_avr_diagnostic_report() is None              # 743-745

    # getSetting raising for a key exercises the per-key try/except (738-739)
    with mock.patch.object(installer, "_paths", return_value=("", "/tmp", "")), \
            mock.patch.object(installer.ADDON, "getSetting", side_effect=RuntimeError("no setting")), \
            mock.patch.object(
                avr_diagnostics, "export_avr_diagnostic_report",
                return_value="/tmp/avr_report.txt",
            ):
        assert installer.export_avr_diagnostic_report() == "/tmp/avr_report.txt"
