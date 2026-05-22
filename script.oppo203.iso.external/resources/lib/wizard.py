"""First-run wizard with Basic/Full mode and Architecture auto-test (v1.0.3)."""

import socket

from diagnostic_logging import format_log_message

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
except ImportError:
    xbmc = xbmcaddon = xbmcgui = None
ADDON_ID = "script.oppo203.iso.external"

# v2.5.0 Build 3: user-facing wizard wording.
# These constants intentionally change copy only; they must not change dialog order,
# defaults, branching, persisted setting keys, or hardware-facing behavior.
WIZARD_TEXT = {
    "welcome_title": "OPPO UDP-203 Setup Wizard",
    "welcome_body": (
        "This wizard configures Kodi to use your OPPO-compatible player. "
        "Choose Basic for the safest essential setup, or Full to review advanced compatibility options."
    ),
    "prerequisites_title": "Before setup",
    "prerequisites_body": (
        "Confirm the player is on the network and IP Control is enabled. "
        "For OPPO-compatible wake/power workflows, Quick Start may also need to be enabled on the player. Continue?"
    ),
    "unreachable_title": "Player not reachable",
    "unreachable_body": (
        "Kodi could not open a TCP connection to the configured player address. "
        "Check the IP address, port, network connection, and player IP Control setting. Continue anyway?"
    ),
    "stock_jailbreak_title": "Stock OPPO jailbreak mode",
    "stock_jailbreak_body": (
        "Is this stock OPPO player using jailbroken/oppo-jb firmware? "
        "Choose Yes only when the JSON HTTP payload compatibility mode is required."
    ),
    "autoscript_title": "AutoScript shell handler",
    "autoscript_body": (
        "Is an AutoScript shell handler bound to OPPO port 23? "
        "Choose Yes only if your AutoScript replaces the normal OPPO port-23 command protocol."
    ),
    "chinoppo_preset_title": "Chinoppo command preset",
    "chinoppo_preset_body": (
        "Apply the Chinoppo #EJT/#PLA command preset? "
        "This is recommended for Chinoppo/M9702-style workflows unless your hardware test plan says otherwise."
    ),
    "player_hardware_guidance_title": "Player hardware class guidance",
    "player_hardware_guidance_fallback": (
        "The selected player will be treated conservatively. "
        "Hardware validation is required before confirmed support is claimed."
    ),
    "quick_start_title": "Quick Start confirmation",
    "quick_start_body": (
        "Is Quick Start enabled on the player? Some OPPO-compatible power/wake workflows require it."
    ),
    "autopower_title": "Kodi startup auto-power",
    "autopower_body": (
        "Do you want Kodi to automatically power on the OPPO/compatible player when Kodi starts? "
        "Choose No if you prefer to keep the player off until playback starts or you power it on manually."
    ),
    "wol_title": "Wake-on-LAN before power-on",
    "wol_body": "Send Wake-on-LAN before the startup power-on command?",
    "arch_test_title": "Architecture auto-test",
    "arch_test_body": "Run a quick connection test before choosing the playback architecture?",
    "architecture_title": "Playback architecture",
    "architecture_body": (
        "Use External Player mode? This remains the recommended and safest default for most OPPO-compatible setups."
    ),
    "xml_naming_title": "4K XML naming requirement",
    "xml_naming_body": (
        "4K external-player XML mode requires naming discipline. "
        "Only disc-style ISO, BDMV, and MPLS sources whose filename or visible folder path contains "
        "4K, UHD, or 2160p will be routed to the OPPO/Chinoppo external player. "
        "Loose video files such as MKV, MP4, M2TS, TS, and VOB stay with Kodi. "
        "Examples: Movie Title (Year) 4K UHD.iso; Movie Title (Year) 2160p/BDMV/index.bdmv. "
        "XML mode cannot inspect metadata, NFO files, stream resolution, or ISO internals."
    ),
    "avr_setup_title": "AVR setup",
    "avr_setup_body": (
        "Configure optional AVR power/input control now? Choose No to keep AVR control disabled. "
        "AVR can be configured later from settings or diagnostics."
    ),
    "avr_family_title": "AVR family",
    "avr_host_title": "AVR host/IP",
    "avr_port_title": "AVR port",
    "avr_player_input_title": "AVR OPPO/player input",
    "avr_restore_input_title": "Optional AVR restore input",
    "avr_sound_mode_title": "Optional AVR sound mode",
    "sony_avr_ack_title": "Sony AVR experimental acknowledgement",
    "sony_avr_ack_body": (
        "Sony Audio Control API AVR support is experimental and not hardware validated. "
        "Enable only if you understand that credentials must be protected and behavior is unconfirmed."
    ),
    "avr_setup_complete_body": (
        "AVR setup metadata saved. AVR remains optional, disabled unless explicitly enabled, "
        "and is not hooked into playback sequencing in this build."
    ),
    "wizard_complete_body": "Configuration saved. You can rerun the wizard later if hardware validation requires changes.",
}


def _text(key):
    return WIZARD_TEXT[key]


# v2.5.0 Build 4: wizard recovery metadata.  These keys are intentionally
# additive so existing v2.2/v2.5 settings remain compatible.
WIZARD_RECOVERY_SETTINGS = (
    "wizard_in_progress",
    "wizard_last_exit",
    "wizard_last_step",
    "wizard_recovery_available",
)


def _mark_wizard_step(addon, step):
    _set(addon, "wizard_in_progress", "true")
    _set(addon, "wizard_last_step", step)


def _mark_wizard_started(addon):
    _set(addon, "wizard_in_progress", "true")
    _set(addon, "wizard_last_exit", "running")
    _set(addon, "wizard_last_step", "started")


def _mark_wizard_cancelled(addon, step, prior_completed=False):
    _set(addon, "wizard_in_progress", "false")
    _set(addon, "wizard_last_exit", "cancelled")
    _set(addon, "wizard_last_step", step)
    _set(addon, "wizard_recovery_available", "true")
    if not prior_completed:
        _set(addon, "wizard_completed", "false")
    return False


def _mark_wizard_error(addon, step, prior_completed=False):
    _set(addon, "wizard_in_progress", "false")
    _set(addon, "wizard_last_exit", "error")
    _set(addon, "wizard_last_step", step)
    _set(addon, "wizard_recovery_available", "true")
    if not prior_completed:
        _set(addon, "wizard_completed", "false")


def _mark_wizard_completed(addon):
    _set(addon, "wizard_in_progress", "false")
    _set(addon, "wizard_last_exit", "completed")
    _set(addon, "wizard_last_step", "completed")
    _set(addon, "wizard_recovery_available", "false")
    _set(addon, "wizard_completed", "true")


def wizard_recovery_summary(addon=None):
    """Return a small support summary for cancel/retry/partial setup states."""
    a = addon if addon is not None else _addon()
    return {
        "completed": _get(a, "wizard_completed", "false"),
        "in_progress": _get(a, "wizard_in_progress", "false"),
        "last_exit": _get(a, "wizard_last_exit", ""),
        "last_step": _get(a, "wizard_last_step", ""),
        "recovery_available": _get(a, "wizard_recovery_available", "false"),
    }


def _addon():
    return xbmcaddon.Addon(ADDON_ID) if xbmcaddon else None


def _set(a, k, v):
    if a is not None:
        try:
            a.setSetting(k, str(v))
        except Exception:
            pass


def _get(a, k, d=""):
    if a is not None:
        try:
            return a.getSetting(k) or d
        except Exception:
            pass
    return d


def _yn(t, m):
    return bool(xbmcgui.Dialog().yesno(t, m)) if xbmcgui else False


def _ok(t, m):
    if xbmcgui:
        xbmcgui.Dialog().ok(t, m)


def show_xml_naming_warning():
    """Surface the v2.5.3 Build 2 naming-discipline warning for XML mode."""
    _ok(_text("xml_naming_title"), _text("xml_naming_body"))


def _in(t, d=""):
    if xbmcgui:
        v = xbmcgui.Dialog().input(t, d)
        return v if v else d
    return d


def _sel(t, opts, preselect=0):
    if xbmcgui:
        try:
            i = xbmcgui.Dialog().select(t, opts, preselect=preselect)
        except TypeError:
            i = xbmcgui.Dialog().select(t, opts)
        return i if i >= 0 else preselect
    return preselect


def _probe(h, p, to=3.0):
    try:
        with socket.create_connection((h, int(p)), timeout=float(to)):
            return True
    except Exception:
        return False


class _AddonSettingsAdapter(dict):
    """Tiny adapter so v0.9.14 compatibility helpers can read/write xbmcaddon settings."""

    def __init__(self, addon):
        super().__init__()
        self._addon = addon
        self.data = self

    def get(self, key, default=None):
        return _get(self._addon, key, default)

    def __getitem__(self, key):
        value = self.get(key, "")
        if value == "":
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        _set(self._addon, key, value)


class _WizardUiAdapter:
    """Expose the small v0.9.14 wizard UI surface through the active wizard."""

    def ok(self, title, message=None):
        _ok(title, message if message is not None else "")

    def notify(self, message):
        _ok("Compatibility warning", message)

    def show_text(self, message):
        _ok("Compatibility warning", message)


def _wizard_log(message):
    try:
        if xbmc:
            xbmc.log(format_log_message("wizard", message), getattr(xbmc, "LOGINFO", 1))
    except Exception:
        pass


def _compat_bool(value, default=False):
    """Return Kodi-style boolean truth for compatibility wizard settings."""
    if isinstance(value, bool):
        return value
    try:
        text = str(value).strip().lower()
    except Exception:
        return bool(default)
    if text == "":
        return bool(default)
    return text in ("1", "true", "yes", "on")


def _compat_flags_from_settings(addon):
    """Read v0.9.14 compatibility flags from the active addon settings."""
    return {
        "jailbreak": _compat_bool(_get(addon, "oppo_jailbreak_enabled", "false")),
        "uses_autoscript_shell": _compat_bool(
            _get(addon, "oppo_autoscript_shell_handler", "false")
        ),
    }


def _ask_compatibility_flags(addon, model_key, is_full=False):
    """Ask/store v0.9.14 compatibility flags in the active wizard full path.

    Build 11 reduces the remaining wizard/UI reconciliation gap by asking for
    the jailbreak JSON-payload flag and AutoScript port-23 shell-handler flag
    inside the active v1.x wizard.  Basic mode remains non-invasive and simply
    uses existing settings values.
    """
    flags = _compat_flags_from_settings(addon)
    if not is_full:
        return flags

    model = str(model_key or "").lower()
    is_stock_oppo = model in (
        "udp_203",
        "udp_205",
        "udp-203",
        "udp-205",
        "udp_203_jailbroken",
        "udp_205_jailbroken",
    )
    if is_stock_oppo:
        jailbreak = _yn(_text("stock_jailbreak_title"), _text("stock_jailbreak_body"))
        flags["jailbreak"] = bool(jailbreak)
        _set(addon, "oppo_jailbreak_enabled", "true" if jailbreak else "false")

    autoscript_shell = _yn(_text("autoscript_title"), _text("autoscript_body"))
    flags["uses_autoscript_shell"] = bool(autoscript_shell)
    _set(addon, "oppo_autoscript_shell_handler", "true" if autoscript_shell else "false")
    return flags


def player_hardware_guidance_text(model_key):
    """Return Build 4 player class guidance for wizard/readiness surfaces.

    This helper is copy-only and read-only. It does not change settings, command
    payloads, playback routing, service interception, or hardware behavior.
    """
    try:
        from .hardware_capabilities import format_player_setup_guidance
    except Exception:
        try:
            from hardware_capabilities import format_player_setup_guidance  # type: ignore
        except Exception as exc:
            _wizard_log(f"player hardware guidance import failed: {exc!r}")
            return _text("player_hardware_guidance_fallback")
    try:
        return format_player_setup_guidance(model_key)
    except Exception as exc:
        _wizard_log(f"player hardware guidance rendering failed: {exc!r}")
        return _text("player_hardware_guidance_fallback")


def _surface_player_hardware_guidance(addon, model_key):
    """Show Build 4 player class guidance after the model selection step."""
    _ok(_text("player_hardware_guidance_title"), player_hardware_guidance_text(model_key))
    return True


def _surface_hardware_compatibility_warnings(
    addon, model_key, ui=None, jailbreak=None, uses_autoscript_shell=None
):
    """Surface v0.9.14 compatibility warnings from the active v1.x wizard path.

    Build 6 wires the warning-surfacing helper into the active wizard without
    replacing the wizard flow or changing the user's existing clone-preset
    confirmation behavior.  It is intentionally warning-only.
    """
    try:
        from first_run_wizard import collect_compatibility_warnings, surface_compatibility_warnings
    except Exception as exc:
        _wizard_log(f"v0.9.14 wizard warning integration import failed: {exc!r}")
        return 0
    flags = _compat_flags_from_settings(addon)
    if jailbreak is not None:
        flags["jailbreak"] = bool(jailbreak)
    if uses_autoscript_shell is not None:
        flags["uses_autoscript_shell"] = bool(uses_autoscript_shell)
    settings = _AddonSettingsAdapter(addon)
    warnings = collect_compatibility_warnings(
        settings=settings,
        model=model_key,
        jailbreak=flags["jailbreak"],
        uses_autoscript_shell=flags["uses_autoscript_shell"],
    )
    return surface_compatibility_warnings(ui or _WizardUiAdapter(), warnings, _log=_wizard_log)


def _apply_and_surface_hardware_compatibility(
    addon, model_key, ui=None, jailbreak=None, uses_autoscript_shell=None
):
    """Apply compatible v0.9.14 wizard settings and surface warnings.

    This deliberately remains a small bridge: it lets stock jailbroken OPPO
    selections apply the JSON-payload mode and lets Reavon remain warning-only.
    Chinoppo clone command changes are still handled by the existing explicit
    active-wizard confirmation path for stability.
    """
    try:
        from first_run_wizard import apply_and_surface_compatibility
    except Exception as exc:
        _wizard_log(f"v0.9.14 wizard apply integration import failed: {exc!r}")
        return {"applied": [], "warnings": [], "surfaced": 0}
    flags = _compat_flags_from_settings(addon)
    if jailbreak is not None:
        flags["jailbreak"] = bool(jailbreak)
    if uses_autoscript_shell is not None:
        flags["uses_autoscript_shell"] = bool(uses_autoscript_shell)
    return apply_and_surface_compatibility(
        _AddonSettingsAdapter(addon),
        model_key,
        jailbreak=flags["jailbreak"],
        uses_autoscript_shell=flags["uses_autoscript_shell"],
        ui=ui or _WizardUiAdapter(),
        _log=_wizard_log,
    )


def _choose_mode(addon):
    prev = (_get(addon, "wizard_mode", "basic") or "basic").lower()
    options = [
        "Basic - just the essentials (~5 questions)",
        "Full  - configure every option (~12+ questions)",
    ]
    pre = 0 if prev == "basic" else 1
    idx = _sel("Configuration mode", options, preselect=pre)
    mode = "basic" if idx == 0 else "full"
    _set(addon, "wizard_mode", mode)
    return mode


class _ArchTestResult:
    __slots__ = ("reachable", "recommended", "details")

    def __init__(self, reachable, recommended, details):
        self.reachable = reachable
        self.recommended = recommended
        self.details = details


def _run_benchmark(
    host,
    port,
    trials=3,
    timer=None,
    probe_external=None,
    probe_service=None,
    playercorefactory_path=None,
):
    """Bridge the wizard to arch_benchmark.run_full. Tests can inject
    deterministic probes/timer; production wires real socket probes."""
    try:
        from . import arch_benchmark as ab
    except (ImportError, ValueError):
        import arch_benchmark as ab

    if probe_external is None:

        def probe_external(_):
            try:
                _probe(host, int(port), timeout=1.5)
            except Exception:
                raise

    if probe_service is None:

        def probe_service(_):
            try:
                _probe(host, int(port), timeout=1.5)
            except Exception:
                raise

    return ab.run_full(
        probe_external=probe_external,
        probe_service=probe_service,
        trials=int(trials),
        timer=timer,
        playercorefactory_path=playercorefactory_path,
    )


def auto_test_architecture(addon, ip, port):
    """Architecture auto-test.

    Returns _ArchTestResult(reachable, recommended, details).
    External Player is recommended in all reachable cases (safe default).
    """
    reachable = _probe(ip, port, to=2.0)
    hw = (_get(addon, "oppo_hardware_model", "udp_203") or "udp_203").lower()
    if not reachable:
        rec = _get(addon, "playback_architecture", "external_player") or "external_player"
        msg = (
            "Could not reach "
            + str(ip)
            + ":"
            + str(port)
            + ". Kept current architecture ("
            + rec
            + "). Retry later if needed."
        )
        return _ArchTestResult(False, rec, msg)
    rec = "external_player"
    try:
        from hardware_presets import is_chinoppo_family as _ifc

        chinoppo = _ifc(hw)
    except Exception:
        chinoppo = hw == "chinoppo"
    if chinoppo:
        msg = (
            "Player reachable. Hardware: Chinoppo-class.\n"
            "External Player is recommended for Chinoppo-class devices."
        )
    else:
        msg = (
            "Player reachable.\n" "External Player is the recommended architecture for most setups."
        )
    return _ArchTestResult(True, rec, msg)


def _run_architecture_auto_test(addon, ip, port):
    res = auto_test_architecture(addon, ip, port)
    if not res.reachable:
        _ok("Architecture auto-test", res.details)
        return res
    if xbmcgui:
        txt = res.details + "\n\nApply '" + res.recommended + "' now?"
        if xbmcgui.Dialog().yesno("Architecture auto-test", txt):
            _set(addon, "playback_architecture", res.recommended)
            _set(addon, "architecture_choice_made", "true")
            _ok("Architecture set", "Recommendation applied.")
    else:
        _set(addon, "playback_architecture", res.recommended)
        _set(addon, "architecture_choice_made", "true")
    return res


def _maybe_generate_transfer_files(addon):
    """Generate ready-to-transfer setup files at the end of the wizard.

    Returns a short message (appended to the completion dialog) listing the
    files written, or "" when generation is unavailable. playercorefactory.xml
    is written only for external-player mode; the remote keymap is always
    written. Any failure is non-fatal and simply yields no note so the wizard
    still completes.
    """
    if xbmc is None:
        return ""
    try:
        import installer
    except Exception as exc:  # pragma: no cover - only when Kodi libs are absent
        _wizard_log(f"transfer file generation skipped: {exc!r}")
        return ""
    try:
        arch = _get(addon, "playback_architecture", "external_player") or "external_player"
        is_external = arch != "service_interception"
        paths = installer.generate_transfer_files(
            include_playercorefactory=is_external,
            include_keymap=True,
            announce=False,
        )
    except Exception as exc:
        _wizard_log(f"transfer file generation failed: {exc!r}")
        return ""
    if not paths:
        return ""
    lines = ["", "", "Setup files written (copy into your Kodi userdata folder):"]
    if "playercorefactory" in paths:
        lines.append("- " + str(paths["playercorefactory"]))
    if "keymap" in paths:
        lines.append("- " + str(paths["keymap"]))
    return "\n".join(lines)


def run_wizard():
    a = _addon()
    prior_completed = _compat_bool(_get(a, "wizard_completed", "false"))
    current_step = "started"
    _mark_wizard_started(a)
    try:
        _mark_wizard_step(a, "welcome")
        _ok(_text("welcome_title"), _text("welcome_body"))
        current_step = "mode"
        _mark_wizard_step(a, current_step)
        mode = _choose_mode(a)
        is_full = mode == "full"
        current_step = "prerequisites"
        _mark_wizard_step(a, current_step)
        if not _yn(_text("prerequisites_title"), _text("prerequisites_body")):
            return _mark_wizard_cancelled(a, current_step, prior_completed=prior_completed)
        current_step = "network"
        _mark_wizard_step(a, current_step)
        ip = _in("Oppo IP", _get(a, "oppo_ip", "192.168.1.50"))
        _set(a, "oppo_ip", ip)
        port = _in("Oppo port", _get(a, "oppo_port", "23"))
        _set(a, "oppo_port", port)
        if _probe(ip, port):
            _ok("Reachable", "TCP " + ip + ":" + str(port) + " ok.")
        else:
            current_step = "network_unreachable"
            _mark_wizard_step(a, current_step)
            if not _yn(_text("unreachable_title"), _text("unreachable_body")):
                return _mark_wizard_cancelled(a, current_step, prior_completed=prior_completed)
        try:
            from hardware_presets import (
                is_chinoppo_family,
                list_presets,
                select_recommended_power_delay,
            )

            pairs = list_presets()
            models = [lbl for _, lbl in pairs]
            keys = [k for k, _ in pairs]
        except Exception:
            models = ["UDP-203", "UDP-205", "Chinoppo / M9702", "Reavon", "Jailbroken OPPO"]
            keys = ["udp_203", "udp_205", "chinoppo", "reavon", "jailbroken_203_205"]

            def is_chinoppo_family(k):
                return k == "chinoppo"

            def select_recommended_power_delay(k):
                return 5

        current_step = "hardware"
        _mark_wizard_step(a, current_step)
        idx = _sel("Hardware", models)
        selected_key = keys[idx]
        _set(a, "oppo_hardware_model", selected_key)
        _surface_player_hardware_guidance(a, selected_key)
        current_step = "compatibility"
        _mark_wizard_step(a, current_step)
        compat_flags = _ask_compatibility_flags(a, selected_key, is_full=is_full)
        if is_chinoppo_family(selected_key):
            _surface_hardware_compatibility_warnings(
                a,
                selected_key,
                jailbreak=compat_flags["jailbreak"],
                uses_autoscript_shell=compat_flags["uses_autoscript_shell"],
            )
        else:
            _apply_and_surface_hardware_compatibility(
                a,
                selected_key,
                jailbreak=compat_flags["jailbreak"],
                uses_autoscript_shell=compat_flags["uses_autoscript_shell"],
            )
        if is_chinoppo_family(selected_key):
            current_step = "chinoppo_preset"
            _mark_wizard_step(a, current_step)
            if _yn(_text("chinoppo_preset_title"), _text("chinoppo_preset_body")):
                _set(a, "oppo_start_commands", "#EJT\n#PLA")
                _set(a, "oppo_start_mode", "tcp_commands")
                _set(a, "oppo_http_activate", "false")
            if is_full and _yn("Chinoppo AutoScript", "Generate autoexec.sh now?"):
                try:
                    from autoscript_helper import run_autoscript_wizard

                    run_autoscript_wizard(a)
                except Exception as exc:
                    _ok("AutoScript failed", str(exc))
        current_step = "quick_start"
        _mark_wizard_step(a, current_step)
        quick = _yn(_text("quick_start_title"), _text("quick_start_body"))
        _set(a, "quick_start_confirmed", "true" if quick else "false")
        current_step = "autopower"
        _mark_wizard_step(a, current_step)
        auto = _yn(_text("autopower_title"), _text("autopower_body"))
        _set(a, "kodi_startup_power_on", "true" if auto else "false")
        if auto:
            rec = str(select_recommended_power_delay(selected_key))
            _set(a, "kodi_startup_power_on_delay", rec)
        if auto and is_full:
            current_step = "autopower_advanced"
            _mark_wizard_step(a, current_step)
            _set(
                a,
                "kodi_startup_power_on_delay",
                _in("Delay (sec)", _get(a, "kodi_startup_power_on_delay", "5")),
            )
            _set(
                a,
                "kodi_startup_power_on_retries",
                _in("Retries", _get(a, "kodi_startup_power_on_retries", "3")),
            )
            if _yn(_text("wol_title"), _text("wol_body")):
                _set(a, "kodi_startup_power_on_use_wol", "true")
                mac = _in("MAC", _get(a, "oppo_mac", ""))
                if mac:
                    _set(a, "oppo_mac", mac)
                    _set(a, "oppo_use_wol", "true")
            else:
                _set(a, "kodi_startup_power_on_use_wol", "false")
        if is_full and _yn(_text("arch_test_title"), _text("arch_test_body")):
            current_step = "architecture_auto_test"
            _mark_wizard_step(a, current_step)
            _run_architecture_auto_test(a, ip, port)
        current_step = "architecture"
        _mark_wizard_step(a, current_step)
        if is_full:
            use_ext = _yn(_text("architecture_title"), _text("architecture_body"))
            _set(
                a, "playback_architecture", "external_player" if use_ext else "service_interception"
            )
        else:
            if not _get(a, "playback_architecture"):
                _set(a, "playback_architecture", "external_player")
        _set(a, "architecture_choice_made", "true")
        if (
            _get(a, "playback_architecture", "external_player") or "external_player"
        ) == "external_player":
            current_step = "xml_naming_warning"
            _mark_wizard_step(a, current_step)
            show_xml_naming_warning()
        _mark_wizard_completed(a)
        _ok(
            "Wizard complete (" + ("Full" if is_full else "Basic") + ")",
            _text("wizard_complete_body") + _maybe_generate_transfer_files(a),
        )
        return True
    except Exception:
        _mark_wizard_error(a, current_step, prior_completed=prior_completed)
        raise


def avr_wizard_support_metadata():
    """Return Build 16 AVR wizard capability metadata without side effects."""
    try:
        from .avr_diagnostics import wizard_capabilities, wizard_family_options
    except Exception:
        from avr_diagnostics import wizard_capabilities, wizard_family_options  # type: ignore
    data = wizard_capabilities()
    data["options"] = wizard_family_options()
    return data


def run_avr_setup_wizard(addon=None):
    """Run the optional Build 16 AVR setup wizard.

    The flow only writes AVR settings. It never sends AVR commands, never hooks
    playback sequencing, and keeps hardware validation unclaimed.
    """
    a = addon if addon is not None else _addon()
    try:
        from .avr_diagnostics import apply_wizard_selection, wizard_family_options
    except Exception:
        from avr_diagnostics import apply_wizard_selection, wizard_family_options  # type: ignore

    if not _yn(_text("avr_setup_title"), _text("avr_setup_body")):
        selection = {"skip_avr_setup": True}
        updated = apply_wizard_selection(
            {"avr_control_enabled": _get(a, "avr_control_enabled", "false")}, selection
        )
        for key, value in updated.items():
            _set(a, key, value)
        return updated

    options = list(wizard_family_options())
    labels = [str(item.get("label", item.get("id", ""))) for item in options]
    idx = _sel(_text("avr_family_title"), labels)
    chosen = dict(options[idx])
    backend = str(chosen.get("backend", chosen.get("id", "disabled")))
    if backend == "disabled":
        chosen["skip_avr_setup"] = True
    else:
        chosen["avr_backend"] = backend
        chosen["avr_host"] = _in(_text("avr_host_title"), _get(a, "avr_host", ""))
        default_port = str(chosen.get("default_port") or _get(a, "avr_port", ""))
        chosen["avr_port"] = _in(_text("avr_port_title"), default_port)
        chosen["avr_player_input"] = _in(
            _text("avr_player_input_title"), _get(a, "avr_player_input", "")
        )
        if _yn("AVR restore", "Configure optional AVR restore input?"):
            chosen["avr_restore_enabled"] = "true"
            chosen["avr_restore_input"] = _in(
                _text("avr_restore_input_title"), _get(a, "avr_restore_input", "")
            )
        if _yn("AVR sound mode", "Store optional sound mode metadata?"):
            chosen["avr_sound_mode"] = _in(
                _text("avr_sound_mode_title"), _get(a, "avr_sound_mode", "")
            )
        if backend == "sony_audio_api":
            chosen["sony_avr_experimental_acknowledged"] = (
                "true" if _yn(_text("sony_avr_ack_title"), _text("sony_avr_ack_body")) else "false"
            )
    current = {
        key: _get(a, key, "")
        for key in (
            "avr_control_enabled",
            "avr_backend",
            "selected_avr_preset_id",
            "avr_host",
            "avr_port",
            "avr_player_input",
            "avr_restore_enabled",
            "avr_restore_input",
            "avr_power_off_enabled",
            "avr_volume_automation_enabled",
            "avr_sound_mode",
            "sony_avr_experimental_acknowledged",
            "sony_avr_psk",
            "sony_avr_api_path",
            "sony_avr_player_input_uri",
            "sony_avr_restore_input_uri",
        )
    }
    updated = apply_wizard_selection(current, chosen)
    for key, value in updated.items():
        _set(a, key, value)
    _ok(_text("avr_setup_title"), _text("avr_setup_complete_body"))
    return updated


def reset_wizard():
    a = _addon()
    _set(a, "wizard_completed", "false")
    _ok("Wizard reset", "Will run on next add-on open.")
