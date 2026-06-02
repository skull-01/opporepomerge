import { redact, type DebugEntry } from "./debug/log";
import type { SessionLogEntry } from "./session_log";
import type { WizardState } from "./state";

/** Host OS/arch + the configurator's own version (from the Rust `diagnostics_env` command). */
export type DiagnosticsEnv = { os: string; arch: string; configurator_version: string };

export type DiagnosticsReport = {
  note: string;
  env: DiagnosticsEnv;
  wizard: unknown;
  debugLog: { count: number; entries: unknown };
  sessionHistory: unknown;
};

const NOTE =
  "OppoKodiAddon Configurator diagnostics export. Secret-bearing fields (PSK / token / " +
  "password / secret / credential) are redacted. Review before sharing.";

/**
 * Assemble a support bundle from the configurator's in-memory state, deep-redacting every
 * secret-bearing field through the shared debug redactor so a Sony PSK / SmartThings token /
 * password can never reach the exported file or the clipboard. Pure — the caller passes the
 * data in — so the redaction is unit-tested without Tauri.
 */
export function buildDiagnosticsReport(input: {
  env: DiagnosticsEnv;
  state: WizardState;
  entries: readonly DebugEntry[];
  sessionHistory?: readonly SessionLogEntry[];
}): DiagnosticsReport {
  const raw = {
    note: NOTE,
    env: input.env,
    wizard: input.state,
    debugLog: { count: input.entries.length, entries: input.entries },
    sessionHistory: input.sessionHistory ?? [],
  };
  return redact(raw) as DiagnosticsReport;
}

/** Pretty-print the report as the JSON written to the export file / copied to the clipboard. */
export function serializeDiagnostics(report: DiagnosticsReport): string {
  return JSON.stringify(report, null, 2);
}
