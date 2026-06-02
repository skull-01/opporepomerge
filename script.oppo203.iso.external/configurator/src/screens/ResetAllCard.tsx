import { useEffect, useRef, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { resetEverything, resetStepPlan, type ResetStep } from "../reset";
import { INITIAL_STATE } from "../state";
import type { ScreenProps } from "./types";

const DANGER = "#b3261e";

/** A `reset-progress` event from the Rust side: the granular thing the box reset is doing now. */
type ResetProgressEvent = { step: string; label: string; status: string; detail: string | null };

function stepGlyph(status: ResetStep["status"]): string {
  if (status === "done") return "✓";
  if (status === "failed") return "✗";
  if (status === "running") return "▶";
  return "○";
}

function stepColor(status: ResetStep["status"]): string {
  if (status === "done") return "#1e7d34";
  if (status === "failed") return DANGER;
  if (status === "running") return "#1a73e8";
  return "#9aa0a6";
}

/**
 * Danger-zone card: a confirm-gated "Reset all configurations" action. On confirm it deletes the
 * add-on + every file the configurator copied to the Kodi box (via the deployed tier), clears the
 * configurator's own persisted state, then resets the in-memory wizard to first-run and returns
 * to the first screen. The box and local resets run as separate stages and stream a live step
 * list (plus the granular `reset-progress` line from Rust) so the user sees what is happening; an
 * unreachable box now fails fast and still lets the local reset complete.
 */
export function ResetAllCard({ go, state, set }: ScreenProps) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [ok, setOk] = useState(false);
  const [steps, setSteps] = useState<ResetStep[]>([]);
  const [live, setLive] = useState<string | null>(null);
  // Only react to reset-progress events while our own reset is in flight (the event is global).
  const busyRef = useRef(false);

  useEffect(() => {
    let alive = true;
    let unlisten: (() => void) | undefined;
    void listen<ResetProgressEvent>("reset-progress", (e) => {
      if (busyRef.current) setLive(e.payload.label);
    })
      .then((u) => {
        if (alive) unlisten = u;
        else u();
      })
      .catch(() => {});
    return () => {
      alive = false;
      if (unlisten) unlisten();
    };
  }, []);

  async function run() {
    setBusy(true);
    busyRef.current = true;
    setMessage(null);
    setLive(null);
    setSteps(resetStepPlan(state));
    const result = await resetEverything(state, setSteps);
    busyRef.current = false;
    setLive(null);
    setOk(result.ok);
    setMessage(result.detail);
    setBusy(false);
    if (result.ok) {
      set(INITIAL_STATE);
      setTimeout(() => go("step0_gate"), 1800);
    }
  }

  return (
    <section className="card" style={{ borderColor: DANGER, marginTop: 16 }}>
      <h3 style={{ color: DANGER, marginTop: 0 }}>Danger zone — reset all configurations</h3>
      <p style={{ marginTop: 0 }}>
        Deletes the add-on <strong>and every file the configurator copied to the Kodi box</strong>{" "}
        (playercorefactory.xml, the remote-bridge keymap, and the add-on's settings/data), then
        resets this configurator to first-run. This cannot be undone.
      </p>
      {!confirming ? (
        <button
          className="btn"
          style={{ background: DANGER, color: "#fff" }}
          onClick={() => {
            setMessage(null);
            setSteps([]);
            setConfirming(true);
          }}
          disabled={busy}
        >
          Reset all configurations…
        </button>
      ) : (
        <div className="row" style={{ gap: 10, alignItems: "center" }}>
          <button
            className="btn"
            style={{ background: DANGER, color: "#fff" }}
            onClick={run}
            disabled={busy}
          >
            {busy ? "Resetting…" : "Yes — delete everything & start over"}
          </button>
          <button className="btn outline" onClick={() => setConfirming(false)} disabled={busy}>
            Cancel
          </button>
        </div>
      )}
      {steps.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0, margin: "14px 0 0" }} aria-label="Reset progress">
          {steps.map((s) => (
            <li key={s.key} style={{ display: "flex", gap: 8, alignItems: "baseline", padding: "3px 0" }}>
              <span aria-hidden style={{ width: 16, flex: "0 0 16px", color: stepColor(s.status) }}>
                {stepGlyph(s.status)}
              </span>
              <span style={{ color: s.status === "pending" ? "#5f6368" : undefined }}>
                {s.label}
                {s.key === "box" && s.status === "running" && live && (
                  <span style={{ color: "#5f6368" }}> — {live}</span>
                )}
                {s.status === "failed" && s.detail && (
                  <span style={{ color: DANGER }}> — {s.detail}</span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}
      {message && (
        <p style={{ marginBottom: 0, color: ok ? "#1e7d34" : DANGER }} role="status">
          {message}
        </p>
      )}
    </section>
  );
}
