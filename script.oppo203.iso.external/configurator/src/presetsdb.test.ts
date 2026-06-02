import { describe, expect, it } from "vitest";
import { PLAYBACK_PRESETS, PLAYBACK_PRESETS_DB, presetForAxes } from "./presetsdb";

describe("playback-presets DB (shared six-option matrix)", () => {
  it("carries exactly the six canonical presets", () => {
    expect(PLAYBACK_PRESETS).toHaveLength(6);
    expect(new Set(PLAYBACK_PRESETS).size).toBe(6);
  });

  it("is the full cross-product of routing x monitor modes", () => {
    const { routing_modes, monitor_modes, preset_by_axes } = PLAYBACK_PRESETS_DB;
    expect(routing_modes.length * monitor_modes.length).toBe(6);
    const pairs = new Set(preset_by_axes.map((e) => `${e.routing}|${e.monitor}`));
    const expected = new Set(routing_modes.flatMap((r) => monitor_modes.map((m) => `${r}|${m}`)));
    expect(pairs).toEqual(expected);
  });

  it("preset_by_axes ids match the presets list and the `${routing}_${monitor}` convention", () => {
    for (const e of PLAYBACK_PRESETS_DB.preset_by_axes) {
      expect(PLAYBACK_PRESETS).toContain(e.preset);
      expect(e.preset).toBe(`${e.routing}_${e.monitor}`);
    }
  });

  it("presetForAxes resolves known pairs and rejects unknown ones", () => {
    expect(presetForAxes("http_handoff", "svm3")).toBe("http_handoff_svm3");
    expect(presetForAxes("playercorefactory", "legacy")).toBe("playercorefactory_legacy");
    expect(presetForAxes("nonsense", "svm3")).toBeNull();
  });

  it("routing_aliases map the stored external_player spelling onto playercorefactory", () => {
    const aliases = Object.fromEntries(
      PLAYBACK_PRESETS_DB.routing_aliases.map((e) => [e.alias, e.routing]),
    );
    expect(aliases.external_player).toBe("playercorefactory");
    expect(aliases.http_handoff).toBe("http_handoff");
  });
});
