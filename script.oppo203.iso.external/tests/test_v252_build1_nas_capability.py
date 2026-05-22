"""v2.5.2 Build 1 - OPPO/Chinoppo NAS playback capability gates."""
import importlib.util
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_current_addon_version_is_v252():
    root = ET.parse(ROOT / "addon.xml").getroot()
    assert root.attrib["version"] == "2.9.11"


def test_oppo20x_firmware_gate_minimum_and_recommended():
    from resources.lib.settings_reader import (
        OPPO20X_AUTOSCRIPT_MIN_FIRMWARE,
        OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE,
        oppo20x_autoscript_firmware_status,
    )

    assert OPPO20X_AUTOSCRIPT_MIN_FIRMWARE == "20X-56"
    assert OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE == "20X-65-0131"

    old = oppo20x_autoscript_firmware_status("20X-54-1127")
    assert old["autoscript_supported"] is False
    assert "oppo20x_firmware_below_20x_56" in old["blockers"]

    minimum = oppo20x_autoscript_firmware_status("20X-56")
    assert minimum["autoscript_supported"] is True
    assert not minimum["blockers"]

    recommended = oppo20x_autoscript_firmware_status("20X-65-0131")
    assert recommended["autoscript_supported"] is True
    assert not recommended["blockers"]


def test_oppo20x_requires_jailbreak_and_valid_firmware_for_nas_playback():
    from resources.lib.settings_reader import nas_playback_capability

    without_jailbreak = nas_playback_capability("udp_203", firmware="20X-65-0131", jailbreak=False)
    assert without_jailbreak["family"] == "oppo20x_jailbroken"
    assert without_jailbreak["requires_jailbreak"] is True
    assert "oppo20x_jailbreak_required" in without_jailbreak["blockers"]

    old_fw = nas_playback_capability("UDP-205", firmware="20X-54-1127", jailbreak=True)
    assert "oppo20x_firmware_below_20x_56" in old_fw["blockers"]
    assert old_fw["supported"] is False

    ready = nas_playback_capability("udp_203", firmware="20X-65-0131", jailbreak=True)
    assert ready["supported"] is True
    assert ready["min_autoscript_firmware"] == "20X-56"
    assert ready["recommended_firmware"] == "20X-65-0131"
    assert ready["wake_command"] == "#PON"


def test_chinoppo_family_requires_capability_confirmation_not_numeric_firmware():
    from resources.lib.settings_reader import nas_playback_capability

    candidate = nas_playback_capability("chinoppo_m9702", confirmed=False)
    assert candidate["family"] == "chinoppo_family"
    assert candidate["requires_capability_confirmation"] is True
    assert candidate["min_autoscript_firmware"] is None
    assert candidate["recommended_firmware"] is None
    assert candidate["wake_command"] == "#EJT"
    assert "chinoppo_firmware_binary_capability_must_be_confirmed" in candidate["warnings"]
    assert candidate["supported"] is True

    confirmed = nas_playback_capability("chinoppo_m9205c", confirmed=True)
    assert confirmed["family"] == "chinoppo_family"
    assert confirmed["warnings"] == []
    assert confirmed["wake_command"] == "#EJT"


def test_reavon_is_blocked_from_oppo_chinoppo_nas_playback_feature():
    from resources.lib.settings_reader import nas_playback_capability

    result = nas_playback_capability("reavon_ubrx200", confirmed=True)
    assert result["family"] == "unsupported_reavon"
    assert result["supported"] is False
    assert "reavon_warning_only_not_supported_for_oppo_chinoppo_nas_playback" in result["blockers"]


def test_startup_power_fix_preserved_no_send_token_import():
    service_text = (ROOT / "service.py").read_text(encoding="utf-8")
    assert "send_token" not in service_text
    assert "query_power_status" in service_text
    assert "_spawn_kodi_startup_power_on(settings)" in service_text
    assert "def _service_main" in service_text


def test_release_audit_requires_v252_build1_evidence():
    spec = importlib.util.spec_from_file_location("audit_release_v252_build1", ROOT / "tools" / "audit_release.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    results = mod.run_audit(mod.project_root(mod.Path(ROOT)), expected_version="2.9.11")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    assert "file:BUILD_NOTES_v2.5.2_BUILD1.md" in names
    assert "file:HARDWARE_VALIDATION_TRACKER_v2.5.2.md" in names


def test_firmware_parser_handles_unknown_empty_and_invalid_values():
    from resources.lib.settings_reader import _firmware_major_build, oppo20x_autoscript_firmware_status

    assert _firmware_major_build(None) is None
    assert _firmware_major_build("") is None
    assert _firmware_major_build("not-a-firmware") is None
    assert _firmware_major_build("20x_60") == 60

    unknown = oppo20x_autoscript_firmware_status("")
    assert "oppo20x_firmware_unknown" in unknown["warnings"]

    supported_but_not_recommended = oppo20x_autoscript_firmware_status("20X-60")
    assert supported_but_not_recommended["autoscript_supported"] is True
    assert "oppo20x_autoscript_supported_but_20x_65_0131_recommended" in supported_but_not_recommended["warnings"]


def test_unknown_model_uses_warning_and_not_supported_claim():
    from resources.lib.settings_reader import nas_playback_capability

    result = nas_playback_capability("mystery-player", firmware="20X-65-0131", jailbreak=True, confirmed=True)
    assert result["family"] == "unknown_oppo_compatible"
    assert result["supported"] is False
    assert "unknown_model_using_safe_oppo20x_assumptions" in result["warnings"]


def test_settings_reader_defensive_branches_covered_for_v252_gate():
    from resources.lib.settings_reader import Settings, save_settings

    s = Settings({"blank": None, "small_float": "0.1"})
    assert s.get_bool("blank", True) is True
    assert s.get_float("small_float", minimum=1.5) == 1.5

    class BadMapping:
        data = object()

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        assert save_settings(td, BadMapping()) is True


def test_diagnostic_logging_print_fallback_for_v252_gate(capsys):
    from resources.lib.diagnostic_logging import log_to_xbmc

    formatted = log_to_xbmc(None, "diag", "coverage fallback")
    out = capsys.readouterr().out
    assert formatted in out
