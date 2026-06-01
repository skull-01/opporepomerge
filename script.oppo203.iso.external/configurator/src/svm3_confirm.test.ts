import { describe, expect, it } from "vitest";
import {
  foldSvm3Frame,
  foldSvm3Frames,
  INITIAL_SVM3_CONFIRM,
  parseLiveLine,
  uplStateLabel,
  type LiveFrame,
} from "./svm3_confirm";

const frame = (raw: string, seq = 0, kind = "raw"): LiveFrame => ({ seq, kind, raw });

describe("parseLiveLine", () => {
  it("strips a leading @ and upper-cases the code", () => {
    expect(parseLiveLine("@UPL PLAY")).toEqual({ code: "UPL", rest: "PLAY" });
    expect(parseLiveLine("upl play")).toEqual({ code: "UPL", rest: "play" });
  });

  it("handles a bare code with no remainder", () => {
    expect(parseLiveLine("@STOP")).toEqual({ code: "STOP", rest: "" });
  });

  it("returns null for an empty/whitespace line", () => {
    expect(parseLiveLine("   ")).toBeNull();
    expect(parseLiveLine("@")).toBeNull();
  });
});

describe("uplStateLabel", () => {
  it("maps active values to PLAY", () => {
    for (const v of ["PLAY", "FFWD", "FREV", "SFWD", "SREV", "LOADING"]) {
      expect(uplStateLabel(v)).toBe("PLAY");
    }
  });

  it("maps pause / menu / stop families", () => {
    expect(uplStateLabel("PAUSE")).toBe("PAUS");
    expect(uplStateLabel("DISC MENU")).toBe("MENU");
    expect(uplStateLabel("HOME MENU")).toBe("HOME");
    expect(uplStateLabel("MEDIA CENTER")).toBe("MCTR");
    expect(uplStateLabel("NO DISC")).toBe("STOP");
  });

  it("returns unknown for anything else", () => {
    expect(uplStateLabel("WHAT")).toBe("unknown");
  });
});

describe("foldSvm3Frame / foldSvm3Frames", () => {
  it("confirms playback only on an active @UPL value", () => {
    const r = foldSvm3Frame(INITIAL_SVM3_CONFIRM, frame("@UPL PLAY"));
    expect(r.confirmedPlayback).toBe(true);
    expect(r.playbackState).toBe("PLAY");
  });

  it("does NOT confirm playback from a pause or menu state", () => {
    const r = foldSvm3Frames([frame("@UPL LOADING"), frame("@UPL PAUSE")]);
    // LOADING confirmed playback; the later PAUSE doesn't un-confirm it, but on its own PAUSE wouldn't.
    expect(r.confirmedPlayback).toBe(true);
    const pauseOnly = foldSvm3Frame(INITIAL_SVM3_CONFIRM, frame("@UPL PAUSE"));
    expect(pauseOnly.confirmedPlayback).toBe(false);
    expect(pauseOnly.playbackState).toBe("PAUS");
  });

  it("confirms progress only when the @UTC time code advances", () => {
    const first = foldSvm3Frame(INITIAL_SVM3_CONFIRM, frame("@UTC 0 0 T 00:00:01"));
    expect(first.confirmedProgress).toBe(false);
    expect(first.utcTicks).toBe(1);
    expect(first.lastUtc).toBe("0 0 T 00:00:01");

    // The SAME code again does not advance progress.
    const same = foldSvm3Frame(first, frame("@UTC 0 0 T 00:00:01"));
    expect(same.confirmedProgress).toBe(false);
    expect(same.utcTicks).toBe(1);

    // A DIFFERENT code advances it.
    const next = foldSvm3Frame(same, frame("@UTC 0 0 T 00:00:02"));
    expect(next.confirmedProgress).toBe(true);
    expect(next.utcTicks).toBe(2);
    expect(next.lastUtc).toBe("0 0 T 00:00:02");
  });

  it("confirms both playback and progress over a realistic stream", () => {
    const r = foldSvm3Frames([
      frame("verbose mode 3 enabled (prior mode 2)", 0, "info"),
      frame("@UPL LOADING", 1, "upl"),
      frame("@UPL PLAY", 2, "upl"),
      frame("@UTC 0 0 T 00:00:01", 3, "utc"),
      frame("@UTC 0 0 T 00:00:02", 4, "utc"),
      frame("@UTC 0 0 T 00:00:03", 5, "utc"),
    ]);
    expect(r.confirmedPlayback).toBe(true);
    expect(r.confirmedProgress).toBe(true);
    expect(r.utcTicks).toBe(3);
    expect(r.stopped).toBe(false);
  });

  it("marks a terminal stop state", () => {
    const r = foldSvm3Frames([frame("@UPL PLAY"), frame("@UPL STOP")]);
    expect(r.stopped).toBe(true);
    expect(r.playbackState).toBe("STOP");
    // a disc MENU is not a stop.
    expect(foldSvm3Frame(INITIAL_SVM3_CONFIRM, frame("@UPL DISC MENU")).stopped).toBe(false);
  });

  it("ignores non-UPL/UTC frames", () => {
    const r = foldSvm3Frame(INITIAL_SVM3_CONFIRM, frame("connection closed by player", 9, "info"));
    expect(r).toEqual(INITIAL_SVM3_CONFIRM);
  });
});
