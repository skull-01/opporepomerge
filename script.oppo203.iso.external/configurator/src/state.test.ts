import { describe, expect, it } from "vitest";
import { coerceScreenId, INITIAL_STATE } from "./state";

describe("coerceScreenId", () => {
  it("keeps a valid screen id", () => {
    expect(coerceScreenId("step2_test")).toBe("step2_test");
    expect(coerceScreenId("test_success")).toBe("test_success");
  });

  it("falls back to step0_gate for an unknown, missing, or non-string id", () => {
    expect(coerceScreenId("step1_advanced")).toBe("step0_gate"); // stale / renamed id
    expect(coerceScreenId("")).toBe("step0_gate");
    expect(coerceScreenId(undefined)).toBe("step0_gate");
    expect(coerceScreenId(42)).toBe("step0_gate");
  });
});

describe("INITIAL_STATE", () => {
  it("starts unverified with no tier", () => {
    expect(INITIAL_STATE.tier).toBeNull();
    expect(INITIAL_STATE.kodiVerified).toBe(false);
  });
});

describe("topology", () => {
  it("starts unset (null) so legacy sessions fall back to the TV chain", () => {
    expect(INITIAL_STATE.topology).toBeNull();
  });
  it("round-trips the step0_chain picker screen id", () => {
    expect(coerceScreenId("step0_chain")).toBe("step0_chain");
  });
});
