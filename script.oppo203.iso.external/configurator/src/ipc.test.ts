import { describe, expect, it, beforeEach, vi } from "vitest";

vi.mock("@tauri-apps/api/core", () => ({ invoke: vi.fn() }));

import { invoke as tauriInvoke } from "@tauri-apps/api/core";
import { invoke } from "./ipc";
import { getEntries, __resetForTest } from "./debug/log";

const invokeMock = vi.mocked(tauriInvoke);

beforeEach(() => {
  __resetForTest();
  invokeMock.mockReset();
});

describe("ipc invoke wrapper", () => {
  it("forwards command + args, returns the result, and records an ok entry", async () => {
    invokeMock.mockResolvedValue("@QPW OK ON");
    const r = await invoke<string>("oppo_query", { host: "10.0.1.5", command: "#QPW" });
    expect(r).toBe("@QPW OK ON");
    expect(invokeMock).toHaveBeenCalledWith("oppo_query", { host: "10.0.1.5", command: "#QPW" });
    const e = getEntries();
    expect(e).toHaveLength(1);
    expect(e[0]).toMatchObject({ command: "oppo_query", ok: true, result: "@QPW OK ON" });
  });

  it("forwards secret args intact to the command but redacts them in the log", async () => {
    invokeMock.mockResolvedValue(undefined);
    await invoke("save_wizard_state", { state: { avrSonyPsk: "TOPSECRET" } });
    expect(invokeMock).toHaveBeenCalledWith("save_wizard_state", {
      state: { avrSonyPsk: "TOPSECRET" },
    });
    const logged = getEntries()[0].args as { state: { avrSonyPsk: string } };
    expect(logged.state.avrSonyPsk).toBe("[redacted]");
  });

  it("rethrows the original error and records a fail entry", async () => {
    invokeMock.mockRejectedValue("boom");
    await expect(invoke("ssh_test", { host: "x", user: "root" })).rejects.toBe("boom");
    const e = getEntries();
    expect(e[0]).toMatchObject({ command: "ssh_test", ok: false, error: "boom" });
  });
});
