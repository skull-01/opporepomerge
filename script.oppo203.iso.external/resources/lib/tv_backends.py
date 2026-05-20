"""TV backend registry for v2.9.10 Build 9B.

The registry is intentionally data-oriented and side-effect free.  It describes
existing TV switching backends so later builds can add presets, diagnostics, and
new protocols without changing the established public TV control APIs.
"""
from __future__ import annotations

TV_BACKEND_ADB = "adb"
TV_BACKEND_SONY_BRAVIA = "sony_bravia"
TV_BACKEND_LG_COMMAND = "lg_command"
TV_BACKEND_SAMSUNG_COMMAND = "samsung_command"
TV_BACKEND_CUSTOM_COMMAND = "custom_command"
TV_BACKEND_ROKU_ECP = "roku_ecp"
TV_BACKEND_SMARTTHINGS = "smartthings"

PRESERVED_TV_BACKENDS = (
    TV_BACKEND_ADB,
    TV_BACKEND_SONY_BRAVIA,
    TV_BACKEND_LG_COMMAND,
    TV_BACKEND_SAMSUNG_COMMAND,
    TV_BACKEND_CUSTOM_COMMAND,
    TV_BACKEND_ROKU_ECP,
    TV_BACKEND_SMARTTHINGS,
)

TV_BACKEND_ALIASES = {
    "android_tv_adb": TV_BACKEND_ADB,
    "google_tv_adb": TV_BACKEND_ADB,
    "sony_ip": TV_BACKEND_SONY_BRAVIA,
    "sony_bravia_ip": TV_BACKEND_SONY_BRAVIA,
    "lg_webos_command": TV_BACKEND_LG_COMMAND,
    "samsung_local_command": TV_BACKEND_SAMSUNG_COMMAND,
    "generic_custom_command": TV_BACKEND_CUSTOM_COMMAND,
    "roku": TV_BACKEND_ROKU_ECP,
    "roku_tv": TV_BACKEND_ROKU_ECP,
    "tcl_roku_tv": TV_BACKEND_ROKU_ECP,
    "hisense_roku_tv": TV_BACKEND_ROKU_ECP,
    "samsung_smartthings": TV_BACKEND_SMARTTHINGS,
    "smartthings_experimental": TV_BACKEND_SMARTTHINGS,
}

TV_BACKENDS = {
    TV_BACKEND_ADB: {
        "id": TV_BACKEND_ADB,
        "label": "ADB / Android TV command backend",
        "kind": "adb_shell",
        "target_settings": {
            "oppo": "oppo_input_adb_shell",
            "kodi": "kodi_input_adb_shell",
        },
        "preserved_existing_backend": True,
        "nonfatal_in_playback_flow": True,
        "hardware_validation_required": True,
    },
    TV_BACKEND_SONY_BRAVIA: {
        "id": TV_BACKEND_SONY_BRAVIA,
        "label": "Sony Bravia IP control",
        "kind": "sony_bravia_ip",
        "target_settings": {
            "oppo": "sony_oppo_hdmi_port",
            "kodi": "sony_kodi_hdmi_port",
        },
        "preserved_existing_backend": True,
        "nonfatal_in_playback_flow": True,
        "hardware_validation_required": True,
    },
    TV_BACKEND_LG_COMMAND: {
        "id": TV_BACKEND_LG_COMMAND,
        "label": "LG editable command backend",
        "kind": "external_command",
        "target_settings": {
            "oppo": "lg_oppo_command",
            "kodi": "lg_kodi_command",
        },
        "preserved_existing_backend": True,
        "nonfatal_in_playback_flow": True,
        "hardware_validation_required": True,
    },
    TV_BACKEND_SAMSUNG_COMMAND: {
        "id": TV_BACKEND_SAMSUNG_COMMAND,
        "label": "Samsung editable command backend",
        "kind": "external_command",
        "target_settings": {
            "oppo": "samsung_oppo_command",
            "kodi": "samsung_kodi_command",
        },
        "preserved_existing_backend": True,
        "nonfatal_in_playback_flow": True,
        "hardware_validation_required": True,
    },
    TV_BACKEND_CUSTOM_COMMAND: {
        "id": TV_BACKEND_CUSTOM_COMMAND,
        "label": "Generic editable command backend",
        "kind": "external_command",
        "target_settings": {
            "oppo": "custom_oppo_command",
            "kodi": "custom_kodi_command",
        },
        "preserved_existing_backend": True,
        "nonfatal_in_playback_flow": True,
        "hardware_validation_required": True,
    },
    TV_BACKEND_ROKU_ECP: {
        "id": TV_BACKEND_ROKU_ECP,
        "label": "Roku TV ECP local input backend",
        "kind": "roku_ecp_http",
        "target_settings": {
            "oppo": "roku_oppo_key",
            "kodi": "roku_kodi_key",
        },
        "default_port": 8060,
        "request_method": "POST",
        "request_path_template": "/keypress/{key}",
        "key_allowlist_required": True,
        "preserved_existing_backend": False,
        "nonfatal_in_playback_flow": True,
        "hardware_validation_required": True,
    },
    TV_BACKEND_SMARTTHINGS: {
        "id": TV_BACKEND_SMARTTHINGS,
        "label": "Samsung SmartThings experimental guarded request backend",
        "kind": "smartthings_experimental_request_helper",
        "target_settings": {
            "oppo": "smartthings_oppo_input_id",
            "kodi": "smartthings_kodi_input_id",
        },
        "experimental": True,
        "requires_explicit_acknowledgement": True,
        "live_api_calls_enabled": True,
        "request_helper_available": True,
        "fake_api_tested": True,
        "token_redaction_required": True,
        "token_setting": "smartthings_token",
        "device_id_setting": "smartthings_device_id",
        "preserved_existing_backend": False,
        "nonfatal_in_playback_flow": True,
        "hardware_validation_required": True,
    },
}


def normalize_backend_id(backend_id: str) -> str:
    """Normalize a backend identifier while preserving unknown values."""
    if not isinstance(backend_id, str):
        return TV_BACKEND_ADB
    stripped = backend_id.strip()
    if stripped in TV_BACKENDS:
        return stripped
    return TV_BACKEND_ALIASES.get(stripped.lower(), stripped)


def is_supported_backend(backend_id: str) -> bool:
    """Return whether the backend is known to the TV backend registry."""
    return normalize_backend_id(backend_id) in TV_BACKENDS


def get_backend(backend_id: str, default: dict[str, object] | None = None) -> dict[str, object]:
    """Return a copy of backend metadata without exposing mutable registry data."""
    canonical = normalize_backend_id(backend_id)
    if canonical in TV_BACKENDS:
        return dict(TV_BACKENDS[canonical])
    return dict(default or {})


def list_backends() -> tuple[str, ...]:
    """Return existing backend identifiers in stable UI/documentation order."""
    return PRESERVED_TV_BACKENDS


def backend_target_setting(backend_id: str, target: str) -> str:
    """Return the setting key used by a backend for an OPPO/Kodi target."""
    backend = get_backend(backend_id)
    targets = backend.get("target_settings") or {}
    if not isinstance(targets, dict):
        return ""
    return str(targets.get(target, ""))


def registry_summary() -> dict[str, object]:
    """Return a compact summary for tests, audit, and diagnostics."""
    return {
        "backends": list_backends(),
        "backend_count": len(TV_BACKENDS),
        "preserved_public_apis": ("switch_to_oppo(settings)", "switch_to_kodi(settings)"),
        "nonfatal_in_playback_flow": True,
        "runtime_behavior_changed": False,
        "hardware_validation_claimed": False,
    }
