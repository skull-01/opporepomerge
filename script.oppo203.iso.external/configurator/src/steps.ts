export type StepId =
  | "step0"
  | "step1"
  | "step2"
  | "step3"
  | "step3_5"
  | "test";

export type ScreenId =
  | "step0_gate"
  | "step0_exit"
  | "step1_intro"
  | "step1_tierA"
  | "step1_tierB"
  | "step1_tierC"
  | "step2_brand"
  | "step2_model"
  | "step2_notfound"
  | "step2_probe"
  | "step2_adb_warn"
  | "step2_test"
  | "step2_fail"
  | "step3_brand"
  | "step3_test"
  | "step3_fail"
  | "step35_intro"
  | "step35_ask"
  | "step35_fallback"
  | "step35_done"
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

export const STEPS: readonly Step[] = [
  { id: "step0", label: "Prerequisite", num: "0" },
  { id: "step1", label: "Kodi box", num: "1" },
  { id: "step2", label: "TV", num: "2" },
  { id: "step3", label: "Player", num: "3" },
  { id: "step3_5", label: "Inputs", num: "3.5" },
  { id: "test", label: "Full test", num: "✓" },
] as const;

export const SCREEN_TO_STEP: Record<ScreenId, StepId> = {
  step0_gate: "step0",
  step0_exit: "step0",
  step1_intro: "step1",
  step1_tierA: "step1",
  step1_tierB: "step1",
  step1_tierC: "step1",
  step2_brand: "step2",
  step2_model: "step2",
  step2_notfound: "step2",
  step2_probe: "step2",
  step2_adb_warn: "step2",
  step2_test: "step2",
  step2_fail: "step2",
  step3_brand: "step3",
  step3_test: "step3",
  step3_fail: "step3",
  step35_intro: "step3_5",
  step35_ask: "step3_5",
  step35_fallback: "step3_5",
  step35_done: "step3_5",
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
  step2_brand: "tv",
  step2_model: "tv",
  step2_notfound: "tv",
  step2_probe: "tv",
  step2_adb_warn: "tv",
  step2_test: "tv",
  step2_fail: "tv",
  step3_brand: "player",
  step3_test: "player",
  step3_fail: "player",
  step35_intro: "tv-player",
  step35_ask: "tv-player",
  step35_fallback: "tv-player",
  step35_done: "tv-player",
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
    case "step3_5":
      return "step35_intro";
    case "test":
      return "test_setup";
  }
}
