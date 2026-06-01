export interface PathRewrite {
  from: string;
  to: string;
}

/**
 * Derive the http_handoff path rewrite (`oppo_http_path_from` -> `oppo_http_path_to`) from the
 * SAME file's Kodi-visible path and OPPO-visible path. Matches the longest run of shared trailing
 * path segments and returns the differing prefixes, so the add-on's `path.replace(from, to)` turns
 * the Kodi path into the OPPO path. Returns null when the two share no trailing segment (likely not
 * the same file) or are identical (no rewrite needed). Paths are compared on `/` boundaries; the
 * OPPO-visible side uses the player's own mount label (e.g. `MyPC`), which is why it must be
 * observed, not derived from the Kodi URL alone.
 */
export function deriveRewrite(kodiPath: string, oppoPath: string): PathRewrite | null {
  const a = kodiPath.trim();
  const b = oppoPath.trim();
  if (!a || !b) return null;
  const aSeg = a.split("/");
  const bSeg = b.split("/");
  let n = 0;
  while (
    n < aSeg.length &&
    n < bSeg.length &&
    aSeg[aSeg.length - 1 - n] === bSeg[bSeg.length - 1 - n] &&
    aSeg[aSeg.length - 1 - n] !== ""
  ) {
    n++;
  }
  if (n === 0) return null;
  const tail = aSeg.slice(aSeg.length - n).join("/");
  const from = a.slice(0, a.length - tail.length);
  const to = b.slice(0, b.length - tail.length);
  if (from === to) return null;
  return { from, to };
}
