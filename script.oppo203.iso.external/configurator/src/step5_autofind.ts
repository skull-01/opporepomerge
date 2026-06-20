import type { WizardState } from "./state";
import { planSwitch, type SwitchCommandPlan } from "./step5_switch";
import { isAvrChain } from "./steps";

/**
 * How Step 5 can auto-find an HDMI input for the current chain/backend:
 *   "sweep"  - the backend can drive discrete HDMI inputs (Roku ECP / ADB), so the configurator
 *              switches to each input in turn and the user says when the OPPO appears — a real,
 *              driven detection that resolves an actual HDMI number.
 *   "manual" - no backend can drive discrete inputs here (SmartThings / LG / Samsung / custom /
 *              Sony, the AVR chain, or no TV IP), so the only honest path is manual entry.
 * No TV/AVR control protocol reports the active input number, so there is no passive read — the
 * sweep is the strongest automation available, and it still needs the user's eyes to confirm.
 */
export type AutoFindMethod = "sweep" | "manual";

/** The discrete HDMI inputs a driven sweep walks, in order. */
export const SWEEP_INPUTS = [1, 2, 3, 4] as const;

/**
 * Whether a driven sweep is possible: TV chain only (the AVR receiver input is a named string set
 * in Step 6, not a 1..4 sweep) on a backend whose switch is a confirmable command for HDMI 1 — i.e.
 * Roku ECP or ADB with a TV IP. Everything else returns "manual".
 */
export function autoFindMethod(state: WizardState): AutoFindMethod {
  if (isAvrChain(state.topology)) return "manual";
  if (state.tvBackend !== "roku_ecp" && state.tvBackend !== "adb") return "manual";
  return planSwitch(state, "oppo", SWEEP_INPUTS[0]).disposition === "command" ? "sweep" : "manual";
}

/**
 * The switch command for one rung of the sweep (target the OPPO at HDMI `hdmi`), or null when the
 * current state cannot drive that input as a command. Reuses planSwitch so the sweep fires exactly
 * the same per-backend command the Test-switch action does.
 */
export function sweepCommandFor(state: WizardState, hdmi: number): SwitchCommandPlan | null {
  const plan = planSwitch(state, "oppo", hdmi);
  return plan.disposition === "command" ? plan : null;
}

/** The control ports to knock on before a sweep, so an unreachable TV fails fast and honestly. */
export function autoFindProbePorts(state: WizardState): number[] {
  if (state.tvBackend === "roku_ecp") return [8060];
  if (state.tvBackend === "adb") return [5555];
  return [];
}
