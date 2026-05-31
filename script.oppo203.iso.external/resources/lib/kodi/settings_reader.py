from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from typing import Any, cast

try:
    from ..oppo.command_map import load_default_command_map_json
    from .settings_schema import SettingIssue, build_default_schema
except ImportError:  # top-level/audit import compatibility
    from command_map import load_default_command_map_json  # type: ignore
    from settings_schema import SettingIssue, build_default_schema  # type: ignore


# v2.5.0 Build 2: conservative stability/validation helpers.
# These helpers are intentionally dependency-free so they can be used by
# service, external-player, wizard, and tests without importing Kodi modules.


DEFAULTS = {
    "python_path": "/usr/bin/python3",
    "oppo_ip": "192.168.1.50",
    "oppo_port": "23",
    "oppo_socket_timeout": "3.0",
    "oppo_start_mode": "tcp_commands",
    "oppo_start_commands": "#PON\n#PLA",
    "oppo_stop_commands": "#STP",
    "oppo_command_delay": "0.1",
    "oppo_already_on_mode": "false",
    "oppo_mac": "",
    "oppo_use_wol": "false",
    "kodi_startup_power_on": "false",
    "kodi_startup_power_on_delay": "5",
    "kodi_startup_power_on_retries": "3",
    "kodi_startup_power_on_use_wol": "true",
    "wizard_mode": "basic",
    "oppo_wol_broadcast": "255.255.255.255",
    "oppo_http_port": "436",
    "oppo_http_activate": "true",
    "oppo_http_broadcast": "255.255.255.255",
    "oppo_http_path_from": "",
    "oppo_http_path_to": "",
    "oppo_http_urlencode_path": "true",
    "oppo_http_disc_folder_root": "true",
    "remote_bridge_only_when_active": "true",
    # v0.9.0/v2.9.1 Build 3: canonical OPPO remote command map.
    # The data lives in resources/data/oppo_command_map.json and is exposed here
    # as compact JSON for backward compatibility with existing settings callers.
    "oppo_remote_command_map": load_default_command_map_json(),
    "tv_backend": "adb",
    "selected_tv_preset_id": "",
    "tv_switching_enabled": "true",
    "adb_path": "adb",
    "tv_ip": "192.168.1.60",
    "tv_adb_port": "5555",
    "adb_connect_before_switch": "true",
    "oppo_input_adb_shell": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW15 -n com.tcl.tv/.TVActivity -f 0x10000000",
    "kodi_input_adb_shell": "am start -a android.intent.action.VIEW -d content://com.tcl.tvpassthrough/.TvPassThroughService/HW16 -n com.tcl.tv/.TVActivity -f 0x10000000",
    "sony_psk": "",
    "sony_oppo_hdmi_port": "1",
    "sony_kodi_hdmi_port": "2",
    "lg_oppo_command": "lgtv --ssl setInput HDMI_1",
    "lg_kodi_command": "lgtv --ssl setInput HDMI_2",
    "samsung_oppo_command": "samsungctl --host {tv_ip} KEY_HDMI",
    "samsung_kodi_command": "samsungctl --host {tv_ip} KEY_HDMI",
    "custom_oppo_command": "",
    "custom_kodi_command": "",
    "roku_ecp_port": "8060",
    "roku_oppo_key": "InputHDMI1",
    "roku_kodi_key": "InputHDMI2",
    "smartthings_experimental_acknowledged": "false",
    "smartthings_token": "",
    "smartthings_device_id": "",
    "smartthings_oppo_input_id": "",
    "smartthings_kodi_input_id": "",
    "smartthings_api_base_url": "https://api.smartthings.com/v1",
    "avr_control_enabled": "false",
    "avr_backend": "disabled",
    "selected_avr_preset_id": "disabled",
    "avr_host": "",
    "avr_port": "",
    "avr_player_input": "",
    "avr_restore_enabled": "false",
    "avr_restore_input": "",
    "avr_power_on_enabled": "false",
    "avr_power_off_enabled": "false",
    "avr_volume_automation_enabled": "false",
    "avr_sound_mode": "",
    "sony_avr_experimental_acknowledged": "false",
    "sony_avr_psk": "",
    "sony_avr_api_path": "/sony/audio",
    "sony_avr_player_input_uri": "",
    "sony_avr_restore_input_uri": "",
    "fast_changeover": "true",
    "include_disc_folder_rules": "true",
    "startup_delay": "0",
    "hold_mode": "tcp_qpl_poll",
    "fixed_timeout_minutes": "180",
    "manual_stop_file": "/tmp/oppo203_iso_stop",
    "http_poll_interval": "5",
    "http_poll_timeout_minutes": "240",
    "http_poll_idle_confirmations": "2",
    "switch_back_on_exit": "true",
    # v0.8.0 new settings
    "oppo_verbose_mode": "0",
    "oppo_preflight_enabled": "false",
    "oppo_http_payload_mode": "raw_path",
    "oppo_http_app_device_type": "2",
    "oppo_http_media_type": "1",
    "playback_architecture": "external_player",
    "architecture_choice_made": "false",
    "tv_adb_preset": "",
    "qpl_poll_interval": "3",
    "qpl_poll_timeout_minutes": "240",
    "qpl_poll_idle_confirmations": "2",
    # v0.9.0 new settings
    "trickplay_suppress_seconds": "45",
    "verbose_push_timeout_minutes": "240",
    "oppo_experimental_filelist_enabled": "false",
    "oppo_hardware_model": "udp_203",
    "oppo_jailbreak_enabled": "false",
    "oppo_autoscript_shell_handler": "false",
    "oppo_firmware_version": "",
    "nas_playback_confirmed": "false",
    "nas_playback_family": "auto",
}


ENUM_VALUES = {
    "oppo_start_mode": ["tcp_commands", "http_api", "tcp_then_http"],
    "tv_backend": [
        "adb",
        "sony_bravia",
        "lg_command",
        "samsung_command",
        "custom_command",
        "roku_ecp",
        "smartthings",
    ],
    "avr_backend": [
        "disabled",
        "denon_marantz",
        "yamaha_yxc",
        "onkyo_eiscp",
        "pioneer_eiscp",
        "sony_audio_api",
    ],
    "hold_mode": ["fixed_timeout", "manual_file", "http_poll", "tcp_qpl_poll", "verbose_push"],
    "oppo_verbose_mode": ["0", "2", "3"],
    "oppo_http_payload_mode": ["raw_path", "json_payload"],
    "playback_architecture": ["external_player", "service_interception"],
    "oppo_hardware_model": [
        "udp_203",
        "udp_205",
        "chinoppo_m9201",
        "chinoppo_m9203",
        "chinoppo_m9205c",
        "chinoppo_m9702",
        "ipuk_uhd8592",
        "giec_bdp_g5300",
        "magnetar_udp800",
        "reavon_ubrx100",
        "reavon_ubrx110",
        "reavon_ubrx200",
        "chinoppo_m9200",
        "chinoppo_m9205",
        "cineultra_v203",
        "cineultra_v204",
        "magnetar_udp900",
        "chinoppo_m9205_v1",
    ],
}


# v2.9.1 Build 9: lightweight typed settings schema.
SETTINGS_SCHEMA = build_default_schema(DEFAULTS, ENUM_VALUES)


def _setting_text(value: object, default: object = "") -> str:
    """Return text for a setting value while preserving legacy fallback safety.

    Some legacy tests and partially corrupted settings objects may provide
    values whose ``__str__`` raises.  Keep that edge isolated here so normal
    parsers can catch narrow conversion exceptions instead of broad
    ``Exception`` around every conversion.
    """
    try:
        return str(default) if value is None else str(value)
    except Exception:
        return str(default)


def _settings_items(data: Any) -> Iterable[tuple[Any, Any]]:
    """Return key/value pairs for a mapping-like settings object."""
    try:
        return dict(data).items()
    except (TypeError, ValueError, AttributeError):
        return []


class Settings:
    def __init__(self, data: Mapping[str, object]) -> None:
        merged: dict[str, object] = dict(DEFAULTS)
        merged.update({k: v for k, v in data.items() if v is not None})
        self.data = merged

    def get(self, key: str, default: object = None) -> Any:
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def get_bool(self, key: str, default: bool = False) -> bool:
        raw = self.get(key, default)
        if raw is None:
            return bool(default)
        if isinstance(raw, bool):
            return raw
        value = _setting_text(raw, default).strip().lower()
        if value == "":
            return bool(default)
        return value in ("1", "true", "yes", "on")

    def get_str(self, key: str, default: str = "") -> str:
        return _setting_text(self.get(key, default), default)

    def get_int(
        self, key: str, default: int = 0, minimum: int | None = None, maximum: int | None = None
    ) -> int:
        """Return an integer setting with safe fallback and optional bounds.

        Invalid values no longer leak ValueError into callers.  Bounds are
        clamped rather than rejected so existing installations recover to the
        nearest safe value without losing the original persisted setting.
        """
        try:
            value = int(_setting_text(self.get(key, default), default).strip())
        except (TypeError, ValueError):
            value = int(default)
        if minimum is not None and value < minimum:
            value = int(minimum)
        if maximum is not None and value > maximum:
            value = int(maximum)
        return value

    def get_float(
        self,
        key: str,
        default: float = 0.0,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> float:
        """Return a float setting with safe fallback and optional bounds."""
        try:
            value = float(_setting_text(self.get(key, default), default).strip())
        except (TypeError, ValueError):
            value = float(default)
        if minimum is not None and value < minimum:
            value = float(minimum)
        if maximum is not None and value > maximum:
            value = float(maximum)
        return value

    def get_path(self, key: str, default: str = "", *, expand_user: bool = True) -> str:
        """Return a normalized path-like setting without requiring it to exist."""
        value = self.get_str(key, default).strip()
        if expand_user and value.startswith("~"):
            value = os.path.expanduser(value)
        return os.path.normpath(value) if value else ""

    def schema_issues(self) -> list[SettingIssue]:
        """Return typed schema issues without mutating settings or throwing.

        Build 9 keeps schema validation advisory. Existing getters still perform
        safe fallback/coercion, so runtime behavior is unchanged.
        """
        return SETTINGS_SCHEMA.validate(self.data)

    def typed_values(self) -> dict[str, Any]:
        """Return schema-coerced values for diagnostic and future hardening use."""
        return SETTINGS_SCHEMA.coerce(self.data)

    def validate_required(self, required: Iterable[str]) -> list[str]:
        """Return missing required setting keys without mutating settings.

        ``required`` may be any iterable of setting keys.  Defaults count as
        present, but explicit empty strings count as missing because that is
        the common partial-setup failure mode in Kodi settings.xml.
        """
        missing = []
        for key in required:
            value = self.get(key, None)
            if value is None or str(value).strip() == "":
                missing.append(str(key))
        return missing

    def validation_summary(self) -> dict[str, object]:
        """Return a compact non-throwing setup validation summary.

        This is a Build 2 supportability guardrail: it lets future code and AI
        agents detect obvious partial configuration without changing playback
        behavior or forcing a wizard rerun.
        """
        required = (
            "python_path",
            "oppo_ip",
            "oppo_port",
            "oppo_start_mode",
            "playback_architecture",
        )
        missing = self.validate_required(required)
        warnings = []
        if self.get("_settings_read_error"):
            warnings.append("settings_read_error")
        if self.get("oppo_start_mode") not in ENUM_VALUES["oppo_start_mode"]:
            warnings.append("invalid_oppo_start_mode")
        if self.get("playback_architecture") not in ENUM_VALUES["playback_architecture"]:
            warnings.append("invalid_playback_architecture")
        schema_issues = self.schema_issues()
        for issue in schema_issues:
            if issue.code.startswith("invalid_") and issue.code not in warnings:
                warnings.append(issue.code)
        port = self.get_int("oppo_port", 23, minimum=1, maximum=65535)
        return {
            "ok": not missing and not warnings,
            "missing": missing,
            "warnings": warnings,
            "oppo_port": port,
            "playback_architecture": self.get("playback_architecture"),
            "schema_issue_count": len(schema_issues),
            "schema_issue_codes": [issue.code for issue in schema_issues],
        }

    def __setitem__(self, key: str, value: object) -> None:
        self.data[key] = value

    def __contains__(self, key: object) -> bool:
        return key in self.data

    def get_lines(self, key: str) -> list[str]:
        return [line.strip() for line in self.get_str(key).splitlines() if line.strip()]


def _setting_value(element: ET.Element[str]) -> str:
    if "value" in element.attrib:
        return element.attrib["value"]
    if element.text:
        return element.text
    for child in element:
        if child.tag == "value" and child.text:
            return child.text
    return ""


def read_settings(addon_data_dir: str) -> Settings:
    settings_path = os.path.join(addon_data_dir, "settings.xml")
    if not os.path.exists(settings_path):
        return Settings({})

    data = {}
    try:
        tree = ET.parse(settings_path)
    except (ET.ParseError, OSError) as exc:
        # v2.5.0 Build 2: recover from corrupt/partial settings.xml by
        # returning defaults plus a diagnostic marker instead of forcing the
        # service or external-player path into a broad exception fallback.
        return Settings({"_settings_read_error": str(exc)})

    for setting in tree.getroot().iter("setting"):
        setting_id = setting.attrib.get("id")
        if setting_id:
            value = _setting_value(setting)
            if setting_id in ENUM_VALUES and value.isdigit():
                values = ENUM_VALUES[setting_id]
                index = int(value)
                if 0 <= index < len(values):
                    value = values[index]
            data[setting_id] = value
    return Settings(data)


def save_settings(addon_data_dir: str, settings: object) -> bool:
    """Persist Settings data to the add-on data settings.xml file.

    This helper is intentionally conservative for the v2.2 merge line: it
    preserves existing XML rows when present, updates or creates <setting>
    elements for current values, and creates parent directories as needed.
    It is used by the service compatibility watcher so v0.9.14 preset
    reapplication survives beyond the in-memory settings object.

    Build 7 hardens the persistence edge case: an empty add-on-data
    directory returns False instead of writing ``settings.xml`` beside the
    current working directory.
    """
    if not addon_data_dir:
        return False
    settings_path = os.path.join(addon_data_dir, "settings.xml")
    os.makedirs(os.path.dirname(settings_path) or ".", exist_ok=True)

    data = getattr(settings, "data", settings)
    items = _settings_items(data)

    root = ET.Element("settings")
    if os.path.exists(settings_path):
        try:
            root = ET.parse(settings_path).getroot()
        except (ET.ParseError, OSError):
            root = ET.Element("settings")

    by_id = {}
    for existing in root.iter("setting"):
        setting_id = existing.attrib.get("id")
        if setting_id:
            by_id[setting_id] = existing

    for key, value in items:
        if str(key).startswith("_") or key == "addon_data_dir":
            continue
        element = by_id.get(str(key))
        if element is None:
            element = ET.SubElement(root, "setting", {"id": str(key)})
            by_id[str(key)] = element
        element.attrib["value"] = "" if value is None else str(value)
        element.text = None
        for child in list(element):
            element.remove(child)

    ET.ElementTree(root).write(settings_path, encoding="utf-8", xml_declaration=True)
    return True


# ---------------------------------------------------------------------------
# v2.0.0 build 1: MVP hardware compatibility layer
# ---------------------------------------------------------------------------

_HARDWARE_ALIASES = {
    "udp-203": "UDP-203",
    "udp_203": "UDP-203",
    "udp203": "UDP-203",
    "udp-205": "UDP-205",
    "udp_205": "UDP-205",
    "udp205": "UDP-205",
    "chinoppo": "M9702",
    "chinoppo_m9702": "M9702",
    "m9702": "M9702",
    "m9702_v1": "M9702",
    "m9702-v1": "M9702",
    "chinoppo_m9702_v1": "M9702",
    "m9702_v2": "M9702",
    "m9702-v2": "M9702",
    "chinoppo_m9702_v2": "M9702",
    "m9702_v3": "M9702",
    "m9702-v3": "M9702",
    "chinoppo_m9702_v3": "M9702",
    "chinoppo_m9200": "M9200",
    "m9200": "M9200",
    "chinoppo_m9201": "M9201",
    "m9201": "M9201",
    "chinoppo_m9203": "M9203",
    "m9203": "M9203",
    "chinoppo_m9205": "M9205",
    "m9205": "M9205",
    "chinoppo_m9205_v1": "M9205-V1",
    "m9205_v1": "M9205-V1",
    "m9205-v1": "M9205-V1",
    "chinoppo_m9205c": "M9205C",
    "m9205c": "M9205C",
    "cineultra_v203": "CineUltra-V203",
    "cineultra-v203": "CineUltra-V203",
    "v203": "CineUltra-V203",
    "cineultra_v204": "CineUltra-V204",
    "cineultra-v204": "CineUltra-V204",
    "v204": "CineUltra-V204",
    "ipuk_uhd8592": "IPUK-UHD8592",
    "ipuk-uhd8592": "IPUK-UHD8592",
    "giec_bdp_g5300": "GIEC-BDP-G5300",
    "giec-bdp-g5300": "GIEC-BDP-G5300",
    "magnetar_udp800": "Magnetar-UDP800",
    "magnetar-udp800": "Magnetar-UDP800",
    "magnetar_udp900": "Magnetar-UDP900",
    "magnetar-udp900": "Magnetar-UDP900",
    "udp900": "Magnetar-UDP900",
    "reavon_ubrx100": "Reavon-UBR-X100",
    "reavon-ubr-x100": "Reavon-UBR-X100",
    "reavon_ubrx110": "Reavon-UBR-X110",
    "reavon-ubr-x110": "Reavon-UBR-X110",
    "reavon_ubrx200": "Reavon-UBR-X200",
    "reavon-ubr-x200": "Reavon-UBR-X200",
}


def normalize_hardware_model(model: object) -> str:
    """Return the canonical v2 hardware model name for settings/UI aliases."""
    if not isinstance(model, str):
        return "UDP-203"
    stripped = model.strip()
    if stripped in HARDWARE_COMPAT:
        return stripped
    return _HARDWARE_ALIASES.get(stripped.lower(), stripped)


HARDWARE_COMPAT: dict[str, dict[str, object]] = {
    "UDP-203": {
        "wake_command": "#PON",
        "protocol_compatible": True,
        "is_clone": False,
        "is_reavon": False,
        "http_api_436": True,
        "src_supported": {"#SRC 0", "#SRC 1", "#SRC 2", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 5", "#SRC 6"},
    },
    "UDP-205": {
        "wake_command": "#PON",
        "protocol_compatible": True,
        "is_clone": False,
        "is_reavon": False,
        "http_api_436": True,
        "src_supported": {"#SRC 0", "#SRC 1", "#SRC 2", "#SRC 3", "#SRC 4", "#SRC 5", "#SRC 6"},
        "src_unsupported": set(),
    },
    "M9200": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "M9201": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "M9203": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "M9205": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "M9205-V1": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "M9205C": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "CineUltra-V203": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "CineUltra-V204": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "M9702": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 1", "#SRC 2", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 5", "#SRC 6"},
    },
    "IPUK-UHD8592": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 5", "#SRC 6"},
    },
    "GIEC-BDP-G5300": {
        "wake_command": "#EJT",
        "protocol_compatible": True,
        "is_clone": True,
        "is_reavon": False,
        "http_api_436": False,
        "src_supported": {"#SRC 0"},
        "src_unsupported": {"#SRC 1", "#SRC 2", "#SRC 3", "#SRC 4", "#SRC 5", "#SRC 6"},
    },
    "Magnetar-UDP800": {
        "wake_command": None,
        "protocol_compatible": False,
        "is_clone": False,
        "is_reavon": False,
        "is_successor": True,
        "http_api_436": False,
        "src_supported": set(),
        "src_unsupported": set(),
    },
    "Magnetar-UDP900": {
        "wake_command": None,
        "protocol_compatible": False,
        "is_clone": False,
        "is_reavon": False,
        "is_successor": True,
        "http_api_436": False,
        "src_supported": set(),
        "src_unsupported": set(),
    },
    "Reavon-UBR-X100": {
        "wake_command": None,
        "protocol_compatible": False,
        "is_clone": False,
        "is_reavon": True,
        "http_api_436": False,
        "src_supported": set(),
        "src_unsupported": set(),
    },
    "Reavon-UBR-X110": {
        "wake_command": None,
        "protocol_compatible": False,
        "is_clone": False,
        "is_reavon": True,
        "http_api_436": False,
        "src_supported": set(),
        "src_unsupported": set(),
    },
    "Reavon-UBR-X200": {
        "wake_command": None,
        "protocol_compatible": False,
        "is_clone": False,
        "is_reavon": True,
        "http_api_436": False,
        "src_supported": set(),
        "src_unsupported": set(),
    },
}


REAVON_WARNING_TEXT = (
    "Reavon UBR-X100/X110/X200 do not use the stock OPPO command map. "
    "Do not mutate settings automatically; obtain Reavon command codes and "
    "override them manually."
)

QUICK_START_PREREQUISITE_TEXT = (
    "Quick Start mode is required for OPPO/Chinoppo IP wake over TCP/23."
)


AUTOSCRIPT_VERBOSE_PUSH_WARNING = (
    "AutoScript shell handlers that replace the OPPO port-23 protocol can break "
    "#SVM 2 verbose-push status parsing. Keep the stock TCP/IP control surface "
    "available or disable verbose-push hold mode."
)


# ---------------------------------------------------------------------------
# v2.5.2 Build 1: OPPO/Chinoppo NAS playback capability gates
# ---------------------------------------------------------------------------

OPPO20X_AUTOSCRIPT_MIN_FIRMWARE = "20X-56"
OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE = "20X-65-0131"
OPPO20X_AUTOSCRIPT_UNSUPPORTED_NOTE = (
    "20X-54-1127 and older/pre-56 firmware are not supported for AutoScript-based NAS playback."
)

CHINOPPO_NAS_PLAYBACK_MODELS = {
    "M9200",
    "M9201",
    "M9203",
    "M9205",
    "M9205-V1",
    "M9205C",
    "M9702",
    "CineUltra-V203",
    "CineUltra-V204",
    "IPUK-UHD8592",
    "GIEC-BDP-G5300",
}

OPPO_LIKE_SUCCESSOR_WARNING_MODELS = {
    "Reavon-UBR-X100",
    "Reavon-UBR-X110",
    "Reavon-UBR-X200",
    "Magnetar-UDP800",
    "Magnetar-UDP900",
}

NAS_PLAYBACK_CAPABILITY = {
    "oppo20x_jailbroken": {
        "models": ("UDP-203", "UDP-205"),
        "requires_jailbreak": True,
        "requires_autoscript": True,
        "requires_path_mapping": True,
        "min_autoscript_firmware": OPPO20X_AUTOSCRIPT_MIN_FIRMWARE,
        "recommended_firmware": OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE,
        "wake_family": "stock_oppo",
    },
    "chinoppo_family": {
        "models": tuple(sorted(CHINOPPO_NAS_PLAYBACK_MODELS)),
        "requires_jailbreak": False,
        "requires_autoscript": True,
        "requires_path_mapping": True,
        "requires_capability_confirmation": True,
        "min_autoscript_firmware": None,
        "recommended_firmware": None,
        "wake_family": "clone_eject_wake",
    },
}


def _firmware_major_build(firmware: object) -> int | None:
    """Return the numeric 20X build component, e.g. 65 for 20X-65-0131."""
    if firmware is None:
        return None
    text = str(firmware).strip().upper().replace("_", "-")
    if not text:
        return None
    if text.startswith("20X-"):
        text = text[4:]
    parts = text.split("-")
    try:
        return int(parts[0])
    except (TypeError, ValueError, IndexError):
        return None


def oppo20x_autoscript_firmware_status(firmware: object) -> dict[str, Any]:
    """Describe whether original OPPO 20x firmware is AutoScript-capable.

    Research added in v45/v2.5.2 planning identifies 20X-56 as the minimum
    AutoScript-capable line for original OPPO UDP-203/205 workflows, with
    20X-65-0131 as the recommended jailbreak target.  Chinoppo-family firmware
    is not reduced to one numeric minimum because capability depends on the
    active patched firmware/binary combination.
    """
    build = _firmware_major_build(firmware)
    result: dict[str, Any] = {
        "firmware": "" if firmware is None else str(firmware).strip(),
        "minimum": OPPO20X_AUTOSCRIPT_MIN_FIRMWARE,
        "recommended": OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE,
        "autoscript_supported": None,
        "warnings": [],
        "blockers": [],
    }
    if build is None:
        result["warnings"].append("oppo20x_firmware_unknown")
        return result
    if build < 56:
        result["autoscript_supported"] = False
        result["blockers"].append("oppo20x_firmware_below_20x_56")
        result["warnings"].append(OPPO20X_AUTOSCRIPT_UNSUPPORTED_NOTE)
        return result
    result["autoscript_supported"] = True
    if build < 65:
        result["warnings"].append("oppo20x_autoscript_supported_but_20x_65_0131_recommended")
    return result


def nas_playback_capability(
    model: object, firmware: object = "", jailbreak: bool = False, confirmed: bool = False
) -> dict[str, object]:
    """Return a conservative NAS-mounted playback capability assessment.

    This is a planning/gating helper only. It does not launch playback, mutate
    firmware, push AutoScript files, or claim universal hardware validation.
    """
    canonical = normalize_hardware_model(model)
    profile = hardware_profile(canonical)
    warnings = []
    blockers = []
    family = "unknown_oppo_compatible"
    minimum = None
    recommended = None
    requires_jailbreak = False
    requires_confirmation = False
    if profile.get("is_reavon"):
        family = "unsupported_reavon"
        blockers.append("reavon_warning_only_not_supported_for_oppo_chinoppo_nas_playback")
    elif profile.get("is_successor") or canonical in OPPO_LIKE_SUCCESSOR_WARNING_MODELS:
        family = "unsupported_oppo_like_successor"
        blockers.append(
            "oppo_like_successor_warning_only_not_supported_for_oppo_chinoppo_nas_playback"
        )
    elif canonical in ("UDP-203", "UDP-205"):
        family = "oppo20x_jailbroken"
        requires_jailbreak = True
        minimum = OPPO20X_AUTOSCRIPT_MIN_FIRMWARE
        recommended = OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE
        if not jailbreak:
            blockers.append("oppo20x_jailbreak_required")
        fw = oppo20x_autoscript_firmware_status(firmware)
        warnings.extend(fw["warnings"])
        blockers.extend(fw["blockers"])
    elif canonical in CHINOPPO_NAS_PLAYBACK_MODELS or profile.get("is_clone"):
        family = "chinoppo_family"
        requires_confirmation = True
        if not confirmed:
            warnings.append("chinoppo_firmware_binary_capability_must_be_confirmed")
    else:
        warnings.append("unknown_model_using_safe_oppo20x_assumptions")
    return {
        "model": canonical,
        "family": family,
        "supported": not blockers and family != "unknown_oppo_compatible",
        "requires_jailbreak": requires_jailbreak,
        "requires_autoscript": family in ("oppo20x_jailbroken", "chinoppo_family"),
        "requires_path_mapping": family in ("oppo20x_jailbroken", "chinoppo_family"),
        "requires_capability_confirmation": requires_confirmation,
        "min_autoscript_firmware": minimum,
        "recommended_firmware": recommended,
        "wake_command": profile.get("wake_command") or "#PON",
        "warnings": warnings,
        "blockers": blockers,
    }


def hardware_profile(model: object) -> dict[str, object]:
    """Return hardware compatibility data, using a safe UDP-203-like fallback."""
    canonical = normalize_hardware_model(model)
    if canonical in HARDWARE_COMPAT:
        return HARDWARE_COMPAT[canonical]
    return {
        "wake_command": "#PON",
        "protocol_compatible": True,
        "is_clone": False,
        "is_reavon": False,
        "http_api_436": True,
        "src_supported": {"#SRC 0", "#SRC 1", "#SRC 2", "#SRC 3", "#SRC 4"},
        "src_unsupported": {"#SRC 5", "#SRC 6"},
    }


def compatibility_preset(model: object, jailbreak: bool = False) -> dict[str, object]:
    """Return recommended MVP setting overrides for a model without mutating settings."""
    profile = hardware_profile(model)
    if profile.get("is_reavon"):
        return {"__reavon_warning__": True}
    if profile.get("is_successor"):
        return {"__successor_warning__": True}
    preset: dict[str, object] = {}
    if profile.get("is_clone"):
        preset["oppo_start_commands"] = "#EJT\n#PLA"
        preset["oppo_start_mode"] = "tcp_commands"
        preset["oppo_http_activate"] = "false"
    if jailbreak and profile.get("protocol_compatible") and not profile.get("is_clone"):
        preset["oppo_http_payload_mode"] = "json_payload"
    return preset


def is_token_supported_by_hardware(token: object, model: object) -> bool:
    """Return False only for known unsupported #SRC tokens on the selected model."""
    if not isinstance(token, str):
        return True
    normalized = token.strip().upper()
    profile = hardware_profile(model)
    if normalized in cast("set[str]", profile.get("src_unsupported", set())):
        return False
    return True


def warn_if_unsupported(token: object, model: object) -> str | None:
    if is_token_supported_by_hardware(token, model):
        return None
    return f"Token {token!r} is not supported by configured hardware model {normalize_hardware_model(model)!r}."
