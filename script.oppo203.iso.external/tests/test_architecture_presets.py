"""Seven-option playback architecture preset mapping + migration.

These pin the two new normalized axes (``playback_monitor_mode`` alongside the
existing ``playback_architecture``) and the combined
``playback_architecture_preset`` so they cannot drift apart:

* ``architecture_preset()`` maps a routing axis + monitor axis to one of the seven
  preset ids, accepting both the stored ``external_player`` spelling and the
  ``playercorefactory`` preset spelling.
* ``normalize_architecture()`` treats an explicit, valid preset as the source of
  truth and otherwise back-fills it from the legacy fields -- so installs created
  before the preset existed keep their exact current behavior.

No runtime playback behavior changes in this PR; the value is only read.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import resources.lib.kodi.settings_reader as sr


class ArchitecturePresetDefaults(unittest.TestCase):
    def test_monitor_mode_default_is_legacy(self):
        self.assertEqual(sr.DEFAULTS["playback_monitor_mode"], "legacy")

    def test_monitor_mode_enum_values(self):
        self.assertEqual(sr.ENUM_VALUES["playback_monitor_mode"], ["legacy", "svm3", "http"])
        self.assertEqual(tuple(sr.ENUM_VALUES["playback_monitor_mode"]), sr.PLAYBACK_MONITOR_MODES)

    def test_preset_has_no_default_so_absence_means_derive(self):
        # A default preset would mask a pre-existing service_interception install;
        # the preset is configurator-written and intentionally absent by default.
        self.assertNotIn("playback_architecture_preset", sr.DEFAULTS)
        self.assertNotIn("playback_architecture_preset", sr.ENUM_VALUES)

    def test_legacy_defaults_are_mutually_consistent(self):
        # The default routing + monitor must derive the legacy default preset, so a
        # fresh, unconfigured install is never self-contradictory.
        self.assertEqual(
            sr.architecture_preset(
                sr.DEFAULTS["playback_architecture"], sr.DEFAULTS["playback_monitor_mode"]
            ),
            "playercorefactory_legacy",
        )


class ArchitecturePresetMapping(unittest.TestCase):
    def test_all_four_combos_preset_vocabulary(self):
        self.assertEqual(
            sr.architecture_preset("playercorefactory", "legacy"), "playercorefactory_legacy"
        )
        self.assertEqual(
            sr.architecture_preset("service_interception", "legacy"),
            "service_interception_legacy",
        )
        self.assertEqual(
            sr.architecture_preset("playercorefactory", "svm3"), "playercorefactory_svm3"
        )
        self.assertEqual(
            sr.architecture_preset("service_interception", "svm3"), "service_interception_svm3"
        )

    def test_external_player_alias_maps_to_playercorefactory(self):
        self.assertEqual(
            sr.architecture_preset("external_player", "legacy"), "playercorefactory_legacy"
        )
        self.assertEqual(
            sr.architecture_preset("external_player", "svm3"), "playercorefactory_svm3"
        )

    def test_unknown_routing_falls_back_to_playercorefactory(self):
        self.assertEqual(sr.architecture_preset("nonsense", "svm3"), "playercorefactory_svm3")

    def test_unknown_monitor_falls_back_to_legacy(self):
        self.assertEqual(
            sr.architecture_preset("service_interception", "bogus"),
            "service_interception_legacy",
        )

    def test_mapping_is_case_and_whitespace_insensitive(self):
        self.assertEqual(
            sr.architecture_preset("  EXTERNAL_PLAYER ", " SVM3 "), "playercorefactory_svm3"
        )

    def test_http_handoff_combos(self):
        self.assertIn("http_handoff", sr.PLAYBACK_ROUTING_MODES)
        self.assertEqual(sr.architecture_preset("http_handoff", "legacy"), "http_handoff_legacy")
        self.assertEqual(sr.architecture_preset("http_handoff", "svm3"), "http_handoff_svm3")

    def test_http_monitor_is_a_mode_and_yields_the_seventh_preset(self):
        self.assertIn("http", sr.PLAYBACK_MONITOR_MODES)
        self.assertEqual(sr.architecture_preset("http_handoff", "http"), "http_handoff_http")
        self.assertEqual(sr.architecture_preset("  HTTP_HANDOFF ", " HTTP "), "http_handoff_http")

    def test_http_monitor_clamps_to_legacy_for_non_http_handoff_routings(self):
        # The http monitor is an asymmetric cell -- only http_handoff has it. Any other routing
        # paired with "http" clamps to that routing's legacy preset (and never KeyErrors).
        self.assertEqual(
            sr.architecture_preset("playercorefactory", "http"), "playercorefactory_legacy"
        )
        self.assertEqual(
            sr.architecture_preset("service_interception", "http"), "service_interception_legacy"
        )
        self.assertEqual(
            sr.architecture_preset("external_player", "http"), "playercorefactory_legacy"
        )


class NormalizeArchitecture(unittest.TestCase):
    def test_explicit_preset_is_source_of_truth(self):
        norm = sr.normalize_architecture(
            sr.Settings({"playback_architecture_preset": "service_interception_svm3"})
        )
        self.assertEqual(
            norm,
            {
                "preset": "service_interception_svm3",
                "routing": "service_interception",
                "monitor_mode": "svm3",
            },
        )

    def test_explicit_preset_overrides_stale_normalized_fields(self):
        # Drift: the preset disagrees with the legacy fields. The preset wins.
        norm = sr.normalize_architecture(
            sr.Settings(
                {
                    "playback_architecture_preset": "playercorefactory_svm3",
                    "playback_architecture": "service_interception",
                    "playback_monitor_mode": "legacy",
                }
            )
        )
        self.assertEqual(norm["preset"], "playercorefactory_svm3")
        self.assertEqual(norm["routing"], "playercorefactory")
        self.assertEqual(norm["monitor_mode"], "svm3")

    def test_fresh_install_normalizes_to_legacy_default(self):
        norm = sr.normalize_architecture(sr.Settings({}))
        self.assertEqual(norm["preset"], "playercorefactory_legacy")
        self.assertEqual(norm["routing"], "playercorefactory")
        self.assertEqual(norm["monitor_mode"], "legacy")

    def test_pre_preset_external_player_install_backfills(self):
        # Install predating the preset: only playback_architecture is configured.
        norm = sr.normalize_architecture(sr.Settings({"playback_architecture": "external_player"}))
        self.assertEqual(norm["preset"], "playercorefactory_legacy")
        self.assertEqual(norm["monitor_mode"], "legacy")

    def test_pre_preset_service_interception_install_backfills(self):
        norm = sr.normalize_architecture(
            sr.Settings({"playback_architecture": "service_interception"})
        )
        self.assertEqual(norm["preset"], "service_interception_legacy")
        self.assertEqual(norm["routing"], "service_interception")

    def test_backfill_respects_explicit_monitor_mode(self):
        norm = sr.normalize_architecture(
            sr.Settings(
                {"playback_architecture": "external_player", "playback_monitor_mode": "svm3"}
            )
        )
        self.assertEqual(norm["preset"], "playercorefactory_svm3")
        self.assertEqual(norm["monitor_mode"], "svm3")

    def test_backfill_invalid_monitor_falls_back_to_legacy(self):
        norm = sr.normalize_architecture(
            sr.Settings(
                {"playback_architecture": "external_player", "playback_monitor_mode": "weird"}
            )
        )
        self.assertEqual(norm["monitor_mode"], "legacy")
        self.assertEqual(norm["preset"], "playercorefactory_legacy")

    def test_invalid_preset_triggers_backfill(self):
        norm = sr.normalize_architecture(
            sr.Settings(
                {
                    "playback_architecture_preset": "garbage",
                    "playback_architecture": "service_interception",
                }
            )
        )
        self.assertEqual(norm["preset"], "service_interception_legacy")

    def test_http_handoff_preset_is_source_of_truth(self):
        norm = sr.normalize_architecture(
            sr.Settings({"playback_architecture_preset": "http_handoff_svm3"})
        )
        self.assertEqual(norm["routing"], "http_handoff")
        self.assertEqual(norm["monitor_mode"], "svm3")

    def test_http_handoff_backfills_from_legacy_fields(self):
        norm = sr.normalize_architecture(
            sr.Settings(
                {"playback_architecture": "http_handoff", "playback_monitor_mode": "legacy"}
            )
        )
        self.assertEqual(norm["preset"], "http_handoff_legacy")
        self.assertEqual(norm["routing"], "http_handoff")

    def test_http_handoff_http_preset_is_source_of_truth(self):
        norm = sr.normalize_architecture(
            sr.Settings({"playback_architecture_preset": "http_handoff_http"})
        )
        self.assertEqual(norm["routing"], "http_handoff")
        self.assertEqual(norm["monitor_mode"], "http")
        self.assertEqual(norm["preset"], "http_handoff_http")

    def test_http_monitor_backfill_on_non_http_routing_clamps_to_legacy(self):
        # An install with playback_monitor_mode=http but a non-http_handoff routing must not
        # produce an invalid (routing, "http") preset -- it backfills to that routing's legacy.
        norm = sr.normalize_architecture(
            sr.Settings(
                {"playback_architecture": "service_interception", "playback_monitor_mode": "http"}
            )
        )
        self.assertEqual(norm["preset"], "service_interception_legacy")
        self.assertEqual(norm["monitor_mode"], "legacy")


class PresetConsistencyGuard(unittest.TestCase):
    def test_every_preset_round_trips(self):
        # Pin preset <-> normalized: normalizing a settings object carrying only a
        # preset must yield routing/monitor that map back to the same preset.
        self.assertEqual(len(sr.PLAYBACK_ARCHITECTURE_PRESETS), 7)
        for preset in sr.PLAYBACK_ARCHITECTURE_PRESETS:
            norm = sr.normalize_architecture(sr.Settings({"playback_architecture_preset": preset}))
            self.assertEqual(norm["preset"], preset)
            self.assertIn(norm["routing"], sr.PLAYBACK_ROUTING_MODES)
            self.assertIn(norm["monitor_mode"], sr.PLAYBACK_MONITOR_MODES)
            self.assertEqual(sr.architecture_preset(norm["routing"], norm["monitor_mode"]), preset)


if __name__ == "__main__":
    unittest.main()
