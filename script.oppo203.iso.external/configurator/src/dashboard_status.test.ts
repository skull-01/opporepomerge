import { describe, expect, it } from "vitest";
import { INITIAL_STATE, type WizardState } from "./state";
import { canStartLiveStream, statusReadPlan } from "./dashboard_status";
import { ADDON_DATA_STATUS_REL, parseOppoStatus } from "./oppo_status";

function make(patch: Partial<WizardState>): WizardState {
  return { ...INITIAL_STATE, ...patch };
}

describe("statusReadPlan", () => {
  it("reads over SSH for tier A, at the status file under userdata", () => {
    const plan = statusReadPlan(make({ tier: "A", kodiIp: "10.0.1.42", sshUser: "root" }));
    expect(plan.supported).toBe(true);
    if (!plan.supported) return;
    expect(plan.command).toBe("read_ssh_file");
    expect(plan.args.rel).toBe(ADDON_DATA_STATUS_REL);
    expect(plan.args.host).toBe("10.0.1.42");
    expect(plan.args.user).toBe("root");
    expect(typeof plan.args.userdataPath).toBe("string");
  });

  it("reads from the SMB share for tier B", () => {
    const plan = statusReadPlan(make({ tier: "B", smbSharePath: "\\\\10.0.1.42\\Kodi" }));
    expect(plan.supported).toBe(true);
    if (!plan.supported) return;
    expect(plan.command).toBe("read_userdata_file");
    expect(plan.args.rel).toBe(ADDON_DATA_STATUS_REL);
    expect(String(plan.args.userdataPath)).toContain("userdata");
  });

  it("is unsupported in manual mode (tier C or unset) and never names a command", () => {
    for (const tier of ["C", null] as const) {
      const plan = statusReadPlan(make({ tier }));
      expect(plan.supported).toBe(false);
      if (plan.supported) return;
      expect(plan.note).toMatch(/manual mode/i);
    }
  });
});

describe("canStartLiveStream (dual-subscriber gate)", () => {
  it("blocks while the add-on reports an active session", () => {
    const starting = parseOppoStatus(
      JSON.stringify({ session_state: "starting", media_file: "x" })
    );
    const gate = canStartLiveStream(starting);
    expect(gate.allowed).toBe(false);
    expect(gate.reason).toMatch(/mid-session/i);
  });

  it("allows when the session has stopped/failed or there is no record", () => {
    const stopped = parseOppoStatus(JSON.stringify({ session_state: "stopped" }));
    const failed = parseOppoStatus(JSON.stringify({ session_state: "failed" }));
    expect(canStartLiveStream(stopped).allowed).toBe(true);
    expect(canStartLiveStream(failed).allowed).toBe(true);
    expect(canStartLiveStream(null).allowed).toBe(true);
  });
});
