import { describe, expect, it } from "vitest";
import { INITIAL_STATE, type WizardState } from "./state";
import { planSwitch, type SwitchExtras } from "./step5_switch";

function make(over: Partial<WizardState>): WizardState {
  return { ...INITIAL_STATE, ...over };
}

const extras = (over: Partial<SwitchExtras>): SwitchExtras => ({
  externalTemplate: "",
  smartthingsDeviceId: "",
  smartthingsInputId: "",
  ...over,
});

describe("planSwitch — TV chain", () => {
  it("fires Roku ECP with the InputHDMI key", () => {
    const plan = planSwitch(make({ tvBackend: "roku_ecp", tvIp: "10.0.1.55" }), "oppo", 3);
    expect(plan.disposition).toBe("command");
    if (plan.disposition !== "command") return;
    expect(plan.command).toBe("tv_switch_roku");
    expect(plan.args).toEqual({ host: "10.0.1.55", key: "InputHDMI3" });
  });

  it("fires ADB over SSH with the discrete HDMI keyevent", () => {
    const plan = planSwitch(
      make({ tvBackend: "adb", tvIp: "10.0.1.55", kodiIp: "10.0.1.42", sshUser: "root" }),
      "oppo",
      2,
    );
    expect(plan.disposition).toBe("command");
    if (plan.disposition !== "command") return;
    expect(plan.command).toBe("tv_switch_adb");
    expect(plan.args).toMatchObject({
      sshHost: "10.0.1.42",
      tvHost: "10.0.1.55",
      tvPort: 5555,
      adbCommand: "input keyevent KEYCODE_TV_INPUT_HDMI_2",
    });
  });

  it("fires Sony Bravia only once a PSK is in state; manual fallback before that", () => {
    expect(
      planSwitch(make({ tvBackend: "sony_bravia", tvIp: "10.0.1.55" }), "oppo", 4).disposition,
    ).toBe("manual");
    const plan = planSwitch(
      make({ tvBackend: "sony_bravia", tvIp: "10.0.1.55", tvSonyPsk: "secret" }),
      "oppo",
      4,
    );
    expect(plan.disposition).toBe("command");
    if (plan.disposition !== "command") return;
    expect(plan.command).toBe("tv_switch_sony_bravia");
    expect(plan.args).toEqual({ host: "10.0.1.55", psk: "secret", port: 4 });
  });

  it("fires the external command only once a template is supplied", () => {
    const base = make({ tvBackend: "lg_command", tvIp: "10.0.1.55", kodiIp: "10.0.1.42" });
    expect(planSwitch(base, "oppo", 1).disposition).toBe("manual");
    const plan = planSwitch(base, "oppo", 1, extras({ externalTemplate: "curl http://{tv_ip}/x" }));
    expect(plan.disposition).toBe("command");
    if (plan.disposition !== "command") return;
    expect(plan.command).toBe("tv_switch_external");
    expect(plan.args).toMatchObject({ template: "curl http://{tv_ip}/x", tvIp: "10.0.1.55" });
  });

  it("builds (does not fire) a SmartThings request once ids are supplied", () => {
    const base = make({ tvBackend: "smartthings", tvIp: "10.0.1.55" });
    expect(planSwitch(base, "oppo", 1).disposition).toBe("manual");
    const plan = planSwitch(
      base,
      "oppo",
      1,
      extras({ smartthingsDeviceId: "dev-1", smartthingsInputId: "HDMI1" }),
    );
    expect(plan.disposition).toBe("request");
    if (plan.disposition !== "request") return;
    expect(plan.command).toBe("smartthings_switch_request");
    expect(plan.args).toEqual({ deviceId: "dev-1", inputId: "HDMI1" });
  });

  it("falls back to manual with no backend or no TV IP", () => {
    expect(planSwitch(make({ tvBackend: null }), "oppo", 1).disposition).toBe("manual");
    expect(planSwitch(make({ tvBackend: "roku_ecp", tvIp: "" }), "oppo", 1).disposition).toBe("manual");
  });
});

describe("planSwitch — AVR chain (receiver is the switcher)", () => {
  const avr = (over: Partial<WizardState>): WizardState =>
    make({
      topology: "kodi_avr_tv_player",
      avrIp: "10.0.1.90",
      avrPlayerInput: "BD",
      avrKodiInput: "CBL/SAT",
      ...over,
    });

  it("uses the receiver player input for the OPPO target (Denon)", () => {
    const plan = planSwitch(avr({ avrBackend: "denon_marantz" }), "oppo", 3);
    expect(plan.disposition).toBe("command");
    if (plan.disposition !== "command") return;
    expect(plan.command).toBe("avr_switch_denon");
    expect(plan.args).toEqual({ host: "10.0.1.90", input: "BD" });
  });

  it("uses the Kodi receiver input for the return target", () => {
    const plan = planSwitch(avr({ avrBackend: "denon_marantz" }), "kodi", 1);
    expect(plan.disposition).toBe("command");
    if (plan.disposition !== "command") return;
    expect(plan.args).toEqual({ host: "10.0.1.90", input: "CBL/SAT" });
  });

  it("sends inputCode for eISCP and input for Yamaha", () => {
    const onkyo = planSwitch(avr({ avrBackend: "onkyo_eiscp" }), "oppo", 1);
    expect(onkyo.disposition === "command" && onkyo.command).toBe("avr_switch_eiscp");
    expect(onkyo.disposition === "command" && onkyo.args).toEqual({ host: "10.0.1.90", inputCode: "BD" });
    const yamaha = planSwitch(avr({ avrBackend: "yamaha_yxc" }), "oppo", 1);
    expect(yamaha.disposition === "command" && yamaha.command).toBe("avr_switch_yamaha");
  });

  it("requires PSK + URI for Sony Audio, else manual", () => {
    expect(planSwitch(avr({ avrBackend: "sony_audio" }), "oppo", 1).disposition).toBe("manual");
    const plan = planSwitch(
      avr({ avrBackend: "sony_audio", avrSonyPsk: "k", avrSonyPlayerInputUri: "extInput:hdmi?port=2" }),
      "oppo",
      1,
    );
    expect(plan.disposition).toBe("command");
    if (plan.disposition !== "command") return;
    expect(plan.command).toBe("avr_switch_sony_audio");
    expect(plan.args).toEqual({ host: "10.0.1.90", inputUri: "extInput:hdmi?port=2", psk: "k" });
  });

  it("custom_command and a blank input fall back to manual", () => {
    expect(planSwitch(avr({ avrBackend: "custom_command" }), "oppo", 1).disposition).toBe("manual");
    expect(planSwitch(avr({ avrBackend: "denon_marantz", avrKodiInput: "" }), "kodi", 1).disposition).toBe(
      "manual",
    );
  });
});
