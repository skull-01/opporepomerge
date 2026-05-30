import bundled from "./players-db/players.json";

// The bundled copy is the offline source; the canonical, refreshable copy lives at
// docs/configurator/players-db/players.json. Keep the two in sync when editing, and keep
// the model order in lockstep with the resources/settings.xml oppo_hardware_model enum
// (enum_order) -- that order is install-base-critical (stored positionally).

export type PlayerPosture = "stock" | "wake-rewrite" | "warning";

export type PlayerRegion = "US" | "UK" | "EU" | "Asia";

export type PlayersDbFamilyUiModel = { label: string; hw: string };

export type PlayersDbFamily = {
  id: string;
  name: string;
  ch: string;
  color: string;
  posture: PlayerPosture;
  ui_models?: PlayersDbFamilyUiModel[];
};

export type PlayersDbModel = {
  key: string;
  hw: string;
  ui_label: string;
  label: string;
  brand: string;
  hardware_class: string;
  protocol_stance: string;
  wake_behavior: string;
  wake_command: string;
  protocol_compatible: boolean;
  is_clone: boolean;
  is_reavon: boolean;
  is_successor: boolean;
  http_api_436: boolean;
  src_supported: string[];
  src_unsupported: string[];
  nas_playback_candidate: boolean;
  aliases: string[];
  regions: PlayerRegion[];
  validated: boolean;
};

export type PlayersDb = {
  schema_version: number;
  db_version: string;
  enum_order: string[];
  families: PlayersDbFamily[];
  models: PlayersDbModel[];
};

export const BUNDLED_PLAYERS_DB = bundled as unknown as PlayersDb;

export const PLAYERS_DB_RAW_URL =
  "https://raw.githubusercontent.com/skull-01/script.oppo203.iso.external/main/docs/configurator/players-db/players.json";

/** The player model families belonging to a configurator brand, in database (enum) order. */
export function modelsForFamily(db: PlayersDb, brandId: string): PlayersDbModel[] {
  return db.models.filter((m) => m.brand === brandId);
}

/** The full model record for a settings enum id (`hw`), or null. */
export function playerModelByHw(db: PlayersDb, hw: string): PlayersDbModel | null {
  return db.models.find((m) => m.hw === hw) ?? null;
}

/** Parse + lightly validate a players DB; returns null on any structural problem. */
export function parsePlayersDb(value: unknown): PlayersDb | null {
  if (!value || typeof value !== "object") return null;
  const v = value as Record<string, unknown>;
  // schema_version is the breaking-change gate; additive optional fields ride through.
  if (v.schema_version !== 1) return null;
  if (!Array.isArray(v.families) || !Array.isArray(v.models)) return null;
  return v as unknown as PlayersDb;
}
