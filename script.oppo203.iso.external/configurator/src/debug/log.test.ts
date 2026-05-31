import { describe, expect, it, beforeEach } from "vitest";
import {
  redact,
  record,
  getEntries,
  clearEntries,
  setCurrentStep,
  entriesForView,
  subscribe,
  __resetForTest,
  type DebugEntry,
} from "./log";

beforeEach(() => __resetForTest());

describe("redact", () => {
  it("blanks secret-bearing keys by name (PSK / token / password / secret / credential)", () => {
    const out = redact({
      sony_avr_psk: "ABC123",
      avrSonyPsk: "x",
      apiToken: "t",
      password: "p",
      mySecret: "s",
      nasCredential: "c",
      host: "10.0.1.5",
    }) as Record<string, unknown>;
    expect(out.sony_avr_psk).toBe("[redacted]");
    expect(out.avrSonyPsk).toBe("[redacted]");
    expect(out.apiToken).toBe("[redacted]");
    expect(out.password).toBe("[redacted]");
    expect(out.mySecret).toBe("[redacted]");
    expect(out.nasCredential).toBe("[redacted]");
    expect(out.host).toBe("10.0.1.5");
  });

  it("truncates long strings (deploy file blobs)", () => {
    const big = "x".repeat(5000);
    const out = redact(big) as string;
    expect(out.length).toBeLessThan(big.length);
    expect(out).toContain("[+3000 chars]");
  });

  it("recurses into nested objects and arrays", () => {
    const out = redact({ files: [{ name: "a", psk: "secret" }] }) as {
      files: { name: string; psk: string }[];
    };
    expect(out.files[0].name).toBe("a");
    expect(out.files[0].psk).toBe("[redacted]");
  });

  it("passes scalars and null through unchanged", () => {
    expect(redact(23)).toBe(23);
    expect(redact(true)).toBe(true);
    expect(redact(null)).toBe(null);
  });
});

describe("record + getEntries", () => {
  it("assigns increasing seq and stamps the current step", () => {
    setCurrentStep("step2");
    record({ ts: 1, command: "oppo_query", args: {}, durationMs: 5, ok: true, result: "@QPW OK ON" });
    setCurrentStep("step3");
    record({ ts: 2, command: "tv_port_probe", args: {}, durationMs: 9, ok: true, result: [] });
    const e = getEntries();
    expect(e.map((x) => x.seq)).toEqual([0, 1]);
    expect(e.map((x) => x.step)).toEqual(["step2", "step3"]);
    expect(e[0].command).toBe("oppo_query");
  });

  it("caps the ring buffer at 500 (drops oldest)", () => {
    for (let i = 0; i < 520; i += 1) {
      record({ ts: i, command: "x", args: {}, durationMs: 0, ok: true });
    }
    const e = getEntries();
    expect(e.length).toBe(500);
    expect(e[0].seq).toBe(20);
    expect(e[e.length - 1].seq).toBe(519);
  });

  it("clearEntries empties the log", () => {
    record({ ts: 1, command: "x", args: {}, durationMs: 0, ok: true });
    clearEntries();
    expect(getEntries()).toEqual([]);
  });
});

describe("subscribe", () => {
  it("notifies on record + clear and stops after unsubscribe", () => {
    let n = 0;
    const off = subscribe(() => {
      n += 1;
    });
    record({ ts: 1, command: "x", args: {}, durationMs: 0, ok: true });
    clearEntries();
    expect(n).toBe(2);
    off();
    record({ ts: 2, command: "y", args: {}, durationMs: 0, ok: true });
    expect(n).toBe(2);
  });
});

describe("entriesForView", () => {
  const mk = (seq: number, step: DebugEntry["step"]): DebugEntry => ({
    seq,
    ts: seq,
    step,
    command: "c",
    args: {},
    durationMs: 0,
    ok: true,
  });
  const all = [mk(0, "step2"), mk(1, "step3"), mk(2, "step2")];

  it("filters to the active step", () => {
    expect(entriesForView(all, "step2", false).map((e) => e.seq)).toEqual([0, 2]);
  });

  it("returns everything when showAll, or when the step is null", () => {
    expect(entriesForView(all, "step2", true).length).toBe(3);
    expect(entriesForView(all, null, false).length).toBe(3);
  });
});
