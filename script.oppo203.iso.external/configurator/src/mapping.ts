import type { InputAddress, PlayerBrand, WizardState } from "./state";

/**
 * The add-on setting IDs the configurator is responsible for writing, derived from the
 * wizard state. Verified against resources/settings.xml and resources/lib/kodi/installer.py
 * (see docs/configurator/CONFIGURATOR_HANDOFF.md §4).
 *
 * Values are strings in Kodi's settings.xml form. For enum settings, the add-on's
 * settings_reader / installer._resolve_enum() accept either the value string ("adb") or its
 * zero-based index, so emitting the value string is safe and more legible.
 */
export type AddonSettings = Record<string, string>;

/** UI (brand, model label) → `oppo_hardware_model` enum value, in settings.xml order. */
const PLAYER_MODEL_TO_HW: Record<PlayerBrand, Record<string, string>> = {
  oppo: { "UDP-203": "udp_203", "UDP-205": "udp_205" },
  chinoppo: {
    M9201: "chinoppo_m9201",
    M9203: "chinoppo_m9203",
    "M9205 V1": "chinoppo_m9205",
    M9205C: "chinoppo_m9205c",
    M9200: "chinoppo_m9200",
    M9205: "chinoppo_m9205",
    M9702: "chinoppo_m9702",
  },
  magnetar: { UDP800: "magnetar_udp800", UDP900: "magnetar_udp900" },
  reavon: {
    "UBR-X100": "reavon_ubrx100",
    "UBR-X110": "reavon_ubrx110",
    "UBR-X200": "reavon_ubrx200",
  },
  cineultra: { V203: "cineultra_v203", V204: "cineultra_v204" },
  ipuk: { UHD8592: "ipuk_uhd8592" },
  giec: { "BDP-G5300": "giec_bdp_g5300" },
  // "Other / clone": conservative stock OPPO vs a clone eject-to-wake default.
  other: {
    "Conservative default": "udp_203",
    "Chinoppo eject-to-wake": "chinoppo_m9205",
  },
};

// The UI lists both "M9205 V1" and "M9205" for Chinoppo, but settings.xml has a single
// non-C enum value (chinoppo_m9205); both collapse to it pending maintainer confirmation
// that they are the same device.

/** Resolve the `oppo_hardware_model` enum value, or null if brand/model is unset/unknown. */
export function playerHardwareModel(state: WizardState): string | null {
  if (!state.playerBrand || !state.playerModel) return null;
  return PLAYER_MODEL_TO_HW[state.playerBrand]?.[state.playerModel] ?? null;
}

function hdmiNumber(value: InputAddress): number | null {
  return typeof value === "number" ? value : null;
}

/**
 * Input-addressable backends (Roku ECP, Sony Bravia) map a bare HDMI number directly to
 * their setting fields. ADB / *_command / SmartThings inputs are preset- or
 * user-command-driven and are wired in the TV-input slice, not here.
 */
function hdmiInputSettings(
  backend: string,
  oppoInput: InputAddress,
  kodiInput: InputAddress,
): AddonSettings {
  const out: AddonSettings = {};
  const oppo = hdmiNumber(oppoInput);
  const kodi = hdmiNumber(kodiInput);
  if (backend === "roku_ecp") {
    if (oppo != null) out.roku_oppo_key = `InputHDMI${oppo}`;
    if (kodi != null) out.roku_kodi_key = `InputHDMI${kodi}`;
  } else if (backend === "sony_bravia") {
    if (oppo != null) out.sony_oppo_hdmi_port = String(oppo);
    if (kodi != null) out.sony_kodi_hdmi_port = String(kodi);
  }
  return out;
}

/**
 * Map the wizard state to the add-on setting IDs the configurator writes.
 *
 * Only deterministic, configurator-owned values currently held in the state are emitted.
 * Excluded by design: tier (a deploy mechanism, not a setting), the `*Verified` flags and
 * `testMode` (UI-only), and `kodi_host` — the Kodi box address has no add-on setting and is
 * held configurator-side (CONFIGURATOR_HANDOFF.md §7 Q3). `tv_ip` and the SSH/SMB credentials
 * are not yet captured in the wizard state; they join this map when those inputs become
 * controlled in a later slice.
 */
export function wizardStateToAddonSettings(state: WizardState): AddonSettings {
  const out: AddonSettings = {
    // Architecture is chosen on the Kodi-box screen and written explicitly.
    playback_architecture: state.playbackArchitecture,
    architecture_choice_made: "true",
    // IP control over TCP :23 is the wizard's assumption.
    oppo_port: "23",
    tv_switching_enabled: state.tvManualSwitch ? "false" : "true",
  };

  const hardwareModel = playerHardwareModel(state);
  if (hardwareModel) out.oppo_hardware_model = hardwareModel;
  if (state.playerIp) out.oppo_ip = state.playerIp;

  if (state.tvBackend) {
    out.tv_backend = state.tvBackend;
    Object.assign(out, hdmiInputSettings(state.tvBackend, state.oppoInput, state.kodiInput));
  }

  return out;
}
