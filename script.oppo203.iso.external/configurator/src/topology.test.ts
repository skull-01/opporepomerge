import { describe, expect, it } from "vitest";
import { chainNodeIds, isAvrChain, step5NextScreen } from "./steps";

describe("isAvrChain", () => {
  it("is true only for the AVR chain", () => {
    expect(isAvrChain("kodi_avr_tv_player")).toBe(true);
    expect(isAvrChain("kodi_tv_player")).toBe(false);
  });

  it("treats a null/legacy topology as the TV chain (soft default)", () => {
    expect(isAvrChain(null)).toBe(false);
  });
});

describe("chainNodeIds", () => {
  it("inserts the receiver node between Kodi and the player for the AVR chain", () => {
    expect(chainNodeIds("kodi_avr_tv_player")).toEqual([
      "media",
      "kodi",
      "avr",
      "player",
      "tv",
    ]);
  });

  it("omits the receiver node for the TV chain and for null", () => {
    expect(chainNodeIds("kodi_tv_player")).toEqual(["media", "kodi", "player", "tv"]);
    expect(chainNodeIds(null)).toEqual(["media", "kodi", "player", "tv"]);
  });
});

describe("step5NextScreen", () => {
  it("hands off to the receiver step in both chains (the AVR chain leads with it)", () => {
    expect(step5NextScreen("kodi_avr_tv_player")).toBe("step6_ask");
    expect(step5NextScreen("kodi_tv_player")).toBe("step6_ask");
    expect(step5NextScreen(null)).toBe("step6_ask");
  });
});
