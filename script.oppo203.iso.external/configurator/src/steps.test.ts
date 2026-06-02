// @vitest-environment node
import { describe, expect, it } from "vitest";
import { SCREEN_TO_CHAIN, SCREEN_TO_STEP, STEPS } from "./steps";

describe("reset_all utility screen wiring", () => {
  it("rides step-0's stepper group", () => {
    expect(SCREEN_TO_STEP.reset_all).toBe("step0");
  });

  it("maps to the media chain target (matches step 0)", () => {
    expect(SCREEN_TO_CHAIN.reset_all).toBe("media");
  });

  it("is reachable but not a numbered wizard step", () => {
    expect(STEPS.some((s) => (s.id as string) === "reset_all")).toBe(false);
  });
});
