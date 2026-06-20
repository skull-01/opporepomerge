import { describe, expect, it } from "vitest";
import { MASKED, diffIsEmpty, diffSettings, sanitizeSettings } from "./settings_diff";

describe("sanitizeSettings", () => {
  it("masks secret-bearing ids and keeps everything else", () => {
    const out = sanitizeSettings({
      oppo_ip: "10.0.1.77",
      tv_backend: "adb",
      sony_psk: "hunter2",
      smartthings_token: "abc123",
      sony_avr_psk: "zzz",
    });
    expect(out.oppo_ip).toBe("10.0.1.77");
    expect(out.tv_backend).toBe("adb");
    expect(out.sony_psk).toBe(MASKED);
    expect(out.smartthings_token).toBe(MASKED);
    expect(out.sony_avr_psk).toBe(MASKED);
  });

  it("never leaks a secret value - a changed secret reads as no-change, an added one shows masked", () => {
    const before = sanitizeSettings({ sony_psk: "old" });
    const after = sanitizeSettings({ sony_psk: "new" });
    expect(diffIsEmpty(diffSettings(before, after))).toBe(true);
    const added = diffSettings({}, sanitizeSettings({ sony_psk: "x" }));
    expect(added.added.map((a) => a.id)).toEqual(["sony_psk"]);
    expect(added.added[0].value).toBe(MASKED);
  });
});

describe("diffSettings", () => {
  it("reports added, removed and changed with ids sorted", () => {
    const d = diffSettings(
      { keep: "1", drop: "x", change: "a" },
      { keep: "1", change: "b", fresh: "y" },
    );
    expect(d.added).toEqual([{ id: "fresh", value: "y" }]);
    expect(d.removed).toEqual([{ id: "drop", value: "x" }]);
    expect(d.changed).toEqual([{ id: "change", from: "a", to: "b" }]);
  });

  it("treats a null baseline as everything-added", () => {
    const d = diffSettings(null, { b: "2", a: "1" });
    expect(d.added.map((a) => a.id)).toEqual(["a", "b"]);
    expect(d.removed).toEqual([]);
    expect(d.changed).toEqual([]);
  });

  it("is empty when nothing changed", () => {
    expect(diffIsEmpty(diffSettings({ a: "1" }, { a: "1" }))).toBe(true);
  });
});
