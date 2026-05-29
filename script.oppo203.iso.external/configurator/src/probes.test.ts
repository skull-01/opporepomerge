import { describe, expect, it } from "vitest";
import { inferBackendFromPorts, parseOppoPowerReply, probePortList } from "./probes";

describe("inferBackendFromPorts", () => {
  it("prefers Roku ECP when :8060 is open", () => {
    expect(
      inferBackendFromPorts([
        { port: 5555, open: true },
        { port: 8060, open: true },
        { port: 20060, open: false },
      ]),
    ).toBe("roku_ecp");
  });

  it("falls to ADB when only :5555 is open", () => {
    expect(
      inferBackendFromPorts([
        { port: 8060, open: false },
        { port: 5555, open: true },
      ]),
    ).toBe("adb");
  });

  it("returns null when nothing answered", () => {
    expect(inferBackendFromPorts([{ port: 5555, open: false }])).toBeNull();
  });
});

describe("parseOppoPowerReply", () => {
  it("reads ON / OFF / unknown from the @QPW reply", () => {
    expect(parseOppoPowerReply("@QPW OK ON")).toBe("on");
    expect(parseOppoPowerReply("@QPW OK OFF")).toBe("off");
    expect(parseOppoPowerReply("")).toBe("unknown");
    expect(parseOppoPowerReply("garbage")).toBe("unknown");
  });

  it("treats an @QPW error reply as unknown (never a power state)", () => {
    expect(parseOppoPowerReply("@QPW ER")).toBe("unknown");
    expect(parseOppoPowerReply("@QPW OK STANDBY")).toBe("unknown");
  });
});

describe("probePortList", () => {
  it("includes the Roku and ADB ports", () => {
    expect(probePortList()).toContain(8060);
    expect(probePortList()).toContain(5555);
  });
});
