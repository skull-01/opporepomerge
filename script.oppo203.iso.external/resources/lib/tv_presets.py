"""TV preset registry for v2.9.10 Build 9B.

Build 9B preserves SmartThings experimental preset/backend metadata and adds
guarded request-helper metadata with fake API coverage. Presets do not perform hardware IO, do not apply
commands automatically, and do not claim hardware validation.
"""
from __future__ import annotations

try:
    from .tv_backends import (
        TV_BACKEND_ADB,
        TV_BACKEND_CUSTOM_COMMAND,
        TV_BACKEND_LG_COMMAND,
        TV_BACKEND_SAMSUNG_COMMAND,
        TV_BACKEND_SONY_BRAVIA,
        TV_BACKEND_ROKU_ECP,
        TV_BACKEND_SMARTTHINGS,
        is_supported_backend,
    )
except ImportError:  # top-level/audit/test compatibility
    from tv_backends import (  # type: ignore
        TV_BACKEND_ADB,
        TV_BACKEND_CUSTOM_COMMAND,
        TV_BACKEND_LG_COMMAND,
        TV_BACKEND_SAMSUNG_COMMAND,
        TV_BACKEND_SONY_BRAVIA,
        TV_BACKEND_ROKU_ECP,
        TV_BACKEND_SMARTTHINGS,
        is_supported_backend,
    )

ADB_COMMAND_FIELDS = ("oppo_input_adb_shell", "kodi_input_adb_shell")
ROKU_ECP_COMMAND_FIELDS = ("roku_oppo_key", "roku_kodi_key")
LG_COMMAND_FIELDS = ("lg_oppo_command", "lg_kodi_command")
SAMSUNG_COMMAND_FIELDS = ("samsung_oppo_command", "samsung_kodi_command")
CUSTOM_COMMAND_FIELDS = ("custom_oppo_command", "custom_kodi_command")
SMARTTHINGS_COMMAND_FIELDS = ("smartthings_oppo_input_id", "smartthings_kodi_input_id")

ANDROID_GOOGLE_TV_PRESET_IDS = (
    "tcl_android_tv",
    "sony_android_tv",
    "hisense_android_tv",
    "philips_android_tv",
    "xiaomi_android_tv",
    "sharp_android_tv",
    "skyworth_android_tv",
    "haier_android_tv",
    "generic_android_tv",
)

ROKU_TV_PRESET_IDS = (
    "roku_tv",
    "tcl_roku_tv",
    "hisense_roku_tv",
    "generic_roku_tv",
)

COMMAND_TV_PRESET_IDS = (
    "lg_webos_command",
    "samsung_command",
    "panasonic_custom_command",
    "vizio_custom_command",
    "generic_custom_command",
)

SMARTTHINGS_EXPERIMENTAL_PRESET_IDS = (
    "samsung_smartthings_experimental",
    "generic_smartthings_experimental",
)



def _command_preset(
    preset_id: str,
    label: str,
    backend: str,
    platform: str,
    command_fields: tuple[str, str],
    notes: str,
) -> dict[str, object]:
    """Return software-only editable command/custom preset metadata."""
    return {
        "id": preset_id,
        "label": label,
        "backend": backend,
        "platform": platform,
        "editable": True,
        "software_preset_only": True,
        "hardware_validation_required": True,
        "hardware_validation_claimed": False,
        "command_fields": command_fields,
        "command_template_editable": True,
        "tv_ip_placeholder_supported": True,
        "missing_command_validation_warning": True,
        "native_protocol_added": False,
        "nonfatal_in_playback_flow": True,
        "notes": notes,
    }

def _smartthings_preset(preset_id: str, label: str, platform: str, notes: str) -> dict[str, object]:
    """Return software-only SmartThings experimental preset metadata."""
    return {
        "id": preset_id,
        "label": label,
        "backend": TV_BACKEND_SMARTTHINGS,
        "platform": platform,
        "editable": True,
        "software_preset_only": True,
        "hardware_validation_required": True,
        "hardware_validation_claimed": False,
        "experimental": True,
        "requires_explicit_acknowledgement": True,
        "acknowledgement_setting": "smartthings_experimental_acknowledged",
        "live_api_calls_enabled": True,
        "request_helper_available": True,
        "fake_api_tested": True,
        "token_redaction_required": True,
        "token_setting": "smartthings_token",
        "device_id_setting": "smartthings_device_id",
        "command_fields": SMARTTHINGS_COMMAND_FIELDS,
        "nonfatal_in_playback_flow": True,
        "notes": notes,
    }

def _roku_preset(preset_id: str, label: str, platform: str, notes: str) -> dict[str, object]:
    """Return software-only Roku ECP preset metadata."""
    return {
        "id": preset_id,
        "label": label,
        "backend": TV_BACKEND_ROKU_ECP,
        "platform": platform,
        "editable": True,
        "software_preset_only": True,
        "hardware_validation_required": True,
        "hardware_validation_claimed": False,
        "command_fields": ROKU_ECP_COMMAND_FIELDS,
        "default_port": 8060,
        "request_method": "POST",
        "request_path_template": "/keypress/{key}",
        "key_allowlist_required": True,
        "notes": notes,
    }

def _adb_preset(preset_id: str, label: str, platform: str, notes: str) -> dict[str, object]:
    """Return software-only editable ADB preset metadata."""
    return {
        "id": preset_id,
        "label": label,
        "backend": TV_BACKEND_ADB,
        "platform": platform,
        "editable": True,
        "software_preset_only": True,
        "hardware_validation_required": True,
        "hardware_validation_claimed": False,
        "command_fields": ADB_COMMAND_FIELDS,
        "adb_command_scope": "model_specific_editable",
        "universal_hdmi_command_claimed": False,
        "notes": notes,
    }


TV_PRESETS = {
    "adb_existing": {
        "id": "adb_existing",
        "label": "Existing editable ADB TV switching",
        "backend": TV_BACKEND_ADB,
        "platform": "Android TV / Google TV / ADB-capable TV",
        "editable": True,
        "software_preset_only": True,
        "hardware_validation_required": True,
        "hardware_validation_claimed": False,
        "command_fields": ADB_COMMAND_FIELDS,
        "adb_command_scope": "user_existing_editable",
        "universal_hdmi_command_claimed": False,
        "notes": "Preserves existing editable ADB command fields.",
    },
    "tcl_android_tv": _adb_preset(
        "tcl_android_tv",
        "TCL Android TV / Google TV editable ADB preset",
        "TCL Android TV / Google TV",
        "Editable ADB preset; existing TCL command values remain user-reviewable and hardware validation is required.",
    ),
    "sony_android_tv": _adb_preset(
        "sony_android_tv",
        "Sony Android TV / Google TV editable ADB preset",
        "Sony Android TV / Google TV",
        "Editable ADB preset for Sony Android/Google TV models; HDMI/input commands are model-specific until tested.",
    ),
    "hisense_android_tv": _adb_preset(
        "hisense_android_tv",
        "Hisense Android TV / Google TV editable ADB preset",
        "Hisense Android TV / Google TV",
        "Editable ADB preset for Hisense Android/Google TV models; commands must be reviewed for the target model.",
    ),
    "philips_android_tv": _adb_preset(
        "philips_android_tv",
        "Philips Android TV / Google TV editable ADB preset",
        "Philips Android TV / Google TV",
        "Editable ADB preset for Philips Android/Google TV models; no universal HDMI command is claimed.",
    ),
    "xiaomi_android_tv": _adb_preset(
        "xiaomi_android_tv",
        "Xiaomi Android TV / Google TV editable ADB preset",
        "Xiaomi Android TV / Google TV",
        "Editable ADB preset for Xiaomi/Mi Android TV models; verify and edit commands before hardware use.",
    ),
    "sharp_android_tv": _adb_preset(
        "sharp_android_tv",
        "Sharp Android TV editable ADB preset",
        "Sharp Android TV",
        "Editable ADB preset for Sharp Android TV models; HDMI/input command behavior remains hardware-owned.",
    ),
    "skyworth_android_tv": _adb_preset(
        "skyworth_android_tv",
        "Skyworth / Coocaa Android TV editable ADB preset",
        "Skyworth / Coocaa Android TV",
        "Editable ADB preset for Skyworth/Coocaa Android TV models; commands remain user-editable.",
    ),
    "haier_android_tv": _adb_preset(
        "haier_android_tv",
        "Haier Android TV editable ADB preset",
        "Haier Android TV",
        "Editable ADB preset for Haier Android TV models; hardware validation is required before support is claimed.",
    ),
    "generic_android_tv": _adb_preset(
        "generic_android_tv",
        "Generic Android TV / Google TV editable ADB preset",
        "Generic Android TV / Google TV",
        "Generic editable ADB preset for unsupported Android/Google TV models; commands are intentionally user-owned.",
    ),

    "roku_tv": _roku_preset(
        "roku_tv",
        "Roku TV editable ECP preset",
        "Roku TV",
        "Software-only Roku ECP preset using local HTTP POST /keypress/<key> with allowlisted input keys.",
    ),
    "tcl_roku_tv": _roku_preset(
        "tcl_roku_tv",
        "TCL Roku TV editable ECP preset",
        "TCL Roku TV",
        "Editable Roku ECP preset for TCL Roku TV models; local control must be enabled and hardware validation is required.",
    ),
    "hisense_roku_tv": _roku_preset(
        "hisense_roku_tv",
        "Hisense Roku TV editable ECP preset",
        "Hisense Roku TV",
        "Editable Roku ECP preset for Hisense Roku TV models; input keys remain user-reviewable.",
    ),
    "generic_roku_tv": _roku_preset(
        "generic_roku_tv",
        "Generic Roku TV editable ECP preset",
        "Generic Roku TV",
        "Generic software-only Roku ECP preset for other Roku TV brands; no hardware validation is claimed.",
    ),

    "samsung_smartthings_experimental": _smartthings_preset(
        "samsung_smartthings_experimental",
        "Samsung SmartThings experimental preset",
        "Samsung SmartThings",
        "Experimental SmartThings preset. Requires explicit acknowledgement; Build 9B adds a guarded request helper covered by fake API tests.",
    ),
    "generic_smartthings_experimental": _smartthings_preset(
        "generic_smartthings_experimental",
        "Generic SmartThings experimental preset",
        "SmartThings-compatible TV",
        "Experimental metadata-only preset for future SmartThings testing. Token values must be redacted and hardware validation is not claimed.",
    ),
    "sony_bravia_ip": {
        "id": "sony_bravia_ip",
        "label": "Sony Bravia IP control",
        "backend": TV_BACKEND_SONY_BRAVIA,
        "platform": "Sony Bravia IP",
        "editable": True,
        "software_preset_only": True,
        "hardware_validation_required": True,
        "hardware_validation_claimed": False,
        "notes": "Preserves existing PSK/HDMI-port based Sony backend.",
    },
    "lg_webos_command": _command_preset(
        "lg_webos_command",
        "LG webOS editable command preset",
        TV_BACKEND_LG_COMMAND,
        "LG webOS command-line helper",
        LG_COMMAND_FIELDS,
        "Editable command preset using the existing lg_command backend; {tv_ip} placeholder behavior is preserved where used.",
    ),
    "lg_command_existing": _command_preset(
        "lg_command_existing",
        "LG existing editable command compatibility preset",
        TV_BACKEND_LG_COMMAND,
        "LG webOS command-line helper",
        LG_COMMAND_FIELDS,
        "Compatibility alias preserving existing lg_command fields for older setups.",
    ),
    "samsung_command": _command_preset(
        "samsung_command",
        "Samsung editable command preset",
        TV_BACKEND_SAMSUNG_COMMAND,
        "Samsung local/custom command",
        SAMSUNG_COMMAND_FIELDS,
        "Editable command preset using the existing samsung_command backend; {tv_ip} placeholder behavior is preserved.",
    ),
    "samsung_command_existing": _command_preset(
        "samsung_command_existing",
        "Samsung existing editable command compatibility preset",
        TV_BACKEND_SAMSUNG_COMMAND,
        "Samsung local/custom command",
        SAMSUNG_COMMAND_FIELDS,
        "Compatibility alias preserving existing samsung_command fields for older setups.",
    ),
    "panasonic_custom_command": _command_preset(
        "panasonic_custom_command",
        "Panasonic editable custom command preset",
        TV_BACKEND_CUSTOM_COMMAND,
        "Panasonic custom command",
        CUSTOM_COMMAND_FIELDS,
        "Software-only custom-command preset for Panasonic TVs; no native Panasonic protocol is added.",
    ),
    "vizio_custom_command": _command_preset(
        "vizio_custom_command",
        "Vizio editable custom command preset",
        TV_BACKEND_CUSTOM_COMMAND,
        "Vizio custom command",
        CUSTOM_COMMAND_FIELDS,
        "Software-only custom-command preset for Vizio TVs; no native Vizio protocol is added.",
    ),
    "generic_custom_command": _command_preset(
        "generic_custom_command",
        "Generic editable custom command preset",
        TV_BACKEND_CUSTOM_COMMAND,
        "Generic unsupported/custom TV",
        CUSTOM_COMMAND_FIELDS,
        "Escape hatch for user-owned command templates; missing command values should produce validation warnings before use.",
    ),
}


def list_presets() -> tuple[str, ...]:
    """Return preset IDs in stable documentation order."""
    return tuple(TV_PRESETS)


def list_android_google_tv_presets() -> tuple[str, ...]:
    """Return Build 6 Android / Google TV ADB preset IDs."""
    return ANDROID_GOOGLE_TV_PRESET_IDS


def list_roku_tv_presets() -> tuple[str, ...]:
    """Return Build 7 Roku TV ECP preset IDs."""
    return ROKU_TV_PRESET_IDS


def list_command_tv_presets() -> tuple[str, ...]:
    """Return Build 8 command/custom TV preset IDs."""
    return COMMAND_TV_PRESET_IDS


def list_smartthings_experimental_presets() -> tuple[str, ...]:
    """Return Build 9B SmartThings experimental preset IDs."""
    return SMARTTHINGS_EXPERIMENTAL_PRESET_IDS


def get_preset(preset_id: str, default: dict[str, object] | None = None) -> dict[str, object]:
    """Return a copy of one preset without exposing mutable registry data."""
    if not isinstance(preset_id, str):
        return dict(default or {})
    preset = TV_PRESETS.get(preset_id.strip())
    return dict(preset) if preset else dict(default or {})


def presets_for_backend(backend_id: str) -> tuple[str, ...]:
    """Return preset IDs using a backend."""
    return tuple(pid for pid, preset in TV_PRESETS.items() if preset.get("backend") == backend_id)


def validate_preset_registry() -> list[str]:
    """Return registry warnings without raising or touching hardware."""
    warnings: list[str] = []
    for preset_id, preset in TV_PRESETS.items():
        backend = str(preset.get("backend", ""))
        if not is_supported_backend(backend):
            warnings.append(f"preset:{preset_id}:unsupported_backend:{backend}")
        if not preset.get("editable"):
            warnings.append(f"preset:{preset_id}:not_editable")
        if preset_id in ANDROID_GOOGLE_TV_PRESET_IDS and backend != TV_BACKEND_ADB:
            warnings.append(f"preset:{preset_id}:android_google_tv_not_adb:{backend}")
        if preset.get("universal_hdmi_command_claimed"):
            warnings.append(f"preset:{preset_id}:universal_hdmi_command_claimed")
        if preset_id in ROKU_TV_PRESET_IDS and backend != TV_BACKEND_ROKU_ECP:
            warnings.append(f"preset:{preset_id}:roku_tv_not_roku_ecp:{backend}")
        if backend == TV_BACKEND_ROKU_ECP and not preset.get("key_allowlist_required"):
            warnings.append(f"preset:{preset_id}:roku_ecp_without_key_allowlist")
        if preset_id in SMARTTHINGS_EXPERIMENTAL_PRESET_IDS:
            if backend != TV_BACKEND_SMARTTHINGS:
                warnings.append(f"preset:{preset_id}:smartthings_not_smartthings_backend:{backend}")
            if not preset.get("experimental"):
                warnings.append(f"preset:{preset_id}:smartthings_not_experimental")
            if not preset.get("requires_explicit_acknowledgement"):
                warnings.append(f"preset:{preset_id}:smartthings_acknowledgement_not_required")
            if not preset.get("live_api_calls_enabled"):
                warnings.append(f"preset:{preset_id}:smartthings_live_api_disabled_in_9b")
            if not preset.get("request_helper_available"):
                warnings.append(f"preset:{preset_id}:smartthings_request_helper_unavailable")
            if not preset.get("token_redaction_required"):
                warnings.append(f"preset:{preset_id}:smartthings_token_redaction_not_required")
        if preset_id in COMMAND_TV_PRESET_IDS:
            if backend not in (TV_BACKEND_LG_COMMAND, TV_BACKEND_SAMSUNG_COMMAND, TV_BACKEND_CUSTOM_COMMAND):
                warnings.append(f"preset:{preset_id}:command_tv_unexpected_backend:{backend}")
            if not preset.get("command_template_editable"):
                warnings.append(f"preset:{preset_id}:command_template_not_editable")
            if not preset.get("missing_command_validation_warning"):
                warnings.append(f"preset:{preset_id}:missing_command_warning_absent")
            if preset.get("native_protocol_added"):
                warnings.append(f"preset:{preset_id}:native_protocol_added")
    return warnings


def android_google_tv_support_matrix() -> tuple[dict[str, object], ...]:
    """Return Build 6 Android/Google TV software preset support records."""
    return tuple(get_preset(preset_id) for preset_id in ANDROID_GOOGLE_TV_PRESET_IDS)


def roku_tv_support_matrix() -> tuple[dict[str, object], ...]:
    """Return Build 7 Roku TV ECP software preset support records."""
    return tuple(get_preset(preset_id) for preset_id in ROKU_TV_PRESET_IDS)


def command_tv_support_matrix() -> tuple[dict[str, object], ...]:
    """Return Build 8 command/custom TV software preset support records."""
    return tuple(get_preset(preset_id) for preset_id in COMMAND_TV_PRESET_IDS)


def smartthings_experimental_support_matrix() -> tuple[dict[str, object], ...]:
    """Return Build 9B SmartThings experimental support records."""
    return tuple(get_preset(preset_id) for preset_id in SMARTTHINGS_EXPERIMENTAL_PRESET_IDS)


def preset_registry_summary() -> dict[str, object]:
    """Return a compact summary for diagnostics and audit tests."""
    return {
        "preset_count": len(TV_PRESETS),
        "preset_ids": list_presets(),
        "android_google_tv_preset_count": len(ANDROID_GOOGLE_TV_PRESET_IDS),
        "android_google_tv_preset_ids": list_android_google_tv_presets(),
        "roku_tv_preset_count": len(ROKU_TV_PRESET_IDS),
        "roku_tv_preset_ids": list_roku_tv_presets(),
        "command_tv_preset_count": len(COMMAND_TV_PRESET_IDS),
        "command_tv_preset_ids": list_command_tv_presets(),
        "smartthings_experimental_preset_count": len(SMARTTHINGS_EXPERIMENTAL_PRESET_IDS),
        "smartthings_experimental_preset_ids": list_smartthings_experimental_presets(),
        "backends": tuple(sorted({str(preset.get("backend")) for preset in TV_PRESETS.values()})),
        "validation_warnings": tuple(validate_preset_registry()),
        "software_preset_only": True,
        "hardware_validation_claimed": False,
        "universal_hdmi_command_claimed": False,
    }
