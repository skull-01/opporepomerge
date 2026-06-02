import { invoke } from "./ipc";
import { addonsDirForPlatform, userdataDirForPlatform, type KodiPlatform } from "./generate";
import { smbAddonsPath, smbUserdataPath } from "./apply";
import type { WizardState } from "./state";

export type ResetResult = { ok: boolean; detail: string; removed: string[] };

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
 * Reset everything: delete the add-on + the files the configurator copied to the Kodi box (via
 * whichever tier deployed them), then clear the configurator's own persisted state (wizard
 * session, dashboard memory, generated files) so it returns to first-run. The caller resets the
 * in-memory wizard state + navigates to the first screen on success.
 */
export async function resetEverything(state: WizardState): Promise<ResetResult> {
  const removed: string[] = [];
  try {
    const box = boxResetCommand(state);
    if (box) {
      removed.push(...(await invoke<string[]>(box.command, box.args)));
    }
    removed.push(...(await invoke<string[]>("reset_app_data", {})));
    const boxNote =
      state.tier === "A"
        ? "Removed the add-on and config from the Kodi box over SSH and restarted Kodi."
        : state.tier === "B"
          ? "Removed the add-on and config from the Kodi share — restart Kodi to drop it from memory."
          : "No files were copied to a box (manual install); cleared the local configurator state.";
    return { ok: true, detail: `${boxNote} The configurator has been reset to first run.`, removed };
  } catch (e) {
    return { ok: false, detail: String(e), removed };
  }
}
