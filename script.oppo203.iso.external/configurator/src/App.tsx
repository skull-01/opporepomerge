import { useCallback, useEffect, useState } from "react";
import { WinShell } from "./shell/WinShell";
import { t } from "./i18n";
import { Chain } from "./shell/Chain";
import { Progress } from "./shell/Progress";
import { Sidebar } from "./shell/Sidebar";
import { DebugPanel } from "./shell/DebugPanel";
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
import { setCurrentStep } from "./debug/log";
import { startWireListener } from "./debug/wireListener";
import { Step0Gate } from "./screens/Step0Gate";
import { Step0Chain } from "./screens/Step0Chain";
import { Step0Exit } from "./screens/Step0Exit";
import { Step1Intro, Step1TierA, Step1TierB, Step1TierC } from "./screens/step1";
import { Step2Brand, Step2Test, Step2Fail } from "./screens/step2";
import { Step3Mode } from "./screens/step3";
import {
  Step4Brand,
  Step4Model,
  Step4NotFound,
  Step4Probe,
  Step4AdbWarn,
  Step4Test,
  Step4Fail,
} from "./screens/step4";
import { Step5Intro, Step5Ask, Step5Fallback, Step5Done } from "./screens/step5";
import { Step6Ask, Step6Brand, Step6Model } from "./screens/step6";
import { TestSetup, TestConfirm, TestSuccess } from "./screens/test";
import { Dashboard } from "./screens/dashboard";
import { ResetAllScreen } from "./screens/ResetAll";
import { DeveloperScreen } from "./screens/developer/Developer";
import type { ScreenProps } from "./screens/types";

// Picking the progress variant in production — change here, not at runtime.
// The prototype's tweaks panel for swapping variants is intentionally dropped.
const PROGRESS_VARIANT: "stepper" | "sidebar" | "minimal" = "stepper";

const SCREEN_RENDERERS: Record<ScreenId, (props: ScreenProps) => JSX.Element> = {
  step0_gate: Step0Gate,
  step0_chain: Step0Chain,
  step0_exit: Step0Exit,
  step1_intro: Step1Intro,
  step1_tierA: Step1TierA,
  step1_tierB: Step1TierB,
  step1_tierC: Step1TierC,
  step2_brand: Step2Brand,
  step2_test: Step2Test,
  step2_fail: Step2Fail,
  step3_mode: Step3Mode,
  step4_brand: Step4Brand,
  step4_model: Step4Model,
  step4_notfound: Step4NotFound,
  step4_probe: Step4Probe,
  step4_adb_warn: Step4AdbWarn,
  step4_test: Step4Test,
  step4_fail: Step4Fail,
  step5_intro: Step5Intro,
  step5_ask: Step5Ask,
  step5_fallback: Step5Fallback,
  step5_done: Step5Done,
  step6_ask: Step6Ask,
  step6_brand: Step6Brand,
  step6_model: Step6Model,
  test_setup: TestSetup,
  test_confirm: TestConfirm,
  test_success: TestSuccess,
  dashboard: Dashboard,
  reset_all: ResetAllScreen,
  developer: DeveloperScreen,
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
  useEffect(() => {
    setCurrentStep(stepId);
  }, [stepId]);

  // Stream raw wire frames (OPPO IP-control bytes) from Rust into the debug log. No-op in a
  // non-Tauri context (vite preview / tests), where the event bridge is absent.
  useEffect(() => {
    let unlisten: (() => void) | undefined;
    void startWireListener()
      .then((un) => {
        unlisten = un;
      })
      .catch(() => {});
    return () => unlisten?.();
  }, []);
  const completed = computeCompleted(state, screen);
  const chainActive = SCREEN_TO_CHAIN[screen];
  const useSidebar = PROGRESS_VARIANT === "sidebar";

  const onJumpStep = (sid: StepId) => go(firstScreenOfStep(sid));

  const Screen = SCREEN_RENDERERS[screen] ?? Step0Gate;

  return (
    <WinShell title={t("app.versionLine", { name: t("app.title"), version: __APP_VERSION__ })}>
      <div className="app-header">
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginBottom: 8 }}>
          {screen !== "developer" && (
            <button className="btn ghost sm" onClick={() => go("developer")}>
              Developer…
            </button>
          )}
          {screen !== "reset_all" && (
            <button className="btn ghost sm" onClick={() => go("reset_all")}>
              Reset all…
            </button>
          )}
        </div>
        {!useSidebar && PROGRESS_VARIANT === "stepper" && (
          <Progress variant="stepper" current={stepId} onJump={onJumpStep} />
        )}
        {!useSidebar && PROGRESS_VARIANT === "minimal" && (
          <Progress variant="minimal" current={stepId} onJump={onJumpStep} />
        )}
        <Chain active={chainActive} completed={completed} topology={state.topology} />
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
      <DebugPanel currentStep={stepId} />
    </WinShell>
  );
}
