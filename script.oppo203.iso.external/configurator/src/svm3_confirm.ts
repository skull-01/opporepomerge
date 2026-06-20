// Fold the OPPO verbose-mode-3 push stream (`oppo-live` frames from the Rust monitor) into a
// playback verdict for the self-test, so the test confirms playback from what the player itself
// reports instead of a manual yes/no. Mirrors the add-on's OppoSvm3PlaybackMonitor
// (resources/lib/oppo/playback_monitor_svm3.py): `@UPL PLAY` confirms playback and an *advancing*
// `@UTC` time code confirms progress -- never because a play command was sent. Pure + framework-free
// so the fold logic is unit-tested without a live player.

// One verbose push frame as the Rust monitor emits it (see lib.rs `LiveFrame` / classify_frame).
export type LiveFrame = { seq: number; kind: string; raw: string };

export type Svm3Confirm = {
  // The normalized @UPL state label: PLAY | PAUS | MENU | HOME | MCTR | STOP | unknown | null.
  playbackState: string | null;
  // True once the player reported an active @UPL state (PLAY/FFWD/…): real playback, not a command.
  confirmedPlayback: boolean;
  // True once a *different* @UTC time code arrived after the first: the time code is advancing.
  confirmedProgress: boolean;
  // The most recent @UTC time code seen, and how many distinct codes have arrived.
  lastUtc: string | null;
  utcTicks: number;
  // True once a terminal @UPL stop state (STOP/HOME/…) arrived.
  stopped: boolean;
};

export const INITIAL_SVM3_CONFIRM: Svm3Confirm = {
  playbackState: null,
  confirmedPlayback: false,
  confirmedProgress: false,
  lastUtc: null,
  utcTicks: 0,
  stopped: false,
};

// @UPL value groups, mirroring _UPL_PLAY / _UPL_PAUSE / _UPL_MENU / _UPL_STOP in the add-on. An
// active/keep-alive value confirms playback; the stop set is terminal (a disc menu stays active).
const UPL_PLAY = new Set(["PLAY", "FFWD", "FREV", "SFWD", "SREV", "LOADING"]);
const UPL_PAUSE = new Set(["PAUSE", "PAUS"]);
const UPL_MENU = new Set(["MENU", "DISC", "DISC MENU"]);
const UPL_STOP = new Set([
  "STOP",
  "STOPPED",
  "HOME",
  "HOME MENU",
  "MCTR",
  "MEDIA CENTER",
  "NO DISC",
  "NODISC",
]);

/** Normalize a raw @UPL value to a status-model state token (mirrors `_upl_state_label`). */
export function uplStateLabel(value: string): string {
  const v = value.toUpperCase().trim();
  if (UPL_PLAY.has(v)) return "PLAY";
  if (UPL_PAUSE.has(v)) return "PAUS";
  if (UPL_MENU.has(v)) return "MENU";
  if (UPL_STOP.has(v)) {
    if (v.startsWith("HOME")) return "HOME";
    if (v === "MCTR" || v === "MEDIA CENTER") return "MCTR";
    return "STOP";
  }
  return "unknown";
}

type ParsedFrame = { code: string; rest: string };

/**
 * Parse one push line into its code + remainder, mirroring `_handle_line`: strip a leading `@`,
 * split on the first run of whitespace, upper-case the code. Returns null for an empty line.
 */
export function parseLiveLine(raw: string): ParsedFrame | null {
  let norm = raw.trim();
  if (norm.startsWith("@")) norm = norm.slice(1);
  norm = norm.trim();
  if (!norm) return null;
  const idx = norm.search(/\s/);
  if (idx === -1) return { code: norm.toUpperCase(), rest: "" };
  return { code: norm.slice(0, idx).toUpperCase(), rest: norm.slice(idx + 1).trim() };
}

/**
 * Fold one `oppo-live` frame into the running verdict (immutable; returns a new object). `@UPL`
 * updates the state label and confirms playback on an active value; `@UTC` confirms progress when
 * the time code differs from the last one. Non-UPL/UTC frames (info/status/raw) pass through
 * unchanged. Matches `_handle_upl` / `_handle_utc` in the add-on monitor.
 */
export function foldSvm3Frame(state: Svm3Confirm, frame: LiveFrame): Svm3Confirm {
  const parsed = parseLiveLine(frame.raw);
  if (!parsed) return state;

  if (parsed.code === "UPL") {
    const label = uplStateLabel(parsed.rest);
    return {
      ...state,
      playbackState: label,
      confirmedPlayback: state.confirmedPlayback || label === "PLAY",
      stopped: state.stopped || UPL_STOP.has(parsed.rest.toUpperCase().trim()),
    };
  }

  if (parsed.code === "UTC") {
    const code = parsed.rest.trim();
    if (!code) return state;
    if (state.lastUtc === null) {
      return { ...state, lastUtc: code, utcTicks: 1 };
    }
    if (code !== state.lastUtc) {
      return { ...state, lastUtc: code, utcTicks: state.utcTicks + 1, confirmedProgress: true };
    }
    return state;
  }

  return state;
}

/** Fold a whole sequence of frames into a single verdict (replays the stream from the initial state). */
export function foldSvm3Frames(frames: readonly LiveFrame[]): Svm3Confirm {
  return frames.reduce(foldSvm3Frame, INITIAL_SVM3_CONFIRM);
}
