import type { KodiPlatform } from "./generate";
import type { TvRegion } from "./tvdb";
import type { AvrRegion } from "./avrdb";

export type Tier = "A" | "B" | "C";

export type TvBackend =
  | "adb"
  | "roku_ecp"
  | "sony_bravia"
  | "smartthings"
  | "lg_command"
  | "samsung_command"
  | "custom_command";

// AVR control-path backends — the AVR DB's own vocabulary (mirrors the bundle's
// backend_schema). Advisory only: the wizard surfaces a candidate backend, it does not
// drive add-on settings. Maps loosely onto the add-on's avr_backend enum.
export type AvrBackend =
  | "denon_marantz"
  | "yamaha_yxc"
  | "onkyo_eiscp"
  | "sony_audio"
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
  kodiPlatform: KodiPlatform | null;
  pythonPath: string;
  smbSharePath: string;
  sshUser: string;

  tvBrand: string | null;
  tvRegion: TvRegion | null;
  tvModel: string | null;
  tvBackend: TvBackend | null;
  tvPlatform: string | null;
  tvVerified: boolean;
  tvAdbWeak: boolean;
  tvManualSwitch: boolean;

  avrBrand: string | null;
  avrRegion: AvrRegion | null;
  avrModel: string | null;
  avrBackend: AvrBackend | null;
  avrReceiverType: string | null;

  playerBrand: PlayerBrand | null;
  playerModel: string | null;
  playerIp: string;
  playerVerified: boolean;

  oppoInput: InputAddress;
  kodiInput: InputAddress;

  testMode: "disc" | "own" | null;
};

import { invoke } from "@tauri-apps/api/core";
import { SCREEN_TO_STEP, type ScreenId } from "./steps";

/**
 * Coerce a persisted `screen` value to a valid ScreenId, falling back to the first screen if
 * it is missing or not a known id. A stale/renamed id from an older build would otherwise
 * render `undefined` and white-screen the app on every launch.
 */
export function coerceScreenId(value: unknown): ScreenId {
  return typeof value === "string" && value in SCREEN_TO_STEP
    ? (value as ScreenId)
    : "step0_gate";
}

export const INITIAL_STATE: WizardState = {
  kodiIp: "10.0.1.42",
  tier: null,
  kodiVerified: false,
  playbackArchitecture: "external_player",
  kodiPlatform: null,
  pythonPath: "/usr/bin/python3",
  smbSharePath: "\\\\10.0.1.42\\Kodi",
  sshUser: "root",
  tvBrand: null,
  tvRegion: null,
  tvModel: null,
  tvBackend: null,
  tvPlatform: null,
  tvVerified: false,
  tvAdbWeak: false,
  tvManualSwitch: false,
  avrBrand: null,
  avrRegion: null,
  avrModel: null,
  avrBackend: null,
  avrReceiverType: null,
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
      const screen = coerceScreenId(obj.screen);
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
