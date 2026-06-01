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
      makeState({ tvBackend: "roku_ecp", playerInput: 1, kodiInput: 2 }),
    );
    expect(out.tv_backend).toBe("roku_ecp");
    expect(out.roku_oppo_key).toBe("InputHDMI1");
    expect(out.roku_kodi_key).toBe("InputHDMI2");
  });

  it("maps Sony HDMI inputs to integer port strings", () => {
    const out = wizardStateToAddonSettings(
      makeState({ tvBackend: "sony_bravia", playerInput: 3, kodiInput: 1 }),
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

describe("topology-aware AVR switcher settings", () => {
  const denonAvrChain: Partial<WizardState> = {
    topology: "kodi_avr_tv_player",
    avrBrand: "denon",
    avrBackend: "denon_marantz",
    avrIp: "10.0.1.91",
    avrPlayerInput: "BD",
    avrKodiInput: "CBL/SAT",
  };

  it("emits receiver power-on + restore-to-Kodi-input for the AVR chain", () => {
    const out = wizardStateToAddonSettings(makeState(denonAvrChain));
    expect(out.avr_control_enabled).toBe("true");
    expect(out.avr_power_on_enabled).toBe("true");
    expect(out.avr_restore_enabled).toBe("true");
    expect(out.avr_restore_input).toBe("CBL/SAT");
  });

  it("sources the restore input from the dedicated receiver field, not the TV's kodiInput", () => {
    const out = wizardStateToAddonSettings(
      makeState({ ...denonAvrChain, kodiInput: 5, avrKodiInput: "8K" }),
    );
    expect(out.avr_restore_input).toBe("8K");
  });

  it("turns TV switching off in the AVR chain even with a TV backend configured", () => {
    const out = wizardStateToAddonSettings(
      makeState({ ...denonAvrChain, tvBackend: "adb", tvManualSwitch: false }),
    );
    expect(out.tv_switching_enabled).toBe("false");
    // the TV backend is still passed through for reference; only switching is gated off
    expect(out.tv_backend).toBe("adb");
  });

  it("does NOT emit restore/power settings for the TV chain (regression pin)", () => {
    const out = wizardStateToAddonSettings(
      makeState({ ...denonAvrChain, topology: "kodi_tv_player" }),
    );
    expect(out.avr_power_on_enabled).toBeUndefined();
    expect(out.avr_restore_enabled).toBeUndefined();
    expect(out.avr_restore_input).toBeUndefined();
    // and the existing AVR control settings are unchanged
    expect(out.avr_backend).toBe("denon_marantz");
    expect(out.avr_control_enabled).toBe("true");
  });

  it("omits the restore input (but still powers on) when no receiver Kodi input is given", () => {
    const out = wizardStateToAddonSettings(
      makeState({ ...denonAvrChain, avrKodiInput: "" }),
    );
    expect(out.avr_power_on_enabled).toBe("true");
    expect(out.avr_restore_enabled).toBeUndefined();
    expect(out.avr_restore_input).toBeUndefined();
  });

  it("writes no switcher settings when AVR control is not enabled (missing input)", () => {
    const out = wizardStateToAddonSettings(
      makeState({ ...denonAvrChain, avrPlayerInput: "" }),
    );
    expect(out.avr_control_enabled).toBe("false");
    expect(out.avr_power_on_enabled).toBeUndefined();
    expect(out.avr_restore_enabled).toBeUndefined();
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

describe("wizardStateToAddonSettings — six-option playback preset", () => {
  it("defaults to the legacy playercorefactory preset", () => {
    const out = wizardStateToAddonSettings(INITIAL_STATE);
    expect(out.playback_monitor_mode).toBe("legacy");
    expect(out.playback_architecture).toBe("external_player");
    expect(out.playback_architecture_preset).toBe("playercorefactory_legacy");
  });

  it("emits playercorefactory_svm3 for external_player + svm3", () => {
    const out = wizardStateToAddonSettings(
      makeState({ playbackArchitecture: "external_player", monitorMode: "svm3" }),
    );
    expect(out.playback_monitor_mode).toBe("svm3");
    expect(out.playback_architecture_preset).toBe("playercorefactory_svm3");
  });

  it("emits service_interception_svm3 for service_interception + svm3", () => {
    const out = wizardStateToAddonSettings(
      makeState({ playbackArchitecture: "service_interception", monitorMode: "svm3" }),
    );
    expect(out.playback_architecture_preset).toBe("service_interception_svm3");
  });

  it("emits service_interception_legacy for service_interception + legacy", () => {
    const out = wizardStateToAddonSettings(
      makeState({ playbackArchitecture: "service_interception", monitorMode: "legacy" }),
    );
    expect(out.playback_architecture_preset).toBe("service_interception_legacy");
  });

  it("emits http_handoff_svm3 for http_handoff + svm3", () => {
    const out = wizardStateToAddonSettings(
      makeState({ playbackArchitecture: "http_handoff", monitorMode: "svm3" }),
    );
    expect(out.playback_architecture).toBe("http_handoff");
    expect(out.playback_architecture_preset).toBe("http_handoff_svm3");
  });

  it("emits http_handoff_legacy for http_handoff + legacy", () => {
    const out = wizardStateToAddonSettings(
      makeState({ playbackArchitecture: "http_handoff", monitorMode: "legacy" }),
    );
    expect(out.playback_architecture_preset).toBe("http_handoff_legacy");
  });

  it("emits json_payload mode only for the http_handoff routing", () => {
    const http = wizardStateToAddonSettings(makeState({ playbackArchitecture: "http_handoff" }));
    expect(http.oppo_http_payload_mode).toBe("json_payload");
    const pcf = wizardStateToAddonSettings(makeState({ playbackArchitecture: "external_player" }));
    expect(pcf.oppo_http_payload_mode).toBeUndefined();
    const svc = wizardStateToAddonSettings(
      makeState({ playbackArchitecture: "service_interception" }),
    );
    expect(svc.oppo_http_payload_mode).toBeUndefined();
  });

  it("keeps the emitted triple internally consistent across all six combos", () => {
    const archByRouting = {
      playercorefactory: "external_player",
      service_interception: "service_interception",
      http_handoff: "http_handoff",
    } as const;
    for (const routing of [
      "playercorefactory",
      "service_interception",
      "http_handoff",
    ] as const) {
      for (const monitor of ["legacy", "svm3"] as const) {
        const out = wizardStateToAddonSettings(
          makeState({ playbackArchitecture: archByRouting[routing], monitorMode: monitor }),
        );
        expect(out.playback_architecture_preset).toBe(`${routing}_${monitor}`);
        expect(out.playback_monitor_mode).toBe(monitor);
        expect(out.playback_architecture).toBe(archByRouting[routing]);
      }
    }
  });
});
