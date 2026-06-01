import type { WizardState } from "./state";
import { isAvrChain } from "./steps";

/**
 * Which HDMI-input target a Step 5 switch is aiming at: the OPPO's input (the handoff target)
 * or the Kodi box's input (the return target). Picks the matching field out of the wizard state.
 */
export type SwitchTarget = "oppo" | "kodi";

/**
 * What the UI should do with a built switch plan:
 *   "command" - a confirmable switch: fire `command` with `args` via invoke and show the reply.
 *   "request" - SmartThings only: build the cloud request (URL + body) for the operator to see;
 *               it is NOT auto-fired (HTTPS with a bearer token, fired on-device by the add-on).
 *   "manual"  - no confirmable backend for this chain/state: fall back to a remote-and-confirm
 *               step honestly, never pretending a switch was driven.
 */
export type SwitchDisposition = "command" | "request" | "manual";

export type SwitchCommandPlan = {
  disposition: "command";
  command: string;
  args: Record<string, unknown>;
  /** The input value sent (HDMI number or backend input string), for the UI to echo. */
  inputLabel: string;
};

export type SwitchRequestPlan = {
  disposition: "request";
  command: "smartthings_switch_request";
  args: { deviceId: string; inputId: string };
  inputLabel: string;
};

export type SwitchManualPlan = {
  disposition: "manual";
  /** Why the configurator can't confirm the switch itself, shown to the user. */
  reason: string;
};

export type SwitchPlan = SwitchCommandPlan | SwitchRequestPlan | SwitchManualPlan;

/**
 * Per-backend control inputs the Step 5 switch needs beyond the chosen HDMI number — supplied
 * inline on the step when the wizard does not already hold them (the TV/AVR steps capture IP and
 * the AVR's own credentials, but not a TV command template or SmartThings ids). Empty strings mean
 * "not provided yet", which routes those backends to the manual fallback. The Sony Bravia PSK is
 * read from state (state.tvSonyPsk), not here.
 */
export type SwitchExtras = {
  externalTemplate: string;
  smartthingsDeviceId: string;
  smartthingsInputId: string;
};

export const EMPTY_SWITCH_EXTRAS: SwitchExtras = {
  externalTemplate: "",
  smartthingsDeviceId: "",
  smartthingsInputId: "",
};

/** The adb keyevent that selects discrete HDMI N, mirroring the add-on's tv_adb_control default. */
function adbHdmiCommand(hdmi: number): string {
  return `input keyevent KEYCODE_TV_INPUT_HDMI_${hdmi}`;
}

/**
 * Plan the AVR-chain switch: in player -> AVR -> TV the receiver is the switcher, so the input is
 * the receiver-input string captured in Step 6 (avrPlayerInput / avrKodiInput), not an HDMI number.
 * Denon/Marantz, Onkyo/Pioneer/Integra (eISCP), and Yamaha have confirmable fire commands; Sony's
 * Audio Control API needs its PSK + URI-form input (held in Step 6 state); custom_command has none.
 */
function planAvrSwitch(state: WizardState, target: SwitchTarget): SwitchPlan {
  const input = target === "oppo" ? state.avrPlayerInput.trim() : state.avrKodiInput.trim();
  if (!state.avrIp.trim()) {
    return { disposition: "manual", reason: "No receiver IP captured — switch with the receiver itself." };
  }
  if (!input) {
    return {
      disposition: "manual",
      reason:
        target === "kodi"
          ? "No Kodi input set on the receiver — switch back with the receiver itself."
          : "No player input set on the receiver — switch with the receiver itself.",
    };
  }
  switch (state.avrBackend) {
    case "denon_marantz":
      return {
        disposition: "command",
        command: "avr_switch_denon",
        args: { host: state.avrIp.trim(), input },
        inputLabel: input,
      };
    case "onkyo_eiscp":
      return {
        disposition: "command",
        command: "avr_switch_eiscp",
        args: { host: state.avrIp.trim(), inputCode: input },
        inputLabel: input,
      };
    case "yamaha_yxc":
      return {
        disposition: "command",
        command: "avr_switch_yamaha",
        args: { host: state.avrIp.trim(), input },
        inputLabel: input,
      };
    case "sony_audio":
      if (!state.avrSonyPsk.trim() || !state.avrSonyPlayerInputUri.trim()) {
        return {
          disposition: "manual",
          reason: "Sony Audio API needs its PSK and input URI (set in the receiver step).",
        };
      }
      return {
        disposition: "command",
        command: "avr_switch_sony_audio",
        args: {
          host: state.avrIp.trim(),
          inputUri: state.avrSonyPlayerInputUri.trim(),
          psk: state.avrSonyPsk.trim(),
        },
        inputLabel: state.avrSonyPlayerInputUri.trim(),
      };
    default:
      return {
        disposition: "manual",
        reason: "This receiver has no native control backend — switch with the receiver itself.",
      };
  }
}

/**
 * Plan the TV-chain switch from the picked HDMI number. Roku ECP and ADB are confirmable with what
 * the wizard already holds (TV IP / Kodi SSH); Sony Bravia and the LG/Samsung/custom external path
 * need one more inline value (PSK / command template) before they can fire; SmartThings builds a
 * cloud request to display rather than firing. Anything without enough to confirm falls to manual.
 */
function planTvSwitch(state: WizardState, hdmi: number, extras: SwitchExtras): SwitchPlan {
  const tvIp = state.tvIp.trim();
  switch (state.tvBackend) {
    case "roku_ecp":
      if (!tvIp) return { disposition: "manual", reason: "No TV IP captured — switch with the remote." };
      return {
        disposition: "command",
        command: "tv_switch_roku",
        args: { host: tvIp, key: `InputHDMI${hdmi}` },
        inputLabel: `HDMI ${hdmi}`,
      };
    case "adb":
      if (!tvIp) return { disposition: "manual", reason: "No TV IP captured — switch with the remote." };
      return {
        disposition: "command",
        command: "tv_switch_adb",
        args: {
          sshHost: state.kodiIp.trim(),
          sshUser: state.sshUser.trim() || "root",
          adbPath: "adb",
          tvHost: tvIp,
          tvPort: 5555,
          adbCommand: adbHdmiCommand(hdmi),
        },
        inputLabel: `HDMI ${hdmi}`,
      };
    case "sony_bravia":
      if (!tvIp) return { disposition: "manual", reason: "No TV IP captured — switch with the remote." };
      if (!state.tvSonyPsk.trim()) {
        return { disposition: "manual", reason: "Add the TV's Pre-Shared Key to test the Sony switch." };
      }
      return {
        disposition: "command",
        command: "tv_switch_sony_bravia",
        args: { host: tvIp, psk: state.tvSonyPsk.trim(), port: hdmi },
        inputLabel: `HDMI ${hdmi}`,
      };
    case "lg_command":
    case "samsung_command":
    case "custom_command":
      if (!tvIp) return { disposition: "manual", reason: "No TV IP captured — switch with the remote." };
      if (!extras.externalTemplate.trim()) {
        return {
          disposition: "manual",
          reason: "Add the TV command (use {tv_ip}) to test this switch, or switch with the remote.",
        };
      }
      return {
        disposition: "command",
        command: "tv_switch_external",
        args: {
          sshHost: state.kodiIp.trim(),
          sshUser: state.sshUser.trim() || "root",
          template: extras.externalTemplate.trim(),
          tvIp,
        },
        inputLabel: `HDMI ${hdmi}`,
      };
    case "smartthings":
      if (!extras.smartthingsDeviceId.trim() || !extras.smartthingsInputId.trim()) {
        return {
          disposition: "manual",
          reason: "Add the SmartThings device id and input id to build the switch request.",
        };
      }
      return {
        disposition: "request",
        command: "smartthings_switch_request",
        args: {
          deviceId: extras.smartthingsDeviceId.trim(),
          inputId: extras.smartthingsInputId.trim(),
        },
        inputLabel: extras.smartthingsInputId.trim(),
      };
    default:
      return { disposition: "manual", reason: "No TV backend configured — switch with the remote." };
  }
}

/**
 * Decide how Step 5 should drive a switch to `hdmi` for `target`, given the wizard state and any
 * inline per-backend extras. The AVR chain routes through the receiver backend (the receiver is the
 * switcher); the TV chain routes through the TV backend. Pure — the screen calls invoke on the plan.
 */
export function planSwitch(
  state: WizardState,
  target: SwitchTarget,
  hdmi: number,
  extras: SwitchExtras = EMPTY_SWITCH_EXTRAS,
): SwitchPlan {
  if (isAvrChain(state.topology)) return planAvrSwitch(state, target);
  return planTvSwitch(state, hdmi, extras);
}
