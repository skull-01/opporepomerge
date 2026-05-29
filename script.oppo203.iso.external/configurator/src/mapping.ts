import type { InputAddress, WizardState } from "./state";
import { hwModelFor } from "./players";

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

/**
 * Resolve the `oppo_hardware_model` enum value, or null if brand/model is unset/unknown. The
 * brand/model catalog and its enum mapping live in ./players as the single source of truth.
 */
export function playerHardwareModel(state: WizardState): string | null {
  return hwModelFor(state.playerBrand, state.playerModel);
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
    python_path: state.pythonPath,
    // IP control over TCP :23 is the wizard's assumption.
    oppo_port: "23",
    // Enable TV switching only when a backend is configured and the user didn't drop to
    // manual; otherwise "false", so a no-TV setup doesn't switch against the default backend.
    tv_switching_enabled: state.tvBackend && !state.tvManualSwitch ? "true" : "false",
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
