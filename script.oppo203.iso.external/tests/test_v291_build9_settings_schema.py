"""v2.9.1 Build 16 settings schema and typed validation regression tests."""
from __future__ import annotations

from resources.lib import settings_reader as sr
from resources.lib import settings_schema as schema


class BadStr:
    def __str__(self):
        raise RuntimeError("broken text")


def test_settings_schema_is_exposed_and_covers_core_runtime_fields():
    keys = set(sr.SETTINGS_SCHEMA.by_key)
    for key in (
        "python_path",
        "oppo_ip",
        "oppo_port",
        "oppo_socket_timeout",
        "kodi_startup_power_on",
        "kodi_startup_power_on_retries",
        "oppo_start_mode",
        "playback_architecture",
        "oppo_hardware_model",
    ):
        assert key in keys


def test_schema_reports_invalid_numbers_enums_and_bools_without_throwing():
    settings = sr.Settings({
        "oppo_port": "99999",
        "oppo_socket_timeout": "not-a-float",
        "kodi_startup_power_on": "maybe",
        "oppo_start_mode": "bad-mode",
        "playback_architecture": "bad-arch",
    })
    issues = settings.schema_issues()
    by_key = {(issue.key, issue.code) for issue in issues}
    assert ("oppo_port", "above_maximum") in by_key
    assert ("oppo_socket_timeout", "invalid_float") in by_key
    assert ("kodi_startup_power_on", "invalid_bool") in by_key
    assert ("oppo_start_mode", "invalid_choice") in by_key
    assert ("playback_architecture", "invalid_choice") in by_key


def test_schema_coerce_matches_existing_safe_getter_fallbacks():
    settings = sr.Settings({
        "oppo_port": "70000",
        "oppo_socket_timeout": "bad",
        "kodi_startup_power_on": "true",
        "kodi_startup_power_on_retries": "999",
        "oppo_command_delay": BadStr(),
    })
    typed = settings.typed_values()
    assert typed["oppo_port"] == 65535
    assert typed["oppo_socket_timeout"] == 3.0
    assert typed["kodi_startup_power_on"] is True
    assert typed["kodi_startup_power_on_retries"] == 20
    assert typed["oppo_command_delay"] == 0.1
    assert settings.get_int("oppo_port", 23, minimum=1, maximum=65535) == typed["oppo_port"]
    assert settings.get_float("oppo_socket_timeout", 3.0, minimum=0.1, maximum=120.0) == typed["oppo_socket_timeout"]


def test_validation_summary_includes_schema_issue_metadata_but_preserves_legacy_keys():
    settings = sr.Settings({
        "oppo_port": "not-int",
        "oppo_start_mode": "bad-mode",
        "playback_architecture": "bad-arch",
    })
    summary = settings.validation_summary()
    assert summary["ok"] is False
    assert "missing" in summary
    assert "warnings" in summary
    assert "oppo_port" in summary
    assert "playback_architecture" in summary
    assert summary["schema_issue_count"] >= 3
    assert "invalid_int" in summary["schema_issue_codes"]
    assert "invalid_choice" in summary["schema_issue_codes"]


def test_schema_helpers_parse_without_runtime_dependencies():
    assert schema.parse_bool("yes") is True
    assert schema.parse_bool("off", True) is False
    assert schema.parse_bool("unknown", True) is True
    assert schema.parse_int("bad", 7, minimum=1, maximum=10) == 7
    assert schema.parse_int("0", 7, minimum=1, maximum=10) == 1
    assert schema.parse_float("99.5", 1.0, minimum=0.0, maximum=10.0) == 10.0
