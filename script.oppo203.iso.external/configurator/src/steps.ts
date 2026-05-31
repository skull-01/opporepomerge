export type StepId =
  | "step0"
  | "step1"
  | "step2"
  | "step3"
  | "step4"
  | "step5"
  | "step6"
  | "test";

export type ScreenId =
  | "step0_gate"
  | "step0_chain"
  | "step0_exit"
  | "step1_intro"
  | "step1_tierA"
  | "step1_tierB"
  | "step1_tierC"
  | "step2_brand"
  | "step2_test"
  | "step2_fail"
  | "step3_mode"
  | "step4_brand"
  | "step4_model"
  | "step4_notfound"
  | "step4_probe"
  | "step4_adb_warn"
  | "step4_test"
  | "step4_fail"
  | "step5_intro"
  | "step5_ask"
  | "step5_fallback"
  | "step5_done"
  | "step6_ask"
  | "step6_brand"
  | "step6_model"
  | "test_setup"
  | "test_confirm"
  | "test_success";

export type ChainTarget =
  | "media"
  | "kodi"
  | "tv"
  | "player"
  | "avr"
  | "tv-player"
  | "all";

export type Step = {
  id: StepId;
  label: string;
  num: string;
};

// Step ids match the displayed order and number: 0 prereq, 1 Kodi, 2 Player, 3 Playback mode,
// 4 TV, 5 HDMI Input, 6 AV receiver (optional), then the final test. Player precedes the
// playback-mode step and TV so the HDMI-input step sits next to the TV step; the optional
// receiver step trails the core chain just before the test. The `step2_*` screens are the
// Player screens, `step3_*` is Playback mode, `step4_*` are TV, `step5_*` are HDMI, `step6_*`
// are the AV receiver — file names, ids, and labels all line up so the code reads the way the
// UI does.
export const STEPS: readonly Step[] = [
  { id: "step0", label: "Playback chain setup", num: "0" },
  { id: "step1", label: "Kodi box", num: "1" },
  { id: "step2", label: "Player", num: "2" },
  { id: "step3", label: "Playback mode", num: "3" },
  { id: "step4", label: "TV", num: "4" },
  { id: "step5", label: "HDMI Input", num: "5" },
  { id: "step6", label: "AV Receiver", num: "6" },
  { id: "test", label: "Playback Test", num: "✓" },
] as const;

export const SCREEN_TO_STEP: Record<ScreenId, StepId> = {
  step0_gate: "step0",
  step0_chain: "step0",
  step0_exit: "step0",
  step1_intro: "step1",
  step1_tierA: "step1",
  step1_tierB: "step1",
  step1_tierC: "step1",
  step2_brand: "step2",
  step2_test: "step2",
  step2_fail: "step2",
  step3_mode: "step3",
  step4_brand: "step4",
  step4_model: "step4",
  step4_notfound: "step4",
  step4_probe: "step4",
  step4_adb_warn: "step4",
  step4_test: "step4",
  step4_fail: "step4",
  step5_intro: "step5",
  step5_ask: "step5",
  step5_fallback: "step5",
  step5_done: "step5",
  step6_ask: "step6",
  step6_brand: "step6",
  step6_model: "step6",
  test_setup: "test",
  test_confirm: "test",
  test_success: "test",
};

export const SCREEN_TO_CHAIN: Record<ScreenId, ChainTarget> = {
  step0_gate: "media",
  step0_chain: "media",
  step0_exit: "media",
  step1_intro: "kodi",
  step1_tierA: "kodi",
  step1_tierB: "kodi",
  step1_tierC: "kodi",
  step2_brand: "player",
  step2_test: "player",
  step2_fail: "player",
  step3_mode: "player",
  step4_brand: "tv",
  step4_model: "tv",
  step4_notfound: "tv",
  step4_probe: "tv",
  step4_adb_warn: "tv",
  step4_test: "tv",
  step4_fail: "tv",
  step5_intro: "tv-player",
  step5_ask: "tv-player",
  step5_fallback: "tv-player",
  step5_done: "tv-player",
  step6_ask: "tv-player",
  step6_brand: "tv-player",
  step6_model: "tv-player",
  test_setup: "all",
  test_confirm: "all",
  test_success: "all",
};

export function firstScreenOfStep(stepId: StepId): ScreenId {
  switch (stepId) {
    case "step0":
      return "step0_gate";
    case "step1":
      return "step1_intro";
    case "step2":
      return "step2_brand";
    case "step3":
      return "step3_mode";
    case "step4":
      return "step4_brand";
    case "step5":
      return "step5_intro";
    case "step6":
      return "step6_ask";
    case "test":
      return "test_setup";
  }
}

import type { Topology } from "./state";

/**
 * Topology-aware flow helpers. Kept as pure functions (no React) so the wizard's
 * branch decisions are unit-testable without rendering. A null topology (legacy/unset)
 * behaves as the TV chain everywhere - the soft default.
 */
export function isAvrChain(topology: Topology | null): boolean {
  return topology === "kodi_avr_tv_player";
}

/**
 * The chain nodes shown in the header visualization, in order. The AVR chain inserts an
 * "avr" node between Kodi and the player (player -> AVR -> TV); the TV chain omits it.
 */
export function chainNodeIds(topology: Topology | null): readonly ChainNodeId[] {
  return isAvrChain(topology)
    ? ["media", "kodi", "avr", "player", "tv"]
    : ["media", "kodi", "player", "tv"];
}

export type ChainNodeId = "media" | "kodi" | "avr" | "player" | "tv";

/**
 * Where Step 5 (HDMI input capture) hands off next. In the AVR chain the receiver does the
 * switching, so the receiver step is the natural next stop; in the TV chain it stays the
 * optional-receiver ask. Both ultimately reach step6_ask, but the AVR chain leads with it.
 */
export function step5NextScreen(_topology: Topology | null): ScreenId {
  return "step6_ask";
}
