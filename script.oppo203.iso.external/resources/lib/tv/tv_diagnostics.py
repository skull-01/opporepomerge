"""TV diagnostics and dry-run validator for v2.9.10 Build 10.

The helpers in this module are deliberately read-only unless ``save_report`` is
called with an explicit destination.  Dry-run reporting never contacts TVs,
Roku devices, ADB, Sony Bravia APIs, SmartThings, or shell commands.  Live test
actions are exposed as explicit helpers and return sanitized, non-fatal results
so playback/routing behavior remains untouched.
"""

from __future__ import annotations

import json
import os
import time as _time
from typing import Any, Callable, cast, overload

try:
    from . import tv_control
    from .tv_backends import (
        backend_target_setting,
        get_backend,
        is_supported_backend,
        normalize_backend_id,
    )
except ImportError:  # pragma: no cover - top-level/audit/test compatibility
    import tv_control  # type: ignore
    from tv_backends import (  # type: ignore
        backend_target_setting,
        get_backend,
        is_supported_backend,
        normalize_backend_id,
    )

try:
    from .smartthings_control import TOKEN_REDACTION, redact_secret_in_text, redact_token
    from .smartthings_control import validation_metadata as smartthings_validation_metadata
except ImportError:  # pragma: no cover - top-level/audit/test compatibility
    try:
        from smartthings_control import (  # type: ignore
            TOKEN_REDACTION,
            redact_secret_in_text,
            redact_token,
        )
        from smartthings_control import (  # type: ignore[no-redef]
            validation_metadata as smartthings_validation_metadata,
        )
    except Exception:  # pragma: no cover - defensive fallback for unusual imports
        TOKEN_REDACTION = "<redacted>"

        def redact_token(value: object, visible_prefix: int = 4, visible_suffix: int = 2) -> str:
            return TOKEN_REDACTION if value else ""

        def redact_secret_in_text(text: object, token: object = "") -> str:
            return "" if text is None else str(text).replace(str(token), TOKEN_REDACTION)

        def smartthings_validation_metadata(settings: dict[str, object]) -> dict[str, object]:
            return {"warnings": (), "hardware_validation_claimed": False}


SECRET_KEY_FRAGMENTS = ("token", "psk", "password", "credential", "secret")
SENSITIVE_OUTPUT_KEYS = ("stdout", "stderr", "output", "command_output", "raw_output")
COMMAND_BACKENDS = {"lg_command", "samsung_command", "custom_command"}
VALIDATION_TARGETS = ("oppo", "kodi")

Switcher = Callable[[dict[str, object]], Any]
Writer = Callable[[str, str], None]


def _settings_dict(settings: dict[str, object] | object | None) -> dict[str, object]:
    """Return a shallow dict copy from a mapping-like settings object."""
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


def _secret_values(settings: dict[str, object]) -> tuple[str, ...]:
    values: list[str] = []
    for key, value in settings.items():
        key_text = str(key).lower()
        value_text = "" if value is None else str(value)
        if value_text and any(fragment in key_text for fragment in SECRET_KEY_FRAGMENTS):
            values.append(value_text)
    return tuple(values)


def _is_secret_key(key: object) -> bool:
    key_text = str(key).lower()
    return any(fragment in key_text for fragment in SECRET_KEY_FRAGMENTS)


def _is_sensitive_output_key(key: object) -> bool:
    key_text = str(key).lower()
    return any(fragment in key_text for fragment in SENSITIVE_OUTPUT_KEYS)


def sanitize_text(value: object, settings: dict[str, object] | object | None = None) -> str:
    """Return text with known TV-control secrets redacted."""
    safe = "" if value is None else str(value)
    source = _settings_dict(settings)
    for secret in _secret_values(source):
        safe = safe.replace(secret, TOKEN_REDACTION)
    return safe


@overload
def sanitize_payload(
    payload: dict[str, Any], settings: dict[str, object] | object | None = None
) -> dict[str, object]: ...
@overload
def sanitize_payload(payload: Any, settings: dict[str, object] | object | None = None) -> Any: ...
def sanitize_payload(payload: Any, settings: dict[str, object] | object | None = None) -> Any:
    """Recursively sanitize diagnostics data for export or logging.

    Raw SmartThings tokens, Sony PSKs, passwords, credentials, secrets, and
    command output fields are replaced.  Non-secret strings are still scanned
    for known secret values from the supplied settings.
    """
    source = _settings_dict(settings)
    if isinstance(payload, dict):
        sanitized: dict[str, Any] = {}
        for key, value in payload.items():
            if _is_secret_key(key):
                value_text = "" if value is None else str(value)
                sanitized[str(key)] = (
                    value_text
                    if "..." in value_text or value_text == TOKEN_REDACTION
                    else redact_token(value)
                )
            elif _is_sensitive_output_key(key):
                sanitized[str(key)] = TOKEN_REDACTION if value not in (None, "") else ""
            else:
                sanitized[str(key)] = sanitize_payload(value, source)
        return sanitized
    if isinstance(payload, (list, tuple)):
        return [sanitize_payload(item, source) for item in payload]
    if isinstance(payload, str):
        return sanitize_text(payload, source)
    return payload


def sanitized_settings_summary(settings: dict[str, object] | object | None) -> dict[str, object]:
    """Return shareable selected TV settings without command bodies or secrets."""
    data = _settings_dict(settings)
    backend = selected_backend_id(data)
    summary: dict[str, object] = {
        "tv_backend": backend,
        "tv_ip_configured": bool(str(data.get("tv_ip", "")).strip()),
        "hardware_validation_claimed": False,
    }
    for key in sorted(data):
        key_text = str(key).lower()
        if key == "tv_backend" or not any(
            token in key_text
            for token in ("smartthings", "sony", "roku", "command", "adb", "input", "tv_ip")
        ):
            continue
        if _is_secret_key(key):
            summary[key] = redact_token(data.get(key))
        elif "command" in key_text:
            summary[f"{key}_configured"] = bool(str(data.get(key, "")).strip())
        elif key == "tv_ip":
            summary["tv_ip_configured"] = bool(str(data.get(key, "")).strip())
        else:
            value = data.get(key, "")
            summary[key] = sanitize_text(value, data) if value not in (None, "") else ""
    return summary


def selected_backend_id(settings: dict[str, object] | object | None) -> str:
    """Return the normalized selected backend without performing IO."""
    data = _settings_dict(settings)
    return normalize_backend_id(str(data.get("tv_backend", "adb") or "adb"))


def target_setting_keys(settings: dict[str, object] | object | None) -> dict[str, str]:
    """Return the target setting keys used by the selected backend."""
    backend = selected_backend_id(settings)
    return {target: backend_target_setting(backend, target) for target in VALIDATION_TARGETS}


def _field_status(data: dict[str, object], key: str) -> dict[str, object]:
    value = data.get(key, "")
    return {
        "setting": key,
        "configured": bool(str(value or "").strip()),
    }


def validate_tv_settings(settings: dict[str, object] | object | None) -> dict[str, object]:
    """Validate selected TV backend settings without performing network IO."""
    data = _settings_dict(settings)
    backend = selected_backend_id(data)
    backend_supported = is_supported_backend(backend)
    backend_meta = get_backend(backend) if backend_supported else {}
    warnings: list[str] = []
    missing: list[str] = []

    if not backend_supported:
        warnings.append("tv_backend_unsupported")

    fields = {
        target: _field_status(data, key) for target, key in target_setting_keys(data).items() if key
    }
    for target, status in fields.items():
        if not status["configured"]:
            missing.append(str(status["setting"]))
            if backend in COMMAND_BACKENDS:
                warnings.append(f"missing_command:{target}")
            else:
                warnings.append(f"missing_{target}_target_setting")

    if backend in {"sony_bravia", "roku_ecp"} and not str(data.get("tv_ip", "")).strip():
        missing.append("tv_ip")
        warnings.append("tv_ip_missing")
    if backend == "sony_bravia" and not str(data.get("sony_psk", "")).strip():
        missing.append("sony_psk")
        warnings.append("sony_psk_missing")
    if backend == "smartthings":
        metadata = smartthings_validation_metadata(data)
        warnings.extend(
            str(item) for item in cast("tuple[object, ...]", metadata.get("warnings", ()))
        )

    return sanitize_payload(
        {
            "backend": backend,
            "backend_supported": backend_supported,
            "backend_kind": backend_meta.get("kind", ""),
            "target_fields": fields,
            "missing": tuple(dict.fromkeys(missing)),
            "warnings": tuple(dict.fromkeys(warnings)),
            "ok": backend_supported and not missing and not warnings,
            "network_called": False,
            "dry_run_only": True,
            "hardware_validation_claimed": False,
        },
        data,
    )


def dry_run_selected_backend(
    settings: dict[str, object] | object | None, target: str = "oppo"
) -> dict[str, object]:
    """Describe the selected backend action without contacting hardware."""
    data = _settings_dict(settings)
    backend = selected_backend_id(data)
    target = "kodi" if target == "kodi" else "oppo"
    validation = validate_tv_settings(data)
    setting_key = target_setting_keys(data).get(target, "")
    configured = bool(setting_key and str(data.get(setting_key, "")).strip())
    return sanitize_payload(
        {
            "backend": backend,
            "target": target,
            "target_setting": setting_key,
            "target_configured": configured,
            "would_call_backend": bool(validation.get("backend_supported")) and configured,
            "network_called": False,
            "dry_run_only": True,
            "validation": validation,
            "hardware_validation_claimed": False,
        },
        data,
    )


def _run_switch_action(
    settings: dict[str, object] | object | None, target: str, switcher: Switcher | None = None
) -> dict[str, object]:
    """Run an explicit TV switch test action and sanitize the result."""
    data = _settings_dict(settings)
    backend = selected_backend_id(data)
    action = "switch_to_kodi" if target == "kodi" else "switch_to_oppo"
    selected_switcher = switcher or (
        tv_control.switch_to_kodi if target == "kodi" else tv_control.switch_to_oppo
    )
    result: dict[str, object] = {
        "action": action,
        "backend": backend,
        "ok": False,
        "nonfatal": True,
        "dry_run_only": False,
        "hardware_validation_claimed": False,
    }
    try:
        raw = selected_switcher(data)
        result.update({"ok": True, "result": raw})
    except Exception as exc:  # TV tests must remain non-fatal in support flows.
        result.update({"ok": False, "error": str(exc)})
    return sanitize_payload(result, data)


def test_switch_to_oppo(
    settings: dict[str, object] | object | None, switcher: Switcher | None = None
) -> dict[str, object]:
    """Explicitly test switching to the OPPO input; failures are non-fatal."""
    return _run_switch_action(settings, "oppo", switcher=switcher)


def test_switch_to_kodi(
    settings: dict[str, object] | object | None, switcher: Switcher | None = None
) -> dict[str, object]:
    """Explicitly test switching back to the Kodi input; failures are non-fatal."""
    return _run_switch_action(settings, "kodi", switcher=switcher)


def build_diagnostic_report(settings: dict[str, object] | object | None) -> dict[str, object]:
    """Build a sanitized TV switching diagnostic report without network IO."""
    data = _settings_dict(settings)
    return sanitize_payload(
        {
            "title": "OPPO203 TV Switching Diagnostic Report",
            "backend": selected_backend_id(data),
            "settings": sanitized_settings_summary(data),
            "validation": validate_tv_settings(data),
            "dry_run": {
                "oppo": dry_run_selected_backend(data, "oppo"),
                "kodi": dry_run_selected_backend(data, "kodi"),
            },
            "network_called": False,
            "hardware_validation_claimed": False,
        },
        data,
    )


def format_report(report: dict[str, object]) -> str:
    """Render a sanitized TV diagnostic report as support-friendly JSON text."""
    safe = sanitize_payload(report, report.get("settings") if isinstance(report, dict) else {})
    return json.dumps(safe, indent=2, sort_keys=True)


def _ts(now: float | Callable[[], float] | None = None) -> str:
    value = now() if callable(now) else (now if now is not None else _time.time())
    # UTC keeps exported diagnostic filenames deterministic across timezones.
    return _time.strftime("%Y%m%d-%H%M%S", _time.gmtime(value))


def default_report_path(root_dir: str, now: float | Callable[[], float] | None = None) -> str:
    """Return the default TV diagnostic report path under an add-on data dir."""
    return os.path.join(root_dir, f"tv-diagnostics-{_ts(now)}.json")


def save_report(
    report: dict[str, object],
    root_dir: str,
    *,
    now: float | Callable[[], float] | None = None,
    writer: Writer | None = None,
) -> str:
    """Save a sanitized TV switching diagnostic report and return the path."""
    path = default_report_path(root_dir, now=now)
    text = format_report(report)
    if writer is None:
        os.makedirs(root_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        writer(path, text)
    return path


def export_tv_diagnostic_report(
    settings: dict[str, object] | object | None,
    root_dir: str,
    *,
    now: float | Callable[[], float] | None = None,
    writer: Writer | None = None,
) -> str:
    """Build and save a sanitized TV diagnostic report."""
    return save_report(build_diagnostic_report(settings), root_dir, now=now, writer=writer)
