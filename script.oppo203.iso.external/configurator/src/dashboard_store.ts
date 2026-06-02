import { invoke } from "./ipc";

/**
 * Thin wrapper over the Rust read_app_json / write_app_json commands, namespacing the dashboard's
 * persisted files under a `dashboard/` subdir of the app data dir (alongside state.json). Reads
 * are best-effort - a missing or unreadable file becomes null; writes surface their error to the
 * caller so a failed persist is not hidden.
 */
const PREFIX = "dashboard/";

export async function readDashboardJson<T>(name: string): Promise<T | null> {
  try {
    const value = await invoke<T | null>("read_app_json", { rel: PREFIX + name });
    return value ?? null;
  } catch {
    return null;
  }
}

export async function writeDashboardJson(name: string, value: unknown): Promise<void> {
  await invoke("write_app_json", { rel: PREFIX + name, value });
}
