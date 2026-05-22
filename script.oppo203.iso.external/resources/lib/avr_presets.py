"""AVR preset registry for v2.9.10 Build 15B.

The registry describes AVR families while keeping control disabled by default.
Denon/Marantz, Yamaha MusicCast/YXC, and Onkyo/Integra/Pioneer eISCP have guarded
software drivers; Sony now has an experimental acknowledgement-gated request helper; hardware evidence is still required before claiming validation.
"""

from __future__ import annotations

try:
    from .avr_types import (
        AVR_BACKEND_DENON_MARANTZ,
        AVR_BACKEND_DISABLED,
        AVR_BACKEND_ONKYO_EISCP,
        AVR_BACKEND_PIONEER_EISCP,
        AVR_BACKEND_SONY_AUDIO_API,
        AVR_BACKEND_YAMAHA_YXC,
    )
except ImportError:  # top-level/audit/test compatibility
    from avr_types import (  # type: ignore
        AVR_BACKEND_DENON_MARANTZ,
        AVR_BACKEND_DISABLED,
        AVR_BACKEND_ONKYO_EISCP,
        AVR_BACKEND_PIONEER_EISCP,
        AVR_BACKEND_SONY_AUDIO_API,
        AVR_BACKEND_YAMAHA_YXC,
    )

AVR_PRESETS: dict[str, dict[str, object]] = {
    "disabled": {
        "id": "disabled",
        "label": "AVR control disabled",
        "backend": AVR_BACKEND_DISABLED,
        "software_support_level": "no_op_default",
        "driver_available": False,
        "enabled_by_default": False,
        "power_off_enabled_by_default": False,
        "volume_automation_enabled_by_default": False,
        "hardware_validation_claimed": False,
        "notes": "Default safe path; no AVR commands are executed.",
    },
    "denon_marantz": {
        "id": "denon_marantz",
        "label": "Denon / Marantz AVR",
        "backend": AVR_BACKEND_DENON_MARANTZ,
        "software_support_level": "software_driver_build12",
        "driver_available": True,
        "default_port": 23,
        "protocol": "telnet_style_commands",
        "power_on_command": "PWON",
        "input_select_prefix": "SI",
        "query_commands": ("PW?", "SI?"),
        "opens_socket_per_command": True,
        "nonfatal_failures": True,
        "hardware_validation_claimed": False,
    },
    "yamaha_yxc": {
        "id": "yamaha_yxc",
        "label": "Yamaha MusicCast / YXC AVR",
        "backend": AVR_BACKEND_YAMAHA_YXC,
        "software_support_level": "software_driver_build13",
        "driver_available": True,
        "default_port": 80,
        "protocol": "http_yxc",
        "power_on_endpoint": "/YamahaExtendedControl/v1/main/setPower?power=on",
        "input_select_endpoint": "/YamahaExtendedControl/v1/main/setInput?input=<input>",
        "status_endpoint": "/YamahaExtendedControl/v1/main/getStatus",
        "http_method": "GET",
        "parses_json_response_code": True,
        "nonfatal_failures": True,
        "hardware_validation_claimed": False,
    },
    "onkyo_eiscp": {
        "id": "onkyo_eiscp",
        "label": "Onkyo / Integra eISCP AVR",
        "backend": AVR_BACKEND_ONKYO_EISCP,
        "software_support_level": "software_driver_build14",
        "driver_available": True,
        "default_port": 60128,
        "protocol": "eiscp",
        "frame_magic": "ISCP",
        "power_on_payload": "!1PWR01",
        "input_select_prefix": "!1SLI",
        "opens_socket_per_command": True,
        "nonfatal_failures": True,
        "hardware_validation_claimed": False,
    },
    "pioneer_eiscp": {
        "id": "pioneer_eiscp",
        "label": "Pioneer eISCP-compatible AVR",
        "backend": AVR_BACKEND_PIONEER_EISCP,
        "software_support_level": "experimental_software_driver_build14",
        "driver_available": True,
        "default_port": 60128,
        "protocol": "eiscp_experimental",
        "frame_magic": "ISCP",
        "power_on_payload": "!1PWR01",
        "input_select_prefix": "!1SLI",
        "opens_socket_per_command": True,
        "nonfatal_failures": True,
        "experimental": True,
        "hardware_validation_claimed": False,
    },
    "sony_audio_api": {
        "id": "sony_audio_api",
        "label": "Sony Audio Control API AVR",
        "backend": AVR_BACKEND_SONY_AUDIO_API,
        "software_support_level": "experimental_request_helper_build15b",
        "driver_available": True,
        "skeleton_available": True,
        "live_api_calls_enabled": True,
        "request_helper_available": True,
        "protocol": "json_http_experimental",
        "requires_experimental_acknowledgement": True,
        "sensitive_fields": (
            "sony_avr_psk",
            "sony_avr_player_input_uri",
            "sony_avr_restore_input_uri",
        ),
        "hardware_validation_claimed": False,
        "experimental_skeleton_families": (),
        "experimental_request_helper_families": (AVR_BACKEND_SONY_AUDIO_API,),
    },
}


def normalize_avr_backend(backend: object) -> str:
    value = "" if backend is None else str(backend).strip().lower().replace("-", "_")
    aliases = {
        "": AVR_BACKEND_DISABLED,
        "none": AVR_BACKEND_DISABLED,
        "off": AVR_BACKEND_DISABLED,
        "disabled": AVR_BACKEND_DISABLED,
        "denon": AVR_BACKEND_DENON_MARANTZ,
        "marantz": AVR_BACKEND_DENON_MARANTZ,
        "denon_marantz": AVR_BACKEND_DENON_MARANTZ,
        "yamaha": AVR_BACKEND_YAMAHA_YXC,
        "yamaha_yxc": AVR_BACKEND_YAMAHA_YXC,
        "musiccast": AVR_BACKEND_YAMAHA_YXC,
        "onkyo": AVR_BACKEND_ONKYO_EISCP,
        "integra": AVR_BACKEND_ONKYO_EISCP,
        "onkyo_eiscp": AVR_BACKEND_ONKYO_EISCP,
        "pioneer": AVR_BACKEND_PIONEER_EISCP,
        "pioneer_eiscp": AVR_BACKEND_PIONEER_EISCP,
        "sony": AVR_BACKEND_SONY_AUDIO_API,
        "sony_audio": AVR_BACKEND_SONY_AUDIO_API,
        "sony_audio_api": AVR_BACKEND_SONY_AUDIO_API,
    }
    return aliases.get(value, value)


def list_avr_presets() -> tuple[str, ...]:
    return tuple(sorted(AVR_PRESETS))


def get_avr_preset(
    preset_id: object, default: dict[str, object] | None = None
) -> dict[str, object]:
    preset = AVR_PRESETS.get(normalize_avr_backend(preset_id))
    if preset is None:
        return dict(default or {})
    return dict(preset)


def avr_support_summary() -> dict[str, object]:
    return {
        "presets": list_avr_presets(),
        "enabled_by_default": False,
        "power_off_enabled_by_default": False,
        "volume_automation_enabled_by_default": False,
        "driver_execution_added": True,
        "driver_execution_families": (
            AVR_BACKEND_DENON_MARANTZ,
            AVR_BACKEND_YAMAHA_YXC,
            AVR_BACKEND_ONKYO_EISCP,
            AVR_BACKEND_PIONEER_EISCP,
            AVR_BACKEND_SONY_AUDIO_API,
        ),
        "playback_sequencing_hooked": True,
        "hardware_validation_claimed": False,
        "experimental_skeleton_families": (),
        "experimental_request_helper_families": (AVR_BACKEND_SONY_AUDIO_API,),
    }
