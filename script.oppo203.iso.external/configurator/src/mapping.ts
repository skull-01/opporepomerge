import type { AvrBackend, InputAddress, WizardState } from "./state";
import { hwModelFor } from "./players";
import { isAvrChain } from "./steps";

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
  playerInput: InputAddress,
  kodiInput: InputAddress,
): AddonSettings {
  const out: AddonSettings = {};
  const oppo = hdmiNumber(playerInput);
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
 * Map the AVR DB's backend vocabulary (+ the selected brand) onto the add-on's `avr_backend`
 * enum. Two deliberate fix-ups: the DB folds Pioneer into `onkyo_eiscp`, but the add-on ships a
 * distinct (experimental) `pioneer_eiscp` driver, so Pioneer splits back out by brand; and the
 * DB names the Sony backend `sony_audio` while the add-on calls it `sony_audio_api`. Returns
 * null for `custom_command` (Anthem/Arcam/NAD) — the add-on has no native backend for those, so
 * the configurator writes no `avr_backend` rather than an enum value its own validator rejects.
 */
export function avrAddonBackend(dbBackend: AvrBackend | null, brand: string | null): string | null {
  switch (dbBackend) {
    case "denon_marantz":
      return "denon_marantz";
    case "yamaha_yxc":
      return "yamaha_yxc";
    case "sony_audio":
      return "sony_audio_api";
    case "onkyo_eiscp":
      return brand === "pioneer" ? "pioneer_eiscp" : "onkyo_eiscp";
    default:
      return null;
  }
}

/**
 * AVR control settings, emitted only when the user actively picked a receiver in Step 5 — so
 * skipping the optional step never disturbs an existing add-on AVR config. `avr_control_enabled`
 * is set true only when the chosen driver has every field it needs to actually run:
 *   - native non-Sony drivers (Denon/Marantz, Yamaha, Onkyo/Integra, Pioneer): host + player input;
 *   - Sony Audio Control API: additionally the experimental acknowledgement, the PSK, and the
 *     URI-form player input the API addresses — mirroring the add-on's own Sony gate
 *     (resources/lib/avr/avr_presets.py: requires_experimental_acknowledgement + the sensitive
 *     sony_avr_psk / sony_avr_player_input_uri fields).
 * custom_command brands (Anthem/Arcam/NAD) have no native driver, so nothing AVR-related is written.
 */
function avrSettings(state: WizardState): AddonSettings {
  const out: AddonSettings = {};
  const backend = avrAddonBackend(state.avrBackend, state.avrBrand);
  if (!backend) return out;
  out.avr_backend = backend;
  if (state.avrIp) out.avr_host = state.avrIp;
  if (state.avrPlayerInput) out.avr_player_input = state.avrPlayerInput;

  if (backend === "sony_audio_api") {
    if (state.avrSonyAcknowledged) out.sony_avr_experimental_acknowledged = "true";
    if (state.avrSonyPsk) out.sony_avr_psk = state.avrSonyPsk;
    if (state.avrSonyPlayerInputUri) out.sony_avr_player_input_uri = state.avrSonyPlayerInputUri;
    const sonyReady =
      state.avrSonyAcknowledged &&
      !!state.avrSonyPsk &&
      !!state.avrSonyPlayerInputUri &&
      !!state.avrIp &&
      !!state.avrPlayerInput;
    out.avr_control_enabled = sonyReady ? "true" : "false";
    return out;
  }

  const enable = !!state.avrIp && !!state.avrPlayerInput;
  out.avr_control_enabled = enable ? "true" : "false";

  // In the AVR chain the receiver is the input switcher: it powers on and selects the
  // player input on handoff, and restores the Kodi input on exit. The add-on reads these
  // (avr_control.py: avr_settings_summary / validate_avr_settings); we only emit them when
  // control is actually enabled, and we reuse the Kodi return target captured in Step 4 as
  // the receiver restore input. Only enabled for native (non-Sony) drivers here; Sony
  // returned above.
  if (enable && isAvrChain(state.topology)) {
    out.avr_power_on_enabled = "true";
    const restore = describeReceiverInput(state.kodiInput);
    if (restore) {
      out.avr_restore_enabled = "true";
      out.avr_restore_input = restore;
    }
  }
  return out;
}

/**
 * Render a captured HDMI InputAddress as the receiver input string the add-on stores. A bare
 * number becomes its string form; a non-numeric address (CEC / blind-cycle) has no meaning on
 * a receiver, so it yields null and no restore input is written.
 */
function describeReceiverInput(value: InputAddress): string | null {
  if (typeof value === "number") return String(value);
  return null;
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
    // In the AVR chain the receiver does the switching and the TV is fixed, so TV switching
    // stays off there even if a TV backend was configured for control.
    tv_switching_enabled:
      state.tvBackend && !state.tvManualSwitch && !isAvrChain(state.topology)
        ? "true"
        : "false",
  };

  const hardwareModel = playerHardwareModel(state);
  if (hardwareModel) out.oppo_hardware_model = hardwareModel;
  if (state.playerIp) out.oppo_ip = state.playerIp;

  if (state.tvBackend) {
    out.tv_backend = state.tvBackend;
    Object.assign(out, hdmiInputSettings(state.tvBackend, state.playerInput, state.kodiInput));
  }

  Object.assign(out, avrSettings(state));

  return out;
}
