import { invoke } from "./ipc";
import { userdataDirForPlatform } from "./generate";
import { smbUserdataPath } from "./apply";
import { ADDON_DATA_STATUS_REL, parseOppoStatus, type OppoSessionStatus } from "./oppo_status";
import type { WizardState } from "./state";

/**
 * How to fetch the add-on status file for the configured deploy tier. Pure so the routing is
 * unit-testable without a live Tauri backend:
 *   A (SSH) -> read_ssh_file over SSH, B (SMB) -> read_userdata_file from the share.
 *   C / unset (manual) -> unsupported: there is no remote link to the box.
 */
export type StatusReadPlan =
  | { supported: false; note: string }
  | {
      supported: true;
      command: "read_ssh_file" | "read_userdata_file";
      args: Record<string, unknown>;
    };

export function statusReadPlan(state: WizardState): StatusReadPlan {
  if (state.tier === "A") {
    return {
      supported: true,
      command: "read_ssh_file",
      args: {
        host: state.kodiIp,
        user: state.sshUser,
        userdataPath: userdataDirForPlatform(state.kodiPlatform ?? "coreelec"),
        rel: ADDON_DATA_STATUS_REL,
      },
    };
  }
  if (state.tier === "B") {
    return {
      supported: true,
      command: "read_userdata_file",
      args: { userdataPath: smbUserdataPath(state.smbSharePath), rel: ADDON_DATA_STATUS_REL },
    };
  }
  return {
    supported: false,
    note: "Manual mode - no live link to the box. Use SSH (tier A) or SMB (tier B) to read session status.",
  };
}

export type StatusReadResult = {
  // false only when the tier has no remote link (manual). true means we attempted a read.
  supported: boolean;
  // null when absent, unreadable, or unsupported.
  status: OppoSessionStatus | null;
  // a human note: the manual-mode explanation, "no session yet", or a read error.
  note: string | null;
};

/**
 * Read and parse the add-on's session status for the configured tier. Reuses the same file-read
 * commands as applyToKodi; never throws (a transport error becomes a note). Thin executor over
 * statusReadPlan + parseOppoStatus - not unit-tested directly (matches applyToKodi).
 */
export async function readOppoStatus(state: WizardState): Promise<StatusReadResult> {
  const plan = statusReadPlan(state);
  if (!plan.supported) return { supported: false, status: null, note: plan.note };
  try {
    const raw = await invoke<string | null>(plan.command, plan.args);
    return {
      supported: true,
      status: parseOppoStatus(raw),
      note: raw == null ? "No session recorded yet." : null,
    };
  } catch (e) {
    return { supported: true, status: null, note: `Could not read status: ${String(e)}` };
  }
}
