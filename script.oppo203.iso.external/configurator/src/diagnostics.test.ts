import { beforeEach, describe, expect, it } from "vitest";
import { buildDiagnosticsReport, serializeDiagnostics } from "./diagnostics";
import { __resetForTest, type DebugEntry } from "./debug/log";
import { INITIAL_STATE, type WizardState } from "./state";

beforeEach(() => __resetForTest());

const env = { os: "windows", arch: "x86_64", configurator_version: "0.8.6" };

describe("buildDiagnosticsReport", () => {
  it("redacts secret-bearing wizard fields but keeps non-secret values", () => {
    const state: WizardState = {
      ...INITIAL_STATE,
      tvSonyPsk: "PSK-1234",
      tvSmartThingsToken: "TOK-abcd",
      avrSonyPsk: "PSK-zzzz",
      kodiIp: "10.0.1.42",
    };
    const json = serializeDiagnostics(buildDiagnosticsReport({ env, state, entries: [] }));
    expect(json).not.toContain("PSK-1234");
    expect(json).not.toContain("TOK-abcd");
    expect(json).not.toContain("PSK-zzzz");
    expect(json).toContain("[redacted]");
    // a non-secret field (the Kodi IP) and the env version survive for support context
    expect(json).toContain("10.0.1.42");
    expect(json).toContain("0.8.6");
  });

  it("includes the debug-log entry count and entries", () => {
    const entries: DebugEntry[] = [
      {
        kind: "ipc",
        seq: 0,
        ts: 0,
        step: null,
        command: "tcp_probe",
        args: { host: "10.0.1.42", port: 8080 },
        durationMs: 5,
        ok: true,
      },
    ];
    const report = buildDiagnosticsReport({ env, state: INITIAL_STATE, entries });
    expect(report.debugLog.count).toBe(1);
    expect(serializeDiagnostics(report)).toContain("tcp_probe");
  });

  it("carries session history through and notes the redaction policy", () => {
    const report = buildDiagnosticsReport({
      env,
      state: INITIAL_STATE,
      entries: [],
      sessionHistory: [{ sessionId: "s1", startedAt: "t", phase: "ended", title: "Disc" } as never],
    });
    const json = serializeDiagnostics(report);
    expect(json).toMatch(/redacted/i);
    expect(json).toContain('"os": "windows"');
    expect(json).toContain("s1");
  });
});
