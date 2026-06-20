"""ENH-#43 test support: legacy addon module name -> canonical sub-package path.

Stub-context managers purge addon modules from ``sys.modules`` so each test
re-imports a fresh, stub-bound copy. After the resources/lib split, importing a
legacy flat name (``resources.lib.installer`` / bare ``installer``) resolves via
the alias finder to a canonical ``resources.lib.<bucket>.<module>`` object. A
context that pops only the legacy name leaves that canonical object cached, so
the next test gets a stale module. ``with_canonical`` adds the canonical path for
every legacy name so both are purged/restored together.
"""

_BUCKETS = {
    "tv": "tv_adb_control tv_roku_ecp_control tv_smartthings_control tv_backends tv_control tv_diagnostics tv_presets",
    "avr": "avr_control avr_denon_marantz avr_onkyo_eiscp avr_presets avr_sequence avr_sony_audio avr_types avr_yamaha avr_diagnostics",
    "oppo": "oppo_control oppo_remote oppo_tcp_client playback_monitor_svm3 playback_monitor_http command_map constants discovery reconnect_backoff hardware_capabilities hardware_presets hardware_profiles hardware_validation_readiness path_mapper nas_playback_adapter autoscript_helper",
    "kodi": "installer intercept disc_classification settings_reader settings_schema keymap_skin playercorefactory_merge i18n diagnostic_logging diagnostic_summary logging_v116 diagnostics arch_benchmark external_player playback_session hdmi_sequencing version",
}
_CANONICAL = {
    mod: f"resources.lib.{bucket}.{mod}"
    for bucket, mods in _BUCKETS.items()
    for mod in mods.split()
}


def with_canonical(names):
    """Return ``names`` plus the canonical ``resources.lib.<bucket>.<module>``
    path for every legacy flat addon name (bare or ``resources.lib.<module>``)."""
    result = set(names)
    for name in set(names):
        canonical = _CANONICAL.get(name.split(".")[-1])
        if canonical is not None:
            result.add(canonical)
    return result
