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
 * One parsed session-status record. The snapshot fields (oppoPlaybackState / utcTickCount /
 * stopReason) are only populated once the monitor finishes, so they are null while the session
 * is still "starting".
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
};

const SESSION_STATES: readonly OppoSessionState[] = ["starting", "stopped", "failed"];

const str = (v: unknown): string => (typeof v === "string" ? v : "");
const strOrNull = (v: unknown): string | null => (typeof v === "string" ? v : null);
const numOrNull = (v: unknown): number | null =>
  typeof v === "number" && Number.isFinite(v) ? v : null;

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
  };
}
