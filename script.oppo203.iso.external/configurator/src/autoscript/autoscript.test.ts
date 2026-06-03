// @vitest-environment node
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { generateAutoexec, type AutoScriptOptions } from "./autoscript-gen";
import {
  OPPO20X_AUTOSCRIPT_MIN_FIRMWARE,
  OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE,
  autoscriptFamily,
  firmwareMajorBuild,
  oppo20xAutoscriptFirmwareStatus,
} from "./capability";

const fixtures = JSON.parse(
  readFileSync(new URL("./autoscript-fixtures.json", import.meta.url), "utf8")
) as Record<string, string>;

// Same opt matrix as tests/test_autoscript_consistency.py. Both sides assert their generator
// reproduces autoscript-fixtures.json byte-for-byte, so the two generators are pinned to agree.
const CASES: Record<string, AutoScriptOptions> = {
  default: {},
  telnet_off: { enableTelnet: false },
  telnet_port_9999: { telnetPort: 9999 },
  no_passwordless: { passwordlessRoot: false },
  nfs: { mountType: "nfs", mountRemote: "10.0.1.10:/mnt/media" },
  cifs_creds: { mountType: "cifs", mountRemote: "//10.0.1.10/Media", cifsUser: "kodi", cifsPass: "pw" },
  adb_on: { enableAdb: true, adbPort: 5555 },
  no_heartbeat: { heartbeatPath: "" },
  full: {
    enableTelnet: true,
    telnetPort: 2323,
    passwordlessRoot: true,
    mountType: "cifs",
    mountRemote: "//nas/Media",
    mountLocal: "/tmp/share",
    cifsUser: "u",
    cifsPass: "p",
    enableAdb: true,
    adbPort: 5555,
    heartbeatPath: "/tmp/usb/sda1/oppo_autoexec_ran",
  },
  crlf_paths: {
    mountType: "cifs",
    mountRemote: "//nas/Media\r",
    mountLocal: "/tmp/share\r\n",
    cifsUser: "u\ru",
    cifsPass: "p\np",
    heartbeatPath: "/tmp/usb/sda1/oppo_autoexec_ran\r",
  },
};

describe("AutoScript generator — byte-identical to the add-on", () => {
  it("covers exactly the committed fixture cases", () => {
    expect(Object.keys(CASES).sort()).toEqual(Object.keys(fixtures).sort());
  });
  for (const [name, opts] of Object.entries(CASES)) {
    it(`reproduces fixture: ${name}`, () => {
      expect(generateAutoexec(opts)).toBe(fixtures[name]);
    });
  }
});

describe("AutoScript firmware capability — mirror of the add-on gating", () => {
  it("pins the thresholds", () => {
    expect(OPPO20X_AUTOSCRIPT_MIN_FIRMWARE).toBe("20X-56");
    expect(OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE).toBe("20X-65-0131");
  });

  it("parses the build component strictly like the add-on", () => {
    expect(firmwareMajorBuild("20X-65-0131")).toBe(65);
    expect(firmwareMajorBuild("20X-54-1127")).toBe(54);
    expect(firmwareMajorBuild("65-0131")).toBe(65);
    expect(firmwareMajorBuild("UDP20X-65-0131")).toBeNull();
    expect(firmwareMajorBuild("")).toBeNull();
    expect(firmwareMajorBuild(null)).toBeNull();
  });

  it("gates by build: <56 blocked · 56..64 supported+recommend · >=65 clean · unknown null", () => {
    const below = oppo20xAutoscriptFirmwareStatus("20X-54-1127");
    expect(below.autoscriptSupported).toBe(false);
    expect(below.blockers).toContain("oppo20x_firmware_below_20x_56");

    const atMin = oppo20xAutoscriptFirmwareStatus("20X-56");
    expect(atMin.autoscriptSupported).toBe(true);
    expect(atMin.warnings).toContain("oppo20x_autoscript_supported_but_20x_65_0131_recommended");

    const rec = oppo20xAutoscriptFirmwareStatus("20X-65-0131");
    expect(rec.autoscriptSupported).toBe(true);
    expect(rec.warnings).toEqual([]);

    expect(oppo20xAutoscriptFirmwareStatus("").autoscriptSupported).toBeNull();
  });

  it("classifies family: clone models vs JB stock OPPO", () => {
    expect(autoscriptFamily("M9702")).toBe("chinoppo_family");
    expect(autoscriptFamily("UDP-203")).toBe("oppo20x_jailbroken");
    expect(autoscriptFamily("UDP-205")).toBe("oppo20x_jailbroken");
    expect(autoscriptFamily("")).toBe("unknown");
  });
});
