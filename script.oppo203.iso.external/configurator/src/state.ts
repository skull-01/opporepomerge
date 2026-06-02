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

export type PlaybackArchitecture = "external_player" | "service_interception" | "http_handoff";

/**
 * How the add-on confirms OPPO playback (Step 4 "Playback mode"):
 *   legacy - the existing hold_mode dispatcher (fixed timeout / file / QPL poll / verbose push).
 *   svm3   - OPPO verbose mode 3: the add-on listens for UPL/UTC status + time-code updates and
 *            treats playback as confirmed only when the OPPO itself reports it.
 *   http   - pure-HTTP/436: the add-on polls /getglobalinfo + /getplayingtime. This monitor is
 *            only valid with the http_handoff routing (the "Pure HTTP" pill sets both axes), so
 *            the only http preset is http_handoff_http.
 * Orthogonal to playbackArchitecture (the routing axis) for legacy/svm3; together they form the
 * preset matrix (6 base presets + the asymmetric http_handoff_http cell).
 */
export type MonitorMode = "legacy" | "svm3" | "http";

/**
 * The physical playback chain being configured, chosen up front (Step 0) so the rest of
 * the wizard can adapt its copy and the settings it writes:
 *   kodi_tv_player      - player -> TV; the TV switches HDMI inputs on handoff.
 *   kodi_avr_tv_player  - player -> AV receiver -> TV; the receiver switches inputs, TV fixed.
 * A soft default - a null (legacy/unset) value just behaves like the TV chain everywhere.
 */
export type Topology = "kodi_tv_player" | "kodi_avr_tv_player";

export type WizardState = {
  kodiIp: string;
  tier: Tier | null;
  kodiVerified: boolean;
  topology: Topology | null;
  playbackArchitecture: PlaybackArchitecture;
  monitorMode: MonitorMode;
  kodiPlatform: KodiPlatform | null;
  pythonPath: string;
  smbSharePath: string;
  sshUser: string;

  tvBrand: string | null;
  tvRegion: TvRegion | null;
  tvModel: string | null;
  tvBackend: TvBackend | null;
  tvIp: string;
  tvPlatform: string | null;
  tvVerified: boolean;
  tvAdbWeak: boolean;
  tvManualSwitch: boolean;
  // Sony Bravia TV Pre-Shared Key, captured in the Step 5 switch test (the only place the TV
  // PSK is needed today); handled as a secret like avrSonyPsk.
  tvSonyPsk: string;
  // External-command TV backends (lg_command / samsung_command / custom_command): the raw
  // {tv_ip}-templated command strings the add-on runs over SSH to switch to the OPPO and back
  // to Kodi. Captured in Step 5 and written verbatim — {tv_ip} is substituted on-device.
  tvOppoCommand: string;
  tvKodiCommand: string;
  // SmartThings backend: the cloud bearer token (a secret, like tvSonyPsk), the device id, and
  // the OPPO/Kodi input ids. Captured in Step 5; feed both the switch test and the add-on config.
  tvSmartThingsToken: string;
  tvSmartThingsDeviceId: string;
  tvSmartThingsOppoInputId: string;
  tvSmartThingsKodiInputId: string;

  avrBrand: string | null;
  avrRegion: AvrRegion | null;
  avrModel: string | null;
  avrBackend: AvrBackend | null;
  avrReceiverType: string | null;
  avrIp: string;
  avrPlayerInput: string;
  avrKodiInput: string;
  avrSonyAcknowledged: boolean;
  avrSonyPsk: string;
  avrSonyPlayerInputUri: string;

  playerBrand: PlayerBrand | null;
  playerModel: string | null;
  playerIp: string;
  playerVerified: boolean;
  // SVM3 (verbose mode 3) capability as probed in the Step 2 player test: true/false once
  // probed, null before. Drives the recommended Playback-mode default (Step 3).
  svm3Supported: boolean | null;
  // How the OPPO addresses the media share for http_handoff (/playnormalfile?path=...): the
  // Kodi-visible prefix is rewritten oppoPathFrom -> oppoPathTo; oppoDiscFolderRoot hands the
  // player the disc folder root rather than the full file path.
  oppoPathFrom: string;
  oppoPathTo: string;
  oppoDiscFolderRoot: boolean;
  // When the player exposes the HTTP API, confirm a BDMV folder via /checkfolderhasBDMV before
  // handing over the folder root (else send the original marker). Advanced; defaults on and is
  // fallback-safe in the add-on -- like oppoDiscFolderRoot, no dedicated UI control.
  oppoBdmvCheckfolder: boolean;

  playerInput: InputAddress;
  kodiInput: InputAddress;

  testMode: "disc" | "own" | null;
};

import { invoke } from "./ipc";
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
  topology: null,
  playbackArchitecture: "http_handoff",
  monitorMode: "svm3",
  kodiPlatform: null,
  pythonPath: "/usr/bin/python3",
  smbSharePath: "\\\\10.0.1.42\\Kodi",
  sshUser: "root",
  tvBrand: null,
  tvRegion: null,
  tvModel: null,
  tvBackend: null,
  tvIp: "",
  tvPlatform: null,
  tvVerified: false,
  tvAdbWeak: false,
  tvManualSwitch: false,
  tvSonyPsk: "",
  tvOppoCommand: "",
  tvKodiCommand: "",
  tvSmartThingsToken: "",
  tvSmartThingsDeviceId: "",
  tvSmartThingsOppoInputId: "",
  tvSmartThingsKodiInputId: "",
  avrBrand: null,
  avrRegion: null,
  avrModel: null,
  avrBackend: null,
  avrReceiverType: null,
  avrIp: "10.0.1.90",
  avrPlayerInput: "",
  avrKodiInput: "",
  avrSonyAcknowledged: false,
  avrSonyPsk: "",
  avrSonyPlayerInputUri: "",
  playerBrand: null,
  playerModel: null,
  playerIp: "10.0.1.77",
  playerVerified: false,
  svm3Supported: null,
  oppoPathFrom: "",
  oppoPathTo: "",
  oppoDiscFolderRoot: true,
  oppoBdmvCheckfolder: true,
  playerInput: null,
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
