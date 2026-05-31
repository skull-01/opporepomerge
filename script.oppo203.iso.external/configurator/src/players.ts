import type { PlayerBrand } from "./state";
import { BUNDLED_PLAYERS_DB, modelsForFamily, type PlayerPosture } from "./playersdb";

export type BrandPosture = PlayerPosture;
export type PlayerModelDef = { label: string; hw: string | null };
export type PlayerBrandDef = {
  id: PlayerBrand;
  name: string;
  ch: string;
  color: string;
  posture: BrandPosture;
  models: readonly PlayerModelDef[];
};

/**
 * Single source of truth for player brands: derived from the canonical players database
 * (configurator/src/players-db/players-models.json). Display metadata (name, logo char, posture)
 * and the model picker labels + their `oppo_hardware_model` enum value all come from the DB,
 * so the Step 2 picker and mapping.ts can't drift from the add-on's hardware taxonomy. The
 * `other` family carries explicit ui_models (UX aliases onto an existing hw value).
 */
export const PLAYER_BRANDS: readonly PlayerBrandDef[] = BUNDLED_PLAYERS_DB.families.map((f) => ({
  id: f.id as PlayerBrand,
  name: f.name,
  ch: f.ch,
  color: f.color,
  posture: f.posture,
  models: f.ui_models
    ? f.ui_models.map((m) => ({ label: m.label, hw: m.hw }))
    : modelsForFamily(BUNDLED_PLAYERS_DB, f.id).map((m) => ({ label: m.ui_label, hw: m.hw })),
}));

export function brandDef(id: PlayerBrand | null): PlayerBrandDef | undefined {
  return PLAYER_BRANDS.find((b) => b.id === id);
}

/** The `oppo_hardware_model` enum value for a brand + model label, or null if unknown. */
export function hwModelFor(brand: PlayerBrand | null, modelLabel: string | null): string | null {
  if (!brand || !modelLabel) return null;
  return brandDef(brand)?.models.find((m) => m.label === modelLabel)?.hw ?? null;
}

/** True when the brand needs the eject-to-wake (#EJT) quirk handled before other commands. */
export function isWakeRewriteBrand(brand: PlayerBrand | null): boolean {
  return brandDef(brand)?.posture === "wake-rewrite";
}
