import { beforeEach, describe, expect, it, vi } from "vitest";
import { boxResetCommand, resetEverything, resetStepPlan, type ResetStep } from "./reset";
import { INITIAL_STATE, type WizardState } from "./state";

const { invokeMock } = vi.hoisted(() => ({ invokeMock: vi.fn() }));
vi.mock("./ipc", () => ({ invoke: invokeMock }));

beforeEach(() => {
  invokeMock.mockReset();
});

const base = (over: Partial<WizardState>): WizardState => ({ ...INITIAL_STATE, ...over });

describe("boxResetCommand", () => {
  it("tier A -> reset_box_ssh against the platform dirs, with a Kodi restart", () => {
    const c = boxResetCommand(
      base({ tier: "A", kodiIp: "10.0.1.42", sshUser: "root", kodiPlatform: "coreelec" }),
    );
    expect(c?.command).toBe("reset_box_ssh");
    expect(c?.args).toMatchObject({
      host: "10.0.1.42",
      user: "root",
      userdataPath: "/storage/.kodi/userdata",
      addonsPath: "/storage/.kodi/addons",
      restart: true,
    });
  });

  it("tier A defaults the platform to coreelec when unset", () => {
    const c = boxResetCommand(base({ tier: "A", kodiPlatform: null }));
    expect(c?.args.addonsPath).toBe("/storage/.kodi/addons");
  });

  it("tier B -> reset_box_userdata against the SMB share's userdata/addons dirs", () => {
    const c = boxResetCommand(base({ tier: "B", smbSharePath: "\\\\10.0.1.42\\Kodi" }));
    expect(c?.command).toBe("reset_box_userdata");
    expect(c?.args.userdataPath).toBe("\\\\10.0.1.42\\Kodi\\userdata");
    expect(c?.args.addonsPath).toBe("\\\\10.0.1.42\\Kodi\\addons");
  });

  it("tier C / unset -> no box command (nothing was copied to a box)", () => {
    expect(boxResetCommand(base({ tier: "C" }))).toBeNull();
    expect(boxResetCommand(base({ tier: null }))).toBeNull();
  });
});

describe("resetStepPlan", () => {
  it("tier A -> box step (SSH) then the local step, all pending", () => {
    const p = resetStepPlan(base({ tier: "A", kodiIp: "10.0.1.42", sshUser: "root" }));
    expect(p.map((s) => s.key)).toEqual(["box", "local"]);
    expect(p[0].label).toMatch(/SSH/);
    expect(p.every((s) => s.status === "pending")).toBe(true);
  });

  it("tier B -> box step (share) then the local step", () => {
    const p = resetStepPlan(base({ tier: "B", smbSharePath: "\\\\10.0.1.42\\Kodi" }));
    expect(p.map((s) => s.key)).toEqual(["box", "local"]);
    expect(p[0].label).toMatch(/share/i);
  });

  it("tier C / unset -> only the local step (nothing was copied to a box)", () => {
    expect(resetStepPlan(base({ tier: "C" })).map((s) => s.key)).toEqual(["local"]);
    expect(resetStepPlan(base({ tier: null })).map((s) => s.key)).toEqual(["local"]);
  });
});

describe("resetEverything", () => {
  it("tier A: runs the box reset then the local reset; both succeed", async () => {
    invokeMock.mockResolvedValueOnce(["/addons/script.oppo203.iso.external"]);
    invokeMock.mockResolvedValueOnce(["state.json", "dashboard"]);
    const progress: ResetStep[][] = [];
    const r = await resetEverything(
      base({ tier: "A", kodiIp: "10.0.1.42", sshUser: "root" }),
      (s) => progress.push(s),
    );
    expect(r.ok).toBe(true);
    expect(r.boxFailed).toBe(false);
    expect(invokeMock).toHaveBeenNthCalledWith(
      1,
      "reset_box_ssh",
      expect.objectContaining({ host: "10.0.1.42" }),
    );
    expect(invokeMock).toHaveBeenNthCalledWith(2, "reset_app_data", {});
    const last = progress[progress.length - 1];
    expect(last.find((s) => s.key === "box")?.status).toBe("done");
    expect(last.find((s) => s.key === "local")?.status).toBe("done");
  });

  it("tier A: an unreachable box fails its step but the local reset still runs and succeeds", async () => {
    invokeMock.mockRejectedValueOnce("Kodi box 10.0.1.42:22 is unreachable over SSH");
    invokeMock.mockResolvedValueOnce(["state.json"]);
    const r = await resetEverything(base({ tier: "A", kodiIp: "10.0.1.42", sshUser: "root" }));
    expect(r.boxFailed).toBe(true);
    expect(r.ok).toBe(true);
    expect(invokeMock).toHaveBeenCalledTimes(2);
    expect(invokeMock).toHaveBeenNthCalledWith(2, "reset_app_data", {});
    expect(r.steps.find((s) => s.key === "box")?.status).toBe("failed");
    expect(r.steps.find((s) => s.key === "box")?.detail).toMatch(/unreachable/);
    expect(r.steps.find((s) => s.key === "local")?.status).toBe("done");
    expect(r.detail).toMatch(/reset to first run/i);
  });

  it("tier C: only the local reset runs", async () => {
    invokeMock.mockResolvedValueOnce([]);
    const r = await resetEverything(base({ tier: "C" }));
    expect(invokeMock).toHaveBeenCalledTimes(1);
    expect(invokeMock).toHaveBeenNthCalledWith(1, "reset_app_data", {});
    expect(r.steps.map((s) => s.key)).toEqual(["local"]);
    expect(r.ok).toBe(true);
    expect(r.boxFailed).toBe(false);
  });

  it("reports ok:false when the local reset itself fails", async () => {
    invokeMock.mockRejectedValueOnce("could not remove state.json");
    const r = await resetEverything(base({ tier: "C" }));
    expect(r.ok).toBe(false);
    expect(r.steps.find((s) => s.key === "local")?.status).toBe("failed");
    expect(r.detail).toMatch(/nothing was reset/i);
  });
});
