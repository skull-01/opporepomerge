import { describe, expect, it } from "vitest";
import { INITIAL_STATE, type WizardState } from "./state";
import { chainNodeViews, type NodeProbe } from "./dashboard_chain";
import type { OppoSessionStatus } from "./oppo_status";

function make(patch: Partial<WizardState>): WizardState {
  return { ...INITIAL_STATE, ...patch };
}

function status(patch: Partial<OppoSessionStatus>): OppoSessionStatus {
  return {
    launchSource: "playercorefactory",
    architecturePreset: "http_handoff_svm3",
    routingMode: "http_handoff",
    monitorMode: "svm3",
    mediaFile: "/storage/Movie.iso",
    sessionState: "starting",
    confirmedPlayback: false,
    confirmedProgress: false,
    oppoPlaybackState: null,
    utcTickCount: null,
    stopReason: null,
    sessionId: null,
    startedAt: null,
    updatedAt: null,
    phase: null,
    ...patch,
  };
}

const up: NodeProbe = { reachable: true };
const down: NodeProbe = { reachable: false };
const checking: NodeProbe = { reachable: null };

describe("chainNodeViews", () => {
  it("orders the TV chain kodi -> player -> tv (no receiver, no media node)", () => {
    const views = chainNodeViews(make({ topology: "kodi_tv_player" }), {}, null);
    expect(views.map((v) => v.id)).toEqual(["kodi", "player", "tv"]);
  });

  it("inserts the receiver in the AVR chain (kodi -> avr -> player -> tv)", () => {
    const views = chainNodeViews(make({ topology: "kodi_avr_tv_player" }), {}, null);
    expect(views.map((v) => v.id)).toEqual(["kodi", "avr", "player", "tv"]);
  });

  it("treats a null topology as the TV chain (soft default)", () => {
    const views = chainNodeViews(make({ topology: null }), {}, null);
    expect(views.map((v) => v.id)).toEqual(["kodi", "player", "tv"]);
  });

  it("maps probe results to up/down/checking and uses each node's host", () => {
    const views = chainNodeViews(
      make({ topology: "kodi_tv_player", tvIp: "10.0.1.55" }),
      { kodi: up, player: down, tv: checking },
      null
    );
    const byId = Object.fromEntries(views.map((v) => [v.id, v]));
    expect(byId.kodi).toMatchObject({ liveness: "up", host: INITIAL_STATE.kodiIp });
    expect(byId.player).toMatchObject({ liveness: "down", host: INITIAL_STATE.playerIp });
    expect(byId.tv).toMatchObject({ liveness: "checking", host: "10.0.1.55" });
  });

  it("reads an addressed node with no probe as 'unprobed', not down", () => {
    // SmartThings TV: on the chain, has an IP, but no plain-TCP liveness check exists for it.
    const views = chainNodeViews(
      make({ topology: "kodi_tv_player", tvBackend: "smartthings", tvIp: "10.0.1.55" }),
      { kodi: up, player: up },
      null
    );
    expect(views.find((v) => v.id === "tv")).toMatchObject({
      liveness: "unprobed",
      host: "10.0.1.55",
    });
  });

  it("reads a node with no captured address as 'no-address' with a null host", () => {
    const views = chainNodeViews(make({ topology: "kodi_tv_player", tvIp: "" }), {}, null);
    expect(views.find((v) => v.id === "tv")).toMatchObject({ liveness: "no-address", host: null });
  });

  it("derives player activity from the OPPO playback state + media, Kodi from the launch", () => {
    const views = chainNodeViews(
      make({ topology: "kodi_tv_player" }),
      {},
      status({ sessionState: "starting", oppoPlaybackState: "PLAY" })
    );
    expect(views.find((v) => v.id === "player")?.activity).toBe("PLAY · Movie.iso");
    expect(views.find((v) => v.id === "kodi")?.activity).toBe("launched Movie.iso");
    expect(views.find((v) => v.id === "tv")?.activity).toBeNull();
  });

  it("falls back to confirmed-playback wording when no live OPPO state is present", () => {
    const views = chainNodeViews(
      make({ topology: "kodi_tv_player" }),
      {},
      status({ sessionState: "stopped", confirmedPlayback: true, oppoPlaybackState: null })
    );
    expect(views.find((v) => v.id === "player")?.activity).toBe("playing Movie.iso");
    // An ended session is not "launched" on Kodi anymore.
    expect(views.find((v) => v.id === "kodi")?.activity).toBeNull();
  });

  it("shows no activity lines when there is no session", () => {
    const views = chainNodeViews(make({ topology: "kodi_avr_tv_player" }), {}, null);
    expect(views.every((v) => v.activity === null)).toBe(true);
  });
});
