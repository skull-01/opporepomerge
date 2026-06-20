import type { AvrBackend } from "./state";
import bundled from "./avr-db/avr-models.json";

// The bundled copy is the offline fallback; the canonical, refreshable copy lives at
// docs/configurator/avr-db/avr-models.json and is fetched from its raw GitHub URL on demand.
// Keep the two in sync when editing (build/gen_avr_db.py writes both). This is the AV-receiver
// twin of tvdb.ts: an informational, candidate-mapping control-path database (validated:false),
// surfaced advisorily in the wizard and not loaded by the add-on at runtime.

export type AvrDbTier = "command";

export type AvrRegion = "US" | "UK" | "EU" | "Asia";

export type AvrDbLineup = {
  id: string;
  brand: string;
  label: string;
  platform: string;
  backend: AvrBackend;
  primary_backend?: AvrBackend;
  tier: AvrDbTier;
  years: [number, number];
  validated: boolean;
  fallback_backends?: AvrBackend[];
  regions?: AvrRegion[];
  release_regions?: AvrRegion[];
  region_notes?: string;
};

export type AvrDbModel = {
  id: string;
  brand: string;
  name: string;
  year: number;
  receiver_type: string;
  channels?: string;
  lineup: string;
  regions: AvrRegion[];
  primary_backend?: AvrBackend;
  fallback_backends?: AvrBackend[];
  validated?: boolean;
  control_notes?: string;
  release_regions?: AvrRegion[];
  region_notes?: string;
};

export type AvrRegionSchema = {
  field: string;
  type: string;
  allowed_values: AvrRegion[];
  meaning?: string;
};

export type AvrDb = {
  schema_version: number;
  db_version: string;
  database_kind?: string;
  lineups: AvrDbLineup[];
  models: AvrDbModel[];
  region_schema?: AvrRegionSchema;
};

export const BUNDLED_AVR_DB = bundled as unknown as AvrDb;

export const AVR_DB_RAW_URL =
  "https://raw.githubusercontent.com/skull-01/script.oppo203.iso.external/main/docs/configurator/avr-db/avr-models.json";

export function lineupFor(db: AvrDb, model: AvrDbModel): AvrDbLineup | null {
  return db.lineups.find((l) => l.id === model.lineup) ?? null;
}

/** Resolved control backend: a per-model primary backend wins, otherwise the lineup's backend. */
export function resolveBackend(db: AvrDb, model: AvrDbModel): AvrBackend | null {
  if (model.primary_backend) return model.primary_backend;
  return lineupFor(db, model)?.backend ?? null;
}

/** Resolved platform: AVR models carry no per-model platform, so use the lineup's. */
export function resolvePlatform(db: AvrDb, model: AvrDbModel): string | null {
  return lineupFor(db, model)?.platform ?? null;
}

export function modelsForBrand(db: AvrDb, brand: string): AvrDbModel[] {
  return db.models.filter((m) => m.brand === brand);
}

export const AVR_REGIONS: readonly AvrRegion[] = ["US", "UK", "EU", "Asia"];

/** Models released/mapped to a given region; a null region passes everything through. */
export function modelsForRegion(models: AvrDbModel[], region: AvrRegion | null): AvrDbModel[] {
  if (!region) return models;
  return models.filter((m) => m.regions.includes(region));
}

/** Parse + lightly validate a fetched DB; returns null on any structural problem. */
export function parseAvrDb(value: unknown): AvrDb | null {
  if (!value || typeof value !== "object") return null;
  const v = value as Record<string, unknown>;
  // schema_version is the breaking-change gate; additive optional fields ride through the cast.
  if (v.schema_version !== 2) return null;
  if (!Array.isArray(v.lineups) || !Array.isArray(v.models)) return null;
  return v as unknown as AvrDb;
}

/**
 * Parse a db_version to a sortable integer (YYYYMMDD) from its leading YYYY.MM.DD. The AVR
 * bundle carries a descriptive suffix (`2026.05.30-avr-...`), so — unlike the TV parser — this
 * reads the leading date instead of requiring the whole string to be a bare date. Returns -1 if
 * the leading token is not a date, so an unexpectedly-formatted version is never mis-ordered.
 */
export function dbVersionKey(version: string): number {
  const m = version.trim().match(/^(\d{4})\.(\d{1,2})\.(\d{1,2})/);
  if (!m) return -1;
  return Number(m[1]) * 10000 + Number(m[2]) * 100 + Number(m[3]);
}

/** True when `candidate` is strictly newer than `current`, comparing parsed db_version dates. */
export function isNewer(current: AvrDb, candidate: AvrDb): boolean {
  const c = dbVersionKey(candidate.db_version);
  const cur = dbVersionKey(current.db_version);
  if (c < 0 || cur < 0) return false;
  return c > cur;
}

/** Best-effort fetch of the published DB. Returns null on any network or parse error. */
export async function fetchRemoteAvrDb(): Promise<AvrDb | null> {
  try {
    const res = await fetch(AVR_DB_RAW_URL, { cache: "no-store" });
    if (!res.ok) return null;
    return parseAvrDb(await res.json());
  } catch {
    return null;
  }
}
