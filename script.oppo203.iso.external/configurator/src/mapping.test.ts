import { describe, expect, it } from "vitest";
import { avrAddonBackend, playerHardwareModel, wizardStateToAddonSettings } from "./mapping";
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

  it("maps Chinoppo M9205 V1 to chinoppo_m9205_v1 (distinct from plain M9205)", () => {
    expect(
      playerHardwareModel(makeState({ playerBrand: "chinoppo", playerModel: "M9205 V1" })),
    ).toBe("chinoppo_m9205_v1");
    expect(
      playerHardwareModel(makeState({ playerBrand: "chinoppo", playerModel: "M9205" })),
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

  it("enables TV switching only with a backend configured and not manual", () => {
    // backend configured + auto -> enabled
    expect(
      wizardStateToAddonSettings(makeState({ tvBackend: "adb", tvManualSwitch: false }))
        .tv_switching_enabled,
    ).toBe("true");
    // backend configured but user dropped to manual -> disabled
    expect(
      wizardStateToAddonSettings(makeState({ tvBackend: "adb", tvManualSwitch: true }))
        .tv_switching_enabled,
    ).toBe("false");
    // no backend (TV setup skipped) -> disabled, so the add-on's default backend isn't switched
    expect(
      wizardStateToAddonSettings(makeState({ tvManualSwitch: false })).tv_switching_enabled,
    ).toBe("false");
  });

  it("never emits kodi_host (configurator-side) or tv_ip (captured later)", () => {
    const out = wizardStateToAddonSettings(makeState({ tvBackend: "adb" }));
    expect(out.kodi_host).toBeUndefined();
    expect(out.tv_ip).toBeUndefined();
  });

  it("omits oppo_hardware_model until a player model is chosen", () => {
    expect(wizardStateToAddonSettings(makeState({})).oppo_hardware_model).toBeUndefined();
  });

  it("writes a Denon receiver as denon_marantz and enables control with host + input", () => {
    const out = wizardStateToAddonSettings(
      makeState({
        avrBrand: "denon",
        avrBackend: "denon_marantz",
        avrIp: "10.0.1.91",
        avrPlayerInput: "BD",
      }),
    );
    expect(out.avr_backend).toBe("denon_marantz");
    expect(out.avr_host).toBe("10.0.1.91");
    expect(out.avr_player_input).toBe("BD");
    expect(out.avr_control_enabled).toBe("true");
  });

  it("splits Pioneer (DB onkyo_eiscp) back out to the add-on's pioneer_eiscp driver", () => {
    const out = wizardStateToAddonSettings(
      makeState({
        avrBrand: "pioneer",
        avrBackend: "onkyo_eiscp",
        avrIp: "10.0.1.92",
        avrPlayerInput: "BD/DVD",
      }),
    );
    expect(out.avr_backend).toBe("pioneer_eiscp");
    expect(out.avr_control_enabled).toBe("true");
  });

  it("keeps Onkyo/Integra on onkyo_eiscp", () => {
    expect(
      wizardStateToAddonSettings(
        makeState({ avrBrand: "onkyo", avrBackend: "onkyo_eiscp", avrIp: "1.2.3.4", avrPlayerInput: "10" }),
      ).avr_backend,
    ).toBe("onkyo_eiscp");
  });

  it("configures Sony as sony_audio_api but leaves control disabled without ack + PSK + URI", () => {
    const out = wizardStateToAddonSettings(
      makeState({
        avrBrand: "sony",
        avrBackend: "sony_audio",
        avrIp: "10.0.1.93",
        avrPlayerInput: "BD",
      }),
    );
    expect(out.avr_backend).toBe("sony_audio_api");
    expect(out.avr_host).toBe("10.0.1.93");
    expect(out.avr_control_enabled).toBe("false");
    expect(out.sony_avr_experimental_acknowledged).toBeUndefined();
    expect(out.sony_avr_psk).toBeUndefined();
  });

  it("enables Sony control once ack + PSK + input URI are supplied", () => {
    const out = wizardStateToAddonSettings(
      makeState({
        avrBrand: "sony",
        avrBackend: "sony_audio",
        avrIp: "10.0.1.93",
        avrPlayerInput: "BD",
        avrSonyAcknowledged: true,
        avrSonyPsk: "1234",
        avrSonyPlayerInputUri: "extInput:hdmi?port=2",
      }),
    );
    expect(out.avr_backend).toBe("sony_audio_api");
    expect(out.avr_control_enabled).toBe("true");
    expect(out.sony_avr_experimental_acknowledged).toBe("true");
    expect(out.sony_avr_psk).toBe("1234");
    expect(out.sony_avr_player_input_uri).toBe("extInput:hdmi?port=2");
  });

  it("keeps Sony disabled when the acknowledgement, PSK, or URI is missing", () => {
    const base: Partial<WizardState> = {
      avrBrand: "sony",
      avrBackend: "sony_audio",
      avrIp: "10.0.1.93",
      avrPlayerInput: "BD",
      avrSonyAcknowledged: true,
      avrSonyPsk: "1234",
      avrSonyPlayerInputUri: "extInput:hdmi?port=2",
    };
    expect(
      wizardStateToAddonSettings(makeState({ ...base, avrSonyAcknowledged: false }))
        .avr_control_enabled,
    ).toBe("false");
    expect(
      wizardStateToAddonSettings(makeState({ ...base, avrSonyPsk: "" })).avr_control_enabled,
    ).toBe("false");
    expect(
      wizardStateToAddonSettings(makeState({ ...base, avrSonyPlayerInputUri: "" }))
        .avr_control_enabled,
    ).toBe("false");
  });

  it("writes no avr_backend for custom_command brands (no native driver)", () => {
    const out = wizardStateToAddonSettings(
      makeState({ avrBrand: "anthem", avrBackend: "custom_command", avrIp: "1.2.3.4", avrPlayerInput: "x" }),
    );
    expect(out.avr_backend).toBeUndefined();
    expect(out.avr_control_enabled).toBeUndefined();
  });

  it("emits nothing AVR-related when the optional step is skipped", () => {
    const out = wizardStateToAddonSettings(makeState({}));
    expect(out.avr_backend).toBeUndefined();
    expect(out.avr_host).toBeUndefined();
    expect(out.avr_control_enabled).toBeUndefined();
  });

  it("records the backend but does not enable when host or input is missing", () => {
    const out = wizardStateToAddonSettings(
      makeState({ avrBrand: "yamaha", avrBackend: "yamaha_yxc", avrIp: "", avrPlayerInput: "" }),
    );
    expect(out.avr_backend).toBe("yamaha_yxc");
    expect(out.avr_control_enabled).toBe("false");
    expect(out.avr_host).toBeUndefined();
  });
});

describe("avrAddonBackend", () => {
  it("maps the DB backend vocabulary onto the add-on avr_backend enum", () => {
    expect(avrAddonBackend("denon_marantz", "denon")).toBe("denon_marantz");
    expect(avrAddonBackend("denon_marantz", "marantz")).toBe("denon_marantz");
    expect(avrAddonBackend("yamaha_yxc", "yamaha")).toBe("yamaha_yxc");
    expect(avrAddonBackend("sony_audio", "sony")).toBe("sony_audio_api");
    expect(avrAddonBackend("onkyo_eiscp", "onkyo")).toBe("onkyo_eiscp");
    expect(avrAddonBackend("onkyo_eiscp", "integra")).toBe("onkyo_eiscp");
    expect(avrAddonBackend("onkyo_eiscp", "pioneer")).toBe("pioneer_eiscp");
  });

  it("returns null for custom_command and unset backends", () => {
    expect(avrAddonBackend("custom_command", "anthem")).toBeNull();
    expect(avrAddonBackend(null, "denon")).toBeNull();
  });
});
