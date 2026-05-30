import { describe, expect, it } from "vitest";
import {
  AVR_REGIONS,
  BUNDLED_AVR_DB,
  isNewer,
  lineupFor,
  modelsForBrand,
  modelsForRegion,
  parseAvrDb,
  resolveBackend,
  type AvrDbModel,
} from "./avrdb";

const ALL_BACKENDS = new Set([
  "denon_marantz",
  "yamaha_yxc",
  "onkyo_eiscp",
  "sony_audio",
  "custom_command",
]);

describe("BUNDLED_AVR_DB", () => {
  it("has schema_version 2 and non-empty lineups + models", () => {
    expect(BUNDLED_AVR_DB.schema_version).toBe(2);
    expect(BUNDLED_AVR_DB.lineups.length).toBeGreaterThan(0);
    expect(BUNDLED_AVR_DB.models.length).toBeGreaterThan(0);
  });

  it("every model references an existing lineup", () => {
    for (const m of BUNDLED_AVR_DB.models) {
      expect(lineupFor(BUNDLED_AVR_DB, m), `model ${m.id}`).not.toBeNull();
    }
  });

  it("every model carries at least one valid region", () => {
    for (const m of BUNDLED_AVR_DB.models) {
      expect(m.regions.length, `model ${m.id}`).toBeGreaterThan(0);
      for (const r of m.regions) expect(AVR_REGIONS, `model ${m.id}`).toContain(r);
    }
  });

  it("every model resolves to a known backend", () => {
    for (const m of BUNDLED_AVR_DB.models) {
      const b = resolveBackend(BUNDLED_AVR_DB, m);
      expect(b, `model ${m.id}`).not.toBeNull();
      expect(ALL_BACKENDS.has(b as string), `model ${m.id} -> ${b}`).toBe(true);
    }
  });
});

describe("resolveBackend", () => {
  it("resolves a Denon model to denon_marantz", () => {
    const m = BUNDLED_AVR_DB.models.find((x) => x.id === "denon-avr-s540bt-2018")!;
    expect(resolveBackend(BUNDLED_AVR_DB, m)).toBe("denon_marantz");
  });

  it("resolves a Sony model to sony_audio", () => {
    const m = BUNDLED_AVR_DB.models.find((x) => x.id === "sony-str-dn1080-current-family-2018")!;
    expect(resolveBackend(BUNDLED_AVR_DB, m)).toBe("sony_audio");
  });

  it("maps Pioneer onto the shared onkyo_eiscp path", () => {
    const m = BUNDLED_AVR_DB.models.find((x) => x.id === "pioneer-vsx-lx103-2018")!;
    expect(resolveBackend(BUNDLED_AVR_DB, m)).toBe("onkyo_eiscp");
  });

  it("prefers the per-model primary_backend over the lineup backend", () => {
    const m: AvrDbModel = {
      id: "x",
      brand: "denon",
      name: "X",
      year: 2024,
      receiver_type: "AV receiver",
      lineup: "denon-avr-ip",
      regions: ["US"],
      primary_backend: "custom_command",
    };
    expect(resolveBackend(BUNDLED_AVR_DB, m)).toBe("custom_command");
  });

  it("falls back to the lineup backend when no primary_backend is set", () => {
    const m: AvrDbModel = {
      id: "y",
      brand: "denon",
      name: "Y",
      year: 2024,
      receiver_type: "AV receiver",
      lineup: "denon-avr-ip",
      regions: ["US"],
    };
    expect(resolveBackend(BUNDLED_AVR_DB, m)).toBe("denon_marantz");
  });
});

describe("modelsForBrand", () => {
  it("returns only the requested brand", () => {
    const denon = modelsForBrand(BUNDLED_AVR_DB, "denon");
    expect(denon.length).toBeGreaterThan(0);
    expect(denon.every((m) => m.brand === "denon")).toBe(true);
  });

  it("returns empty for a brand not in the database", () => {
    expect(modelsForBrand(BUNDLED_AVR_DB, "bose")).toEqual([]);
  });
});

describe("modelsForRegion", () => {
  it("keeps only models mapped to the region", () => {
    const all = modelsForBrand(BUNDLED_AVR_DB, "denon");
    const us = modelsForRegion(all, "US");
    expect(us.length).toBeGreaterThan(0);
    expect(us.every((m) => m.regions.includes("US"))).toBe(true);
    expect(us.length).toBeLessThanOrEqual(all.length);
  });

  it("passes everything through for a null region", () => {
    const all = modelsForBrand(BUNDLED_AVR_DB, "denon");
    expect(modelsForRegion(all, null)).toEqual(all);
  });
});

describe("parseAvrDb", () => {
  it("accepts a valid v2 db", () => {
    expect(parseAvrDb(BUNDLED_AVR_DB)).not.toBeNull();
  });

  it("rejects a wrong schema_version or shape", () => {
    expect(parseAvrDb({ schema_version: 1, lineups: [], models: [] })).toBeNull();
    expect(parseAvrDb({ schema_version: 3, lineups: [], models: [] })).toBeNull();
    expect(parseAvrDb({ schema_version: 2, lineups: {}, models: [] })).toBeNull();
    expect(parseAvrDb(null)).toBeNull();
    expect(parseAvrDb("nope")).toBeNull();
  });
});

describe("isNewer", () => {
  it("compares parsed db_version dates, ignoring the descriptive suffix", () => {
    const base = { ...BUNDLED_AVR_DB, db_version: "2026.05.30-avr-2018-2025-region-schema" };
    expect(isNewer(base, { ...base, db_version: "2026.06.01-avr" })).toBe(true);
    expect(isNewer(base, { ...base, db_version: "2026.05.30-avr-2018-2025-region-schema" })).toBe(
      false
    );
    expect(isNewer(base, { ...base, db_version: "2026.05.01-avr" })).toBe(false);
  });

  it("handles unpadded month/day correctly (not a raw string compare)", () => {
    const oct = { ...BUNDLED_AVR_DB, db_version: "2026.10.01" };
    const jun = { ...BUNDLED_AVR_DB, db_version: "2026.6.1" };
    expect(isNewer(oct, jun)).toBe(false);
    expect(isNewer(jun, oct)).toBe(true);
  });

  it("never treats an unparseable version as newer", () => {
    const base = { ...BUNDLED_AVR_DB, db_version: "2026.05.30" };
    expect(isNewer(base, { ...base, db_version: "garbage" })).toBe(false);
  });
});
