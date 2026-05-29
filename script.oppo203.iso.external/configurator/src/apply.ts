import { invoke } from "@tauri-apps/api/core";
import {
  KEYMAP_FILENAME,
  buildKeymapXml,
  kodiTargetForPlatform,
  userdataDirForPlatform,
  type KodiPlatform,
} from "./generate";
import { wizardStateToAddonSettings } from "./mapping";
import { mergePlayercorefactory } from "./merge";
import { ADDON_DATA_SETTINGS_REL, serializeSettingsXml } from "./settings_xml";
import type { WizardState } from "./state";

export type ApplyResult = { ok: boolean; detail: string };

type DeployReport = { written: string[]; backed_up: string[] };

/**
 * Build the full set of files to deploy, keyed by path relative to Kodi userdata/. Merges the
 * existing playercorefactory.xml when one is provided. Pure — unit-testable.
 */
export function buildApplyFileSet(
  state: WizardState,
  existingPcf: string | null,
): Record<string, string> {
  const platform: KodiPlatform = state.kodiPlatform ?? "coreelec";
  const target = kodiTargetForPlatform(platform, state.pythonPath);
  return {
    "playercorefactory.xml": mergePlayercorefactory(existingPcf, target),
    [`keymaps/${KEYMAP_FILENAME}`]: buildKeymapXml(),
    [ADDON_DATA_SETTINGS_REL]: serializeSettingsXml(wizardStateToAddonSettings(state)),
  };
}

/**
 * Apply the configuration to Kodi via the chosen tier:
 *  - A (SSH): write over SSH and restart Kodi (remote backup of any existing file).
 *  - B (SMB): read + merge the existing playercorefactory, then write to the userdata share.
 *  - C / unset: generate the files locally for the user to copy.
 */
export async function applyToKodi(state: WizardState): Promise<ApplyResult> {
  try {
    if (state.tier === "A") {
      const userdata = userdataDirForPlatform(state.kodiPlatform ?? "coreelec");
      // A remote read-back over SSH is not implemented; deploy_ssh backs up any existing file
      // remotely before writing, so the user's original is preserved.
      const report = await invoke<DeployReport>("deploy_ssh", {
        host: state.kodiIp,
        user: state.sshUser,
        userdataPath: userdata,
        files: buildApplyFileSet(state, null),
        restart: true,
      });
      return { ok: true, detail: `Wrote ${report.written.length} files over SSH and restarted Kodi.` };
    }

    if (state.tier === "B") {
      const userdata = state.smbSharePath.replace(/[\\/]+$/, "") + "\\userdata";
      const existing = await invoke<string | null>("read_userdata_file", {
        userdataPath: userdata,
        rel: "playercorefactory.xml",
      });
      const report = await invoke<DeployReport>("deploy_to_userdata", {
        userdataPath: userdata,
        files: buildApplyFileSet(state, existing ?? null),
      });
      return {
        ok: true,
        detail: `Wrote ${report.written.length} files to the share. Restart Kodi to load them.`,
      };
    }

    const dir = await invoke<string>("generate_files", { files: buildApplyFileSet(state, null) });
    return { ok: true, detail: `Files generated at ${dir} — copy them into your Kodi userdata folder.` };
  } catch (e) {
    return { ok: false, detail: String(e) };
  }
}
