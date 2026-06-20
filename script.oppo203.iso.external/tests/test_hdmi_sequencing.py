"""PR5 (Xnoppo V3 adoption): hdmi_sequencing policy (mode + delays).

Pure arithmetic/policy, no I/O. The ordering wiring is exercised in test_playback_session_modes.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _p in (str(ROOT), str(LIB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from resources.lib.kodi import hdmi_sequencing as hs


def test_switch_mode_default_and_clamp():
    assert hs.switch_mode({}) == "immediate"
    assert hs.switch_mode({"hdmi_switch_mode": "delayed"}) == "delayed"
    assert hs.switch_mode({"hdmi_switch_mode": " DELAYED "}) == "delayed"
    assert hs.switch_mode({"hdmi_switch_mode": "immediate"}) == "immediate"
    assert hs.switch_mode({"hdmi_switch_mode": "bogus"}) == "immediate"


def test_compute_play_delay_base_for_non_disc():
    assert hs.compute_play_delay("/m/film.mkv", "2") == 2
    assert hs.compute_play_delay("/m/film.mkv", "0") == 0
    assert hs.compute_play_delay("/m/film.mkv", "9") == 9
    assert hs.compute_play_delay("/m/film.mkv", "junk") == 2  # default base
    assert hs.compute_play_delay("/m/film.mkv", "-3") == 0  # clamped to >= 0


def test_compute_play_delay_floors_disc_sources_at_six():
    assert hs.compute_play_delay("/m/film.iso", "2") == 6
    assert hs.compute_play_delay("/m/FILM.ISO", "1") == 6
    assert hs.compute_play_delay("/m/Movie/BDMV/index.bdmv", "0") == 6
    assert hs.compute_play_delay("/m/film.iso", "10") == 10  # base above the floor wins


def test_av_stagger():
    assert hs.av_stagger({}) == 0
    assert hs.av_stagger({"av_delay_hdmi": "3"}) == 3
    assert hs.av_stagger({"av_delay_hdmi": "-1"}) == 0
    assert hs.av_stagger({"av_delay_hdmi": "junk"}) == 0
