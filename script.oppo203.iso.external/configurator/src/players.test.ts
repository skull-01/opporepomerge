import { describe, expect, it } from "vitest";
import { PLAYER_BRANDS, brandDef, hwModelFor, isWakeRewriteBrand } from "./players";
import {
  BUNDLED_PLAYERS_DB,
  modelsForFamily,
  parsePlayersDb,
  playerModelByHw,
} from "./playersdb";
import type { PlayerBrand } from "./state";

// Regression pin: every (brand, picker label) -> oppo_hardware_model enum value that the
// hand-written catalog produced must still resolve identically from the database.
const EXPECTED_HW: ReadonlyArray<[PlayerBrand, string, string]> = [
  ["oppo", "UDP-203", "udp_203"],
  ["oppo", "UDP-205", "udp_205"],
  ["chinoppo", "M9201", "chinoppo_m9201"],
  ["chinoppo", "M9203", "chinoppo_m9203"],
  ["chinoppo", "M9205 V1", "chinoppo_m9205_v1"],
  ["chinoppo", "M9205C", "chinoppo_m9205c"],
  ["chinoppo", "M9200", "chinoppo_m9200"],
  ["chinoppo", "M9205", "chinoppo_m9205"],
  ["chinoppo", "M9702", "chinoppo_m9702"],
  ["magnetar", "UDP800", "magnetar_udp800"],
  ["magnetar", "UDP900", "magnetar_udp900"],
  ["reavon", "UBR-X100", "reavon_ubrx100"],
  ["reavon", "UBR-X110", "reavon_ubrx110"],
  ["reavon", "UBR-X200", "reavon_ubrx200"],
  ["cineultra", "V203", "cineultra_v203"],
  ["cineultra", "V204", "cineultra_v204"],
  ["ipuk", "UHD8592", "ipuk_uhd8592"],
  ["giec", "BDP-G5300", "giec_bdp_g5300"],
  ["other", "Conservative default", "udp_203"],
  ["other", "Chinoppo eject-to-wake", "chinoppo_m9205"],
];

describe("players catalog (derived from players.json)", () => {
  it("maps every known brand + model label to its oppo_hardware_model enum value", () => {
    for (const [brand, label, hw] of EXPECTED_HW) {
      expect(hwModelFor(brand, label), `${brand}/${label}`).toBe(hw);
    }
  });

  it("returns null for an unset or unknown brand/model", () => {
    expect(hwModelFor(null, "UDP-203")).toBeNull();
    expect(hwModelFor("oppo", null)).toBeNull();
    expect(hwModelFor("oppo", "UDP-999")).toBeNull();
  });

  it("identifies eject-to-wake (clone) brands by posture", () => {
    expect(isWakeRewriteBrand("chinoppo")).toBe(true);
    expect(isWakeRewriteBrand("giec")).toBe(true);
    expect(isWakeRewriteBrand("oppo")).toBe(false);
    expect(isWakeRewriteBrand(null)).toBe(false);
  });

  it("every model maps to a non-empty enum value", () => {
    for (const b of PLAYER_BRANDS) {
      for (const m of b.models) {
        expect(m.hw, `${b.id}/${m.label}`).toBeTruthy();
      }
    }
    expect(brandDef("oppo")?.name).toBe("OPPO");
  });

  it("exposes one brand per database family, in order", () => {
    expect(PLAYER_BRANDS.map((b) => b.id)).toEqual(BUNDLED_PLAYERS_DB.families.map((f) => f.id));
  });
});

describe("players DB", () => {
  it("has schema_version 1, 18 models, and an 18-id enum order", () => {
    expect(BUNDLED_PLAYERS_DB.schema_version).toBe(1);
    expect(BUNDLED_PLAYERS_DB.models.length).toBe(18);
    expect(BUNDLED_PLAYERS_DB.enum_order.length).toBe(18);
  });

  it("every model carries at least one region and a valid brand", () => {
    const familyIds = new Set(BUNDLED_PLAYERS_DB.families.map((f) => f.id));
    for (const m of BUNDLED_PLAYERS_DB.models) {
      expect(m.regions.length, m.key).toBeGreaterThan(0);
      expect(familyIds.has(m.brand), m.key).toBe(true);
    }
  });

  it("lists models in the settings enum order", () => {
    expect(BUNDLED_PLAYERS_DB.models.map((m) => m.hw)).toEqual(BUNDLED_PLAYERS_DB.enum_order);
  });

  it("modelsForFamily + playerModelByHw resolve", () => {
    const oppo = modelsForFamily(BUNDLED_PLAYERS_DB, "oppo");
    expect(oppo.length).toBe(2);
    expect(oppo.every((m) => m.brand === "oppo")).toBe(true);
    expect(playerModelByHw(BUNDLED_PLAYERS_DB, "reavon_ubrx200")?.is_reavon).toBe(true);
    expect(playerModelByHw(BUNDLED_PLAYERS_DB, "nope")).toBeNull();
  });

  it("parsePlayersDb gates schema_version and shape", () => {
    expect(parsePlayersDb(BUNDLED_PLAYERS_DB)).not.toBeNull();
    expect(parsePlayersDb({ schema_version: 2, families: [], models: [] })).toBeNull();
    expect(parsePlayersDb({ schema_version: 1, families: {}, models: [] })).toBeNull();
    expect(parsePlayersDb(null)).toBeNull();
    expect(parsePlayersDb("nope")).toBeNull();
  });
});
