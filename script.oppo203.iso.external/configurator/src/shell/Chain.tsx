import { Fragment } from "react";
import { Icon, type IconName } from "../icons";
import type { ChainCompletion } from "../state";
import type { ChainTarget } from "../steps";

type Node = {
  id: keyof ChainCompletion;
  icon: IconName;
  label: string;
};

const NODES: readonly Node[] = [
  { id: "media", icon: "media", label: "Media" },
  { id: "kodi", icon: "kodi", label: "Kodi box" },
  { id: "tv", icon: "tv", label: "TV" },
  { id: "player", icon: "player", label: "Player" },
];

type Props = {
  active: ChainTarget;
  completed: ChainCompletion;
};

export function Chain({ active, completed }: Props) {
  const isActive = (id: Node["id"]) =>
    active === id ||
    (active === "all" && id !== "media") ||
    (active === "tv-player" && (id === "tv" || id === "player"));

  const isDone = (id: Node["id"]) => {
    if (active === "all") return completed[id];
    if (id === "media" && completed.media) return true;
    if (isActive(id)) return false;
    return completed[id];
  };

  const edgeState = (a: Node["id"], b: Node["id"]) => {
    if (active === "tv-player" && a === "tv" && b === "player") return "bidir";
    if (isActive(a) && completed[b]) return "active";
    if (isActive(b) && completed[a]) return "active";
    if (completed[a] && completed[b]) return "done";
    return "";
  };

  return (
    <div className="chain">
      {NODES.map((n, i) => {
        const gated = n.id === "media" && completed.media && !isActive(n.id);
        const classes = [
          "chain-node",
          isActive(n.id) ? "active" : "",
          isDone(n.id) ? "done" : "",
          gated ? "gated" : "",
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
