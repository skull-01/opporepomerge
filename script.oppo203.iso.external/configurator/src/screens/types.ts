import type { WizardState } from "../state";
import type { ScreenId } from "../steps";

export type ScreenProps = {
  go: (id: ScreenId) => void;
  state: WizardState;
  set: (patch: Partial<WizardState>) => void;
};
