import {
  XML_4K_TAG_FILENAME_PATTERN,
  buildPlayerElementXml,
  buildPlayercorefactoryXml,
  buildRuleXml,
  type KodiTarget,
} from "./generate";

const PLAYER_NAME = "Oppo203ISO";

// The filetypes of the rules we generate. Used to identify our own prior rules for
// idempotent replacement without touching user-authored rules that target our player.
const OUR_RULE_FILETYPES = new Set(["iso", "bdmv", "mpls"]);

/**
 * True when a rule filename is one WE generate: the 4K/UHD tag pattern OR a configured-folder
 * pattern. Both are wrapped in `.*...*.`; a literal user-authored filename (or none) is not, so
 * those are preserved across a re-merge.
 */
function isOurGeneratedFilename(filename: string | null): boolean {
  if (!filename) return false;
  if (filename === XML_4K_TAG_FILENAME_PATTERN) return true;
  return filename.startsWith(".*") && filename.endsWith(".*");
}

/**
 * Merge our <player>/<rule> entries into an existing playercorefactory.xml, preserving the
 * user's other players and rules. Idempotent: re-running replaces our own entries rather than
 * duplicating them. Returns a fresh document when there is no existing file, and REFUSES
 * (throws) when an existing file is malformed or not a playercorefactory document — mirroring
 * resources/lib/kodi/playercorefactory_merge.py, which never blind-overwrites a file it can't
 * safely merge.
 */
export function mergePlayercorefactory(
  existing: string | null,
  target: KodiTarget,
  includeDiscFolderRules = true,
  discFolders: readonly string[] = [],
): string {
  if (!existing || existing.trim() === "") {
    return buildPlayercorefactoryXml(target, includeDiscFolderRules, discFolders);
  }

  const doc = new DOMParser().parseFromString(existing, "application/xml");
  const root = doc.documentElement;
  const malformed = doc.getElementsByTagName("parsererror").length > 0;
  if (malformed) {
    throw new Error(
      "existing playercorefactory.xml is malformed; refusing to merge. Fix or move the file first.",
    );
  }
  if (!root || root.nodeName !== "playercorefactory") {
    throw new Error(
      `existing playercorefactory.xml root is <${root?.nodeName ?? "unknown"}>, expected ` +
        "<playercorefactory>; refusing to merge. Fix or move the file first.",
    );
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

  // Drop our own prior entries so a re-run is idempotent, WITHOUT removing user-authored
  // players/rules that merely target our player. Our generated rules are disc-filetype rules
  // for our player whose filename is a wrapped `.*...*.` pattern (the 4K tag pattern OR a
  // configured-folder pattern). A hand-added rule like <rule filetypes="img" player="..."/>
  // (non-disc filetype) or one with a literal, non-wildcard filename is therefore preserved.
  Array.from(players.getElementsByTagName("player"))
    .filter((p) => p.getAttribute("name") === PLAYER_NAME)
    .forEach((p) => p.remove());
  Array.from(rules.getElementsByTagName("rule"))
    .filter(
      (r) =>
        r.getAttribute("player") === PLAYER_NAME &&
        OUR_RULE_FILETYPES.has(r.getAttribute("filetypes") ?? "") &&
        isOurGeneratedFilename(r.getAttribute("filename")),
    )
    .forEach((r) => r.remove());

  const playerFrag = new DOMParser().parseFromString(buildPlayerElementXml(target), "application/xml");
  players.appendChild(doc.importNode(playerFrag.documentElement, true));

  const rulesFrag = new DOMParser().parseFromString(
    `<rules>${buildRuleXml(includeDiscFolderRules, discFolders)}</rules>`,
    "application/xml",
  );
  Array.from(rulesFrag.documentElement.getElementsByTagName("rule")).forEach((r) =>
    rules.appendChild(doc.importNode(r, true)),
  );

  return new XMLSerializer().serializeToString(doc) + "\n";
}
