import { useState } from "react";
import { resetEverything } from "../reset";
import { INITIAL_STATE } from "../state";
import type { ScreenProps } from "./types";

const DANGER = "#b3261e";

/**
 * Danger-zone card: a confirm-gated "Reset all configurations" action. On confirm it deletes the
 * add-on + every file the configurator copied to the Kodi box (via the deployed tier), clears the
 * configurator's own persisted state, then resets the in-memory wizard to first-run and returns
 * to the first screen.
 */
export function ResetAllCard({ go, state, set }: ScreenProps) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [ok, setOk] = useState(false);

  async function run() {
    setBusy(true);
    setMessage(null);
    const result = await resetEverything(state);
    setOk(result.ok);
    setMessage(result.detail);
    setBusy(false);
    if (result.ok) {
      set(INITIAL_STATE);
      setTimeout(() => go("step0_gate"), 1500);
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
      {message && (
        <p style={{ marginBottom: 0, color: ok ? "#1e7d34" : DANGER }} role="status">
          {message}
        </p>
      )}
    </section>
  );
}
