import { describe, expect, it } from "vitest";
import { INITIAL_STATE, type WizardState } from "./state";
import { livenessTargets } from "./dashboard_targets";

function make(patch: Partial<WizardState>): WizardState {
  return { ...INITIAL_STATE, ...patch };
}

describe("livenessTargets", () => {
  it("checks the Kodi box and the player, and omits the TV until an IP is captured", () => {
    const targets = livenessTargets(make({ topology: "kodi_tv_player" }));
    expect(targets.map((t) => t.id)).toEqual(["kodi", "player"]);
    const player = targets.find((t) => t.id === "player");
    expect(player).toMatchObject({ host: INITIAL_STATE.playerIp, port: 23, kind: "oppo" });
  });

  it("adds the TV when a backend with a TCP port and an IP are set, else omits it", () => {
    expect(
      livenessTargets(make({ tvBackend: "roku_ecp", tvIp: "10.0.1.55" })).find((t) => t.id === "tv")
    ).toMatchObject({ host: "10.0.1.55", port: 8060, kind: "tcp" });
    expect(
      livenessTargets(make({ tvBackend: "adb", tvIp: "10.0.1.55" })).find((t) => t.id === "tv")?.port
    ).toBe(5555);
    expect(livenessTargets(make({ tvBackend: "roku_ecp", tvIp: "" })).some((t) => t.id === "tv")).toBe(
      false
    );
    expect(
      livenessTargets(make({ tvBackend: "smartthings", tvIp: "10.0.1.55" })).some((t) => t.id === "tv")
    ).toBe(false);
  });

  it("probes the Kodi box on SSH 22 by default and SMB 445 for tier B", () => {
    expect(livenessTargets(make({ tier: "A" })).find((t) => t.id === "kodi")?.port).toBe(22);
    expect(livenessTargets(make({ tier: null })).find((t) => t.id === "kodi")?.port).toBe(22);
    expect(livenessTargets(make({ tier: "B" })).find((t) => t.id === "kodi")?.port).toBe(445);
  });

  it("adds the receiver in the AVR chain, with the backend's control port", () => {
    const denon = livenessTargets(
      make({ topology: "kodi_avr_tv_player", avrBackend: "denon_marantz", avrIp: "10.0.1.90" })
    );
    expect(denon.find((t) => t.id === "avr")).toMatchObject({ host: "10.0.1.90", port: 23, kind: "tcp" });
    expect(
      livenessTargets(make({ topology: "kodi_avr_tv_player", avrBackend: "yamaha_yxc", avrIp: "10.0.1.90" })).find(
        (t) => t.id === "avr"
      )?.port
    ).toBe(80);
    expect(
      livenessTargets(make({ topology: "kodi_avr_tv_player", avrBackend: "onkyo_eiscp", avrIp: "10.0.1.90" })).find(
        (t) => t.id === "avr"
      )?.port
    ).toBe(60128);
  });

  it("omits the receiver when it has no plain TCP control port (Sony/custom) or no IP", () => {
    expect(
      livenessTargets(make({ topology: "kodi_avr_tv_player", avrBackend: "sony_audio", avrIp: "10.0.1.90" })).some(
        (t) => t.id === "avr"
      )
    ).toBe(false);
    expect(
      livenessTargets(make({ topology: "kodi_avr_tv_player", avrBackend: "custom_command", avrIp: "10.0.1.90" })).some(
        (t) => t.id === "avr"
      )
    ).toBe(false);
    expect(
      livenessTargets(make({ topology: "kodi_avr_tv_player", avrBackend: "denon_marantz", avrIp: "" })).some(
        (t) => t.id === "avr"
      )
    ).toBe(false);
  });

  it("omits the receiver in the TV chain even if AVR fields are set", () => {
    expect(
      livenessTargets(make({ topology: "kodi_tv_player", avrBackend: "denon_marantz", avrIp: "10.0.1.90" })).some(
        (t) => t.id === "avr"
      )
    ).toBe(false);
  });
});
