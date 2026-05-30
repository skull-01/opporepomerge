export type StepId =
  | "step0"
  | "step1"
  | "step2"
  | "step3"
  | "step4"
  | "step5"
  | "test";

export type ScreenId =
  | "step0_gate"
  | "step0_exit"
  | "step1_intro"
  | "step1_tierA"
  | "step1_tierB"
  | "step1_tierC"
  | "step2_brand"
  | "step2_test"
  | "step2_fail"
  | "step3_brand"
  | "step3_model"
  | "step3_notfound"
  | "step3_probe"
  | "step3_adb_warn"
  | "step3_test"
  | "step3_fail"
  | "step4_intro"
  | "step4_ask"
  | "step4_fallback"
  | "step4_done"
  | "step5_ask"
  | "step5_brand"
  | "step5_model"
  | "test_setup"
  | "test_confirm"
  | "test_success";

export type ChainTarget =
  | "media"
  | "kodi"
  | "tv"
  | "player"
  | "tv-player"
  | "all";

export type Step = {
  id: StepId;
  label: string;
  num: string;
};

// Step ids match the displayed order and number: 0 prereq, 1 Kodi, 2 Player, 3 TV,
// 4 HDMI Input, 5 AV receiver (optional), then the final test. Player precedes TV so the
// HDMI-input step sits next to the TV step; the optional receiver step trails the core chain
// just before the test. The `step2_*` screens are the Player screens, `step3_*` are TV,
// `step4_*` are HDMI, `step5_*` are the AV receiver — file names, ids, and labels all line up
// so the code reads the way the UI does.
export const STEPS: readonly Step[] = [
  { id: "step0", label: "Playback chain setup", num: "0" },
  { id: "step1", label: "Kodi box", num: "1" },
  { id: "step2", label: "Player", num: "2" },
  { id: "step3", label: "TV", num: "3" },
  { id: "step4", label: "HDMI Input", num: "4" },
  { id: "step5", label: "AV Receiver", num: "5" },
  { id: "test", label: "Playback Test", num: "✓" },
] as const;

export const SCREEN_TO_STEP: Record<ScreenId, StepId> = {
  step0_gate: "step0",
  step0_exit: "step0",
  step1_intro: "step1",
  step1_tierA: "step1",
  step1_tierB: "step1",
  step1_tierC: "step1",
  step2_brand: "step2",
  step2_test: "step2",
  step2_fail: "step2",
  step3_brand: "step3",
  step3_model: "step3",
  step3_notfound: "step3",
  step3_probe: "step3",
  step3_adb_warn: "step3",
  step3_test: "step3",
  step3_fail: "step3",
  step4_intro: "step4",
  step4_ask: "step4",
  step4_fallback: "step4",
  step4_done: "step4",
  step5_ask: "step5",
  step5_brand: "step5",
  step5_model: "step5",
  test_setup: "test",
  test_confirm: "test",
  test_success: "test",
};

export const SCREEN_TO_CHAIN: Record<ScreenId, ChainTarget> = {
  step0_gate: "media",
  step0_exit: "media",
  step1_intro: "kodi",
  step1_tierA: "kodi",
  step1_tierB: "kodi",
  step1_tierC: "kodi",
  step2_brand: "player",
  step2_test: "player",
  step2_fail: "player",
  step3_brand: "tv",
  step3_model: "tv",
  step3_notfound: "tv",
  step3_probe: "tv",
  step3_adb_warn: "tv",
  step3_test: "tv",
  step3_fail: "tv",
  step4_intro: "tv-player",
  step4_ask: "tv-player",
  step4_fallback: "tv-player",
  step4_done: "tv-player",
  step5_ask: "tv-player",
  step5_brand: "tv-player",
  step5_model: "tv-player",
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
      return "step3_brand";
    case "step4":
      return "step4_intro";
    case "step5":
      return "step5_ask";
    case "test":
      return "test_setup";
  }
}
