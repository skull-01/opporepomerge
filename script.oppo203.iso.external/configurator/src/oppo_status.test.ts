import { describe, expect, it } from "vitest";
import { parseOppoStatus } from "./oppo_status";

const STOPPED = JSON.stringify({
  launch_source: "service_interception",
  architecture_preset: "service_interception_svm3",
  routing_mode: "service_interception",
  monitor_mode: "svm3",
  media_file: "/storage/movie.iso",
  session_state: "stopped",
  confirmed_playback: true,
  confirmed_progress: true,
  oppo_playback_state: "PLAY",
  utc_tick_count: 42,
  stop_reason: "oppo_stop",
});

const STARTING = JSON.stringify({
  launch_source: "playercorefactory",
  architecture_preset: "playercorefactory_legacy",
  routing_mode: "playercorefactory",
  monitor_mode: "legacy",
  media_file: "/storage/movie.iso",
  session_state: "starting",
  confirmed_playback: false,
  confirmed_progress: false,
});

describe("parseOppoStatus", () => {
  it("maps a completed (snapshot) record to camelCase", () => {
    const s = parseOppoStatus(STOPPED);
    expect(s).toEqual({
      launchSource: "service_interception",
      architecturePreset: "service_interception_svm3",
      routingMode: "service_interception",
      monitorMode: "svm3",
      mediaFile: "/storage/movie.iso",
      sessionState: "stopped",
      confirmedPlayback: true,
      confirmedProgress: true,
      oppoPlaybackState: "PLAY",
      utcTickCount: 42,
      stopReason: "oppo_stop",
    });
  });

  it("parses a starting record with no snapshot fields (they default to null)", () => {
    const s = parseOppoStatus(STARTING);
    expect(s?.sessionState).toBe("starting");
    expect(s?.oppoPlaybackState).toBeNull();
    expect(s?.utcTickCount).toBeNull();
    expect(s?.stopReason).toBeNull();
    expect(s?.confirmedPlayback).toBe(false);
  });

  it("returns null for an unrecognized or missing session_state", () => {
    expect(parseOppoStatus(JSON.stringify({ session_state: "paused" }))).toBeNull();
    expect(parseOppoStatus(JSON.stringify({ media_file: "x" }))).toBeNull();
  });

  it("returns null for non-JSON, empty, or null input", () => {
    expect(parseOppoStatus("not json")).toBeNull();
    expect(parseOppoStatus("")).toBeNull();
    expect(parseOppoStatus(null)).toBeNull();
    expect(parseOppoStatus(undefined)).toBeNull();
  });

  it("coerces wrong-typed fields rather than trusting them (booleans/number)", () => {
    const s = parseOppoStatus(
      JSON.stringify({
        session_state: "stopped",
        confirmed_playback: "yes",
        utc_tick_count: "12",
        oppo_playback_state: 5,
      })
    );
    expect(s?.confirmedPlayback).toBe(false);
    expect(s?.utcTickCount).toBeNull();
    expect(s?.oppoPlaybackState).toBeNull();
  });
});
