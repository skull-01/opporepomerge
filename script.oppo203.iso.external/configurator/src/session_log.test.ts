import { describe, expect, it } from "vitest";
import { foldObservation, sessionSignature, type SessionLogEntry } from "./session_log";
import type { OppoSessionStatus } from "./oppo_status";

function status(patch: Partial<OppoSessionStatus> = {}): OppoSessionStatus {
  return {
    launchSource: "external_player",
    architecturePreset: "svm3",
    routingMode: "fast_start",
    monitorMode: "svm3",
    mediaFile: "/movies/a.iso",
    sessionState: "starting",
    confirmedPlayback: false,
    confirmedProgress: false,
    oppoPlaybackState: null,
    utcTickCount: null,
    stopReason: null,
    sessionId: null,
    startedAt: null,
    updatedAt: null,
    phase: null,
    ...patch,
  };
}

describe("foldObservation", () => {
  it("appends the first observed session", () => {
    const log = foldObservation([], status(), "t1");
    expect(log).toHaveLength(1);
    expect(log[0].sessionState).toBe("starting");
    expect(log[0].firstSeenAt).toBe("t1");
    expect(log[0].observedAt).toBe("t1");
  });

  it("returns the same array reference when the status is unchanged (idle poll, no persist)", () => {
    const log = foldObservation([], status(), "t1");
    const again = foldObservation(log, status(), "t2");
    expect(again).toBe(log);
  });

  it("updates the same session in place as it advances start -> stop", () => {
    const a = foldObservation([], status(), "t1");
    const b = foldObservation(
      a,
      status({ sessionState: "stopped", confirmedPlayback: true, stopReason: "ended" }),
      "t2",
    );
    expect(b).toHaveLength(1);
    expect(b[0].sessionState).toBe("stopped");
    expect(b[0].confirmedPlayback).toBe(true);
    expect(b[0].firstSeenAt).toBe("t1");
    expect(b[0].observedAt).toBe("t2");
  });

  it("opens a new entry when the same media replays after the prior session ended (id-less)", () => {
    const a = foldObservation([], status({ sessionState: "stopped" }), "t1");
    const b = foldObservation(a, status({ sessionState: "starting" }), "t2");
    expect(b).toHaveLength(2);
    expect(b[1].firstSeenAt).toBe("t2");
  });

  it("opens a new entry for a different session signature", () => {
    const a = foldObservation([], status({ mediaFile: "/movies/a.iso" }), "t1");
    const b = foldObservation(a, status({ mediaFile: "/movies/b.iso" }), "t2");
    expect(b.map((e) => e.mediaFile)).toEqual(["/movies/a.iso", "/movies/b.iso"]);
  });

  it("caps history to the newest `cap` entries", () => {
    let log: SessionLogEntry[] = [];
    for (let i = 0; i < 5; i++) {
      log = foldObservation(log, status({ sessionState: "stopped", mediaFile: `/m/${i}.iso` }), `t${i}`, 2);
    }
    expect(log).toHaveLength(2);
    expect(log.map((e) => e.mediaFile)).toEqual(["/m/3.iso", "/m/4.iso"]);
  });

  it("uses session_id for exact identity: same media, distinct ids -> distinct entries", () => {
    const a = foldObservation([], status({ sessionId: "s1", sessionState: "stopped" }), "t1");
    const b = foldObservation(a, status({ sessionId: "s2", sessionState: "starting" }), "t2");
    expect(b).toHaveLength(2);
    expect(b.map((e) => e.sessionId)).toEqual(["s1", "s2"]);
  });

  it("folds a heartbeat that only advances updatedAt/phase into the same entry (same session_id)", () => {
    const a = foldObservation(
      [],
      status({ sessionId: "s1", startedAt: 100, updatedAt: 100, phase: "launching" }),
      "t1",
    );
    const b = foldObservation(
      a,
      status({ sessionId: "s1", startedAt: 100, updatedAt: 160, phase: "monitoring" }),
      "t2",
    );
    expect(b).toHaveLength(1);
    expect(b[0].updatedAt).toBe(160);
    expect(b[0].phase).toBe("monitoring");
    expect(b[0].firstSeenAt).toBe("t1");
    expect(b[0].observedAt).toBe("t2");
  });

  it("sessionSignature ignores the volatile snapshot fields", () => {
    expect(sessionSignature(status({ utcTickCount: 10, oppoPlaybackState: "PLAY" }))).toBe(
      sessionSignature(status({ utcTickCount: 99, oppoPlaybackState: "STOP" })),
    );
  });

  it("sessionSignature is the session_id when present", () => {
    expect(sessionSignature(status({ sessionId: "abc" }))).toBe("id:abc");
  });
});
