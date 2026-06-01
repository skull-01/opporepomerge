/**
 * The add-on's split-truth session status file, mirrored on the configurator side so the
 * dashboard can read it. Written by resources/lib/kodi/playback_session.py `_status` at session
 * start and end (never continuously), next to settings.xml under the add-on's addon_data dir.
 */

/** Path of the add-on's status JSON relative to Kodi userdata/ (sibling of settings.xml). */
export const ADDON_DATA_STATUS_REL =
  "addon_data/script.oppo203.iso.external/oppo203iso-status.json";

export type OppoSessionState = "starting" | "stopped" | "failed";

/**
 * The add-on's session lifecycle phase, finer-grained than sessionState:
 *   launching  - fast_start in flight (TV switch + AVR pre-sequence + OPPO start).
 *   monitoring - the hold/SVM3 monitor is running.
 *   ended      - fast_return done, session cleared.
 * Optional: only present on records written by the richer status writer (add-on PR #183+).
 */
export type OppoSessionPhase = "launching" | "monitoring" | "ended";

/**
 * One parsed session-status record. The snapshot fields (oppoPlaybackState / utcTickCount /
 * stopReason) are only populated once the monitor finishes, so they are null while the session
 * is still "starting". The identity/timing fields (sessionId / startedAt / updatedAt / phase) are
 * only written by the richer status writer (add-on PR #183+), so they are null on older records.
 */
export type OppoSessionStatus = {
  launchSource: string;
  architecturePreset: string;
  routingMode: string;
  monitorMode: string;
  mediaFile: string;
  sessionState: OppoSessionState;
  confirmedPlayback: boolean;
  confirmedProgress: boolean;
  oppoPlaybackState: string | null;
  utcTickCount: number | null;
  stopReason: string | null;
  // Stable per session so two back-to-back sessions can be told apart; null on older records.
  sessionId: string | null;
  // Epoch seconds the session started / was last written; null on older records.
  startedAt: number | null;
  updatedAt: number | null;
  phase: OppoSessionPhase | null;
};

const SESSION_STATES: readonly OppoSessionState[] = ["starting", "stopped", "failed"];
const SESSION_PHASES: readonly OppoSessionPhase[] = ["launching", "monitoring", "ended"];

const str = (v: unknown): string => (typeof v === "string" ? v : "");
const strOrNull = (v: unknown): string | null => (typeof v === "string" ? v : null);
const numOrNull = (v: unknown): number | null =>
  typeof v === "number" && Number.isFinite(v) ? v : null;
const phaseOrNull = (v: unknown): OppoSessionPhase | null =>
  typeof v === "string" && SESSION_PHASES.includes(v as OppoSessionPhase)
    ? (v as OppoSessionPhase)
    : null;

/**
 * Parse the raw status JSON into a typed record, or null when it is absent, not JSON, not an
 * object, or carries no recognized session_state. Tolerant of missing optional fields so a
 * "starting" record (no snapshot yet) parses cleanly; never throws.
 */
export function parseOppoStatus(raw: string | null | undefined): OppoSessionStatus | null {
  if (raw == null || raw.trim() === "") return null;
  let obj: unknown;
  try {
    obj = JSON.parse(raw);
  } catch {
    return null;
  }
  if (!obj || typeof obj !== "object") return null;
  const o = obj as Record<string, unknown>;
  const sessionState = o.session_state;
  if (
    typeof sessionState !== "string" ||
    !SESSION_STATES.includes(sessionState as OppoSessionState)
  ) {
    return null;
  }
  return {
    launchSource: str(o.launch_source),
    architecturePreset: str(o.architecture_preset),
    routingMode: str(o.routing_mode),
    monitorMode: str(o.monitor_mode),
    mediaFile: str(o.media_file),
    sessionState: sessionState as OppoSessionState,
    confirmedPlayback: o.confirmed_playback === true,
    confirmedProgress: o.confirmed_progress === true,
    oppoPlaybackState: strOrNull(o.oppo_playback_state),
    utcTickCount: numOrNull(o.utc_tick_count),
    stopReason: strOrNull(o.stop_reason),
    sessionId: strOrNull(o.session_id),
    startedAt: numOrNull(o.started_at),
    updatedAt: numOrNull(o.updated_at),
    phase: phaseOrNull(o.phase),
  };
}

/**
 * A compact "Nm ago" / "Nh Mm ago" relative-age string from an epoch-seconds timestamp, given a
 * reference now (epoch ms, injectable for tests). Returns null when the timestamp is absent so the
 * caller can simply omit the line for older status records that carry no timing. A future or
 * <1-minute timestamp reads as "just now" rather than a negative/zero-second age.
 */
export function formatEpochAge(
  epochSeconds: number | null,
  nowMs: number = Date.now()
): string | null {
  if (epochSeconds == null) return null;
  const seconds = Math.floor(nowMs / 1000 - epochSeconds);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  const remMinutes = minutes % 60;
  return remMinutes === 0 ? `${hours}h ago` : `${hours}h ${remMinutes}m ago`;
}

/**
 * Whether a session's last write (updatedAt) is recent enough to call the record "fresh". The
 * richer status writer refreshes updatedAt on every phase write, so a stale updatedAt on a
 * still-"starting" record means the add-on process likely died mid-session. Null updatedAt (older
 * records) returns null - freshness is simply unknown, not stale.
 */
export function isStatusFresh(
  updatedAt: number | null,
  nowMs: number = Date.now(),
  maxAgeSeconds = 120
): boolean | null {
  if (updatedAt == null) return null;
  return nowMs / 1000 - updatedAt <= maxAgeSeconds;
}
