"""AVR control data types for v2.9.10 Build 11.

Build 11 intentionally adds only a disabled-by-default framework skeleton.  It
provides safe result/validation containers for future brand drivers without
executing real AVR commands or hooking AVR control into playback sequencing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

AVR_BACKEND_DISABLED = "disabled"
AVR_BACKEND_DENON_MARANTZ = "denon_marantz"
AVR_BACKEND_YAMAHA_YXC = "yamaha_yxc"
AVR_BACKEND_ONKYO_EISCP = "onkyo_eiscp"
AVR_BACKEND_PIONEER_EISCP = "pioneer_eiscp"
AVR_BACKEND_SONY_AUDIO_API = "sony_audio_api"

AVR_BACKENDS = (
    AVR_BACKEND_DISABLED,
    AVR_BACKEND_DENON_MARANTZ,
    AVR_BACKEND_YAMAHA_YXC,
    AVR_BACKEND_ONKYO_EISCP,
    AVR_BACKEND_PIONEER_EISCP,
    AVR_BACKEND_SONY_AUDIO_API,
)

AVR_DRIVER_IMPLEMENTED = False
DENON_MARANTZ_DRIVER_IMPLEMENTED = True
YAMAHA_YXC_DRIVER_IMPLEMENTED = True
ONKYO_EISCP_DRIVER_IMPLEMENTED = True
PIONEER_EISCP_EXPERIMENTAL_DRIVER_IMPLEMENTED = True
SONY_AUDIO_API_EXPERIMENTAL_SKELETON_AVAILABLE = True
SONY_AUDIO_API_REQUEST_HELPER_AVAILABLE = True
SONY_AUDIO_API_LIVE_CALLS_ENABLED = True
HARDWARE_VALIDATION_CLAIMED = False


@dataclass(frozen=True)
class AvrResult:
    """Non-throwing AVR operation result used by future drivers and diagnostics."""

    ok: bool
    action: str
    backend: str = AVR_BACKEND_DISABLED
    message: str = ""
    warnings: tuple[str, ...] = ()
    nonfatal: bool = True
    hardware_validation_claimed: bool = False
    command_sent: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "action": self.action,
            "backend": self.backend,
            "message": self.message,
            "warnings": self.warnings,
            "nonfatal": self.nonfatal,
            "hardware_validation_claimed": self.hardware_validation_claimed,
            "command_sent": self.command_sent,
        }


@dataclass(frozen=True)
class AvrValidation:
    """AVR setup validation summary with non-fatal warning semantics."""

    ok: bool
    backend: str
    enabled: bool = False
    missing: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    driver_available: bool = False
    hardware_validation_claimed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "backend": self.backend,
            "enabled": self.enabled,
            "missing": self.missing,
            "warnings": self.warnings,
            "driver_available": self.driver_available,
            "hardware_validation_claimed": self.hardware_validation_claimed,
        }
