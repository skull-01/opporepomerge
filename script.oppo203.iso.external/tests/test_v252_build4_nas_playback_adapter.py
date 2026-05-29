"""v2.5.2 Build 4 - OPPO/Chinoppo NAS playback trigger adapter by family."""

from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file


def test_build4_metadata_and_release_evidence():
    text = (ROOT / "addon.xml").read_text(encoding="utf-8")
    assert "Version 2.5.2 Build 4" in text
    assert "OPPO/Chinoppo NAS playback trigger adapter by family" in text
    assert (
        "Version 2.5.2 Build 2 optimized runtime installable package policy remains preserved"
        in text
    )

    for rel in [
        "BUILD_NOTES_v2.5.2_BUILD4.md",
        "RELEASE_MANIFEST_v2.5.2_BUILD4.md",
        "RELEASE_NOTES_v2.5.2_BUILD4.md",
        "COVERAGE_REPORT_v2.5.2_BUILD4.md",
        "TEST_AUDIT_REPORT_v2.5.2_BUILD4.md",
    ]:
        assert find_project_file(ROOT, rel).exists(), rel

    spec = importlib.util.spec_from_file_location(
        "audit_release_v252_build4", ROOT / "tools" / "audit_release.py"
    )
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.13")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:BUILD_NOTES_v2.5.2_BUILD4.md" in names
    assert "file:TEST_AUDIT_REPORT_v2.5.2_BUILD4.md" in names


def test_oppo20x_plan_uses_stock_wake_and_http_trigger():
    from resources.lib.nas_playback_adapter import build_nas_playback_plan
    from resources.lib.path_mapper import PathMappingRule
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "udp_203",
            "oppo_jailbreak_enabled": "true",
            "oppo_firmware_version": "20X-65-0131",
            "oppo_ip": "192.168.1.50",
            "nas_playback_trigger_mode": "http_api",
        }
    )
    rules = [PathMappingRule("smb://truenas/media", "/mnt/nas/media")]
    plan = build_nas_playback_plan(settings, "smb://truenas/media/Movies/Test.iso", rules)

    assert plan["ready"] is True
    assert plan["adapter"]["name"] == "Oppo20xJailbrokenNasAdapter"
    assert plan["adapter"]["family"] == "oppo20x_jailbroken"
    assert plan["wake_command"] == "#PON"
    assert plan["trigger_mode"] == "http_api"
    assert plan["player_path"] == "/mnt/nas/media/Movies/Test.iso"
    assert plan["blockers"] == []


def test_chinoppo_plan_uses_eject_wake_and_preserves_confirmation_warning():
    from resources.lib.nas_playback_adapter import build_nas_playback_plan
    from resources.lib.path_mapper import PathMappingRule
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "chinoppo_m9702",
            "nas_playback_confirmed": "false",
            "oppo_ip": "192.168.1.51",
        }
    )
    plan = build_nas_playback_plan(
        settings, "/kodi/media/Movie.mkv", [PathMappingRule("/kodi/media", "/mnt/nas/media")]
    )

    assert plan["ready"] is True
    assert plan["adapter"]["name"] == "ChinoppoNasAdapter"
    assert plan["wake_command"] == "#EJT"
    assert plan["player_path"] == "/mnt/nas/media/Movie.mkv"
    assert "chinoppo_firmware_binary_capability_must_be_confirmed" in plan["warnings"]
    assert plan["blockers"] == []


def test_plan_blocks_unsupported_reavon_and_missing_mapping():
    from resources.lib.nas_playback_adapter import build_nas_playback_plan
    from resources.lib.settings_reader import Settings

    settings = Settings({"oppo_hardware_model": "reavon_ubrx200", "oppo_ip": "192.168.1.55"})
    plan = build_nas_playback_plan(settings, "smb://truenas/media/Test.iso", [])

    assert plan["ready"] is False
    assert plan["adapter"]["name"] == "UnsupportedNasAdapter"
    assert "reavon_warning_only_not_supported_for_oppo_chinoppo_nas_playback" in plan["blockers"]
    assert "no_matching_nas_path_mapping_rule" in plan["blockers"]


def test_trigger_dry_run_does_not_call_clients():
    from resources.lib.nas_playback_adapter import trigger_nas_playback
    from resources.lib.path_mapper import PathMappingRule
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "udp_205",
            "oppo_jailbreak_enabled": "true",
            "oppo_firmware_version": "20X-65-0131",
            "oppo_ip": "192.168.1.50",
        }
    )
    calls = []

    def wake(settings, command):
        calls.append(("wake", command))

    def play(settings, path):
        calls.append(("play", path))

    result = trigger_nas_playback(
        settings,
        "smb://truenas/media/BDMV/index.bdmv",
        [PathMappingRule("smb://truenas/media", "/mnt/nas/media")],
        wake_client=wake,
        playback_client=play,
        dry_run=True,
    )

    assert result["success"] is True
    assert result["action"] == "dry_run"
    assert result["player_path"] == "/mnt/nas/media/BDMV/index.bdmv"
    assert calls == []


def test_trigger_invokes_wake_and_playback_clients_by_family():
    from resources.lib.nas_playback_adapter import trigger_nas_playback
    from resources.lib.path_mapper import PathMappingRule
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "chinoppo_m9205c",
            "nas_playback_confirmed": "true",
            "oppo_ip": "192.168.1.51",
            "nas_playback_power_on_before_trigger": "true",
        }
    )
    calls = []

    def wake(settings, command):
        calls.append(("wake", command))
        return ["@EJT OK"]

    def play(settings, path):
        calls.append(("play", path))
        return "play-ok"

    result = trigger_nas_playback(
        settings,
        "smb://truenas/media/Movies/Clone.iso",
        [PathMappingRule("smb://truenas/media", "/mnt/nas/media")],
        wake_client=wake,
        playback_client=play,
    )

    assert result["success"] is True
    assert result["action"] == "triggered"
    assert result["wake_result"] == ["@EJT OK"]
    assert result["playback_result"] == "play-ok"
    assert calls == [("wake", "#EJT"), ("play", "/mnt/nas/media/Movies/Clone.iso")]


def test_trigger_blocks_and_strict_raises_for_not_ready():
    import pytest
    from resources.lib.nas_playback_adapter import NasPlaybackNotReady, trigger_nas_playback
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "udp_203",
            "oppo_jailbreak_enabled": "false",
            "oppo_firmware_version": "20X-54-1127",
            "oppo_ip": "192.168.1.50",
        }
    )
    result = trigger_nas_playback(settings, "smb://truenas/media/Test.iso", [])
    assert result["success"] is False
    assert result["action"] == "blocked"
    assert "oppo20x_jailbreak_required" in result["blockers"]

    with pytest.raises(NasPlaybackNotReady):
        trigger_nas_playback(settings, "smb://truenas/media/Test.iso", [], strict=True)


def test_unsupported_trigger_mode_and_missing_oppo_ip_are_blockers():
    from resources.lib.nas_playback_adapter import build_nas_playback_plan
    from resources.lib.path_mapper import PathMappingRule
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "udp_203",
            "oppo_jailbreak_enabled": "true",
            "oppo_firmware_version": "20X-65-0131",
            "oppo_ip": "",
            "nas_playback_trigger_mode": "telnet_future",
        }
    )
    plan = build_nas_playback_plan(
        settings,
        "smb://truenas/media/Test.iso",
        [PathMappingRule("smb://truenas/media", "/mnt/nas/media")],
    )
    assert plan["ready"] is False
    assert "unsupported_nas_playback_trigger_mode" in plan["blockers"]
    assert "oppo_ip_required" in plan["blockers"]


def test_settings_rules_are_used_when_explicit_rules_are_omitted():
    from resources.lib.nas_playback_adapter import build_nas_playback_plan
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "chinoppo_m9702",
            "nas_playback_confirmed": "true",
            "oppo_ip": "192.168.1.51",
            "nas_kodi_path_prefix": "smb://truenas/media",
            "nas_player_path_prefix": "/mnt/nas/media",
        }
    )
    plan = build_nas_playback_plan(settings, "smb://truenas/media/Concerts/Show.mkv")
    assert plan["ready"] is True
    assert plan["player_path"] == "/mnt/nas/media/Concerts/Show.mkv"
    assert plan["mapping"]["rule"]["label"] == "settings_prefix"


def test_runtime_zip_includes_adapter_but_excludes_build4_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "package_installable_zip", ROOT / "tools" / "package_installable_zip.py"
    )
    packager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packager)
    output = tmp_path / "runtime.zip"
    names = set(packager.create_installable_zip(ROOT, output))
    assert "script.oppo203.iso.external/resources/lib/oppo/nas_playback_adapter.py" in names
    assert "script.oppo203.iso.external/resources/lib/oppo/path_mapper.py" in names
    assert "script.oppo203.iso.external/BUILD_NOTES_v2.5.2_BUILD4.md" not in names
    assert "script.oppo203.iso.external/tests/test_v252_build4_nas_playback_adapter.py" not in names
    with zipfile.ZipFile(output) as zf:
        assert set(zf.namelist()) == names


def test_adapter_private_getters_cover_non_settings_inputs():
    from resources.lib import nas_playback_adapter as adapter

    assert adapter._get({"x": "y"}, "x") == "y"

    class BadDict:
        def __iter__(self):
            raise TypeError("not iterable")

    assert adapter._get(BadDict(), "missing", "fallback") == "fallback"
    assert adapter._get_bool({"flag": True}, "flag") is True
    assert adapter._get_bool({"flag": "yes"}, "flag") is True
    assert adapter._get_bool({"flag": "off"}, "flag", True) is False
    assert adapter._get_bool({"flag": "maybe"}, "flag", True) is True

    class BadBool:
        def get_bool(self, key, default=False):
            raise RuntimeError("boom")

    assert adapter._get_bool(BadBool(), "flag", True) is True


def test_default_wake_and_playback_clients_use_existing_oppo_control(monkeypatch):
    from resources.lib.settings_reader import Settings

    from resources.lib import nas_playback_adapter as adapter
    from resources.lib import oppo_control

    calls = []

    def fake_send(host, port, commands, timeout=3.0, delay=1.0):
        calls.append(("send", host, port, tuple(commands), timeout, delay))
        return ["ok"]

    def fake_activate(settings):
        calls.append(("activate", settings.get("oppo_ip")))
        return "activated"

    def fake_signin(settings):
        calls.append(("signin", settings.get("oppo_ip")))
        return "signed"

    def fake_play(settings, path):
        calls.append(("play", path))
        return "played"

    monkeypatch.setattr(oppo_control, "send_commands", fake_send)
    monkeypatch.setattr(oppo_control, "activate_http_api", fake_activate)
    monkeypatch.setattr(oppo_control, "signin_http_api", fake_signin)
    monkeypatch.setattr(oppo_control, "play_media_http_api", fake_play)

    settings = Settings(
        {
            "oppo_ip": "1.2.3.4",
            "oppo_port": "24",
            "oppo_socket_timeout": "4",
            "oppo_command_delay": "0",
        }
    )
    assert adapter._default_wake_client(settings, "#PON") == ["ok"]
    assert adapter._default_playback_client(settings, "/mnt/nas/media/Movie.iso") == "played"
    assert calls == [
        ("send", "1.2.3.4", 24, ("#PON",), 4.0, 0.0),
        ("activate", "1.2.3.4"),
        ("signin", "1.2.3.4"),
        ("play", "/mnt/nas/media/Movie.iso"),
    ]


def test_trigger_can_skip_power_on_before_playback():
    from resources.lib.nas_playback_adapter import trigger_nas_playback
    from resources.lib.path_mapper import PathMappingRule
    from resources.lib.settings_reader import Settings

    settings = Settings(
        {
            "oppo_hardware_model": "udp_203",
            "oppo_jailbreak_enabled": "true",
            "oppo_firmware_version": "20X-65-0131",
            "oppo_ip": "192.168.1.50",
            "nas_playback_power_on_before_trigger": "false",
        }
    )
    calls = []
    result = trigger_nas_playback(
        settings,
        "smb://truenas/media/SkipWake.iso",
        [PathMappingRule("smb://truenas/media", "/mnt/nas/media")],
        wake_client=lambda s, c: calls.append(("wake", c)),
        playback_client=lambda s, p: calls.append(("play", p)) or "ok",
    )
    assert result["success"] is True
    assert result["wake_result"] is None
    assert result["playback_result"] == "ok"
    assert calls == [("play", "/mnt/nas/media/SkipWake.iso")]


def test_build4_covers_path_mapper_edges_used_by_adapter():
    from resources.lib.path_mapper import normalize_player_path, rules_from_settings

    assert normalize_player_path(".") == ""
    try:
        rules_from_settings({"nas_kodi_path_prefix": "smb://truenas/media"})
    except Exception as exc:
        assert "player_prefix is required" in str(exc)
