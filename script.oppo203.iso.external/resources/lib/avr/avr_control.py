"""Generic AVR framework skeleton for v2.9.10 Build 11.

Build 15B keeps AVR disabled by default and adds a guarded Sony Audio API
experimental request helper with explicit acknowledgement required,
preserving the Build 12 Denon/Marantz, Build 13 Yamaha, and Build 14
eISCP drivers. All failures are represented as non-fatal warnings so future
playback sequencing can opt in without destabilizing OPPO/Kodi routing.
"""

from __future__ import annotations

from typing import Any, cast

try:
    from .avr_denon_marantz import DenonMarantzAvrController
    from .avr_onkyo_eiscp import OnkyoEiscpAvrController
    from .avr_presets import get_avr_preset, normalize_avr_backend
    from .avr_sony_audio import SonyAudioApiAvrController
    from .avr_sony_audio import validation_metadata as sony_validation_metadata
    from .avr_types import (
        AVR_BACKEND_DENON_MARANTZ,
        AVR_BACKEND_DISABLED,
        AVR_BACKEND_ONKYO_EISCP,
        AVR_BACKEND_PIONEER_EISCP,
        AVR_BACKEND_SONY_AUDIO_API,
        AVR_BACKEND_YAMAHA_YXC,
        AVR_BACKENDS,
        AvrResult,
        AvrValidation,
    )
    from .avr_yamaha import YamahaYxcAvrController
except ImportError:  # pragma: no cover - top-level/audit/test compatibility
    from avr_denon_marantz import DenonMarantzAvrController  # type: ignore
    from avr_onkyo_eiscp import OnkyoEiscpAvrController  # type: ignore
    from avr_presets import get_avr_preset, normalize_avr_backend  # type: ignore
    from avr_sony_audio import SonyAudioApiAvrController  # type: ignore
    from avr_sony_audio import (  # type: ignore[no-redef]
        validation_metadata as sony_validation_metadata,
    )
    from avr_types import (  # type: ignore
        AVR_BACKEND_DENON_MARANTZ,
        AVR_BACKEND_DISABLED,
        AVR_BACKEND_ONKYO_EISCP,
        AVR_BACKEND_PIONEER_EISCP,
        AVR_BACKEND_SONY_AUDIO_API,
        AVR_BACKEND_YAMAHA_YXC,
        AVR_BACKENDS,
        AvrResult,
        AvrValidation,
    )
    from avr_yamaha import YamahaYxcAvrController  # type: ignore

REQUIRED_ENABLED_FIELDS = ("avr_host", "avr_backend", "avr_player_input")
NO_DRIVER_WARNING = "avr_driver_not_implemented_build11"
DISABLED_WARNING = "avr_control_disabled"
INCOMPLETE_WARNING = "avr_config_incomplete"


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


def selected_avr_backend(settings: dict[str, object] | object | None) -> str:
    data = _settings_dict(settings)
    return normalize_avr_backend(data.get("avr_backend", AVR_BACKEND_DISABLED))


def avr_enabled(settings: dict[str, object] | object | None) -> bool:
    data = _settings_dict(settings)
    return _truthy(data.get("avr_control_enabled", "false"), False)


def avr_settings_summary(settings: dict[str, object] | object | None) -> dict[str, object]:
    data = _settings_dict(settings)
    backend = selected_avr_backend(data)
    return {
        "avr_control_enabled": avr_enabled(data),
        "avr_backend": backend,
        "avr_host_configured": bool(str(data.get("avr_host", "")).strip()),
        "avr_port_configured": bool(str(data.get("avr_port", "")).strip()),
        "avr_player_input_configured": bool(str(data.get("avr_player_input", "")).strip()),
        "avr_restore_enabled": _truthy(data.get("avr_restore_enabled", "false"), False),
        "avr_restore_input_configured": bool(str(data.get("avr_restore_input", "")).strip()),
        "avr_power_off_enabled": _truthy(data.get("avr_power_off_enabled", "false"), False),
        "avr_volume_automation_enabled": _truthy(
            data.get("avr_volume_automation_enabled", "false"), False
        ),
        "driver_execution_added": True,
        "driver_execution_families": (
            AVR_BACKEND_DENON_MARANTZ,
            AVR_BACKEND_YAMAHA_YXC,
            AVR_BACKEND_ONKYO_EISCP,
            AVR_BACKEND_PIONEER_EISCP,
            AVR_BACKEND_SONY_AUDIO_API,
        ),
        "experimental_skeleton_families": (),
        "sony_live_api_calls_enabled": True,
        "playback_sequencing_hooked": True,
        "hardware_validation_claimed": False,
    }


def validate_avr_settings(settings: dict[str, object] | object | None) -> AvrValidation:
    data = _settings_dict(settings)
    enabled = avr_enabled(data)
    backend = selected_avr_backend(data)
    warnings: list[str] = []
    missing: list[str] = []

    if not enabled:
        return AvrValidation(
            ok=True,
            backend=AVR_BACKEND_DISABLED,
            enabled=False,
            warnings=(DISABLED_WARNING,),
            driver_available=False,
            hardware_validation_claimed=False,
        )

    if backend not in AVR_BACKENDS or backend == AVR_BACKEND_DISABLED:
        missing.append("avr_backend")
        warnings.append("avr_backend_invalid_or_disabled")

    for key in REQUIRED_ENABLED_FIELDS:
        if key == "avr_backend":
            continue
        if not str(data.get(key, "")).strip():
            missing.append(key)

    if missing:
        warnings.append(INCOMPLETE_WARNING)

    if backend == AVR_BACKEND_SONY_AUDIO_API:
        sony_meta = sony_validation_metadata(data)
        warnings.extend(
            str(item) for item in cast("tuple[object, ...]", sony_meta.get("warnings", ()))
        )
        for sony_key in cast(  # metadata-only Sony skeleton fields
            "tuple[object, ...]", sony_meta.get("missing", ())
        ):
            missing.append(str(sony_key))
        if not sony_meta.get("acknowledged", False):
            warnings.append("sony_audio_api_refused_without_acknowledgement")

    preset = get_avr_preset(backend)
    driver_available = bool(preset.get("driver_available", False))
    if not driver_available and backend != AVR_BACKEND_DISABLED:
        warnings.append(NO_DRIVER_WARNING)

    return AvrValidation(
        ok=not missing and driver_available,
        backend=backend,
        enabled=True,
        missing=tuple(dict.fromkeys(missing)),
        warnings=tuple(dict.fromkeys(warnings)),
        driver_available=driver_available,
        hardware_validation_claimed=False,
    )


class NoOpAvrController:
    """Explicit no-op controller used only when callers request one for tests."""

    def __init__(self, backend: str = AVR_BACKEND_DISABLED):
        self.backend = backend

    def run(self, action: str, **_: Any) -> AvrResult:
        return AvrResult(
            ok=False,
            action=action,
            backend=self.backend,
            message="AVR command execution is not implemented in Build 11.",
            warnings=(NO_DRIVER_WARNING,),
            nonfatal=True,
            hardware_validation_claimed=False,
            command_sent=False,
        )


def controller_factory(
    settings: dict[str, object] | object | None,
    *,
    allow_noop: bool = False,
    socket_factory: object | None = None,
    http_get: object | None = None,
    sony_post: object | None = None,
) -> object | None:
    """Return an AVR controller only when a guarded driver is safely available.

    Build 12 added Denon/Marantz, Build 13 added Yamaha MusicCast/YXC,
    Build 14 added Onkyo/Integra plus experimental Pioneer eISCP, and Build
    15B adds a Sony experimental request helper only.
    The default disabled path still returns ``None``; Sony API execution
    requires explicit acknowledgement and complete configuration. ``allow_noop=True`` remains a
    diagnostic/test escape hatch and never sends commands.
    """
    validation = validate_avr_settings(settings)
    if not validation.enabled:
        return None
    if allow_noop:
        return NoOpAvrController(validation.backend)
    if not validation.ok:
        return None
    data = _settings_dict(settings)
    if validation.backend == AVR_BACKEND_DENON_MARANTZ:
        return DenonMarantzAvrController(
            data.get("avr_host", ""),
            port=data.get("avr_port", "23"),
            timeout=data.get("avr_timeout", "3.0"),
            player_input=data.get("avr_player_input", ""),
            socket_factory=socket_factory,  # type: ignore[arg-type]
        )
    if validation.backend == AVR_BACKEND_YAMAHA_YXC:
        return YamahaYxcAvrController(
            data.get("avr_host", ""),
            port=data.get("avr_port", "80"),
            timeout=data.get("avr_timeout", "3.0"),
            player_input=data.get("avr_player_input", ""),
            http_get=http_get,  # type: ignore[arg-type]
        )
    if validation.backend in {AVR_BACKEND_ONKYO_EISCP, AVR_BACKEND_PIONEER_EISCP}:
        return OnkyoEiscpAvrController(
            data.get("avr_host", ""),
            port=data.get("avr_port", "60128"),
            timeout=data.get("avr_timeout", "3.0"),
            player_input=data.get("avr_player_input", ""),
            socket_factory=socket_factory,  # type: ignore[arg-type]
            experimental_pioneer=validation.backend == AVR_BACKEND_PIONEER_EISCP,
        )
    if validation.backend == AVR_BACKEND_SONY_AUDIO_API:
        return SonyAudioApiAvrController(data, post=sony_post)  # type: ignore[arg-type]
    return None


def build_nonfatal_result(
    action: str, settings: dict[str, object] | object | None, message: str = ""
) -> AvrResult:
    validation = validate_avr_settings(settings)
    warning_list = list(validation.warnings)
    if message:
        warning_list.append(message)
    return AvrResult(
        ok=False,
        action=action,
        backend=validation.backend,
        message=message or "AVR framework skeleton only; no command was sent.",
        warnings=tuple(dict.fromkeys(warning_list)),
        nonfatal=True,
        hardware_validation_claimed=False,
        command_sent=False,
    )
