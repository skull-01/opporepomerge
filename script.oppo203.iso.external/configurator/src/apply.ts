import { invoke } from "./ipc";
import {
  addonsDirForPlatform,
  buildTransferFiles,
  kodiTargetForPlatform,
  parseDiscFolders,
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

/** The Kodi addons directory inside an SMB share (sibling of the userdata folder). */
export function smbAddonsPath(sharePath: string): string {
  return smbUserdataPath(sharePath).replace(/userdata$/, "addons");
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
  const discFolders = parseDiscFolders(state.oppoDiscFolders);
  return {
    ...buildTransferFiles(target, true, discFolders),
    "playercorefactory.xml": mergePlayercorefactory(existingPcf, target, true, discFolders),
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

export type InstallResult = { ok: boolean; detail: string };

/**
 * Install the bundled add-on into Kodi's addons/ directory via the chosen tier (the config write
 * still goes through applyToKodi). Tier A installs over SSH (+restart); B extracts into the
 * SMB/local addons dir; C points at the bundled ZIP for a manual "Install from zip file". The
 * on-box install is software-verified only -- not hardware-tested.
 */
export async function installAddonToKodi(state: WizardState): Promise<InstallResult> {
  try {
    const platform: KodiPlatform = state.kodiPlatform ?? "coreelec";
    if (state.tier === "A") {
      const report = await invoke<{ version: string; target: string }>("install_addon", {
        tier: "A",
        host: state.kodiIp,
        user: state.sshUser,
        addonsPath: addonsDirForPlatform(platform),
        restart: true,
      });
      // D-3: enable via JSON-RPC; fall back to a manual restart message if that doesn't take.
      let note: string;
      try {
        const enabled = await invoke<boolean>("kodi_set_addon_enabled", {
          host: state.kodiIp,
          user: state.sshUser,
        });
        note = enabled
          ? " Enabled it via Kodi."
          : " Couldn't auto-enable — enable it in Kodi → Add-ons, or restart Kodi.";
      } catch {
        note = " Couldn't auto-enable — restart Kodi (or enable it in Add-ons) manually.";
      }
      return {
        ok: true,
        detail: `Installed add-on ${report.version} to ${report.target} over SSH (Kodi restarted).${note}`,
      };
    }
    if (state.tier === "B") {
      const report = await invoke<{ version: string; files: number; target: string }>(
        "install_addon",
        { tier: "B", addonsPath: smbAddonsPath(state.smbSharePath), restart: false },
      );
      return {
        ok: true,
        detail: `Installed add-on ${report.version} (${report.files} files) to ${report.target}. Restart Kodi to load it.`,
      };
    }
    const info = await invoke<{ version: string; path: string }>("bundled_addon_info");
    return {
      ok: true,
      detail: `Manual install: add-on ${info.version} is bundled at ${info.path} — install it in Kodi via "Install from zip file".`,
    };
  } catch (e) {
    return { ok: false, detail: String(e) };
  }
}
