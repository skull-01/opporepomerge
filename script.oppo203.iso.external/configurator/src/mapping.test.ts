import { describe, expect, it } from "vitest";
import { playerHardwareModel, wizardStateToAddonSettings } from "./mapping";
import { INITIAL_STATE, type WizardState } from "./state";

function makeState(patch: Partial<WizardState>): WizardState {
  return { ...INITIAL_STATE, ...patch };
}

describe("playerHardwareModel", () => {
  it("maps OPPO UDP-203 to the udp_203 enum value", () => {
    expect(
      playerHardwareModel(makeState({ playerBrand: "oppo", playerModel: "UDP-203" })),
    ).toBe("udp_203");
  });

  it("maps Chinoppo M9205 V1 to chinoppo_m9205", () => {
    expect(
      playerHardwareModel(makeState({ playerBrand: "chinoppo", playerModel: "M9205 V1" })),
    ).toBe("chinoppo_m9205");
  });

  it("maps Reavon UBR-X110 to reavon_ubrx110", () => {
    expect(
      playerHardwareModel(makeState({ playerBrand: "reavon", playerModel: "UBR-X110" })),
    ).toBe("reavon_ubrx110");
  });

  it("returns null when brand or model is unset", () => {
    expect(playerHardwareModel(makeState({ playerBrand: "oppo", playerModel: null }))).toBeNull();
    expect(playerHardwareModel(makeState({ playerBrand: null, playerModel: "UDP-203" }))).toBeNull();
  });

  it("returns null for an unknown model label", () => {
    expect(
      playerHardwareModel(makeState({ playerBrand: "oppo", playerModel: "UDP-999" })),
    ).toBeNull();
  });
});

describe("wizardStateToAddonSettings", () => {
  it("always writes the architecture choice", () => {
    const out = wizardStateToAddonSettings(
      makeState({ playbackArchitecture: "service_interception" }),
    );
    expect(out.playback_architecture).toBe("service_interception");
    expect(out.architecture_choice_made).toBe("true");
  });

  it("writes python_path from state", () => {
    expect(
      wizardStateToAddonSettings(makeState({ pythonPath: "/usr/bin/python3.11" })).python_path,
    ).toBe("/usr/bin/python3.11");
  });

  it("writes oppo_ip from playerIp and pins oppo_port to 23", () => {
    const out = wizardStateToAddonSettings(makeState({ playerIp: "10.0.1.80" }));
    expect(out.oppo_ip).toBe("10.0.1.80");
    expect(out.oppo_port).toBe("23");
  });

  it("passes tv_backend through and maps Roku HDMI inputs to InputHDMIn", () => {
    const out = wizardStateToAddonSettings(
      makeState({ tvBackend: "roku_ecp", oppoInput: 1, kodiInput: 2 }),
    );
    expect(out.tv_backend).toBe("roku_ecp");
    expect(out.roku_oppo_key).toBe("InputHDMI1");
    expect(out.roku_kodi_key).toBe("InputHDMI2");
  });

  it("maps Sony HDMI inputs to integer port strings", () => {
    const out = wizardStateToAddonSettings(
      makeState({ tvBackend: "sony_bravia", oppoInput: 3, kodiInput: 1 }),
    );
    expect(out.sony_oppo_hdmi_port).toBe("3");
    expect(out.sony_kodi_hdmi_port).toBe("1");
  });

  it("disables TV switching when the user dropped to manual", () => {
    expect(
      wizardStateToAddonSettings(makeState({ tvManualSwitch: true })).tv_switching_enabled,
    ).toBe("false");
    expect(
      wizardStateToAddonSettings(makeState({ tvManualSwitch: false })).tv_switching_enabled,
    ).toBe("true");
  });

  it("never emits kodi_host (configurator-side) or tv_ip (captured later)", () => {
    const out = wizardStateToAddonSettings(makeState({ tvBackend: "adb" }));
    expect(out.kodi_host).toBeUndefined();
    expect(out.tv_ip).toBeUndefined();
  });

  it("omits oppo_hardware_model until a player model is chosen", () => {
    expect(wizardStateToAddonSettings(makeState({})).oppo_hardware_model).toBeUndefined();
  });
});
