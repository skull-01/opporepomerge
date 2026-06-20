import { describe, expect, it } from "vitest";
import { appendTranscript, type TranscriptLine } from "./devTranscript";

describe("devTranscript.appendTranscript", () => {
  it("appends and assigns nothing (ids are caller-supplied)", () => {
    const a: TranscriptLine[] = [{ id: 0, dir: "tx", text: "a" }];
    const out = appendTranscript(a, [{ id: 1, dir: "rx", text: "b" }]);
    expect(out.map((l) => l.text)).toEqual(["a", "b"]);
  });

  it("caps to the most recent lines", () => {
    const many: TranscriptLine[] = Array.from({ length: 420 }, (_, i) => ({
      id: i,
      dir: "info" as const,
      text: `line ${i}`,
    }));
    const out = appendTranscript([], many, 300);
    expect(out.length).toBe(300);
    expect(out[0].text).toBe("line 120");
    expect(out[out.length - 1].text).toBe("line 419");
  });
});
