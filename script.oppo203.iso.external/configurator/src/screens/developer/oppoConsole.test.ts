import { describe, expect, it } from "vitest";
import { appendTranscript, httpRequestLabel, isSensitiveEndpoint, type TranscriptLine } from "./oppoConsole";

describe("OPPO console helpers", () => {
  it("flags the two credential-bearing endpoints as sensitive", () => {
    expect(isSensitiveEndpoint("/loginSambaWithID")).toBe(true);
    expect(isSensitiveEndpoint("/loginNfsServer")).toBe(true);
    expect(isSensitiveEndpoint("/getmovieplayinfo")).toBe(false);
    expect(isSensitiveEndpoint("/totally-unknown")).toBe(false);
  });

  it("redacts the query of sensitive endpoints in the transcript label", () => {
    expect(httpRequestLabel("/loginSambaWithID", "user=admin&password=hunter2")).toBe(
      "GET /loginSambaWithID?[redacted]"
    );
    // Non-sensitive endpoints keep their query visible for troubleshooting.
    expect(httpRequestLabel("/sendremotekey", "key=Up")).toBe("GET /sendremotekey?key=Up");
    // No query → no question mark.
    expect(httpRequestLabel("/getglobalinfo", "")).toBe("GET /getglobalinfo");
  });

  it("caps the transcript length, keeping the most recent lines", () => {
    const start: TranscriptLine[] = [];
    const many: TranscriptLine[] = Array.from({ length: 350 }, (_, i) => ({
      id: i,
      dir: "info" as const,
      text: `line ${i}`,
    }));
    const capped = appendTranscript(start, many, 300);
    expect(capped.length).toBe(300);
    expect(capped[0].text).toBe("line 50");
    expect(capped[capped.length - 1].text).toBe("line 349");
  });
});
