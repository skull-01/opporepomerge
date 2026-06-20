import { Chain } from "./Chain";
import { Progress } from "./Progress";
import type { ChainCompletion } from "../state";
import { SCREEN_TO_STEP, type ChainTarget, type ScreenId, type StepId } from "../steps";

type Props = {
  progressVariant: "stepper" | "minimal";
  screenId: ScreenId;
  completed: ChainCompletion;
  chainActive: ChainTarget;
  onJump: (id: StepId) => void;
};

export function AppHeader({ progressVariant, screenId, completed, chainActive, onJump }: Props) {
  const stepId = SCREEN_TO_STEP[screenId];
  return (
    <div className="app-header">
      <Progress variant={progressVariant} current={stepId} onJump={onJump} />
      <Chain active={chainActive} completed={completed} />
    </div>
  );
}
