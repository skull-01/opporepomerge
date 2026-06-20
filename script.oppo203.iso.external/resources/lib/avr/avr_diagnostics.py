"""AVR wizard, diagnostics, and safety helpers for v2.9.10 Build 16.

These helpers are deliberately opt-in and non-sequencing.  They validate AVR
settings, describe setup wizard capabilities, run query-only diagnostics without
changing AVR state, require explicit confirmation for power/input tests, and
export sanitized support reports that never claim hardware validation.
"""

from __future__ import annotations

import json
import os
import time as _time
from typing import Any, Callable, overload

try:
    from . import avr_control
    from .avr_presets import get_avr_preset, list_avr_presets
    from .avr_types import AVR_BACKEND_DISABLED, AvrResult
except ImportError:  # pragma: no cover - top-level/audit/test compatibility
    import avr_control  # type: ignore
    from avr_presets import get_avr_preset, list_avr_presets  # type: ignore
    from avr_types import AVR_BACKEND_DISABLED, AvrResult  # type: ignore

SECRET_KEY_FRAGMENTS = ("psk", "password", "credential", "token", "secret", "key")
SENSITIVE_OUTPUT_KEYS = ("stdout", "stderr", "output", "raw", "response", "headers")
REDACTION = "<redacted>"
Writer = Callable[[str, str], None]


AVR_WIZARD_CAPABILITIES: dict[str, object] = {
    "supports_skip_avr_setup": True,
    "supports_family_selection": True,
    "supports_host_and_port": True,
    "supports_player_input": True,
    "supports_optional_restore_input": True,
    "supports_optional_sound_mode_metadata": True,
    "supports_sony_experimental_acknowledgement": True,
    "avr_enabled_by_default": False,
    "query_only_tests_change_state": False,
    "power_input_tests_require_explicit_user_action": True,
    "playback_sequencing_hooked": True,
    "hardware_validation_claimed": False,
}


def _settings_dict(settings: dict[str, object] | object | None) -> dict[str, object]:
    if settings is None:
        return {}
    if isinstance(settings, dict):
        return dict(settings)
    if hasattr(settings, "data") and isinstance(settings.data, dict):
        return dict(settings.data)
    if hasattr(settings, "items"):
        try:
            return dict(settings.items())
        except Exception:
            return {}
    return {}


def _truthy(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    text = "" if value is None else str(value).strip().lower()
    if text == "":
        return default
    return text in {"1", "true", "yes", "on"}


def _is_secret_key(key: object) -> bool:
    key_text = str(key).lower()
    return any(fragment in key_text for fragment in SECRET_KEY_FRAGMENTS)


def _is_sensitive_key(key: object) -> bool:
    key_text = str(key).lower()
    return any(fragment in key_text for fragment in SENSITIVE_OUTPUT_KEYS)


def _secret_values(settings: dict[str, object]) -> tuple[str, ...]:
    values: list[str] = []
    for key, value in settings.items():
        text = "" if value is None else str(value)
        if text and _is_secret_key(key):
            values.append(text)
    return tuple(values)


def redact_value(value: object) -> str:
    text = "" if value is None else str(value)
    if not text:
        return ""
    if len(text) <= 6:
        return REDACTION
    return f"{text[:3]}...{text[-2:]}"


def sanitize_text(value: object, settings: dict[str, object] | object | None = None) -> str:
    text = "" if value is None else str(value)
    data = _settings_dict(settings)
    for secret in _secret_values(data):
        text = text.replace(secret, REDACTION)
    return text


@overload
def sanitize_payload(
    payload: dict[str, object], settings: dict[str, object] | object | None = None
) -> dict[str, object]: ...


@overload
def sanitize_payload(payload: Any, settings: dict[str, object] | object | None = None) -> Any: ...


def sanitize_payload(payload: Any, settings: dict[str, object] | object | None = None) -> Any:
    data = _settings_dict(settings)
    if isinstance(payload, dict):
        out: dict[str, Any] = {}
        for key, value in payload.items():
            if _is_secret_key(key):
                out[str(key)] = redact_value(value)
            elif _is_sensitive_key(key):
                out[str(key)] = REDACTION if value not in (None, "") else ""
            else:
                out[str(key)] = sanitize_payload(value, data)
        return out
    if isinstance(payload, (list, tuple)):
        return [sanitize_payload(item, data) for item in payload]
    if isinstance(payload, str):
        return sanitize_text(payload, data)
    return payload


def wizard_capabilities() -> dict[str, object]:
    """Return AVR setup wizard capability metadata for tests and UI wiring."""
    data = dict(AVR_WIZARD_CAPABILITIES)
    data["families"] = tuple(pid for pid in list_avr_presets() if pid != AVR_BACKEND_DISABLED)
    return data


def wizard_family_options() -> tuple[dict[str, object], ...]:
    """Return selectable AVR families, including the safe skip/default option."""
    options: list[dict[str, object]] = [
        {
            "id": AVR_BACKEND_DISABLED,
            "label": "Skip AVR setup / keep AVR control disabled",
            "enabled_by_default": False,
            "hardware_validation_claimed": False,
        }
    ]
    for preset_id in list_avr_presets():
        if preset_id == AVR_BACKEND_DISABLED:
            continue
        preset = get_avr_preset(preset_id)
        options.append(
            {
                "id": preset["id"],
                "label": preset.get("label", preset_id),
                "backend": preset.get("backend", preset_id),
                "experimental": bool(
                    preset.get("experimental")
                    or preset.get("requires_experimental_acknowledgement")
                ),
                "requires_sony_experimental_acknowledgement": preset.get("backend")
                == "sony_audio_api",
                "hardware_validation_claimed": False,
            }
        )
    return tuple(options)


def apply_wizard_selection(
    settings: dict[str, object] | object | None, selection: dict[str, object]
) -> dict[str, object]:
    """Apply AVR wizard answers to a settings dict without executing commands."""
    current = _settings_dict(settings)
    backend = str(
        selection.get("avr_backend")
        or selection.get("backend")
        or selection.get("id")
        or AVR_BACKEND_DISABLED
    )
    if backend == AVR_BACKEND_DISABLED or _truthy(selection.get("skip_avr_setup", False)):
        current.update(
            {
                "avr_control_enabled": "false",
                "avr_backend": AVR_BACKEND_DISABLED,
                "selected_avr_preset_id": AVR_BACKEND_DISABLED,
                "avr_power_off_enabled": "false",
                "avr_volume_automation_enabled": "false",
            }
        )
        return current

    current["avr_control_enabled"] = "true"
    current["avr_backend"] = backend
    current["selected_avr_preset_id"] = backend
    for key in (
        "avr_host",
        "avr_port",
        "avr_player_input",
        "avr_restore_input",
        "avr_sound_mode",
        "sony_avr_psk",
        "sony_avr_api_path",
        "sony_avr_player_input_uri",
        "sony_avr_restore_input_uri",
    ):
        if key in selection:
            current[key] = str(selection.get(key, ""))
    current["avr_restore_enabled"] = (
        "true" if _truthy(selection.get("avr_restore_enabled", False)) else "false"
    )
    current["avr_power_off_enabled"] = (
        "true" if _truthy(selection.get("avr_power_off_enabled", False)) else "false"
    )
    current["avr_volume_automation_enabled"] = (
        "true" if _truthy(selection.get("avr_volume_automation_enabled", False)) else "false"
    )
    current["sony_avr_experimental_acknowledged"] = (
        "true"
        if _truthy(
            selection.get(
                "sony_avr_experimental_acknowledged",
                current.get("sony_avr_experimental_acknowledged", "false"),
            )
        )
        else "false"
    )
    return current


def validate_avr_for_diagnostics(settings: dict[str, object] | object | None) -> dict[str, object]:
    data = _settings_dict(settings)
    validation: dict[str, object] = avr_control.validate_avr_settings(data).as_dict()
    validation["hardware_validation_claimed"] = False
    return sanitize_payload(validation, data)


def settings_summary(settings: dict[str, object] | object | None) -> dict[str, object]:
    data = _settings_dict(settings)
    keys = (
        "avr_control_enabled",
        "avr_backend",
        "avr_host",
        "avr_port",
        "avr_player_input",
        "avr_restore_enabled",
        "avr_restore_input",
        "avr_power_on_enabled",
        "avr_power_off_enabled",
        "avr_volume_automation_enabled",
        "avr_sound_mode",
        "sony_avr_experimental_acknowledged",
        "sony_avr_psk",
        "sony_avr_api_path",
        "sony_avr_player_input_uri",
        "sony_avr_restore_input_uri",
    )
    summary: dict[str, object] = {"hardware_validation_claimed": False}
    for key in keys:
        value = data.get(key, "")
        if _is_secret_key(key):
            summary[key] = redact_value(value)
        elif key in {
            "avr_host",
            "avr_player_input",
            "avr_restore_input",
            "sony_avr_player_input_uri",
            "sony_avr_restore_input_uri",
        }:
            summary[f"{key}_configured"] = bool(str(value).strip())
        else:
            summary[key] = value
    return sanitize_payload(summary, data)


def dry_run_avr_action(
    settings: dict[str, object] | object | None, action: str
) -> dict[str, object]:
    data = _settings_dict(settings)
    validation = validate_avr_for_diagnostics(data)
    return sanitize_payload(
        {
            "action": action,
            "backend": validation.get("backend", AVR_BACKEND_DISABLED),
            "would_call_driver": bool(validation.get("ok")),
            "network_called": False,
            "dry_run_only": True,
            "state_changing": action in {"power_on", "select_input", "restore_input", "power_off"},
            "requires_explicit_user_action": action
            in {"power_on", "select_input", "restore_input", "power_off"},
            "hardware_validation_claimed": False,
            "validation": validation,
        },
        data,
    )


def _result_to_dict(result: object) -> dict[str, object]:
    if hasattr(result, "as_dict"):
        return dict(result.as_dict())
    if isinstance(result, dict):
        return dict(result)
    return {"ok": False, "message": str(result), "nonfatal": True, "command_sent": False}


def _blocked(action: str, settings: dict[str, object], warning: str) -> dict[str, object]:
    backend = avr_control.selected_avr_backend(settings)
    return AvrResult(
        ok=False,
        action=action,
        backend=backend,
        message=warning,
        warnings=(warning,),
        nonfatal=True,
        hardware_validation_claimed=False,
        command_sent=False,
    ).as_dict()


def run_query_only_test(
    settings: dict[str, object] | object | None,
    query: str = "power",
    *,
    controller: object | None = None,
) -> dict[str, object]:
    """Run a query-only diagnostic action.  It must not change AVR state."""
    data = _settings_dict(settings)
    validation = avr_control.validate_avr_settings(data)
    if not validation.enabled or not validation.ok:
        return sanitize_payload(_blocked("query_" + query, data, "avr_query_not_available"), data)
    ctrl = controller if controller is not None else avr_control.controller_factory(data)
    if ctrl is None:
        return sanitize_payload(
            _blocked("query_" + query, data, "avr_controller_unavailable"), data
        )
    method_name = "query_input" if query == "input" else "query_power"
    method = getattr(ctrl, method_name, None)
    if method is None:
        return sanitize_payload(_blocked(method_name, data, "avr_query_method_unavailable"), data)
    try:
        result = _result_to_dict(method())
    except Exception as exc:
        result = _blocked(method_name, data, f"avr_query_error_nonfatal:{exc}")
    result.update(
        {
            "query_only": True,
            "state_changing": False,
            "hardware_validation_claimed": False,
        }
    )
    return sanitize_payload(result, data)


def run_explicit_test_action(
    settings: dict[str, object] | object | None,
    action: str,
    *,
    explicit_user_action: bool = False,
    controller: object | None = None,
) -> dict[str, object]:
    """Run a state-changing AVR test only after explicit user action."""
    data = _settings_dict(settings)
    if (
        action in {"power_on", "select_input", "restore_input", "power_off"}
        and not explicit_user_action
    ):
        return sanitize_payload(_blocked(action, data, "explicit_user_action_required"), data)
    validation = avr_control.validate_avr_settings(data)
    if not validation.enabled or not validation.ok:
        return sanitize_payload(_blocked(action, data, "avr_test_action_not_available"), data)
    ctrl = controller if controller is not None else avr_control.controller_factory(data)
    if ctrl is None:
        return sanitize_payload(_blocked(action, data, "avr_controller_unavailable"), data)
    method_name = "select_input" if action in {"select_input", "restore_input"} else action
    method = getattr(ctrl, method_name, None)
    if method is None:
        return sanitize_payload(_blocked(action, data, "avr_test_method_unavailable"), data)
    try:
        result = _result_to_dict(method())
    except Exception as exc:
        result = _blocked(action, data, f"avr_test_error_nonfatal:{exc}")
    result.update(
        {
            "query_only": False,
            "state_changing": action in {"power_on", "select_input", "restore_input", "power_off"},
            "explicit_user_action": True,
            "hardware_validation_claimed": False,
        }
    )
    return sanitize_payload(result, data)


def build_diagnostic_report(settings: dict[str, object] | object | None) -> dict[str, object]:
    data = _settings_dict(settings)
    return sanitize_payload(
        {
            "title": "OPPO203 AVR Diagnostic Report",
            "settings": settings_summary(data),
            "wizard_capabilities": wizard_capabilities(),
            "validation": validate_avr_for_diagnostics(data),
            "dry_run": {
                "power_query": dry_run_avr_action(data, "query_power"),
                "input_query": dry_run_avr_action(data, "query_input"),
                "power_on_test": dry_run_avr_action(data, "power_on"),
                "input_select_test": dry_run_avr_action(data, "select_input"),
            },
            "playback_sequencing_hooked": True,
            "hardware_validation_claimed": False,
        },
        data,
    )


def format_report(
    report: dict[str, object], settings: dict[str, object] | object | None = None
) -> str:
    return json.dumps(sanitize_payload(report, settings), indent=2, sort_keys=True)


def _ts(now: float | Callable[[], float] | None = None) -> str:
    value = now() if callable(now) else (now if now is not None else _time.time())
    # UTC keeps exported diagnostic filenames deterministic across timezones.
    return _time.strftime("%Y%m%d-%H%M%S", _time.gmtime(value))


def default_report_path(root_dir: str, now: float | Callable[[], float] | None = None) -> str:
    return os.path.join(root_dir, f"avr-diagnostics-{_ts(now)}.json")


def save_report(
    report: dict[str, object],
    root_dir: str,
    *,
    now: float | Callable[[], float] | None = None,
    writer: Writer | None = None,
    settings: dict[str, object] | object | None = None,
) -> str:
    path = default_report_path(root_dir, now=now)
    text = format_report(report, settings=settings)
    if writer is None:
        os.makedirs(root_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        writer(path, text)
    return path


def export_avr_diagnostic_report(
    settings: dict[str, object] | object | None,
    root_dir: str,
    *,
    now: float | Callable[[], float] | None = None,
    writer: Writer | None = None,
) -> str:
    return save_report(
        build_diagnostic_report(settings), root_dir, now=now, writer=writer, settings=settings
    )
