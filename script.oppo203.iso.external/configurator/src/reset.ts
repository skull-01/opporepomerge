import { invoke } from "./ipc";
import { addonsDirForPlatform, userdataDirForPlatform, type KodiPlatform } from "./generate";
import { smbAddonsPath, smbUserdataPath } from "./apply";
import type { WizardState } from "./state";

export type ResetStepStatus = "pending" | "running" | "done" | "failed";

/** One line in the live progress list the card renders so the user sees what the reset is doing. */
export type ResetStep = { key: "box" | "local"; label: string; status: ResetStepStatus; detail?: string };

export type ResetResult = {
  /** The local reset (return-to-first-run) succeeded — this is what makes "start over" possible. */
  ok: boolean;
  /** A box reset was attempted and failed (e.g. unreachable); the local reset still ran. */
  boxFailed: boolean;
  detail: string;
  removed: string[];
  steps: ResetStep[];
};

export type BoxResetCommand = { command: string; args: Record<string, unknown> };

/**
 * The on-box delete to run for the tier the user deployed with, or null when nothing was copied
 * to a box (tier C / unset = manual install). Pure, so the per-tier routing is unit-testable.
 *  - A (SSH): reset_box_ssh against the platform's userdata/addons dirs (+ Kodi restart).
 *  - B (SMB/local): reset_box_userdata against the share's userdata/addons dirs.
 * The Rust side deletes only the four configurator-owned paths under those dirs, never the root.
 */
export function boxResetCommand(state: WizardState): BoxResetCommand | null {
  if (state.tier === "A") {
    const platform: KodiPlatform = state.kodiPlatform ?? "coreelec";
    return {
      command: "reset_box_ssh",
      args: {
        host: state.kodiIp,
        user: state.sshUser,
        userdataPath: userdataDirForPlatform(platform),
        addonsPath: addonsDirForPlatform(platform),
        restart: true,
      },
    };
  }
  if (state.tier === "B") {
    return {
      command: "reset_box_userdata",
      args: {
        userdataPath: smbUserdataPath(state.smbSharePath),
        addonsPath: smbAddonsPath(state.smbSharePath),
      },
    };
  }
  return null;
}

/**
 * The ordered, labeled steps a reset will run for the given tier: an optional box step (tier A/B)
 * then the always-present local step. Pure, so the card can render the plan before anything runs
 * and the per-tier shape is unit-tested.
 */
export function resetStepPlan(state: WizardState): ResetStep[] {
  const steps: ResetStep[] = [];
  if (boxResetCommand(state)) {
    const label =
      state.tier === "A"
        ? "Reset the Kodi box over SSH — remove the add-on + config, restart Kodi"
        : "Reset the Kodi share — remove the add-on + config files";
    steps.push({ key: "box", label, status: "pending" });
  }
  steps.push({
    key: "local",
    label: "Clear this configurator's state — return to first run",
    status: "pending",
  });
  return steps;
}

/** The closing summary, given whether the box step failed and whether the local reset succeeded. */
function resetDetail(state: WizardState, boxFailed: boolean, localOk: boolean): string {
  if (!localOk) {
    return "Couldn't clear the local configurator state — nothing was reset. See the steps above for what failed.";
  }
  if (boxFailed) {
    return "Couldn't reach the Kodi box, so its files were left untouched — but this configurator has been reset to first run. Run the reset again once the box is reachable to remove the add-on from it.";
  }
  const boxNote =
    state.tier === "A"
      ? "Removed the add-on and config from the Kodi box over SSH and restarted Kodi."
      : state.tier === "B"
        ? "Removed the add-on and config from the Kodi share — restart Kodi to drop it from memory."
        : "No files were copied to a box (manual install); cleared the local configurator state.";
  return `${boxNote} The configurator has been reset to first run.`;
}

/**
 * Reset everything: delete the add-on + the files the configurator copied to the Kodi box (via
 * whichever tier deployed them), then clear the configurator's own persisted state (wizard
 * session, dashboard memory, generated files) so it returns to first-run.
 *
 * The box and local resets run as SEPARATE stages: a box failure (e.g. an unreachable device, which
 * the Rust side now fails fast on) no longer aborts the local reset, so "start over" always works.
 * `onProgress` is called with a fresh copy of the step list on every transition so the caller can
 * show a live progress view. The caller resets the in-memory wizard state + navigates to the first
 * screen when `ok` (the local reset succeeded).
 */
export async function resetEverything(
  state: WizardState,
  onProgress?: (steps: ResetStep[]) => void,
): Promise<ResetResult> {
  const steps = resetStepPlan(state);
  const removed: string[] = [];
  const emit = () => onProgress?.(steps.map((s) => ({ ...s })));
  const setStep = (key: ResetStep["key"], status: ResetStepStatus, detail?: string) => {
    const s = steps.find((x) => x.key === key);
    if (s) {
      s.status = status;
      if (detail !== undefined) s.detail = detail;
    }
    emit();
  };

  emit();

  let boxFailed = false;
  const box = boxResetCommand(state);
  if (box) {
    setStep("box", "running");
    try {
      removed.push(...(await invoke<string[]>(box.command, box.args)));
      setStep("box", "done");
    } catch (e) {
      boxFailed = true;
      setStep("box", "failed", String(e));
    }
  }

  setStep("local", "running");
  let localOk = false;
  try {
    removed.push(...(await invoke<string[]>("reset_app_data", {})));
    setStep("local", "done");
    localOk = true;
  } catch (e) {
    setStep("local", "failed", String(e));
  }

  return { ok: localOk, boxFailed, detail: resetDetail(state, boxFailed, localOk), removed, steps };
}
