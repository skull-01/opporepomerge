import { useCallback, useEffect, useState } from "react";
import { WinShell } from "./shell/WinShell";
import { Chain } from "./shell/Chain";
import { Progress } from "./shell/Progress";
import { Sidebar } from "./shell/Sidebar";
import {
  INITIAL_STATE,
  computeCompleted,
  loadPersistedSession,
  savePersistedSession,
  type WizardState,
} from "./state";
import {
  SCREEN_TO_CHAIN,
  SCREEN_TO_STEP,
  firstScreenOfStep,
  type ScreenId,
  type StepId,
} from "./steps";
import { Step0Gate } from "./screens/Step0Gate";
import { Step0Exit } from "./screens/Step0Exit";
import { Step1Intro, Step1TierA, Step1TierB, Step1TierC } from "./screens/step1";
import {
  Step2Brand,
  Step2Model,
  Step2NotFound,
  Step2Probe,
  Step2AdbWarn,
  Step2Test,
  Step2Fail,
} from "./screens/step2";
import { Step3Brand, Step3Test, Step3Fail } from "./screens/step3";
import { Step35Intro, Step35Ask, Step35Fallback, Step35Done } from "./screens/step35";
import { TestSetup, TestConfirm, TestSuccess } from "./screens/test";
import type { ScreenProps } from "./screens/types";

// Picking the progress variant in production — change here, not at runtime.
// The prototype's tweaks panel for swapping variants is intentionally dropped.
const PROGRESS_VARIANT: "stepper" | "sidebar" | "minimal" = "stepper";

const SCREEN_RENDERERS: Record<ScreenId, (props: ScreenProps) => JSX.Element> = {
  step0_gate: Step0Gate,
  step0_exit: Step0Exit,
  step1_intro: Step1Intro,
  step1_tierA: Step1TierA,
  step1_tierB: Step1TierB,
  step1_tierC: Step1TierC,
  step2_brand: Step2Brand,
  step2_model: Step2Model,
  step2_notfound: Step2NotFound,
  step2_probe: Step2Probe,
  step2_adb_warn: Step2AdbWarn,
  step2_test: Step2Test,
  step2_fail: Step2Fail,
  step3_brand: Step3Brand,
  step3_test: Step3Test,
  step3_fail: Step3Fail,
  step35_intro: Step35Intro,
  step35_ask: Step35Ask,
  step35_fallback: Step35Fallback,
  step35_done: Step35Done,
  test_setup: TestSetup,
  test_confirm: TestConfirm,
  test_success: TestSuccess,
};

export default function App() {
  const [screen, setScreen] = useState<ScreenId>("step0_gate");
  const [state, setState] = useState<WizardState>(INITIAL_STATE);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    void loadPersistedSession().then((loaded) => {
      if (loaded) {
        setState(loaded.state);
        setScreen(loaded.screen);
      }
      setHydrated(true);
    });
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    void savePersistedSession({ state, screen });
  }, [state, screen, hydrated]);

  const set = useCallback(
    (patch: Partial<WizardState>) => setState((s) => ({ ...s, ...patch })),
    []
  );

  const go = useCallback((id: ScreenId) => {
    setScreen(id);
    requestAnimationFrame(() => {
      const c = document.querySelector(".content-inner, .app-content");
      if (c) c.scrollTop = 0;
    });
  }, []);

  const stepId: StepId = SCREEN_TO_STEP[screen];
  const completed = computeCompleted(state, screen);
  const chainActive = SCREEN_TO_CHAIN[screen];
  const useSidebar = PROGRESS_VARIANT === "sidebar";

  const onJumpStep = (sid: StepId) => go(firstScreenOfStep(sid));

  const Screen = SCREEN_RENDERERS[screen];

  return (
    <WinShell title="OppoKodiAddon Configurator · setup wizard">
      <div className="app-header">
        {!useSidebar && PROGRESS_VARIANT === "stepper" && (
          <Progress variant="stepper" current={stepId} onJump={onJumpStep} />
        )}
        {!useSidebar && PROGRESS_VARIANT === "minimal" && (
          <Progress variant="minimal" current={stepId} onJump={onJumpStep} />
        )}
        <Chain active={chainActive} completed={completed} />
      </div>

      {useSidebar ? (
        <div className="app-content with-sidebar">
          <Sidebar current={stepId} onJump={onJumpStep} />
          <div className="content-inner">
            <Screen go={go} state={state} set={set} />
          </div>
        </div>
      ) : (
        <div className="app-content">
          <Screen go={go} state={state} set={set} />
        </div>
      )}
    </WinShell>
  );
}
