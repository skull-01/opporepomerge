"""M3 guard: every configurator-emitted architecture / HDMI / HTTP key is declared in
resources/settings.xml so a Kodi settings-GUI save preserves it instead of silently dropping
it (Kodi regenerates settings.xml from the schema and discards undeclared ids)."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SETTINGS_XML = ROOT / "resources" / "settings.xml"

# Keys the configurator writes into addon_data/settings.xml (configurator/src/mapping.ts) that
# are not otherwise declared by a visible setting.
CONFIGURATOR_OWNED_KEYS = (
    "playback_architecture",
    "architecture_choice_made",
    "playback_monitor_mode",
    "playback_architecture_preset",
    "hdmi_switch_mode",
    "play_delay_hdmi",
    "av_delay_hdmi",
    "oppo_http_refresh_seconds",
    "oppo_bdmv_checkfolder",
)

# These five also carry a DEFAULTS entry; playback_architecture_preset is deliberately absent
# from DEFAULTS (its empty value drives the normalize_architecture back-fill).
DEFAULTED_KEYS = (
    "hdmi_switch_mode",
    "play_delay_hdmi",
    "av_delay_hdmi",
    "oppo_http_refresh_seconds",
    "oppo_bdmv_checkfolder",
)


def _declared_ids():
    root = ET.parse(SETTINGS_XML).getroot()
    return {s.get("id") for s in root.iter("setting")}


def test_configurator_owned_keys_are_declared_in_settings_xml():
    declared = _declared_ids()
    missing = [k for k in CONFIGURATOR_OWNED_KEYS if k not in declared]
    assert not missing, f"configurator-owned keys missing from settings.xml: {missing}"


def test_timing_keys_have_defaults_and_preset_does_not():
    from resources.lib.kodi import settings_reader as sr

    for key in DEFAULTED_KEYS:
        assert key in sr.DEFAULTS, f"{key} missing from DEFAULTS"
    assert "playback_architecture_preset" not in sr.DEFAULTS  # must stay empty for the back-fill
