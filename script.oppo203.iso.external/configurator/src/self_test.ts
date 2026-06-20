// Pure core for the OPPO self-test orchestration (Phase 4.4). The sequence is power-cycle → mount →
// http_handoff play → SVM3-confirm → control-forwarding, each with an honest fallback. Keeping the
// step model and the path rewrite framework-free makes the orchestration unit-testable without a
// player or React; the screen drives the side effects (invoke / live monitor).

/**
 * Translate a Kodi-visible media path into the OPPO-visible path by replacing the FIRST occurrence
 * of the `from` prefix with `to`. Mirrors the add-on's `_translate_media_path`
 * (`translated.replace(source, target, 1)` in resources/lib/oppo/oppo_control.py). Returns the path
 * unchanged when `from` is empty or absent, so a missing/incorrect rewrite degrades to "play the
 * raw path" rather than throwing — the honest fallback the self-test surfaces.
 */
export function applyRewrite(path: string, from: string, to: string): string {
  const p = path.trim();
  if (!from) return p;
  const idx = p.indexOf(from);
  if (idx === -1) return p;
  return p.slice(0, idx) + to + p.slice(idx + from.length);
}

export type SelfTestStepId = "power_cycle" | "mount" | "play" | "confirm" | "control";

export type StepStatus = "idle" | "running" | "ok" | "fail" | "skipped";

export type SelfTestStep = {
  id: SelfTestStepId;
  label: string;
  // What the operator should do / what the configurator does, and the honest fallback if it can't.
  detail: string;
};

// The fixed self-test order. `mount` is informational for http_handoff: the player mounts the
// network share itself when handed the path on `play`, so there is no separate mount command --
// the step exists to make that explicit and to host the manual fallback when the share isn't seen.
export const SELF_TEST_STEPS: readonly SelfTestStep[] = [
  {
    id: "power_cycle",
    label: "Power-cycle the player",
    detail: "Send #POF then #PON over IP control so the test starts from a known state.",
  },
  {
    id: "mount",
    label: "Reach the media share",
    detail:
      "For http_handoff the player mounts the share itself on play — no separate command. " +
      "If it can't see the share, mount it once in the player's own browser first.",
  },
  {
    id: "play",
    label: "Hand off the file (http_handoff)",
    detail:
      "Fire /playnormalfile with the OPPO-visible path (the Kodi path rewritten via the captured " +
      "from→to mapping).",
  },
  {
    id: "confirm",
    label: "Confirm playback (SVM3)",
    detail: "Watch verbose-mode-3 frames for @UPL PLAY + an advancing @UTC, not a manual guess.",
  },
  {
    id: "control",
    label: "Test control forwarding",
    detail: "Drive the disc menu with the Kodi remote, then answer the confirmation questions.",
  },
] as const;

export type SelfTestState = Record<SelfTestStepId, StepStatus>;

export const INITIAL_SELF_TEST: SelfTestState = {
  power_cycle: "idle",
  mount: "idle",
  play: "idle",
  confirm: "idle",
  control: "idle",
};

/** Whether every step has reached a terminal state (ok or skipped) — i.e. the sequence is done. */
export function selfTestComplete(state: SelfTestState): boolean {
  return SELF_TEST_STEPS.every((s) => state[s.id] === "ok" || state[s.id] === "skipped");
}

/** True once playback was confirmed end-to-end: the play handoff and the SVM3 confirm both passed. */
export function selfTestPlaybackConfirmed(state: SelfTestState): boolean {
  return state.play === "ok" && state.confirm === "ok";
}

/**
 * Whether the play step can run yet: it needs an OPPO-visible path, which means a captured rewrite
 * (oppo_http_path_from set) OR a path the operator typed directly. A blank result means "no path —
 * capture it on the Player step first", the honest gate before firing a play at nothing.
 */
export function canFireHttpPlay(oppoPath: string): boolean {
  return oppoPath.trim().length > 0;
}
