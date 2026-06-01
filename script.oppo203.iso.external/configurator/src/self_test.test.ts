import { describe, expect, it } from "vitest";
import {
  applyRewrite,
  canFireHttpPlay,
  INITIAL_SELF_TEST,
  selfTestComplete,
  selfTestPlaybackConfirmed,
  SELF_TEST_STEPS,
  type SelfTestState,
} from "./self_test";

describe("applyRewrite", () => {
  it("replaces the from-prefix with the to-prefix (SMB)", () => {
    expect(
      applyRewrite("smb://192.168.1.10/Movies/Film.iso", "smb://192.168.1.10/", "MyPC/"),
    ).toBe("MyPC/Movies/Film.iso");
  });

  it("matches the add-on's first-occurrence replace semantics", () => {
    // only the FIRST occurrence of the prefix is rewritten.
    expect(applyRewrite("smb://h/a/smb://h/a/x", "smb://h/a/", "X/")).toBe("X/smb://h/a/x");
  });

  it("returns the path unchanged when the prefix is empty (no rewrite configured)", () => {
    expect(applyRewrite("smb://nas/x.iso", "", "")).toBe("smb://nas/x.iso");
  });

  it("returns the path unchanged when the prefix is absent (fallback to raw path)", () => {
    expect(applyRewrite("nfs://nas/x.iso", "smb://other/", "MyPC/")).toBe("nfs://nas/x.iso");
  });

  it("trims surrounding whitespace on the input path", () => {
    expect(applyRewrite("  smb://nas/share/x.iso  ", "smb://nas/share/", "D/")).toBe("D/x.iso");
  });
});

describe("canFireHttpPlay", () => {
  it("is true for a non-empty OPPO path", () => {
    expect(canFireHttpPlay("MyPC/Movies/Film.iso")).toBe(true);
  });
  it("is false for an empty / whitespace path", () => {
    expect(canFireHttpPlay("")).toBe(false);
    expect(canFireHttpPlay("   ")).toBe(false);
  });
});

describe("self-test step model", () => {
  it("defines the five steps in the locked order", () => {
    expect(SELF_TEST_STEPS.map((s) => s.id)).toEqual([
      "power_cycle",
      "mount",
      "play",
      "confirm",
      "control",
    ]);
  });

  it("is not complete from the initial state", () => {
    expect(selfTestComplete(INITIAL_SELF_TEST)).toBe(false);
    expect(selfTestPlaybackConfirmed(INITIAL_SELF_TEST)).toBe(false);
  });

  it("is complete when every step is ok or skipped", () => {
    const done: SelfTestState = {
      power_cycle: "ok",
      mount: "skipped",
      play: "ok",
      confirm: "ok",
      control: "ok",
    };
    expect(selfTestComplete(done)).toBe(true);
  });

  it("is NOT complete while a step is still failed/running/idle", () => {
    const partial: SelfTestState = { ...INITIAL_SELF_TEST, power_cycle: "ok", play: "fail" };
    expect(selfTestComplete(partial)).toBe(false);
  });

  it("reports playback confirmed only when play AND confirm both passed", () => {
    expect(
      selfTestPlaybackConfirmed({ ...INITIAL_SELF_TEST, play: "ok", confirm: "ok" }),
    ).toBe(true);
    expect(
      selfTestPlaybackConfirmed({ ...INITIAL_SELF_TEST, play: "ok", confirm: "fail" }),
    ).toBe(false);
    // a skipped play does not count as confirmed.
    expect(
      selfTestPlaybackConfirmed({ ...INITIAL_SELF_TEST, play: "skipped", confirm: "ok" }),
    ).toBe(false);
  });
});
