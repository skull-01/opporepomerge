import type { TvBackend } from "./state";
import bundled from "./tv-db/tv-models.json";

// The bundled copy is the offline fallback; the canonical, refreshable copy lives at
// docs/configurator/tv-db/tv-models.json and is fetched from its raw GitHub URL on demand.
// Keep the two in sync when editing.

export type TvDbTier = "preferred" | "fallback" | "probe";

export type TvRegion = "US" | "UK" | "EU" | "Asia";

export type TvMappingConfidence = "high" | "medium" | "low";

export type TvDbLineup = {
  id: string;
  brand: string;
  label: string;
  platform: string;
  backend: TvBackend;
  tier: TvDbTier;
  years: [number, number];
  validated: boolean;
  fallback_backends?: TvBackend[];
  notes?: string;
  regions?: TvRegion[];
  release_regions?: TvRegion[];
  region_notes?: string;
};

export type TvDbModel = {
  id: string;
  brand: string;
  name: string;
  year: number;
  size: string;
  lineup: string;
  regions: TvRegion[];
  platform?: string;
  primary_backend?: TvBackend;
  fallback_backends?: TvBackend[];
  mapping_confidence?: TvMappingConfidence;
  validated?: boolean;
  notes?: string;
  release_regions?: TvRegion[];
  region_notes?: string;
};

export type TvRegionSchema = {
  field: string;
  type: string;
  allowed_values: TvRegion[];
  meaning?: string;
  usage?: string;
  validation_status?: string;
};

export type TvDb = {
  schema_version: number;
  db_version: string;
  lineups: TvDbLineup[];
  models: TvDbModel[];
  region_schema?: TvRegionSchema;
};

export const BUNDLED_TV_DB = bundled as unknown as TvDb;

export const TV_DB_RAW_URL =
  "https://raw.githubusercontent.com/skull-01/script.oppo203.iso.external/main/docs/configurator/tv-db/tv-models.json";

export function lineupFor(db: TvDb, model: TvDbModel): TvDbLineup | null {
  return db.lineups.find((l) => l.id === model.lineup) ?? null;
}

/** Resolved control backend: a per-model primary backend wins, otherwise the lineup's backend. */
export function resolveBackend(db: TvDb, model: TvDbModel): TvBackend | null {
  if (model.primary_backend) return model.primary_backend;
  return lineupFor(db, model)?.backend ?? null;
}

/** Resolved platform: the model's specific platform wins, otherwise the lineup's. */
export function resolvePlatform(db: TvDb, model: TvDbModel): string | null {
  return model.platform ?? lineupFor(db, model)?.platform ?? null;
}

export function resolveTier(db: TvDb, model: TvDbModel): TvDbTier | null {
  return lineupFor(db, model)?.tier ?? null;
}

export function modelsForBrand(db: TvDb, brand: string): TvDbModel[] {
  return db.models.filter((m) => m.brand === brand);
}

export const TV_REGIONS: readonly TvRegion[] = ["US", "UK", "EU", "Asia"];

/** Models released/mapped to a given region; a null region passes everything through. */
export function modelsForRegion(models: TvDbModel[], region: TvRegion | null): TvDbModel[] {
  if (!region) return models;
  return models.filter((m) => m.regions.includes(region));
}

/** Parse + lightly validate a fetched DB; returns null on any structural problem. */
export function parseTvDb(value: unknown): TvDb | null {
  if (!value || typeof value !== "object") return null;
  const v = value as Record<string, unknown>;
  // schema_version is the breaking-change gate. Additive optional fields ride through the
  // cast below without a bump (bump db_version instead); only a structural break bumps this.
  if (v.schema_version !== 2) return null;
  if (!Array.isArray(v.lineups) || !Array.isArray(v.models)) return null;
  return v as unknown as TvDb;
}

/**
 * Parse a db_version (YYYY.MM.DD) to a sortable integer (YYYYMMDD). Returns -1 if it does not
 * match that shape, so an unexpectedly-formatted version is never mis-ordered or treated as
 * newer by a raw string compare.
 */
export function dbVersionKey(version: string): number {
  const m = version.trim().match(/^(\d{4})\.(\d{1,2})\.(\d{1,2})$/);
  if (!m) return -1;
  return Number(m[1]) * 10000 + Number(m[2]) * 100 + Number(m[3]);
}

/** True when `candidate` is strictly newer than `current`, comparing parsed db_version dates. */
export function isNewer(current: TvDb, candidate: TvDb): boolean {
  const c = dbVersionKey(candidate.db_version);
  const cur = dbVersionKey(current.db_version);
  if (c < 0 || cur < 0) return false;
  return c > cur;
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
