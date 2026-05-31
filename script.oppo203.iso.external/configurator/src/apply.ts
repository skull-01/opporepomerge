import { invoke } from "./ipc";
import {
  buildTransferFiles,
  kodiTargetForPlatform,
  userdataDirForPlatform,
  type KodiPlatform,
} from "./generate";
import { wizardStateToAddonSettings } from "./mapping";
import { mergePlayercorefactory } from "./merge";
import { ADDON_DATA_SETTINGS_REL, mergeSettingsXml } from "./settings_xml";
import type { WizardState } from "./state";

export type ApplyResult = { ok: boolean; detail: string };

type DeployReport = { written: string[]; backed_up: string[] };

/**
 * The Kodi userdata directory inside an SMB share. The share is expected to contain the
 * userdata folder (see the Step 1 SMB hint), so the test-write and the deploy must target the
 * same composed path — exported and used by both.
 */
export function smbUserdataPath(sharePath: string): string {
  return sharePath.replace(/[\\/]+$/, "") + "\\userdata";
}

/**
 * Build the full set of files to deploy, keyed by path relative to Kodi userdata/. Merges into
 * any existing playercorefactory.xml / settings.xml so user content is never blind-overwritten.
 * Builds on buildTransferFiles so the box-level files have a single source of truth. Pure.
 */
export function buildApplyFileSet(
  state: WizardState,
  existingPcf: string | null,
  existingSettings: string | null = null,
): Record<string, string> {
  const platform: KodiPlatform = state.kodiPlatform ?? "coreelec";
  const target = kodiTargetForPlatform(platform, state.pythonPath);
  return {
    ...buildTransferFiles(target),
    "playercorefactory.xml": mergePlayercorefactory(existingPcf, target),
    [ADDON_DATA_SETTINGS_REL]: mergeSettingsXml(existingSettings, wizardStateToAddonSettings(state)),
  };
}

/**
 * Apply the configuration to Kodi via the chosen tier. Every tier reads back any existing
 * playercorefactory.xml + settings.xml first and merges into them (never blind-overwrites):
 *  - A (SSH): read back + merge over SSH, write, and restart Kodi (remote backup first).
 *  - B (SMB): read back + merge from the userdata share, then write (you restart Kodi).
 *  - C / unset: generate the files locally for the user to copy.
 */
export async function applyToKodi(state: WizardState): Promise<ApplyResult> {
  try {
    if (state.tier === "A") {
      const userdata = userdataDirForPlatform(state.kodiPlatform ?? "coreelec");
      const existingPcf = await invoke<string | null>("read_ssh_file", {
        host: state.kodiIp,
        user: state.sshUser,
        userdataPath: userdata,
        rel: "playercorefactory.xml",
      });
      const existingSettings = await invoke<string | null>("read_ssh_file", {
        host: state.kodiIp,
        user: state.sshUser,
        userdataPath: userdata,
        rel: ADDON_DATA_SETTINGS_REL,
      });
      const report = await invoke<DeployReport>("deploy_ssh", {
        host: state.kodiIp,
        user: state.sshUser,
        userdataPath: userdata,
        files: buildApplyFileSet(state, existingPcf, existingSettings),
        restart: true,
      });
      return { ok: true, detail: `Wrote ${report.written.length} files over SSH and restarted Kodi.` };
    }

    if (state.tier === "B") {
      const userdata = smbUserdataPath(state.smbSharePath);
      const existingPcf = await invoke<string | null>("read_userdata_file", {
        userdataPath: userdata,
        rel: "playercorefactory.xml",
      });
      const existingSettings = await invoke<string | null>("read_userdata_file", {
        userdataPath: userdata,
        rel: ADDON_DATA_SETTINGS_REL,
      });
      const report = await invoke<DeployReport>("deploy_to_userdata", {
        userdataPath: userdata,
        files: buildApplyFileSet(state, existingPcf, existingSettings),
      });
      return {
        ok: true,
        detail: `Wrote ${report.written.length} files to the share. Restart Kodi to load them.`,
      };
    }

    const dir = await invoke<string>("generate_files", {
      files: buildApplyFileSet(state, null, null),
    });
    return { ok: true, detail: `Files generated at ${dir} — copy them into your Kodi userdata folder.` };
  } catch (e) {
    return { ok: false, detail: String(e) };
  }
}
