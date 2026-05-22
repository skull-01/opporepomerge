"""Compatibility-preset helpers preserved from the v0.9.14 hardware line.

This module is intentionally narrow in the v2.2 merge line.  The existing
`wizard.py` remains the active Kodi wizard; these helpers provide the v0.9.14
preset/reapply/logging behavior needed by the service settings watcher and by
future full superset-merge slices.
"""

from __future__ import annotations


def _setting_get(settings, key, default=None):
    try:
        return settings.get(key, default)
    except Exception:
        return default


def _setting_set(settings, key, value):
    try:
        settings[key] = value
        return True
    except Exception:
        try:
            data = settings.data
            data[key] = value
            return True
        except Exception:
            return False


def _bool(value, default=False):
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    try:
        text = str(value).strip().lower()
    except Exception:
        return bool(default)
    if text == "":
        return bool(default)
    return text in ("1", "true", "yes", "on")


def apply_compatibility_preset(settings, model, jailbreak=False, _log=None):
    """Apply model-specific compatibility settings in place.

    Returns ``(applied, warnings)`` where ``applied`` is a list of
    ``(key, old_value, new_value)`` tuples.  Reavon remains warning-only and
    never mutates OPPO command maps.
    """
    try:
        from settings_reader import (
            QUICK_START_PREREQUISITE_TEXT,
            REAVON_WARNING_TEXT,
            compatibility_preset,
            hardware_profile,
        )
    except Exception:
        return ([], [])

    preset = dict(compatibility_preset(model, jailbreak=bool(jailbreak)))
    warnings = []
    if preset.pop("__reavon_warning__", False):
        warnings.append(REAVON_WARNING_TEXT)

    try:
        profile = hardware_profile(model)
    except Exception:
        profile = {}
    if profile.get("protocol_compatible"):
        warnings.append(QUICK_START_PREREQUISITE_TEXT)

    applied = []
    for key, value in preset.items():
        old = _setting_get(settings, key)
        if _setting_set(settings, key, value):
            applied.append((key, old, value))
            if _log:
                try:
                    _log(f"[v0.9.12-preset] {key}: {old!r} -> {value!r}")
                except Exception:
                    pass
    return (applied, warnings)


def quick_start_required(model):
    """Return True when the selected model relies on OPPO-compatible IP wake."""
    try:
        from settings_reader import hardware_profile

        return bool(hardware_profile(model).get("protocol_compatible"))
    except Exception:
        return True


def autoscript_verbose_push_warning(uses_autoscript_shell):
    """Return the v0.9.14 AutoScript warning text when applicable."""
    if not uses_autoscript_shell:
        return None
    try:
        from settings_reader import AUTOSCRIPT_VERBOSE_PUSH_WARNING

        return AUTOSCRIPT_VERBOSE_PUSH_WARNING
    except Exception:
        return (
            "AutoScript shell handlers that replace the OPPO port-23 protocol "
            "can break #SVM 2 verbose-push status parsing."
        )


def reapply_preset_on_model_change(settings, prev_model, new_model, jailbreak=None, _log=None):
    """Re-run compatibility presets after a Kodi settings change.

    The v0.9.14 behavior was model-change driven.  In the v2.2 merge line this
    also supports the stock-OPPO jailbreak toggle because that setting affects
    JSON HTTP payload mode while preserving the same public helper name.
    """
    if jailbreak is None:
        jailbreak = _bool(_setting_get(settings, "oppo_jailbreak_enabled", "false"))
        if prev_model == new_model:
            return ([], [])
    applied, warnings = apply_compatibility_preset(
        settings, new_model, jailbreak=jailbreak, _log=_log
    )
    if _log:
        try:
            _log(
                f"[v0.9.14-model-change] {prev_model} -> {new_model} "
                f"applied={len(applied)} warnings={len(warnings)}"
            )
        except Exception:
            pass
    return (applied, warnings)


def collect_compatibility_warnings(
    settings=None, model=None, jailbreak=None, uses_autoscript_shell=None
):
    """Collect v0.9.14 compatibility warnings for support logging.

    This helper is intentionally side-effect free.  It lets the service watcher
    preserve the v0.9.14 behavior of logging compatibility warnings even when
    the user changes settings outside the wizard and dismisses any modal UI.
    """
    if model is None and settings is not None:
        model = _setting_get(settings, "oppo_hardware_model", "UDP-203")
    if jailbreak is None and settings is not None:
        jailbreak = _bool(_setting_get(settings, "oppo_jailbreak_enabled", "false"))
    if uses_autoscript_shell is None and settings is not None:
        uses_autoscript_shell = _bool(
            _setting_get(settings, "oppo_autoscript_shell_handler", "false")
        )

    warnings = []
    try:
        from settings_reader import (
            QUICK_START_PREREQUISITE_TEXT,
            REAVON_WARNING_TEXT,
            compatibility_preset,
            hardware_profile,
        )

        preset = dict(compatibility_preset(model or "UDP-203", jailbreak=bool(jailbreak)))
        if preset.get("__reavon_warning__"):
            warnings.append(REAVON_WARNING_TEXT)
        if hardware_profile(model or "UDP-203").get("protocol_compatible"):
            warnings.append(QUICK_START_PREREQUISITE_TEXT)
    except Exception:
        pass

    autoscript_warning = autoscript_verbose_push_warning(bool(uses_autoscript_shell))
    if autoscript_warning:
        warnings.append(autoscript_warning)

    deduped = []
    for warning in warnings:
        if warning and warning not in deduped:
            deduped.append(warning)
    return deduped


def log_compatibility_warnings(warnings, _log=None):
    """Log compatibility warnings without ever blocking playback or settings UI."""
    if not warnings or not _log:
        return 0
    count = 0
    for warning in warnings:
        try:
            _log("[v0.9.14-warning] " + (warning if isinstance(warning, str) else repr(warning)))
            count += 1
        except Exception:
            pass
    return count


# ---------------------------------------------------------------------------
# v2.2.0 Build 5: wizard/UI compatibility-warning surfacing helpers
# ---------------------------------------------------------------------------


def _ui_call(ui, name, *args):
    """Call an optional wizard UI method without making Kodi a test dependency."""
    if ui is None:
        return False
    method = getattr(ui, name, None)
    if method is None:
        return False
    try:
        method(*args)
        return True
    except TypeError:
        # Some older test/UI adapters expose single-argument methods.  Fall
        # back to the final positional argument, which is always the message.
        try:
            method(args[-1])
            return True
        except Exception:
            return False
    except Exception:
        return False


def surface_compatibility_warnings(ui, warnings, _log=None, title="Compatibility warning"):
    """Surface v0.9.14 compatibility warnings through a wizard-style UI.

    The historical v0.9.14 wizard showed compatibility warnings modally while
    also logging them.  This helper restores that behavior in a testable,
    side-effect-safe form for the gradual v2.2 merge line.  It prefers
    ``ui.ok(title, message)``, falls back to ``ui.notify(message)`` and then
    ``ui.show_text(message)``.  Failures are swallowed so warning surfacing can
    never block playback or settings changes.
    """
    surfaced = 0
    for warning in warnings or []:
        if not warning:
            continue
        message = warning if isinstance(warning, str) else repr(warning)
        if _log:
            try:
                _log("[v0.9.14-warning] " + message)
            except Exception:
                pass
        if (
            _ui_call(ui, "ok", title, message)
            or _ui_call(ui, "notify", message)
            or _ui_call(ui, "show_text", message)
        ):
            surfaced += 1
    return surfaced


def ask_choice(ui, prompt, choices, default=None):
    """Use a v0.9.14-style UI choice method with validation and fallback."""
    choices = list(choices or [])
    if not choices:
        return default
    if default not in choices:
        default = choices[0]
    if ui is None or not hasattr(ui, "ask_choice"):
        return default
    try:
        answer = ui.ask_choice(prompt, choices, default)
    except Exception:
        return default
    return answer if answer in choices else default


def apply_and_surface_compatibility(
    settings, model, jailbreak=False, uses_autoscript_shell=False, ui=None, _log=None
):
    """Apply compatibility presets, collect warnings, and surface them.

    This is a bridge helper for the gradual superset merge: it keeps Reavon
    warning-only behavior, clone preset mutation, Quick Start warnings,
    AutoScript verbose-push warnings, support-log markers, and UI surfacing in
    one small testable unit without replacing the active v1.x wizard flow.
    """
    applied, warnings = apply_compatibility_preset(
        settings, model, jailbreak=bool(jailbreak), _log=_log
    )
    merged = list(warnings)
    for warning in collect_compatibility_warnings(
        settings=settings,
        model=model,
        jailbreak=jailbreak,
        uses_autoscript_shell=uses_autoscript_shell,
    ):
        if warning not in merged:
            merged.append(warning)
    surfaced = surface_compatibility_warnings(ui, merged, _log=_log)
    return {
        "applied": applied,
        "warnings": merged,
        "surfaced": surfaced,
    }
