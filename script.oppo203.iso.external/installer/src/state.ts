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

export type WizardState = {
  kodiIp: string;
  tier: Tier | null;
  kodiVerified: boolean;

  tvBrand: string | null;
  tvModel: string | null;
  tvBackend: TvBackend | null;
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

export const INITIAL_STATE: WizardState = {
  kodiIp: "10.0.1.42",
  tier: null,
  kodiVerified: false,
  tvBrand: null,
  tvModel: null,
  tvBackend: null,
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
