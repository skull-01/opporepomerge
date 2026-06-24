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
 * The HDMI-number-addressable part of a TV backend: Roku ECP and Sony Bravia map a bare HDMI
 * number straight to their input fields. The rest of each backend's runtime config (the Sony
 * PSK, the ADB keyevent shells, the LG/Samsung/custom command templates, the SmartThings
 * credentials) is captured in Step 5 and emitted by tvControlSettings.
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

/** The adb keyevent that selects discrete HDMI N — mirrors step5_switch adbHdmiCommand and the
 * add-on's tv_adb_control default. */
function adbHdmiShell(hdmi: number): string {
  return `input keyevent KEYCODE_TV_INPUT_HDMI_${hdmi}`;
}

/**
 * The runtime config the add-on needs to actually drive the selected TV backend, beyond the bare
 * HDMI ports in hdmiInputSettings. Each branch writes only its own keys, and only when the values
 * are present, so a half-filled or switched backend never leaks stale config from another:
 *   - sony_bravia: the Pre-Shared Key the Sony API authenticates with (the HDMI ports come from
 *     hdmiInputSettings).
 *   - adb: the two HDMI keyevent shells, derived from the captured HDMI numbers (KEYCODE_TV_INPUT_
 *     HDMI_<n>) — no extra UI, mirroring step5_switch.
 *   - lg/samsung/custom_command: the user's raw {tv_ip}-templated OPPO/Kodi command strings,
 *     written verbatim; the add-on substitutes {tv_ip} at runtime (tv_control._run_external).
 *   - smartthings: the bearer token, device id, and OPPO/Kodi input ids; the experimental
 *     acknowledgement is set true only once all four are present, matching the add-on's own gate
 *     (tv_smartthings_control.is_acknowledged / validation_metadata).
 * The token is a secret like the AVR Sony PSK: it must reach settings.xml for the add-on, and the
 * debug redactor (debug/log.ts SENSITIVE_KEY) masks it in the panel.
 */
function tvControlSettings(state: WizardState): AddonSettings {
  const out: AddonSettings = {};
  const oppo = hdmiNumber(state.playerInput);
  const kodi = hdmiNumber(state.kodiInput);
  switch (state.tvBackend) {
    case "sony_bravia":
      if (state.tvSonyPsk) out.sony_psk = state.tvSonyPsk;
      break;
    case "adb":
      if (oppo != null) out.oppo_input_adb_shell = adbHdmiShell(oppo);
      if (kodi != null) out.kodi_input_adb_shell = adbHdmiShell(kodi);
      break;
    case "lg_command":
      if (state.tvOppoCommand) out.lg_oppo_command = state.tvOppoCommand;
      if (state.tvKodiCommand) out.lg_kodi_command = state.tvKodiCommand;
      break;
    case "samsung_command":
      if (state.tvOppoCommand) out.samsung_oppo_command = state.tvOppoCommand;
      if (state.tvKodiCommand) out.samsung_kodi_command = state.tvKodiCommand;
      break;
    case "custom_command":
      if (state.tvOppoCommand) out.custom_oppo_command = state.tvOppoCommand;
      if (state.tvKodiCommand) out.custom_kodi_command = state.tvKodiCommand;
      break;
    case "smartthings": {
      const token = state.tvSmartThingsToken;
      const device = state.tvSmartThingsDeviceId;
      const oppoInput = state.tvSmartThingsOppoInputId;
      const kodiInput = state.tvSmartThingsKodiInputId;
      if (token) out.smartthings_token = token;
      if (device) out.smartthings_device_id = device;
      if (oppoInput) out.smartthings_oppo_input_id = oppoInput;
      if (kodiInput) out.smartthings_kodi_input_id = kodiInput;
      if (token && device && oppoInput && kodiInput) {
        out.smartthings_experimental_acknowledged = "true";
      }
      break;
    }
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
 * AVR control settings, emitted only when the user actively picked a receiver in Step 6 — so
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
  // control is actually enabled. The restore target is the receiver input the Kodi box is
  // plugged into, captured in Step 6 (avrKodiInput) - distinct from kodiInput, which is the
  // TV's HDMI input used by the TV-chain switcher. A blank avrKodiInput emits no restore
  // input, which the add-on treats as a non-fatal skip (avr_sequence.py). Native (non-Sony)
  // drivers only; Sony returned above.
  if (enable && isAvrChain(state.topology)) {
    out.avr_power_on_enabled = "true";
    if (state.avrKodiInput) {
      out.avr_restore_enabled = "true";
      out.avr_restore_input = state.avrKodiInput;
    }
  }
  return out;
}

/**
 * Map the wizard state to the add-on setting IDs the configurator writes.
 *
 * Only deterministic, configurator-owned values currently held in the state are emitted.
 * Excluded by design: tier (a deploy mechanism, not a setting), the `*Verified` flags and
 * `testMode` (UI-only), and `kodi_host` — the Kodi box address has no add-on setting and is
 * held configurator-side (CONFIGURATOR_HANDOFF.md §7 Q3). The SSH/SMB credentials live in the
 * wizard state but are a deploy mechanism, not an add-on setting, so they are never emitted
 * here. `tv_ip` IS emitted — when a TV backend and its IP are both set (see below).
 */
export function wizardStateToAddonSettings(state: WizardState): AddonSettings {
  // Routing axis in the preset vocabulary; the stored playback_architecture's "external_player"
  // is the playercorefactory routing. http_handoff carries through unchanged.
  const routing =
    state.playbackArchitecture === "service_interception"
      ? "service_interception"
      : state.playbackArchitecture === "http_handoff"
        ? "http_handoff"
        : "playercorefactory";
  const out: AddonSettings = {
    // Architecture is chosen on the Kodi-box screen and written explicitly.
    playback_architecture: state.playbackArchitecture,
    architecture_choice_made: "true",
    // Monitor axis (Step 3) + the combined seven-option preset, derived here so the triple is
    // always internally consistent. The add-on treats playback_architecture_preset as the
    // source of truth and back-fills it from the legacy fields when absent (settings_reader).
    playback_monitor_mode: state.monitorMode,
    playback_architecture_preset: `${routing}_${state.monitorMode}`,
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

  // HDMI switch timing (applies to every routing's TV switch). immediate is the frozen default.
  out.hdmi_switch_mode = state.hdmiSwitchMode;
  if (state.playDelayHdmi) out.play_delay_hdmi = state.playDelayHdmi;
  if (state.avDelayHdmi) out.av_delay_hdmi = state.avDelayHdmi;

  const hardwareModel = playerHardwareModel(state);
  if (hardwareModel) out.oppo_hardware_model = hardwareModel;
  if (state.playerIp) out.oppo_ip = state.playerIp;

  if (routing === "http_handoff") {
    // The community NAS HTTP launch uses the documented JSON payload form (path / index /
    // type / appDeviceType / extraNetPath / playMode). The OPPO-visible path translation
    // (oppo_http_path_from/to) is player- and mount-specific -- the wizard cannot know the
    // player's NAS mount namespace, so the operator sets it. Candidate; hardware-pending.
    out.oppo_http_payload_mode = "json_payload";
    out.oppo_http_disc_folder_root = state.oppoDiscFolderRoot ? "true" : "false";
    // checkfolderhasBDMV-first disc nav (add-on gates it on player HTTP capability + fallback-safe).
    out.oppo_bdmv_checkfolder = state.oppoBdmvCheckfolder ? "true" : "false";
    // "Refresh Rate" for the http monitor + process monitor poll.
    if (state.oppoHttpRefreshSeconds) out.oppo_http_refresh_seconds = state.oppoHttpRefreshSeconds;
    if (state.oppoPathFrom) out.oppo_http_path_from = state.oppoPathFrom;
    if (state.oppoPathTo) out.oppo_http_path_to = state.oppoPathTo;
  }

  // Always-route disc folders -> playercorefactory routing rules (external_player). Routing-only,
  // so it is emitted regardless of the monitor / HTTP mode above.
  if (state.oppoDiscFolders.trim()) out.oppo_disc_folders = state.oppoDiscFolders.trim();

  if (state.tvBackend) {
    out.tv_backend = state.tvBackend;
    if (state.tvIp) out.tv_ip = state.tvIp;
    Object.assign(out, hdmiInputSettings(state.tvBackend, state.playerInput, state.kodiInput));
    Object.assign(out, tvControlSettings(state));
  }

  Object.assign(out, avrSettings(state));

  return out;
}
