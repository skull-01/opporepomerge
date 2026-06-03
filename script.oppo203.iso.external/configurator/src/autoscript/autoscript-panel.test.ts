import { describe, expect, it } from "vitest";
import { oppo20xAutoscriptFirmwareStatus, parseQvrFirmware } from "./capability";
import { autoscriptReadme } from "./readme";

describe("parseQvrFirmware", () => {
  it("extracts the 20X build from #QVR replies (dropping the UDP prefix)", () => {
    expect(parseQvrFirmware("OK UDP20X-65-0131")).toBe("20X-65-0131");
    expect(parseQvrFirmware("@QVR OK UDP20X-56-1234")).toBe("20X-56-1234");
    expect(parseQvrFirmware("OK 20X-54-1127")).toBe("20X-54-1127");
    expect(parseQvrFirmware("ER INVALID")).toBe("");
    expect(parseQvrFirmware("")).toBe("");
  });

  it("feeds the capability gate end-to-end", () => {
    expect(oppo20xAutoscriptFirmwareStatus(parseQvrFirmware("OK UDP20X-65-0131")).autoscriptSupported).toBe(true);
    expect(oppo20xAutoscriptFirmwareStatus(parseQvrFirmware("OK UDP20X-54-1127")).autoscriptSupported).toBe(false);
  });
});

describe("autoscriptReadme", () => {
  it("covers the USB install essentials", () => {
    const r = autoscriptReadme({ telnetPort: 2323 });
    expect(r).toContain("FAT32");
    expect(r).toContain("autoexec.sh");
    expect(r).toMatch(/ROOT of the USB/i);
    expect(r).toContain("2323");
  });

  it("warns about the plaintext NAS password only when a CIFS password is set", () => {
    const withPw = autoscriptReadme({ mountType: "cifs", cifsPass: "secret" });
    expect(withPw).toMatch(/PLAIN TEXT/);
    const without = autoscriptReadme({ mountType: "none" });
    expect(without).not.toMatch(/PLAIN TEXT/);
  });
});
