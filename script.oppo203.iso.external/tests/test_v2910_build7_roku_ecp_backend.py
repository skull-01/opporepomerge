"""v2.9.10 Build 16 - Roku TV ECP backend and presets."""

import importlib
import importlib.util
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import read_project_file

LIB = ROOT / "resources" / "lib"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _Response:
    status = 200

    def __init__(self, body=b"ok"):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


def test_build7_adds_roku_ecp_backend_with_strict_metadata():
    backends = _load("tv_backends_build7", "resources/lib/tv/tv_backends.py")
    assert "roku_ecp" in backends.list_backends()
    assert backends.normalize_backend_id("roku_tv") == "roku_ecp"
    assert backends.normalize_backend_id("tcl_roku_tv") == "roku_ecp"
    backend = backends.get_backend("roku_ecp")
    assert backend["kind"] == "roku_ecp_http"
    assert backend["default_port"] == 8060
    assert backend["request_method"] == "POST"
    assert backend["request_path_template"] == "/keypress/{key}"
    assert backend["key_allowlist_required"] is True
    assert backend["nonfatal_in_playback_flow"] is True
    assert backends.backend_target_setting("roku_ecp", "oppo") == "roku_oppo_key"
    assert backends.backend_target_setting("roku_ecp", "kodi") == "roku_kodi_key"
    summary = backends.registry_summary()
    assert summary["runtime_behavior_changed"] is False
    assert summary["hardware_validation_claimed"] is False


def test_build7_roku_ecp_helper_posts_only_allowlisted_keypress_paths():
    roku = _load("tv_roku_ecp_control_build7", "resources/lib/tv/tv_roku_ecp_control.py")
    settings = {"tv_ip": "192.0.2.60", "roku_ecp_port": "8060"}
    seen = []

    def opener(request, timeout=0):
        seen.append((request.full_url, request.get_method(), timeout))
        return _Response()

    assert roku.switch_input(settings, "InputHDMI1", urlopen=opener) == "ok"
    assert seen == [("http://192.0.2.60:8060/keypress/InputHDMI1", "POST", 10)]
    assert (
        roku.build_keypress_url(settings, "InputHDMI2")
        == "http://192.0.2.60:8060/keypress/InputHDMI2"
    )
    for bad_key in ("InputHDMI1/../../query", "InputHDMI1?x=1", "Home", ""):
        try:
            roku.build_keypress_url(settings, bad_key)
        except roku.RokuEcpError as exc:
            assert "allowlisted" in str(exc) or "key" in str(exc)
        else:  # pragma: no cover - defensive assertion branch
            raise AssertionError("unsafe Roku key should be rejected")
    for bad_settings in (
        {"tv_ip": "192.0.2.60/path"},
        {"tv_ip": "", "roku_ecp_port": "8060"},
        {"tv_ip": "192.0.2.60", "roku_ecp_port": "99999"},
    ):
        try:
            roku.build_keypress_url(bad_settings, "InputHDMI1")
        except roku.RokuEcpError:
            pass
        else:  # pragma: no cover - defensive assertion branch
            raise AssertionError("unsafe Roku settings should be rejected")


def test_build7_tv_control_dispatches_roku_nonfatal_backend_without_touching_adb(monkeypatch):
    sys.path.insert(0, str(LIB))
    try:
        tv_control = importlib.import_module("tv_control")
        calls = []
        monkeypatch.setattr(
            tv_control,
            "roku_switch_input",
            lambda settings, key: calls.append((settings.get("tv_backend"), key)) or "roku-ok",
        )
        settings = {
            "tv_backend": "roku_tv",
            "roku_oppo_key": "InputHDMI1",
            "roku_kodi_key": "InputHDMI2",
        }
        assert tv_control.selected_backend_id(settings) == "roku_ecp"
        assert tv_control.switch_to_oppo(settings) == "roku-ok"
        assert tv_control.switch_to_kodi(settings) == "roku-ok"
        assert calls == [("roku_tv", "InputHDMI1"), ("roku_tv", "InputHDMI2")]
    finally:
        try:
            sys.path.remove(str(LIB))
        except ValueError:
            pass


def test_build7_roku_presets_are_software_only_and_require_local_control():
    presets = _load("tv_presets_build7", "resources/lib/tv/tv_presets.py")
    expected = ("roku_tv", "tcl_roku_tv", "hisense_roku_tv", "generic_roku_tv")
    assert presets.list_roku_tv_presets() == expected
    summary = presets.preset_registry_summary()
    assert summary["roku_tv_preset_count"] == 4
    assert summary["roku_tv_preset_ids"] == expected
    assert summary["validation_warnings"] == ()
    for preset_id in expected:
        preset = presets.get_preset(preset_id)
        assert preset["backend"] == "roku_ecp"
        assert preset["editable"] is True
        assert preset["software_preset_only"] is True
        assert preset["hardware_validation_required"] is True
        assert preset["hardware_validation_claimed"] is False
        assert preset["command_fields"] == ("roku_oppo_key", "roku_kodi_key")
        assert preset["default_port"] == 8060
        assert preset["request_method"] == "POST"
        assert preset["request_path_template"] == "/keypress/{key}"
        assert preset["key_allowlist_required"] is True


def test_build7_settings_add_roku_backend_defaults_without_changing_player_behavior():
    sr = _load("settings_reader_build7", "resources/lib/kodi/settings_reader.py")
    assert sr.DEFAULTS["tv_backend"] == "adb"
    assert "roku_ecp" in sr.ENUM_VALUES["tv_backend"]
    assert sr.DEFAULTS["roku_ecp_port"] == "8060"
    assert sr.DEFAULTS["roku_oppo_key"] == "InputHDMI1"
    assert sr.DEFAULTS["roku_kodi_key"] == "InputHDMI2"
    cfg = sr.Settings({"tv_backend": "roku_ecp"})
    assert cfg.get("oppo_start_mode") == sr.DEFAULTS["oppo_start_mode"]
    assert cfg.get("roku_ecp_port") == "8060"


def test_build7_docs_and_audit_evidence_identity():
    version = _load("version_build7", "resources/lib/kodi/version.py")
    assert version.BUILD_ID == "v2.9.15 Final"
    assert version.BUILD_NUMBER == 24
    for rel in ("addon.xml", "README.md", "reference.md", "web-references.md"):
        text = read_project_file(ROOT, rel)
        assert "Version 2.9.10 Build 11" in text
        assert "Roku TV ECP backend" in text
        if rel == "addon.xml":
            assert "HTTP POST to /keypress/&lt;key&gt;" in text
        else:
            assert "HTTP POST to /keypress/<key>" in text
        assert "Hardware validation is not claimed" in text
    audit = _load("audit_release_build7", "tools/audit_release.py")
    results = audit.run_audit(ROOT, expected_version="2.9.15")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:release-evidence/v2.9.10-build7/MANIFEST.txt" in names
    assert "file:BUILD_NOTES_v2.9.10_BUILD7.md" in names
    assert "file:RELEASE_MANIFEST_v2.9.10_BUILD7.md" in names
    assert "file:HARDWARE_ECOSYSTEM_SUPPORT_MATRIX_v2.9.10_BUILD7.md" in names


def test_build7_runtime_zip_includes_roku_helper_but_excludes_evidence(tmp_path):
    package_tool = _load("package_installable_zip_build7", "tools/package_installable_zip.py")
    output = tmp_path / "runtime.zip"
    names = package_tool.create_installable_zip(ROOT, output)
    assert "script.oppo203.iso.external/resources/lib/tv/tv_roku_ecp_control.py" in names
    assert "script.oppo203.iso.external/resources/lib/tv/tv_backends.py" in names
    with zipfile.ZipFile(output) as zf:
        assert zf.testzip() is None
        bad = [
            name
            for name in zf.namelist()
            if any(
                token in name
                for token in (
                    "tests/",
                    "tools/",
                    "scripts/",
                    "release-evidence/",
                    "BUILD_NOTES",
                    "HARDWARE_ECOSYSTEM_SUPPORT_MATRIX",
                )
            )
        ]
    assert bad == []


def test_build7_roku_preset_edge_paths_for_coverage(monkeypatch):
    presets = _load("tv_presets_build7_edges", "resources/lib/tv/tv_presets.py")
    monkeypatch.setitem(
        presets.TV_PRESETS,
        "bad_roku",
        {"backend": "adb", "editable": True, "key_allowlist_required": True},
    )
    monkeypatch.setattr(presets, "ROKU_TV_PRESET_IDS", presets.ROKU_TV_PRESET_IDS + ("bad_roku",))
    warnings = presets.validate_preset_registry()
    assert "preset:bad_roku:roku_tv_not_roku_ecp:adb" in warnings
    monkeypatch.setitem(
        presets.TV_PRESETS, "bad_roku_allowlist", {"backend": "roku_ecp", "editable": True}
    )
    warnings = presets.validate_preset_registry()
    assert "preset:bad_roku_allowlist:roku_ecp_without_key_allowlist" in warnings


def test_build7_roku_helper_error_paths_and_injected_urlopen(monkeypatch):
    import urllib.error

    roku = _load("tv_roku_ecp_control_build7_errors", "resources/lib/tv/tv_roku_ecp_control.py")
    for bad_key in (None,):
        try:
            roku.normalize_roku_key(bad_key)
        except roku.RokuEcpError as exc:
            assert "string" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("non-string Roku key should fail")
    try:
        roku.build_keypress_url(
            {"tv_ip": "192.0.2.60", "roku_ecp_port": "not-a-port"}, "InputHDMI1"
        )
    except roku.RokuEcpError as exc:
        assert "port" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("bad port should fail")

    class NoGet:
        pass

    try:
        roku.switch_input(NoGet(), "InputHDMI1", urlopen=lambda *a, **k: _Response())
    except roku.RokuEcpError as exc:
        assert "get" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("settings object without get should fail")

    class ErrorResponse(_Response):
        status = 500

    try:
        roku.send_keypress(
            {"tv_ip": "192.0.2.60"}, "InputHDMI1", urlopen=lambda *a, **k: ErrorResponse(b"bad")
        )
    except roku.RokuEcpError as exc:
        assert "HTTP 500" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("HTTP error response should fail")

    def url_error(*args, **kwargs):
        raise urllib.error.URLError("down")

    try:
        roku.send_keypress({"tv_ip": "192.0.2.60"}, "InputHDMI1", urlopen=url_error)
    except roku.RokuEcpError as exc:
        assert "request failed" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("URL error should fail")

    seen = []
    settings = {
        "tv_ip": "192.0.2.60",
        "_roku_urlopen": lambda request, timeout=0: seen.append(request.full_url) or _Response(),
    }
    assert roku.switch_input(settings, "InputTuner") == "ok"
    assert seen == ["http://192.0.2.60:8060/keypress/InputTuner"]


def test_build7_support_matrix_helpers_and_unmatched_backend_branch(monkeypatch):
    presets = _load("tv_presets_build7_matrix", "resources/lib/tv/tv_presets.py")
    assert len(presets.android_google_tv_support_matrix()) == 9
    assert len(presets.roku_tv_support_matrix()) == 4

    sys.path.insert(0, str(LIB))
    try:
        tv_control = importlib.import_module("tv_control")
        monkeypatch.setattr(tv_control, "normalize_backend_id", lambda backend: "future_backend")
        monkeypatch.setattr(tv_control, "is_supported_backend", lambda backend: True)
        try:
            tv_control.switch_to_oppo({"tv_backend": "future_backend"})
        except tv_control.TVControlError as exc:
            assert "Unsupported TV backend" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("unmatched supported backend should fail safely")
    finally:
        try:
            sys.path.remove(str(LIB))
        except ValueError:
            pass
