import { invoke } from "./ipc";
import { fileReadPlan } from "./dashboard_status";
import { ADDON_DATA_SETTINGS_REL, parseSettingsXml } from "./settings_xml";
import { diffSettings, sanitizeSettings, type SettingsDiff } from "./settings_diff";
import { readDashboardJson, writeDashboardJson } from "./dashboard_store";
import type { AddonSettings } from "./mapping";
import type { WizardState } from "./state";

/** File (under the dashboard appdata dir) holding the last sanitized settings snapshot. */
const SNAPSHOT_FILE = "settings-snapshot.json";

/** A persisted, already-sanitized settings snapshot plus when it was taken. */
export type SettingsSnapshot = { takenAt: string; settings: AddonSettings };

export type SnapshotResult =
  | { ok: false; note: string }
  | { ok: true; baseline: true; count: number }
  | { ok: true; baseline: false; diff: SettingsDiff; prevTakenAt: string };

/**
 * Read the box's current settings.xml over the configured tier, sanitize it, diff it against the
 * previously stored snapshot, then persist the new (sanitized) snapshot. The first capture has no
 * baseline to diff and is reported as `baseline`. Thin executor over fileReadPlan + parseSettingsXml
 * + diffSettings + the dashboard store; never throws (transport / parse errors become a note).
 * `nowIso` is injected so the orchestration stays deterministic for the caller.
 */
export async function captureSettingsSnapshot(
  state: WizardState,
  nowIso: string,
): Promise<SnapshotResult> {
  const plan = fileReadPlan(state, ADDON_DATA_SETTINGS_REL);
  if (!plan.supported) return { ok: false, note: plan.note };

  let settings: AddonSettings;
  try {
    const raw = await invoke<string | null>(plan.command, plan.args);
    if (raw == null) return { ok: false, note: "No settings.xml on the box yet." };
    settings = sanitizeSettings(parseSettingsXml(raw));
  } catch (e) {
    return { ok: false, note: `Could not read settings: ${String(e)}` };
  }

  const prior = await readDashboardJson<SettingsSnapshot>(SNAPSHOT_FILE);
  try {
    await writeDashboardJson(SNAPSHOT_FILE, { takenAt: nowIso, settings });
  } catch {
    // best-effort: a failed persist still lets us show the diff we just computed
  }
  if (!prior) return { ok: true, baseline: true, count: Object.keys(settings).length };
  return {
    ok: true,
    baseline: false,
    diff: diffSettings(prior.settings, settings),
    prevTakenAt: prior.takenAt,
  };
}
