import { Fragment } from "react";
import { Icon, type IconName } from "../icons";
import type { ChainCompletion } from "../state";
import { chainNodeIds, type ChainNodeId, type ChainTarget } from "../steps";
import type { Topology } from "../state";

type Node = {
  id: ChainNodeId;
  icon: IconName;
  label: string;
};

const NODE_DEFS: Record<ChainNodeId, Node> = {
  media: { id: "media", icon: "media", label: "ISO Playback" },
  kodi: { id: "kodi", icon: "kodi", label: "Kodi box" },
  avr: { id: "avr", icon: "avr", label: "Receiver" },
  player: { id: "player", icon: "player", label: "Player" },
  tv: { id: "tv", icon: "tv", label: "TV" },
};

type Props = {
  active: ChainTarget;
  completed: ChainCompletion;
  // Optional so the static summary/header call sites keep working; null = TV chain.
  topology?: Topology | null;
};

export function Chain({ active, completed, topology = null }: Props) {
  const NODES: readonly Node[] = chainNodeIds(topology).map((id) => NODE_DEFS[id]);
  // The "avr" node has no completion flag of its own; treat receiver-step screens as its
  // active state and never mark it done (it is advisory, not a verified gate).
  const completedFor = (id: Node["id"]): boolean =>
    id === "avr" ? false : completed[id];

  const isActive = (id: Node["id"]) =>
    active === id ||
    (active === "all" && id !== "media") ||
    (active === "tv-player" && (id === "tv" || id === "player" || id === "avr"));

  const isDone = (id: Node["id"]) => {
    if (id === "avr") return false;
    if (active === "all") return completed[id];
    if (id === "media" && completed.media) return true;
    if (isActive(id)) return false;
    return completed[id];
  };

  const edgeState = (a: Node["id"], b: Node["id"]) => {
    if (active === "tv-player" && a === "player" && b === "tv") return "bidir";
    if (isActive(a) && completedFor(b)) return "active";
    if (isActive(b) && completedFor(a)) return "active";
    if (completedFor(a) && completedFor(b)) return "done";
    return "";
  };

  return (
    <div className="chain">
      {NODES.map((n, i) => {
        const classes = [
          "chain-node",
          isActive(n.id) ? "active" : "",
          isDone(n.id) ? "done" : "",
        ]
          .filter(Boolean)
          .join(" ");
        return (
          <Fragment key={n.id}>
            <div className={classes}>
              <div className="chain-icon">
                <Icon name={n.icon} size={20} />
              </div>
              <div className="chain-node-label">{n.label}</div>
            </div>
            {i < NODES.length - 1 && (
              <div className={`chain-edge ${edgeState(n.id, NODES[i + 1].id)}`.trim()}>
                <div className="chain-edge-line" />
              </div>
            )}
          </Fragment>
        );
      })}
    </div>
  );
}
