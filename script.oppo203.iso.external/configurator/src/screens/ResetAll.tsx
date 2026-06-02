import { ResetAllCard } from "./ResetAllCard";
import type { ScreenProps } from "./types";

/**
 * Hosts the danger-zone reset card on its own screen so it is reachable from persistent
 * entry points (the app header and the Step-0 gate), independent of the dashboard — which
 * is only reachable after a completed setup. The card and the reset action are unchanged.
 */
export function ResetAllScreen({ go, state, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Reset all configurations</h1>
        <p className="screen-subtitle">
          Start over from scratch — remove the add-on and everything this configurator
          deployed, and return this wizard to its first screen.
        </p>
      </div>
      <ResetAllCard go={go} state={state} set={set} />
      <div className="footer-nav">
        {/* Back returns to the first screen: reset is a start-over action and its target
            user is at or near first-run; the stepper still reflects completed steps. */}
        <button className="btn ghost" onClick={() => go("step0_gate")}>
          ← Back
        </button>
      </div>
    </div>
  );
}
