import { describe, expect, it } from "vitest";
import {
  BUNDLED_TV_DB,
  isNewer,
  lineupFor,
  modelsForBrand,
  parseTvDb,
  resolveBackend,
  type TvDbModel,
} from "./tvdb";

describe("BUNDLED_TV_DB", () => {
  it("has schema_version 1 and non-empty lineups + models", () => {
    expect(BUNDLED_TV_DB.schema_version).toBe(1);
    expect(BUNDLED_TV_DB.lineups.length).toBeGreaterThan(0);
    expect(BUNDLED_TV_DB.models.length).toBeGreaterThan(0);
  });

  it("every model references an existing lineup", () => {
    for (const m of BUNDLED_TV_DB.models) {
      expect(lineupFor(BUNDLED_TV_DB, m), `model ${m.id}`).not.toBeNull();
    }
  });
});

describe("resolveBackend", () => {
  it("resolves a TCL Google TV model to adb via its lineup", () => {
    const m = BUNDLED_TV_DB.models.find((x) => x.id === "tcl-65q9-2023")!;
    expect(resolveBackend(BUNDLED_TV_DB, m)).toBe("adb");
  });

  it("resolves a TCL Roku model to roku_ecp", () => {
    const m = BUNDLED_TV_DB.models.find((x) => x.id === "tcl-55r5-2022")!;
    expect(resolveBackend(BUNDLED_TV_DB, m)).toBe("roku_ecp");
  });

  it("honors a per-model backend_override", () => {
    const m: TvDbModel = {
      id: "x",
      brand: "tcl",
      name: "X",
      year: 2024,
      size: '55"',
      lineup: "tcl-googletv",
      backend_override: "custom_command",
    };
    expect(resolveBackend(BUNDLED_TV_DB, m)).toBe("custom_command");
  });
});

describe("modelsForBrand", () => {
  it("returns only the requested brand", () => {
    const tcl = modelsForBrand(BUNDLED_TV_DB, "tcl");
    expect(tcl.length).toBeGreaterThan(0);
    expect(tcl.every((m) => m.brand === "tcl")).toBe(true);
  });

  it("returns empty for a brand with lineups but no seeded models", () => {
    expect(modelsForBrand(BUNDLED_TV_DB, "lg")).toEqual([]);
  });
});

describe("parseTvDb", () => {
  it("accepts a valid db", () => {
    expect(parseTvDb(BUNDLED_TV_DB)).not.toBeNull();
  });

  it("rejects a wrong schema_version or shape", () => {
    expect(parseTvDb({ schema_version: 2, lineups: [], models: [] })).toBeNull();
    expect(parseTvDb({ schema_version: 1, lineups: {}, models: [] })).toBeNull();
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
