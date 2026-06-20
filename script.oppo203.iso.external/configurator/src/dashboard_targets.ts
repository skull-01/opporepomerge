import type { WizardState } from "./state";
import { isAvrChain } from "./steps";

/**
 * How the dashboard checks one device for liveness:
 *   "tcp"      - a plain TCP connect (tcp_probe): reachable if the port accepts a connection.
 *   "oppo"     - an OPPO #QPW query (oppo_query): reachable if the player replies, and the reply
 *                also yields a power state to show.
 *   "oppo-http" - an OPPO HTTP/436 request (oppo_playback_info): reachable if the player answers
 *                over HTTP. Chosen for a Pure-HTTP (http monitor) install so the dashboard's
 *                process monitor uses the same transport the add-on does (Step-4 decision).
 */
export type LivenessKind = "tcp" | "oppo" | "oppo-http";

export type LivenessTarget = {
  id: "kodi" | "player" | "tv" | "avr";
  label: string;
  host: string;
  port: number;
  kind: LivenessKind;
};

/**
 * The AVR control port to probe, by control backend. Mirrors controlProbePort() in
 * screens/step6.tsx and resources/lib/avr/avr_presets.py (Denon/Marantz telnet 23, Yamaha YXC
 * HTTP 80, Onkyo/Pioneer eISCP 60128). Sony (authenticated HTTP/PSK) and custom_command have no
 * plain TCP check, so they return null and the receiver row is omitted rather than shown wrong.
 */
function avrControlPort(backend: WizardState["avrBackend"]): number | null {
  switch (backend) {
    case "denon_marantz":
      return 23;
    case "yamaha_yxc":
      return 80;
    case "onkyo_eiscp":
      return 60128;
    default:
      return null;
  }
}

/**
 * The TV control port to probe, by backend. Mirrors TV_PROBE_PORTS in probes.ts (Roku ECP 8060,
 * ADB 5555, Sony IP control 20060). SmartThings / LG / Samsung / custom_command have no plain TCP
 * check, so they return null and the TV row is omitted rather than shown wrong.
 */
function tvControlPort(backend: WizardState["tvBackend"]): number | null {
  switch (backend) {
    case "roku_ecp":
      return 8060;
    case "adb":
      return 5555;
    case "sony_bravia":
      return 20060;
    default:
      return null;
  }
}

/**
 * The devices the dashboard checks for liveness, derived from the configured chain. Only devices
 * the wizard actually persists an address for are included:
 *   - Kodi box (kodiIp) - probed on its deploy transport port (SMB 445 for tier B, else SSH 22).
 *   - OPPO player (playerIp) - queried over IP control on 23 (also surfaces power state).
 *   - TV (tvIp) - when Step 4's probe persisted an IP and the backend has a plain TCP control
 *     port (Roku ECP / ADB / Sony IP control); SmartThings / LG / Samsung / custom have none.
 *   - AV receiver (avrIp) - AVR chain only, and only for a backend with a TCP control port.
 */
export function livenessTargets(state: WizardState): LivenessTarget[] {
  const targets: LivenessTarget[] = [
    {
      id: "kodi",
      label: "Kodi box",
      host: state.kodiIp,
      port: state.tier === "B" ? 445 : 22,
      kind: "tcp",
    },
    {
      id: "player",
      label: "Player",
      host: state.playerIp,
      port: 23,
      // Pure-HTTP installs probe the player over HTTP/436, matching the add-on's http monitor.
      kind: state.monitorMode === "http" ? "oppo-http" : "oppo",
    },
  ];
  const tvPort = tvControlPort(state.tvBackend);
  if (state.tvIp && tvPort != null) {
    targets.push({ id: "tv", label: "TV", host: state.tvIp, port: tvPort, kind: "tcp" });
  }
  if (isAvrChain(state.topology)) {
    const port = avrControlPort(state.avrBackend);
    if (state.avrIp && port != null) {
      targets.push({ id: "avr", label: "Receiver", host: state.avrIp, port, kind: "tcp" });
    }
  }
  return targets;
}
