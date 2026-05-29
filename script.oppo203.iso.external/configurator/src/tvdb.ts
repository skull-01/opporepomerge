import type { TvBackend } from "./state";
import bundled from "./tv-db/tv-models.json";

// The bundled copy is the offline fallback; the canonical, refreshable copy lives at
// docs/configurator/tv-db/tv-models.json and is fetched from its raw GitHub URL on demand.
// Keep the two in sync when editing.

export type TvDbTier = "probe" | "command";

export type TvDbLineup = {
  id: string;
  brand: string;
  label: string;
  platform: string;
  backend: TvBackend;
  tier: TvDbTier;
  years: [number, number];
  validated: boolean;
};

export type TvDbModel = {
  id: string;
  brand: string;
  name: string;
  year: number;
  size: string;
  lineup: string;
  backend_override?: TvBackend | null;
  validated?: boolean;
};

export type TvDb = {
  schema_version: number;
  db_version: string;
  lineups: TvDbLineup[];
  models: TvDbModel[];
};

export const BUNDLED_TV_DB = bundled as unknown as TvDb;

export const TV_DB_RAW_URL =
  "https://raw.githubusercontent.com/skull-01/script.oppo203.iso.external/main/docs/configurator/tv-db/tv-models.json";

export function lineupFor(db: TvDb, model: TvDbModel): TvDbLineup | null {
  return db.lineups.find((l) => l.id === model.lineup) ?? null;
}

/** Resolved control backend: a per-model override wins, otherwise the lineup's backend. */
export function resolveBackend(db: TvDb, model: TvDbModel): TvBackend | null {
  if (model.backend_override) return model.backend_override;
  return lineupFor(db, model)?.backend ?? null;
}

export function resolvePlatform(db: TvDb, model: TvDbModel): string | null {
  return lineupFor(db, model)?.platform ?? null;
}

export function resolveTier(db: TvDb, model: TvDbModel): TvDbTier | null {
  return lineupFor(db, model)?.tier ?? null;
}

export function modelsForBrand(db: TvDb, brand: string): TvDbModel[] {
  return db.models.filter((m) => m.brand === brand);
}

/** Parse + lightly validate a fetched DB; returns null on any structural problem. */
export function parseTvDb(value: unknown): TvDb | null {
  if (!value || typeof value !== "object") return null;
  const v = value as Record<string, unknown>;
  if (v.schema_version !== 1) return null;
  if (!Array.isArray(v.lineups) || !Array.isArray(v.models)) return null;
  return v as unknown as TvDb;
}

/** True when `candidate` is strictly newer than `current` (db_version is a sortable date). */
export function isNewer(current: TvDb, candidate: TvDb): boolean {
  return candidate.db_version > current.db_version;
}

/** Best-effort fetch of the published DB. Returns null on any network or parse error. */
export async function fetchRemoteTvDb(): Promise<TvDb | null> {
  try {
    const res = await fetch(TV_DB_RAW_URL, { cache: "no-store" });
    if (!res.ok) return null;
    return parseTvDb(await res.json());
  } catch {
    return null;
  }
}
