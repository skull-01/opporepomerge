import bundled from "./presets-db/playback-presets.json";
import type { MonitorMode } from "./state";

/**
 * The canonical six-option playback-architecture preset matrix - the cross-product of 3 routing
 * modes x 2 monitor modes. This JSON is the single cross-language source of truth, shared with the
 * add-on (resources/lib/kodi/settings_reader.py) and pinned to its Python registries by
 * tests/test_playback_presets_consistency.py. Changing the set is a deliberate cross-area contract
 * change - update both sides + this file in lock-step (AGENTS.md: "six playback-architecture
 * presets are a maintained matrix").
 */
export type RoutingMode = "playercorefactory" | "service_interception" | "http_handoff";

export type PlaybackPresetsDb = {
  schema_version: number;
  routing_modes: RoutingMode[];
  monitor_modes: MonitorMode[];
  presets: string[];
  preset_by_axes: { routing: RoutingMode; monitor: MonitorMode; preset: string }[];
  routing_aliases: { alias: string; routing: RoutingMode }[];
};

export const PLAYBACK_PRESETS_DB = bundled as PlaybackPresetsDb;

/** The six canonical preset ids, in the add-on's PLAYBACK_ARCHITECTURE_PRESETS order. */
export const PLAYBACK_PRESETS: readonly string[] = PLAYBACK_PRESETS_DB.presets;

/** Resolve the preset id for a routing + monitor axis pair, or null when the pair is unknown. */
export function presetForAxes(routing: string, monitor: string): string | null {
  const hit = PLAYBACK_PRESETS_DB.preset_by_axes.find(
    (e) => e.routing === routing && e.monitor === monitor,
  );
  return hit ? hit.preset : null;
}
