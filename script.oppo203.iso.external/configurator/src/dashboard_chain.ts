/**
 * Full-chain view model (Phase 5.3): every node on the playback chain (Kodi / OPPO / TV / AVR) in
 * topology order, each with its liveness and current activity. Pure so the assembly is
 * unit-testable without a live backend - the dashboard feeds it the probe results it already has
 * plus the parsed session status.
 *
 * The chain order follows chainNodeIds() minus the "media" source node (the NAS share is not a
 * probed network device): the TV chain is kodi -> player -> tv; the AVR chain inserts the receiver,
 * kodi -> avr -> player -> tv. A node is shown even when it has no liveness probe (e.g. a
 * SmartThings TV with no plain TCP port) so the chain is never silently missing a hop.
 */
import type { WizardState } from "./state";
import { chainNodeIds } from "./steps";
import { isAvrChain } from "./steps";
import type { OppoSessionStatus } from "./oppo_status";

export type ChainNodeKind = "kodi" | "player" | "tv" | "avr";

/**
 * Liveness as the dashboard already knows it for a node:
 *   "up"       - the probe answered.
 *   "down"     - the probe ran and got no answer.
 *   "checking" - the first probe has not resolved yet.
 *   "unprobed" - the node is on the chain and has an address, but no plain-TCP liveness check
 *                exists for its backend (so absence of a probe is not "down").
 *   "no-address" - the wizard never captured an address for this node.
 */
export type ChainLiveness = "up" | "down" | "checking" | "unprobed" | "no-address";

export type ChainNodeView = {
  id: ChainNodeKind;
  label: string;
  // The address the dashboard probes, or null when none was captured / it is a host-run node.
  host: string | null;
  liveness: ChainLiveness;
  // A short human activity line derived from the add-on session, or null when nothing is known.
  activity: string | null;
};

const NODE_LABEL: Record<ChainNodeKind, string> = {
  kodi: "Kodi box",
  avr: "Receiver",
  player: "Player",
  tv: "TV",
};

/** One probe outcome as the dashboard holds it: reachable null = first probe still in flight. */
export type NodeProbe = { reachable: boolean | null };

function baseName(path: string): string {
  return path.split(/[\\/]/).pop() || path;
}

/**
 * The host the chain view shows for a node, or null when the wizard has no address for it. Kodi
 * and the player always have a (default-seeded) address; the TV and AVR are optional.
 */
function hostFor(id: ChainNodeKind, state: WizardState): string | null {
  switch (id) {
    case "kodi":
      return state.kodiIp || null;
    case "player":
      return state.playerIp || null;
    case "tv":
      return state.tvIp || null;
    case "avr":
      return state.avrIp || null;
  }
}

/**
 * Liveness for a node, reconciling the probe map (keyed by the same ids the dashboard probes) with
 * addressing. A node with no address reads "no-address"; an addressed node with no probe entry
 * reads "unprobed" (its backend has no plain-TCP check); otherwise the probe result maps to
 * up/down/checking.
 */
function livenessFor(host: string | null, probe: NodeProbe | undefined): ChainLiveness {
  if (host == null) return "no-address";
  if (probe === undefined) return "unprobed";
  if (probe.reachable == null) return "checking";
  return probe.reachable ? "up" : "down";
}

/**
 * The current-activity line for a node, derived from the add-on's session status. Only the player
 * has device-reported activity (the OPPO's playback state + media); Kodi shows what it launched
 * while a session is live; the TV/AVR switch state is not observable, so they stay null. Returns
 * null when there is no session or nothing meaningful to show.
 */
function activityFor(id: ChainNodeKind, status: OppoSessionStatus | null): string | null {
  if (status == null) return null;
  const playing = status.sessionState === "starting";
  const media = status.mediaFile ? baseName(status.mediaFile) : "";
  if (id === "kodi") {
    return playing && media ? `launched ${media}` : null;
  }
  if (id === "player") {
    if (status.oppoPlaybackState) {
      return media ? `${status.oppoPlaybackState} · ${media}` : status.oppoPlaybackState;
    }
    if (status.confirmedPlayback) return media ? `playing ${media}` : "playback confirmed";
    if (playing && media) return `starting ${media}`;
    return null;
  }
  return null;
}

/**
 * Assemble the ordered full-chain view. `probes` is keyed by node id (the dashboard's existing
 * liveness map); `status` is the parsed add-on session (or null when none was read).
 */
export function chainNodeViews(
  state: WizardState,
  probes: Record<string, NodeProbe>,
  status: OppoSessionStatus | null
): ChainNodeView[] {
  const ids = chainNodeIds(state.topology).filter(
    (id): id is ChainNodeKind => id !== "media"
  );
  return ids.map((id) => {
    const host = hostFor(id, state);
    return {
      id,
      label: NODE_LABEL[id],
      host,
      liveness: livenessFor(host, probes[id]),
      activity: activityFor(id, status),
    };
  });
}

/** Whether the AVR receiver is part of the configured chain (re-exported for the dashboard). */
export function chainHasReceiver(state: WizardState): boolean {
  return isAvrChain(state.topology);
}
