import { isSensitiveKey } from "./debug/log";
import type { AddonSettings } from "./mapping";

/** One setting whose value changed between two snapshots. */
export type SettingChange = { id: string; from: string; to: string };

/** A structural diff of two add-on settings snapshots; ids are sorted for a stable display. */
export type SettingsDiff = {
  added: { id: string; value: string }[];
  removed: { id: string; value: string }[];
  changed: SettingChange[];
};

/** The fixed sentinel stored and shown in place of any secret-bearing setting value. */
export const MASKED = "[secret]";

/**
 * Replace the values of secret-bearing settings (Sony PSK, SmartThings token, passwords) with a
 * fixed sentinel, keeping the keys. Applied before a snapshot is persisted AND before it is
 * diffed, so a secret value never reaches disk or the screen. Because the mask is constant, a
 * secret's value change reads as no-change by design (its key add/remove still shows). The single
 * sensitivity policy lives in debug/log.ts isSensitiveKey, shared with the debug redactor.
 */
export function sanitizeSettings(settings: AddonSettings): AddonSettings {
  const out: AddonSettings = {};
  for (const [id, value] of Object.entries(settings)) {
    out[id] = isSensitiveKey(id) ? MASKED : value;
  }
  return out;
}

/**
 * Diff two flat settings maps into added / removed / changed lists (ids sorted). Pure and
 * secret-agnostic: callers sanitize first so masked secrets compare equal. A null `prev` means
 * there is no baseline yet, so everything in `curr` is reported as added.
 */
export function diffSettings(prev: AddonSettings | null, curr: AddonSettings): SettingsDiff {
  const before = prev ?? {};
  const added: { id: string; value: string }[] = [];
  const removed: { id: string; value: string }[] = [];
  const changed: SettingChange[] = [];
  for (const id of Object.keys(curr).sort()) {
    if (!(id in before)) added.push({ id, value: curr[id] });
    else if (before[id] !== curr[id]) changed.push({ id, from: before[id], to: curr[id] });
  }
  for (const id of Object.keys(before).sort()) {
    if (!(id in curr)) removed.push({ id, value: before[id] });
  }
  return { added, removed, changed };
}

/** Whether a diff carries no change at all (drives the "no changes since last snapshot" UI). */
export function diffIsEmpty(d: SettingsDiff): boolean {
  return d.added.length === 0 && d.removed.length === 0 && d.changed.length === 0;
}
