"""Lightweight typed settings schema for script.oppo203.iso.external.

Build 9 adds a dependency-free schema layer that can validate and safely coerce
common Kodi settings without changing the existing Settings fallback behavior.
The runtime still reads settings through settings_reader.Settings; this module is
an opt-in validation layer used by diagnostics, tests, and future hardening.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SettingIssue:
    """A non-throwing validation issue for one setting."""

    key: str
    code: str
    message: str
    severity: str = "warning"


@dataclass(frozen=True)
class SettingSpec:
    """Typed validation/coercion rule for a single setting key."""

    key: str
    kind: str = "str"
    default: Any = ""
    required: bool = False
    choices: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None
    allow_empty: bool = True


TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
FALSE_VALUES = frozenset({"0", "false", "no", "off"})


def safe_text(value: Any, default: Any = "") -> str:
    """Convert a raw setting value to text without leaking broken __str__ objects."""
    try:
        return str(default) if value is None else str(value)
    except Exception:
        return str(default)


def parse_bool(value: Any, default: bool = False) -> bool:
    """Coerce Kodi-style boolean strings with the existing Settings semantics."""
    if isinstance(value, bool):
        return value
    text = safe_text(value, str(default)).strip().lower()
    if text == "":
        return bool(default)
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    return bool(default)


def parse_int(
    value: Any, default: int = 0, minimum: int | None = None, maximum: int | None = None
) -> int:
    try:
        parsed = int(safe_text(value, default).strip())
    except (TypeError, ValueError):
        parsed = int(default)
    if minimum is not None and parsed < minimum:
        parsed = int(minimum)
    if maximum is not None and parsed > maximum:
        parsed = int(maximum)
    return parsed


def parse_float(
    value: Any, default: float = 0.0, minimum: float | None = None, maximum: float | None = None
) -> float:
    try:
        parsed = float(safe_text(value, default).strip())
    except (TypeError, ValueError):
        parsed = float(default)
    if minimum is not None and parsed < minimum:
        parsed = float(minimum)
    if maximum is not None and parsed > maximum:
        parsed = float(maximum)
    return parsed


class SettingsSchema:
    """Validate a mapping of Kodi setting values without mutating it."""

    def __init__(self, specs: list[SettingSpec] | tuple[SettingSpec, ...]):
        self.specs = tuple(specs)
        self.by_key = {spec.key: spec for spec in self.specs}

    def validate_setting(self, spec: SettingSpec, raw_value: Any) -> list[SettingIssue]:
        issues: list[SettingIssue] = []
        text = safe_text(raw_value, spec.default)
        if spec.required and text.strip() == "":
            issues.append(SettingIssue(spec.key, "required_empty", f"{spec.key} is required"))
        if not spec.allow_empty and text.strip() == "":
            issues.append(
                SettingIssue(spec.key, "empty_not_allowed", f"{spec.key} may not be empty")
            )
        if spec.choices and text not in spec.choices:
            issues.append(
                SettingIssue(
                    spec.key,
                    "invalid_choice",
                    f"{spec.key} must be one of {', '.join(spec.choices)}",
                )
            )
        if spec.kind == "int":
            try:
                parsed = int(text.strip())
            except (TypeError, ValueError):
                issues.append(
                    SettingIssue(spec.key, "invalid_int", f"{spec.key} must be an integer")
                )
            else:
                if spec.minimum is not None and parsed < spec.minimum:
                    issues.append(
                        SettingIssue(
                            spec.key, "below_minimum", f"{spec.key} must be >= {int(spec.minimum)}"
                        )
                    )
                if spec.maximum is not None and parsed > spec.maximum:
                    issues.append(
                        SettingIssue(
                            spec.key, "above_maximum", f"{spec.key} must be <= {int(spec.maximum)}"
                        )
                    )
        elif spec.kind == "float":
            try:
                parsed_float = float(text.strip())
            except (TypeError, ValueError):
                issues.append(
                    SettingIssue(spec.key, "invalid_float", f"{spec.key} must be a number")
                )
            else:
                if spec.minimum is not None and parsed_float < spec.minimum:
                    issues.append(
                        SettingIssue(
                            spec.key, "below_minimum", f"{spec.key} must be >= {spec.minimum:g}"
                        )
                    )
                if spec.maximum is not None and parsed_float > spec.maximum:
                    issues.append(
                        SettingIssue(
                            spec.key, "above_maximum", f"{spec.key} must be <= {spec.maximum:g}"
                        )
                    )
        elif spec.kind == "bool":
            lowered = text.strip().lower()
            if lowered and lowered not in TRUE_VALUES and lowered not in FALSE_VALUES:
                issues.append(
                    SettingIssue(spec.key, "invalid_bool", f"{spec.key} must be true or false")
                )
        return issues

    def validate(self, values: Mapping[str, Any]) -> list[SettingIssue]:
        issues: list[SettingIssue] = []
        for spec in self.specs:
            raw = values.get(spec.key, spec.default)
            issues.extend(self.validate_setting(spec, raw))
        return issues

    def coerce(self, values: Mapping[str, Any]) -> dict[str, Any]:
        coerced: dict[str, Any] = {}
        for spec in self.specs:
            raw = values.get(spec.key, spec.default)
            if spec.kind == "bool":
                coerced[spec.key] = parse_bool(raw, bool(spec.default))
            elif spec.kind == "int":
                coerced[spec.key] = parse_int(
                    raw,
                    int(spec.default),
                    None if spec.minimum is None else int(spec.minimum),
                    None if spec.maximum is None else int(spec.maximum),
                )
            elif spec.kind == "float":
                coerced[spec.key] = parse_float(
                    raw, float(spec.default), spec.minimum, spec.maximum
                )
            else:
                coerced[spec.key] = safe_text(raw, spec.default)
        return coerced


def build_default_schema(
    defaults: Mapping[str, Any], enum_values: Mapping[str, list[str] | tuple[str, ...]]
) -> SettingsSchema:
    """Build the active schema from settings defaults and enum choices."""
    specs = [
        SettingSpec(
            "python_path",
            "path",
            defaults.get("python_path", "/usr/bin/python3"),
            required=True,
            allow_empty=False,
        ),
        SettingSpec(
            "oppo_ip",
            "str",
            defaults.get("oppo_ip", "192.168.1.50"),
            required=True,
            allow_empty=False,
        ),
        SettingSpec(
            "oppo_port",
            "int",
            defaults.get("oppo_port", "23"),
            minimum=1,
            maximum=65535,
            allow_empty=False,
        ),
        SettingSpec(
            "oppo_socket_timeout",
            "float",
            defaults.get("oppo_socket_timeout", "3.0"),
            minimum=0.1,
            maximum=120.0,
            allow_empty=False,
        ),
        SettingSpec(
            "oppo_command_delay",
            "float",
            defaults.get("oppo_command_delay", "0.1"),
            minimum=0.0,
            maximum=10.0,
            allow_empty=False,
        ),
        SettingSpec(
            "kodi_startup_power_on", "bool", defaults.get("kodi_startup_power_on", "false")
        ),
        SettingSpec(
            "kodi_startup_power_on_delay",
            "int",
            defaults.get("kodi_startup_power_on_delay", "5"),
            minimum=0,
            maximum=3600,
        ),
        SettingSpec(
            "kodi_startup_power_on_retries",
            "int",
            defaults.get("kodi_startup_power_on_retries", "3"),
            minimum=0,
            maximum=20,
        ),
        SettingSpec(
            "kodi_startup_power_on_use_wol",
            "bool",
            defaults.get("kodi_startup_power_on_use_wol", "true"),
        ),
        SettingSpec("oppo_use_wol", "bool", defaults.get("oppo_use_wol", "false")),
        SettingSpec("avr_control_enabled", "bool", defaults.get("avr_control_enabled", "false")),
        SettingSpec("avr_restore_enabled", "bool", defaults.get("avr_restore_enabled", "false")),
        SettingSpec("avr_power_on_enabled", "bool", defaults.get("avr_power_on_enabled", "false")),
        SettingSpec(
            "avr_power_off_enabled", "bool", defaults.get("avr_power_off_enabled", "false")
        ),
        SettingSpec(
            "avr_volume_automation_enabled",
            "bool",
            defaults.get("avr_volume_automation_enabled", "false"),
        ),
        SettingSpec(
            "sony_avr_experimental_acknowledged",
            "bool",
            defaults.get("sony_avr_experimental_acknowledged", "false"),
        ),
        SettingSpec(
            "oppo_http_port", "int", defaults.get("oppo_http_port", "436"), minimum=1, maximum=65535
        ),
        SettingSpec(
            "http_poll_interval",
            "int",
            defaults.get("http_poll_interval", "5"),
            minimum=1,
            maximum=3600,
        ),
        SettingSpec(
            "http_poll_timeout_minutes",
            "int",
            defaults.get("http_poll_timeout_minutes", "240"),
            minimum=1,
            maximum=1440,
        ),
        SettingSpec(
            "fixed_timeout_minutes",
            "int",
            defaults.get("fixed_timeout_minutes", "180"),
            minimum=1,
            maximum=1440,
        ),
    ]
    for key, choices in sorted(enum_values.items()):
        specs.append(
            SettingSpec(
                key, "enum", defaults.get(key, ""), choices=tuple(choices), allow_empty=False
            )
        )
    return SettingsSchema(specs)
