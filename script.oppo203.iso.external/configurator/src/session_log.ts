import type { OppoSessionStatus } from "./oppo_status";

/**
 * One observed session in the dashboard's local history: the add-on's status record plus when the
 * dashboard first saw the session and when it last recorded a change to it.
 */
export type SessionLogEntry = OppoSessionStatus & {
  firstSeenAt: string;
  observedAt: string;
};

/** Default cap on retained history entries (the newest `cap` are kept). */
export const DEFAULT_LOG_CAP = 50;

/**
 * Identity used to decide whether a freshly-read status is the same session as the newest log
 * entry. Prefers the add-on's stable `session_id` (richer status writer, add-on PR #183+) for an
 * EXACT match, so two identical back-to-back sessions are told apart. Falls back to the stable
 * descriptors for older records that carry no id - then two identical back-to-back sessions cannot
 * be distinguished (the heuristic limitation the legacy `_status` schema forces).
 */
export function sessionSignature(s: OppoSessionStatus): string {
  if (s.sessionId) return `id:${s.sessionId}`;
  return [s.launchSource, s.architecturePreset, s.routingMode, s.monitorMode, s.mediaFile].join("|");
}

function isTerminal(s: OppoSessionStatus): boolean {
  return s.sessionState === "stopped" || s.sessionState === "failed";
}

function statusEqual(a: OppoSessionStatus, b: OppoSessionStatus): boolean {
  return (
    a.launchSource === b.launchSource &&
    a.architecturePreset === b.architecturePreset &&
    a.routingMode === b.routingMode &&
    a.monitorMode === b.monitorMode &&
    a.mediaFile === b.mediaFile &&
    a.sessionState === b.sessionState &&
    a.confirmedPlayback === b.confirmedPlayback &&
    a.confirmedProgress === b.confirmedProgress &&
    a.oppoPlaybackState === b.oppoPlaybackState &&
    a.utcTickCount === b.utcTickCount &&
    a.stopReason === b.stopReason &&
    a.sessionId === b.sessionId &&
    a.startedAt === b.startedAt &&
    a.updatedAt === b.updatedAt &&
    a.phase === b.phase
  );
}

/**
 * Fold one freshly-read status into the history (newest entry LAST). If it is the same session as
 * the newest entry, the entry is updated in place as the session advances (e.g. starting ->
 * stopped, or a heartbeat that only refreshes updatedAt/phase), preserving its firstSeenAt.
 * Otherwise the status opens a new entry. Same-session identity prefers the add-on's session_id;
 * without one (older records) a fresh "starting" after the newest entry already ended is treated
 * as a new session (a same-media replay) - the heuristic the legacy schema forces. Returns the
 * SAME array reference when nothing changed, so the caller can skip a redundant persist on the
 * many idle polls that re-read an unchanged file. `nowIso` is injected for deterministic tests;
 * the result is capped to the newest `cap` entries.
 */
export function foldObservation(
  log: SessionLogEntry[],
  status: OppoSessionStatus,
  nowIso: string,
  cap: number = DEFAULT_LOG_CAP,
): SessionLogEntry[] {
  const last = log.length > 0 ? log[log.length - 1] : null;
  const sameSignature = last != null && sessionSignature(last) === sessionSignature(status);
  // Only the id-less fallback needs the replay heuristic: with a real session_id a replay already
  // has a different signature, so an identical signature there always means the same session.
  const replayAfterEnd =
    !status.sessionId && status.sessionState === "starting" && last != null && isTerminal(last);
  const sameSession = sameSignature && !replayAfterEnd;

  if (sameSession && last != null) {
    if (statusEqual(last, status)) return log;
    const updated: SessionLogEntry = { ...status, firstSeenAt: last.firstSeenAt, observedAt: nowIso };
    return [...log.slice(0, -1), updated];
  }

  const entry: SessionLogEntry = { ...status, firstSeenAt: nowIso, observedAt: nowIso };
  const next = [...log, entry];
  return next.length > cap ? next.slice(next.length - cap) : next;
}
