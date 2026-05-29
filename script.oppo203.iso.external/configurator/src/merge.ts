import {
  buildPlayerElementXml,
  buildPlayercorefactoryXml,
  buildRuleXml,
  type KodiTarget,
} from "./generate";

const PLAYER_NAME = "Oppo203ISO";

/**
 * Merge our <player>/<rule> entries into an existing playercorefactory.xml, preserving the
 * user's other players and rules. Idempotent: re-running replaces our own entries rather than
 * duplicating them. Returns a fresh document when there is no usable existing file. Mirrors
 * resources/lib/kodi/playercorefactory_merge.py (merge, never blind-overwrite).
 */
export function mergePlayercorefactory(
  existing: string | null,
  target: KodiTarget,
  includeDiscFolderRules = true,
): string {
  if (!existing || existing.trim() === "") {
    return buildPlayercorefactoryXml(target, includeDiscFolderRules);
  }

  const doc = new DOMParser().parseFromString(existing, "application/xml");
  const root = doc.documentElement;
  const malformed = doc.getElementsByTagName("parsererror").length > 0;
  if (malformed || !root || root.nodeName !== "playercorefactory") {
    // Not a usable playercorefactory document — fall back to a fresh file.
    return buildPlayercorefactoryXml(target, includeDiscFolderRules);
  }

  let players = root.getElementsByTagName("players")[0];
  if (!players) {
    players = doc.createElement("players");
    root.appendChild(players);
  }
  let rules = root.getElementsByTagName("rules")[0];
  if (!rules) {
    rules = doc.createElement("rules");
    rules.setAttribute("action", "prepend");
    root.appendChild(rules);
  }

  // Drop any prior entries of ours so a re-run is idempotent.
  Array.from(players.getElementsByTagName("player"))
    .filter((p) => p.getAttribute("name") === PLAYER_NAME)
    .forEach((p) => p.remove());
  Array.from(rules.getElementsByTagName("rule"))
    .filter((r) => r.getAttribute("player") === PLAYER_NAME)
    .forEach((r) => r.remove());

  const playerFrag = new DOMParser().parseFromString(buildPlayerElementXml(target), "application/xml");
  players.appendChild(doc.importNode(playerFrag.documentElement, true));

  const rulesFrag = new DOMParser().parseFromString(
    `<rules>${buildRuleXml(includeDiscFolderRules)}</rules>`,
    "application/xml",
  );
  Array.from(rulesFrag.documentElement.getElementsByTagName("rule")).forEach((r) =>
    rules.appendChild(doc.importNode(r, true)),
  );

  return new XMLSerializer().serializeToString(doc) + "\n";
}
