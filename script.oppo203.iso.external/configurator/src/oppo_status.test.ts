import { describe, expect, it } from "vitest";
import { formatEpochAge, isStatusFresh, parseOppoStatus } from "./oppo_status";

const STOPPED = JSON.stringify({
  session_id: "a1b2c3d4e5f60718",
  started_at: 1717000000,
  updated_at: 1717000125,
  phase: "ended",
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
      sessionId: "a1b2c3d4e5f60718",
      startedAt: 1717000000,
      updatedAt: 1717000125,
      phase: "ended",
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

  it("treats the identity/timing/phase fields as optional (null on an older record)", () => {
    const s = parseOppoStatus(STARTING);
    expect(s?.sessionId).toBeNull();
    expect(s?.startedAt).toBeNull();
    expect(s?.updatedAt).toBeNull();
    expect(s?.phase).toBeNull();
  });

  it("reads the identity/timing/phase fields when present and coerces a bad phase to null", () => {
    const s = parseOppoStatus(
      JSON.stringify({
        session_state: "starting",
        session_id: "deadbeef",
        started_at: 100,
        updated_at: 160,
        phase: "monitoring",
      })
    );
    expect(s?.sessionId).toBe("deadbeef");
    expect(s?.startedAt).toBe(100);
    expect(s?.updatedAt).toBe(160);
    expect(s?.phase).toBe("monitoring");

    const bad = parseOppoStatus(
      JSON.stringify({ session_state: "starting", phase: "paused", started_at: "soon" })
    );
    expect(bad?.phase).toBeNull();
    expect(bad?.startedAt).toBeNull();
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

describe("formatEpochAge", () => {
  const now = 2_000_000 * 1000; // 2,000,000s in ms

  it("returns null when the timestamp is absent (older records carry no timing)", () => {
    expect(formatEpochAge(null, now)).toBeNull();
  });

  it("reads sub-minute and future timestamps as 'just now'", () => {
    expect(formatEpochAge(2_000_000 - 5, now)).toBe("just now");
    expect(formatEpochAge(2_000_000 + 30, now)).toBe("just now");
  });

  it("formats minutes, whole hours, and hours+minutes", () => {
    expect(formatEpochAge(2_000_000 - 5 * 60, now)).toBe("5m ago");
    expect(formatEpochAge(2_000_000 - 2 * 3600, now)).toBe("2h ago");
    expect(formatEpochAge(2_000_000 - (3 * 3600 + 7 * 60), now)).toBe("3h 7m ago");
  });
});

describe("isStatusFresh", () => {
  const now = 1_000_000 * 1000;

  it("returns null when updatedAt is absent (freshness unknown)", () => {
    expect(isStatusFresh(null, now)).toBeNull();
  });

  it("is fresh within the window and stale beyond it", () => {
    expect(isStatusFresh(1_000_000 - 30, now)).toBe(true);
    expect(isStatusFresh(1_000_000 - 119, now)).toBe(true);
    expect(isStatusFresh(1_000_000 - 600, now)).toBe(false);
  });
});
