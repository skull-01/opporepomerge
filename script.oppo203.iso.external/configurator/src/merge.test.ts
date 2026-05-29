// @vitest-environment happy-dom
import { describe, expect, it } from "vitest";
import { kodiTargetForPlatform } from "./generate";
import { mergePlayercorefactory } from "./merge";

const target = kodiTargetForPlatform("coreelec");

describe("mergePlayercorefactory", () => {
  it("returns a fresh document when there is no existing file", () => {
    const xml = mergePlayercorefactory(null, target);
    expect(xml).toContain('<player name="Oppo203ISO"');
    expect(xml).toContain('filetypes="iso"');
  });

  it("preserves an existing unrelated player and rule, and adds ours", () => {
    const existing =
      '<playercorefactory><players>' +
      '<player name="MPV" type="ExternalPlayer"><filename>mpv</filename></player>' +
      '</players><rules><rule filetypes="mkv" player="MPV"/></rules></playercorefactory>';
    const xml = mergePlayercorefactory(existing, target);
    expect(xml).toContain('name="MPV"');
    expect(xml).toContain('name="Oppo203ISO"');
    expect(xml).toContain('player="MPV"');
  });

  it("is idempotent - merging twice keeps exactly one of our players", () => {
    const once = mergePlayercorefactory(null, target);
    const twice = mergePlayercorefactory(once, target);
    const count = (twice.match(/name="Oppo203ISO"/g) || []).length;
    expect(count).toBe(1);
  });

  it("falls back to a fresh document for a non-playercorefactory file", () => {
    const xml = mergePlayercorefactory("<advancedsettings><foo/></advancedsettings>", target);
    expect(xml).toContain('<player name="Oppo203ISO"');
  });
});
