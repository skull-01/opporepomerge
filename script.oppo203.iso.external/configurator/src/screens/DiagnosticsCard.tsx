import { useState } from "react";
import { invoke } from "../ipc";
import { getEntries } from "../debug/log";
import { buildDiagnosticsReport, serializeDiagnostics, type DiagnosticsEnv } from "../diagnostics";
import type { SessionLogEntry } from "../session_log";
import type { WizardState } from "../state";

/**
 * Dashboard card: export a sanitized support bundle (app version + OS + recent activity log +
 * session history + the wizard configuration, with secret-bearing fields redacted) to a file the
 * user can attach to a bug report, plus copy-to-clipboard. The redaction happens in the pure
 * builder (diagnostics.ts) so a PSK/token/password never reaches the file or the clipboard.
 */
export function DiagnosticsCard({
  state,
  sessionHistory,
}: {
  state: WizardState;
  sessionHistory: SessionLogEntry[];
}) {
  const [busy, setBusy] = useState(false);
  const [savedPath, setSavedPath] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [json, setJson] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function exportNow() {
    setBusy(true);
    setErr(null);
    setCopied(false);
    setSavedPath(null);
    try {
      const env = await invoke<DiagnosticsEnv>("diagnostics_env");
      const report = buildDiagnosticsReport({ env, state, entries: getEntries(), sessionHistory });
      const text = serializeDiagnostics(report);
      setJson(text);
      setSavedPath(await invoke<string>("write_diagnostics", { contents: text }));
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function copyJson() {
    if (!json) return;
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
    } catch (e) {
      setErr(`Couldn't copy to clipboard: ${String(e)}`);
    }
  }

  return (
    <section className="card" style={{ marginTop: 16 }}>
      <h3 style={{ marginTop: 0 }}>Diagnostics export</h3>
      <p style={{ marginTop: 0 }}>
        Save a sanitized snapshot — app version, OS, the recent activity log, session history, and
        your configuration with <strong>secrets redacted</strong> (PSK / token / password) — to
        attach to a bug report.
      </p>
      <div className="row" style={{ gap: 10, alignItems: "center" }}>
        <button className="btn" onClick={exportNow} disabled={busy}>
          {busy ? "Exporting…" : "Export diagnostics"}
        </button>
        {json && (
          <button className="btn outline" onClick={copyJson} disabled={busy}>
            {copied ? "Copied ✓" : "Copy to clipboard"}
          </button>
        )}
      </div>
      {savedPath && (
        <p style={{ marginBottom: 0, color: "#1e7d34" }} role="status">
          Saved to {savedPath} — secrets redacted; review before sharing.
        </p>
      )}
      {err && (
        <p style={{ marginBottom: 0, color: "#b3261e" }} role="status">
          {err}
        </p>
      )}
    </section>
  );
}
