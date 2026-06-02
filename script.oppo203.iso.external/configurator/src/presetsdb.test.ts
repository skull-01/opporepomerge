import { describe, expect, it } from "vitest";
import { PLAYBACK_PRESETS, PLAYBACK_PRESETS_DB, presetForAxes } from "./presetsdb";

describe("playback-presets DB (shared playback-architecture matrix)", () => {
  it("carries exactly the seven canonical presets", () => {
    expect(PLAYBACK_PRESETS).toHaveLength(7);
    expect(new Set(PLAYBACK_PRESETS).size).toBe(7);
  });

  it("is the routing x {legacy,svm3} cross-product plus the asymmetric http cell", () => {
    // legacy + svm3 apply to every routing; the http monitor exists only for http_handoff (the
    // 7th preset). Mirrors the add-on's settings_reader._PRESET_BY_AXES.
    const { routing_modes, preset_by_axes } = PLAYBACK_PRESETS_DB;
    const pairs = new Set(preset_by_axes.map((e) => `${e.routing}|${e.monitor}`));
    const expected = new Set([
      ...routing_modes.flatMap((r) => ["legacy", "svm3"].map((m) => `${r}|${m}`)),
      "http_handoff|http",
    ]);
    expect(pairs).toEqual(expected);
    expect(pairs.size).toBe(7);
  });

  it("preset_by_axes ids match the presets list and the `${routing}_${monitor}` convention", () => {
    for (const e of PLAYBACK_PRESETS_DB.preset_by_axes) {
      expect(PLAYBACK_PRESETS).toContain(e.preset);
      expect(e.preset).toBe(`${e.routing}_${e.monitor}`);
    }
  });

  it("presetForAxes resolves known pairs and rejects unknown ones", () => {
    expect(presetForAxes("http_handoff", "svm3")).toBe("http_handoff_svm3");
    expect(presetForAxes("http_handoff", "http")).toBe("http_handoff_http");
    expect(presetForAxes("playercorefactory", "legacy")).toBe("playercorefactory_legacy");
    expect(presetForAxes("nonsense", "svm3")).toBeNull();
    // the http monitor is http_handoff-only: no other routing has an http cell
    expect(presetForAxes("playercorefactory", "http")).toBeNull();
    expect(presetForAxes("service_interception", "http")).toBeNull();
  });

  it("routing_aliases map the stored external_player spelling onto playercorefactory", () => {
    const aliases = Object.fromEntries(
      PLAYBACK_PRESETS_DB.routing_aliases.map((e) => [e.alias, e.routing]),
    );
    expect(aliases.external_player).toBe("playercorefactory");
    expect(aliases.http_handoff).toBe("http_handoff");
  });
});
