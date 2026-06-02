import { describe, expect, it } from "vitest";
import { boxResetCommand } from "./reset";
import { INITIAL_STATE, type WizardState } from "./state";

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
