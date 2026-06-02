import { describe, expect, it } from "vitest";
import {
  BUNDLED_TV_DB,
  isNewer,
  lineupFor,
  modelsForBrand,
  modelsForRegion,
  parseTvDb,
  resolveBackend,
  TV_REGIONS,
  type TvDbModel,
} from "./tvdb";

describe("BUNDLED_TV_DB", () => {
  it("has schema_version 2 and non-empty lineups + models", () => {
    expect(BUNDLED_TV_DB.schema_version).toBe(2);
    expect(BUNDLED_TV_DB.lineups.length).toBeGreaterThan(0);
    expect(BUNDLED_TV_DB.models.length).toBeGreaterThan(0);
  });

  it("every model references an existing lineup", () => {
    for (const m of BUNDLED_TV_DB.models) {
      expect(lineupFor(BUNDLED_TV_DB, m), `model ${m.id}`).not.toBeNull();
    }
  });

  it("every model carries at least one region", () => {
    for (const m of BUNDLED_TV_DB.models) {
      expect(m.regions.length, `model ${m.id}`).toBeGreaterThan(0);
    }
  });
});

describe("resolveBackend", () => {
  it("resolves a Roku TV model to roku_ecp via its primary backend", () => {
    const m = BUNDLED_TV_DB.models.find((x) => x.id === "hisense-r6-roku-tv-2018")!;
    expect(resolveBackend(BUNDLED_TV_DB, m)).toBe("roku_ecp");
  });

  it("resolves a Samsung model to samsung_command", () => {
    const m = BUNDLED_TV_DB.models.find((x) => x.id === "samsung-nu8000-crystal-uhd-2018")!;
    expect(resolveBackend(BUNDLED_TV_DB, m)).toBe("samsung_command");
  });

  it("prefers the per-model primary_backend over the lineup backend", () => {
    const m: TvDbModel = {
      id: "x",
      brand: "tcl",
      name: "X",
      year: 2024,
      size: "various",
      lineup: "tcl-roku",
      regions: ["US"],
      primary_backend: "custom_command",
    };
    expect(resolveBackend(BUNDLED_TV_DB, m)).toBe("custom_command");
  });

  it("falls back to the lineup backend when no primary_backend is set", () => {
    const m: TvDbModel = {
      id: "y",
      brand: "tcl",
      name: "Y",
      year: 2024,
      size: "various",
      lineup: "tcl-roku",
      regions: ["US"],
    };
    expect(resolveBackend(BUNDLED_TV_DB, m)).toBe("roku_ecp");
  });
});

describe("modelsForBrand", () => {
  it("returns only the requested brand", () => {
    const lg = modelsForBrand(BUNDLED_TV_DB, "lg");
    expect(lg.length).toBeGreaterThan(0);
    expect(lg.every((m) => m.brand === "lg")).toBe(true);
  });

  it("returns empty for a brand not in the database", () => {
    expect(modelsForBrand(BUNDLED_TV_DB, "vizio")).toEqual([]);
  });
});

describe("modelsForRegion", () => {
  it("keeps only models mapped to the region", () => {
    const all = modelsForBrand(BUNDLED_TV_DB, "hisense");
    const us = modelsForRegion(all, "US");
    expect(us.length).toBeGreaterThan(0);
    expect(us.every((m) => m.regions.includes("US"))).toBe(true);
    expect(us.length).toBeLessThanOrEqual(all.length);
  });

  it("passes everything through for a null region", () => {
    const all = modelsForBrand(BUNDLED_TV_DB, "hisense");
    expect(modelsForRegion(all, null)).toEqual(all);
  });
});

describe("parseTvDb", () => {
  it("accepts a valid v2 db", () => {
    expect(parseTvDb(BUNDLED_TV_DB)).not.toBeNull();
  });

  it("rejects a wrong schema_version or shape", () => {
    expect(parseTvDb({ schema_version: 1, lineups: [], models: [] })).toBeNull();
    expect(parseTvDb({ schema_version: 3, lineups: [], models: [] })).toBeNull();
    expect(parseTvDb({ schema_version: 2, lineups: {}, models: [] })).toBeNull();
    expect(parseTvDb(null)).toBeNull();
    expect(parseTvDb("nope")).toBeNull();
  });
});

describe("isNewer", () => {
  it("compares parsed db_version dates", () => {
    const base = { ...BUNDLED_TV_DB, db_version: "2026.05.30" };
    expect(isNewer(base, { ...base, db_version: "2026.06.01" })).toBe(true);
    expect(isNewer(base, { ...base, db_version: "2026.05.30" })).toBe(false);
    expect(isNewer(base, { ...base, db_version: "2026.05.01" })).toBe(false);
  });

  it("handles unpadded month/day correctly (not a raw string compare)", () => {
    const oct = { ...BUNDLED_TV_DB, db_version: "2026.10.01" };
    const jun = { ...BUNDLED_TV_DB, db_version: "2026.6.1" };
    // "2026.6.1" > "2026.10.01" as raw strings, but June is older than October
    expect(isNewer(oct, jun)).toBe(false);
    expect(isNewer(jun, oct)).toBe(true);
  });

  it("never treats an unparseable version as newer", () => {
    const base = { ...BUNDLED_TV_DB, db_version: "2026.05.30" };
    expect(isNewer(base, { ...base, db_version: "garbage" })).toBe(false);
  });
});

describe("CN region (China-domestic models)", () => {
  it("TV_REGIONS includes CN", () => {
    expect(TV_REGIONS).toContain("CN");
  });

  it("returns China TCL and Hisense families for the CN region", () => {
    const tcl = modelsForRegion(modelsForBrand(BUNDLED_TV_DB, "tcl"), "CN");
    const hisense = modelsForRegion(modelsForBrand(BUNDLED_TV_DB, "hisense"), "CN");
    expect(tcl.length).toBeGreaterThan(0);
    expect(hisense.length).toBeGreaterThan(0);
    expect(tcl.every((m) => m.regions.includes("CN"))).toBe(true);
    expect(hisense.every((m) => m.regions.includes("CN"))).toBe(true);
  });
});
