import { describe, expect, it } from "vitest";
import { PLAYER_BRANDS, brandDef, hwModelFor, isWakeRewriteBrand } from "./players";

describe("players catalog", () => {
  it("maps brand + model label to the oppo_hardware_model enum value", () => {
    expect(hwModelFor("oppo", "UDP-203")).toBe("udp_203");
    expect(hwModelFor("chinoppo", "M9205 V1")).toBe("chinoppo_m9205_v1");
    expect(hwModelFor("reavon", "UBR-X110")).toBe("reavon_ubrx110");
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
});
