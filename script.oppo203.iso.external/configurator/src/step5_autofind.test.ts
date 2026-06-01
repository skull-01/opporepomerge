import { describe, expect, it } from "vitest";
import { INITIAL_STATE, type WizardState } from "./state";
import { autoFindMethod, autoFindProbePorts, sweepCommandFor } from "./step5_autofind";

function make(over: Partial<WizardState>): WizardState {
  return { ...INITIAL_STATE, ...over };
}

describe("autoFindMethod", () => {
  it("sweeps for Roku ECP and ADB once a TV IP is set", () => {
    expect(autoFindMethod(make({ tvBackend: "roku_ecp", tvIp: "10.0.1.55" }))).toBe("sweep");
    expect(autoFindMethod(make({ tvBackend: "adb", tvIp: "10.0.1.55", kodiIp: "10.0.1.42" }))).toBe(
      "sweep",
    );
  });

  it("is manual without a TV IP, or for non-sweepable backends", () => {
    expect(autoFindMethod(make({ tvBackend: "roku_ecp", tvIp: "" }))).toBe("manual");
    expect(autoFindMethod(make({ tvBackend: "sony_bravia", tvIp: "10.0.1.55" }))).toBe("manual");
    expect(autoFindMethod(make({ tvBackend: "smartthings", tvIp: "10.0.1.55" }))).toBe("manual");
    expect(autoFindMethod(make({ tvBackend: "lg_command", tvIp: "10.0.1.55" }))).toBe("manual");
    expect(autoFindMethod(make({ tvBackend: null }))).toBe("manual");
  });

  it("is manual in the AVR chain (receiver input is a named string, not a 1..4 sweep)", () => {
    expect(
      autoFindMethod(
        make({ topology: "kodi_avr_tv_player", avrBackend: "denon_marantz", avrIp: "10.0.1.90" }),
      ),
    ).toBe("manual");
  });
});

describe("sweepCommandFor", () => {
  it("yields the Roku per-input command for each rung", () => {
    const plan = sweepCommandFor(make({ tvBackend: "roku_ecp", tvIp: "10.0.1.55" }), 2);
    expect(plan?.command).toBe("tv_switch_roku");
    expect(plan?.args).toEqual({ host: "10.0.1.55", key: "InputHDMI2" });
  });

  it("is null when the backend cannot drive a discrete input", () => {
    expect(sweepCommandFor(make({ tvBackend: "smartthings", tvIp: "10.0.1.55" }), 1)).toBeNull();
    expect(sweepCommandFor(make({ tvBackend: "roku_ecp", tvIp: "" }), 1)).toBeNull();
  });
});

describe("autoFindProbePorts", () => {
  it("knocks on the right control port per backend", () => {
    expect(autoFindProbePorts(make({ tvBackend: "roku_ecp" }))).toEqual([8060]);
    expect(autoFindProbePorts(make({ tvBackend: "adb" }))).toEqual([5555]);
    expect(autoFindProbePorts(make({ tvBackend: "sony_bravia" }))).toEqual([]);
  });
});
