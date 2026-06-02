"""Unified AVR playback sequencing for v2.9.10 Build 17.

This module is deliberately small and non-throwing. It connects the optional,
disabled-by-default AVR framework to the external-player handoff path without
changing OPPO routing, service interception, playercorefactory.xml behavior,
NAS/AutoScript behavior, or TV switching semantics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

try:
    from .avr_control import avr_enabled, controller_factory, selected_avr_backend
    from .avr_types import AVR_BACKEND_DISABLED, AVR_BACKEND_SONY_AUDIO_API  # noqa: F401
except ImportError:  # pragma: no cover - top-level/test compatibility
    from avr_control import avr_enabled, controller_factory, selected_avr_backend  # type: ignore
    from avr_types import (  # type: ignore  # noqa: F401
        AVR_BACKEND_DISABLED,
        AVR_BACKEND_SONY_AUDIO_API,
    )


@dataclass(frozen=True)
class AvrSequenceResult:
    """Non-throwing sequence result for playback-flow callers and tests."""

    ok: bool
    phase: str
    skipped: bool = False
    actions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    nonfatal: bool = True
    hardware_validation_claimed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "phase": self.phase,
            "skipped": self.skipped,
            "actions": self.actions,
            "warnings": self.warnings,
            "nonfatal": self.nonfatal,
            "hardware_validation_claimed": self.hardware_validation_claimed,
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


def _settle_after_power_on(data: dict[str, object]) -> None:
    """Pause between AVR power-on and input-select.

    Many receivers ignore an input command issued in the first 1-3 s after a cold power-on,
    leaving the wrong input selected. Only called when a power-on was actually issued; a value
    of 0 disables the wait. Default 1.5 s.
    """
    raw = data.get("avr_power_on_settle_seconds", "1.5")
    try:
        seconds = float(str(raw).strip() or "1.5")
    except (TypeError, ValueError):
        seconds = 1.5
    if seconds > 0:
        time.sleep(seconds)


_AVR_ELIGIBLE_ROUTINGS = frozenset({"external_player", "http_handoff"})


def eligible_for_external_player_avr_sequence(settings: dict[str, object] | object | None) -> bool:
    """Return True for the OPPO handoff postures that run through the external-player wrapper.

    Both the ``external_player`` (playercorefactory) routing and the ``http_handoff`` routing
    invoke the wrapper (``fast_start`` / ``fast_start_http``), so AVR sequencing is eligible for
    both. ``service_interception`` is excluded: its handoff does not flow through the wrapper, so
    AVR sequencing must not run even if the wrapper is called directly. An empty/default value is
    treated as ``external_player`` and stays eligible.
    """
    data = _settings_dict(settings)
    routing = str(data.get("playback_architecture", "external_player") or "").strip().lower()
    return routing in _AVR_ELIGIBLE_ROUTINGS


def _result_from_exception(phase: str, exc: Exception, actions: list[str]) -> AvrSequenceResult:
    return AvrSequenceResult(
        ok=False,
        phase=phase,
        skipped=False,
        actions=tuple(actions),
        warnings=(f"avr_{phase}_sequence_failed_nonfatal", exc.__class__.__name__),
        nonfatal=True,
        hardware_validation_claimed=False,
    )


def _call_controller(controller: object, action: str, *args: object) -> object:
    method = getattr(controller, action, None)
    if callable(method):
        return method(*args)
    run = getattr(controller, "run", None)
    if callable(run):
        if action == "select_input" and args:
            return run("select_input", input_name=args[0], input_code=args[0])
        return run(action)
    raise AttributeError(action)


def pre_playback_sequence(
    settings: dict[str, object] | object | None, *, controller: object | None = None
) -> AvrSequenceResult:
    """Run optional AVR power/input preparation before OPPO playback.

    Disabled, ineligible, or incomplete AVR configuration is a no-op/nonfatal
    result. Any controller failure is captured and returned; callers do not need
    to wrap this helper to protect playback.
    """
    if not eligible_for_external_player_avr_sequence(settings):
        return AvrSequenceResult(
            True, "pre", skipped=True, warnings=("avr_sequence_ineligible_external_player",)
        )
    if not avr_enabled(settings):
        return AvrSequenceResult(True, "pre", skipped=True, warnings=("avr_control_disabled",))

    data = _settings_dict(settings)
    active_controller = controller if controller is not None else controller_factory(settings)
    if active_controller is None:
        return AvrSequenceResult(
            False, "pre", skipped=True, warnings=("avr_controller_unavailable_nonfatal",)
        )

    actions: list[str] = []
    try:
        if _truthy(data.get("avr_power_on_enabled", "false"), False):
            _call_controller(active_controller, "power_on")
            actions.append("power_on")
            _settle_after_power_on(data)
        _call_controller(active_controller, "select_input")
        actions.append("select_input")
        return AvrSequenceResult(True, "pre", skipped=False, actions=tuple(actions))
    except Exception as exc:  # deliberately nonfatal for playback flow
        return _result_from_exception("pre", exc, actions)


def _restore_input_for(settings: dict[str, object] | object | None) -> str:
    data = _settings_dict(settings)
    if selected_avr_backend(data) == AVR_BACKEND_SONY_AUDIO_API:
        sony_uri = str(data.get("sony_avr_restore_input_uri", "") or "").strip()
        if sony_uri:
            return sony_uri
    return str(data.get("avr_restore_input", "") or "").strip()


def post_playback_sequence(
    settings: dict[str, object] | object | None, *, controller: object | None = None
) -> AvrSequenceResult:
    """Run optional AVR restore after OPPO playback has been stopped."""
    if not eligible_for_external_player_avr_sequence(settings):
        return AvrSequenceResult(
            True, "post", skipped=True, warnings=("avr_sequence_ineligible_external_player",)
        )
    if not avr_enabled(settings):
        return AvrSequenceResult(True, "post", skipped=True, warnings=("avr_control_disabled",))

    data = _settings_dict(settings)
    if not _truthy(data.get("avr_restore_enabled", "false"), False):
        return AvrSequenceResult(True, "post", skipped=True, warnings=("avr_restore_disabled",))

    restore_input = _restore_input_for(settings)
    if not restore_input:
        return AvrSequenceResult(
            False, "post", skipped=True, warnings=("avr_restore_input_missing_nonfatal",)
        )

    active_controller = controller if controller is not None else controller_factory(settings)
    if active_controller is None:
        return AvrSequenceResult(
            False, "post", skipped=True, warnings=("avr_controller_unavailable_nonfatal",)
        )

    actions: list[str] = []
    try:
        _call_controller(active_controller, "select_input", restore_input)
        actions.append("restore_input")
        return AvrSequenceResult(True, "post", skipped=False, actions=tuple(actions))
    except Exception as exc:  # deliberately nonfatal for playback flow
        return _result_from_exception("post", exc, actions)


def sequencing_metadata() -> dict[str, object]:
    return {
        "playback_sequencing_hooked": True,
        "avr_sequence_external_player_only": False,
        "avr_sequence_routings": ("external_player", "http_handoff"),
        "avr_disabled_path_noop": True,
        "avr_failures_block_playback": False,
        "tv_failures_block_playback": False,
        "optional_avr_restore_supported": True,
        "hardware_validation_claimed": False,
    }
