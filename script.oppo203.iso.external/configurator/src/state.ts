export type Tier = "A" | "B" | "C";

export type TvBackend =
  | "adb"
  | "roku_ecp"
  | "sony_bravia"
  | "smartthings"
  | "lg_command"
  | "samsung_command"
  | "custom_command";

export type PlayerBrand =
  | "oppo"
  | "chinoppo"
  | "magnetar"
  | "reavon"
  | "cineultra"
  | "ipuk"
  | "giec"
  | "other";

export type InputAddress = number | "cec" | string | null;

export type PlaybackArchitecture = "external_player" | "service_interception";

export type WizardState = {
  kodiIp: string;
  tier: Tier | null;
  kodiVerified: boolean;
  playbackArchitecture: PlaybackArchitecture;

  tvBrand: string | null;
  tvModel: string | null;
  tvBackend: TvBackend | null;
  tvPlatform: string | null;
  tvVerified: boolean;
  tvAdbWeak: boolean;
  tvManualSwitch: boolean;

  playerBrand: PlayerBrand | null;
  playerModel: string | null;
  playerIp: string;
  playerVerified: boolean;

  oppoInput: InputAddress;
  kodiInput: InputAddress;

  testMode: "disc" | "own" | null;
};

import { invoke } from "@tauri-apps/api/core";
import type { ScreenId } from "./steps";

export const INITIAL_STATE: WizardState = {
  kodiIp: "10.0.1.42",
  tier: null,
  kodiVerified: false,
  playbackArchitecture: "external_player",
  tvBrand: null,
  tvModel: null,
  tvBackend: null,
  tvPlatform: null,
  tvVerified: false,
  tvAdbWeak: false,
  tvManualSwitch: false,
  playerBrand: null,
  playerModel: null,
  playerIp: "10.0.1.77",
  playerVerified: false,
  oppoInput: null,
  kodiInput: null,
  testMode: null,
};

/** Persisted between sessions: the wizard state plus the screen to resume on. */
export type PersistedSession = { state: WizardState; screen: ScreenId };

export async function loadPersistedSession(): Promise<PersistedSession | null> {
  try {
    const loaded = await invoke<unknown>("load_wizard_state");
    if (!loaded || typeof loaded !== "object") return null;
    const obj = loaded as Record<string, unknown>;
    // Current envelope shape: { state, screen }.
    if (obj.state && typeof obj.state === "object") {
      const screen =
        typeof obj.screen === "string" ? (obj.screen as ScreenId) : "step0_gate";
      return {
        state: { ...INITIAL_STATE, ...(obj.state as Partial<WizardState>) },
        screen,
      };
    }
    // Legacy shape: a bare WizardState written before screen persistence existed.
    return {
      state: { ...INITIAL_STATE, ...(obj as Partial<WizardState>) },
      screen: "step0_gate",
    };
  } catch {
    return null;
  }
}

export async function savePersistedSession(session: PersistedSession): Promise<void> {
  try {
    await invoke("save_wizard_state", { state: session });
  } catch {
    // best-effort; persistence must never block the UI
  }
}

export type ChainCompletion = {
  media: boolean;
  kodi: boolean;
  tv: boolean;
  player: boolean;
};

export function computeCompleted(
  state: WizardState,
  screenId: string
): ChainCompletion {
  return {
    media: screenId !== "step0_gate",
    kodi: state.kodiVerified,
    tv: state.tvVerified,
    player: state.playerVerified,
  };
}
