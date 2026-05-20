"""Hardware-validation readiness helper for OPPO ISO External.

v2.5.3 Build 5 adds a read-only readiness/export helper for testers.  The
helper prepares a consistent checklist and compact diagnostic report before
real OPPO/Chinoppo/Kodi/NAS/TV/ADB testing.  It does not contact hardware,
launch playback, mutate settings, or claim validation has passed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

try:  # pragma: no cover - import style differs under Kodi and pytest
    from .diagnostic_summary import build_summary, format_summary
    from .hardware_capabilities import nas_direct_playback_gate, player_setup_guidance
    from .hardware_profiles import get_profile, normalize_profile_key
    from .settings_reader import Settings, nas_playback_capability
except Exception:  # pragma: no cover
    from diagnostic_summary import build_summary, format_summary  # type: ignore
    from hardware_capabilities import nas_direct_playback_gate, player_setup_guidance  # type: ignore
    from hardware_profiles import get_profile, normalize_profile_key  # type: ignore
    from settings_reader import Settings, nas_playback_capability  # type: ignore

CHECKLIST = (
    {
        "id": "install_clean_runtime_zip",
        "label": "Install the runtime ZIP in Kodi and confirm the add-on opens without errors.",
        "evidence": "Kodi add-on version screen shows 2.5.3 and no import/runtime error appears.",
    },
    {
        "id": "confirm_player_model",
        "label": "Confirm the configured hardware model matches the real OPPO/Chinoppo device.",
        "evidence": "Record device model, firmware/build, and whether it is stock, jailbroken, or Chinoppo-family firmware.",
    },
    {
        "id": "confirm_network_control",
        "label": "Confirm OPPO TCP control path can power/wake and send a harmless command.",
        "evidence": "Record OPPO IP, port, wake behavior, and command response/result.",
    },
    {
        "id": "confirm_4k_disc_style_interception",
        "label": "Test tagged 4K/UHD/2160p disc-style ISO/BDMV/MPLS playback handoff.",
        "evidence": "Record source path, expected OPPO-visible path, and whether Kodi handed off correctly.",
    },
    {
        "id": "confirm_loose_video_stays_kodi",
        "label": "Test tagged loose/raw video such as MKV/MP4/M2TS/TS/VOB stays with Kodi.",
        "evidence": "Record source path and verify Kodi default player remains active.",
    },
    {
        "id": "confirm_option4_xml_mode",
        "label": "If XML mode is used, confirm naming convention and playercorefactory.xml routing behavior.",
        "evidence": "Record whether filename/path contains 4K, UHD, or 2160p and whether untagged disc-style media remains with Kodi.",
    },
    {
        "id": "confirm_tv_switching_if_enabled",
        "label": "If TV/ADB switching is enabled, confirm switch-to-OPPO and switch-back behavior.",
        "evidence": "Record TV model/input path, ADB result, and whether failures are non-fatal.",
    },
    {
        "id": "record_failure_logs",
        "label": "If any step fails, export Kodi log excerpt plus this readiness report before changing settings.",
        "evidence": "Attach the exported readiness report and relevant Kodi log lines to the handoff/test notes.",
    },
)

REQUIRED_TESTER_RESULTS = (
    "device_model",
    "firmware_or_build",
    "kodi_platform_version",
    "oppo_ip_and_port",
    "test_source_paths",
    "expected_player_visible_paths",
    "observed_handoff_result",
    "loose_video_negative_test_result",
    "tv_switching_result_if_enabled",
    "issues_or_logs",
)


def _as_settings(settings=None, addon_data_dir=None) -> Settings:
    if isinstance(settings, Settings):
        return settings
    if isinstance(settings, dict):
        return Settings(settings)
    if addon_data_dir:
        try:
            from .settings_reader import read_settings
        except Exception:  # pragma: no cover - top-level Kodi import compatibility
            from settings_reader import read_settings  # type: ignore
        return read_settings(addon_data_dir)
    return Settings({})


def build_readiness_report(settings=None, *, addon_data_dir=None, root_dir=None, path_exists=None) -> dict:
    """Return a non-invasive hardware-validation readiness report.

    The report combines the existing diagnostic summary with NAS/AutoScript
    capability gates and a fixed tester checklist.  It is intentionally a
    readiness document, not a hardware pass/fail certificate.
    """
    cfg = _as_settings(settings=settings, addon_data_dir=addon_data_dir)
    summary = build_summary(cfg, root_dir=root_dir, path_exists=path_exists)
    selected_player = normalize_profile_key(cfg.get("oppo_hardware_model"))
    player_profile = get_profile(selected_player)
    capability = nas_playback_capability(
        selected_player,
        firmware=cfg.get("oppo_firmware_version", ""),
        jailbreak=cfg.get_bool("oppo_jailbreak_enabled", False),
        confirmed=cfg.get_bool("nas_playback_confirmed", False),
    )
    gate = nas_direct_playback_gate(selected_player)
    guidance = player_setup_guidance(selected_player)
    blockers = list(summary.get("missing") or []) + list(capability.get("blockers") or [])
    warnings = list(summary.get("warnings") or []) + list(capability.get("warnings") or [])
    option4 = {
        "approved_tags": ["4K", "UHD", "2160p"],
        "disc_style_filetypes": ["iso", "bdmv", "mpls"],
        "loose_video_negative_tests": ["mkv", "mp4", "m2ts", "ts", "vob"],
        "xml_mode_naming_driven": True,
        "metadata_or_iso_internal_inspection": False,
    }
    return {
        "title": "v2.5.3 Build 5 hardware-validation readiness report",
        "hardware_validation_claimed": False,
        "safe_to_claim_hardware_pass": False,
        "ok_for_hardware_test": not blockers,
        "summary": summary,
        "player_hardware": {
            "model": selected_player,
            "hardware_class": player_profile.get("hardware_class", "unknown"),
            "protocol_stance": player_profile.get("protocol_stance", "unknown"),
            "wake_behavior": player_profile.get("wake_behavior", "unknown"),
            "warning_only_successor": bool(gate.get("warning_only_successor")),
            "automatic_oppo_command_map_allowed": bool(gate.get("automatic_oppo_command_map_allowed")),
            "hardware_validation_required": bool(player_profile.get("hardware_validation_required", True)),
            "hardware_validation_claimed": False,
        },
        "player_setup_guidance": guidance,
        "nas_mount_question_status": guidance.get("nas_mount_question_status", "documented_readiness_gate"),
        "nas_direct_playback_gate": gate,
        "nas_playback_capability": capability,
        "option4_xml_mode": option4,
        "checklist": [dict(item) for item in CHECKLIST],
        "required_tester_results": list(REQUIRED_TESTER_RESULTS),
        "warnings": warnings,
        "blockers": blockers,
    }


def format_readiness_report(report: dict) -> str:
    """Render a readiness report as a tester-friendly text export."""
    if not isinstance(report, dict):
        return "OPPO203 hardware-validation readiness report unavailable"
    cap = report.get("nas_playback_capability", {}) or {}
    option4 = report.get("option4_xml_mode", {}) or {}
    lines = [
        "OPPO203 Hardware Validation Readiness Report",
        f"Hardware validation claimed: {'yes' if report.get('hardware_validation_claimed') else 'no'}",
        f"Safe to claim hardware pass: {'yes' if report.get('safe_to_claim_hardware_pass') else 'no'}",
        f"Ready for tester execution: {'yes' if report.get('ok_for_hardware_test') else 'no'}",
        "",
        format_summary(report.get("summary", {})),
        "",
        "Player hardware class gate:",
        f"- Model: {(report.get('player_hardware') or {}).get('model', 'unknown')}",
        f"- Class: {(report.get('player_hardware') or {}).get('hardware_class', 'unknown')}",
        f"- Protocol stance: {(report.get('player_hardware') or {}).get('protocol_stance', 'unknown')}",
        f"- Automatic OPPO command-map allowed: {'yes' if (report.get('player_hardware') or {}).get('automatic_oppo_command_map_allowed') else 'no'}",
        f"- Warning-only successor: {'yes' if (report.get('player_hardware') or {}).get('warning_only_successor') else 'no'}",
        f"- Hardware validation required: {'yes' if (report.get('player_hardware') or {}).get('hardware_validation_required', True) else 'no'}",
        f"- Hardware validation claimed: {'yes' if (report.get('player_hardware') or {}).get('hardware_validation_claimed') else 'no'}",
        "",
        "Player setup guidance:",
        "- " + str((report.get('player_setup_guidance') or {}).get('summary', '')),
        "- " + str((report.get('player_setup_guidance') or {}).get('nas_mount_guidance', '')),
        "",
        "NAS / AutoScript capability gate:",
        f"- Model: {cap.get('model', 'unknown')}",
        f"- Family: {cap.get('family', 'unknown')}",
        f"- Supported for NAS playback path: {'yes' if cap.get('supported') else 'no'}",
        f"- Requires jailbreak: {'yes' if cap.get('requires_jailbreak') else 'no'}",
        f"- Requires capability confirmation: {'yes' if cap.get('requires_capability_confirmation') else 'no'}",
        "",
        "Option 4 XML negative/positive checks:",
        "- Approved tags: " + ", ".join(option4.get("approved_tags", [])),
        "- Disc-style filetypes: " + ", ".join(option4.get("disc_style_filetypes", [])),
        "- Loose-video negative tests: " + ", ".join(option4.get("loose_video_negative_tests", [])),
        "- XML mode is naming-driven; it cannot inspect metadata, NFO files, stream resolution, or ISO internals.",
        "",
        "Tester checklist:",
    ]
    for index, item in enumerate(report.get("checklist") or [], 1):
        lines.append(f"{index}. {item.get('label', '')}")
        lines.append(f"   Evidence to record: {item.get('evidence', '')}")
    lines.extend(["", "Required tester result fields:"])
    for item in report.get("required_tester_results") or []:
        lines.append(f"- {item}")
    blockers = report.get("blockers") or []
    warnings = report.get("warnings") or []
    if blockers:
        lines.append("\nReadiness blockers: " + ", ".join(str(item) for item in blockers))
    if warnings:
        lines.append("Warnings: " + ", ".join(str(item) for item in warnings))
    return "\n".join(lines)


def export_readiness_report(addon_data_dir, report: dict | None = None, *, now=None) -> str:
    """Write the readiness report to addon_data and return the path.

    This is the only mutating helper in this module; it writes a text report
    only.  It does not change settings or contact hardware.
    """
    if not addon_data_dir:
        raise ValueError("addon_data_dir is required")
    timestamp = (now or (lambda: datetime.now(timezone.utc)))().strftime("%Y%m%d-%H%M%S")
    root = Path(addon_data_dir)
    root.mkdir(parents=True, exist_ok=True)
    output = root / f"hardware-validation-readiness-{timestamp}.txt"
    data = report if report is not None else build_readiness_report(addon_data_dir=addon_data_dir)
    output.write_text(format_readiness_report(data), encoding="utf-8")
    return str(output)
