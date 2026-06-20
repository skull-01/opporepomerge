import { useEffect, useState, useSyncExternalStore } from "react";
import type { StepId } from "../steps";
import {
  subscribe,
  getEntries,
  clearEntries,
  entriesForView,
  type DebugEntry,
} from "../debug/log";

const DEV_MODE_KEY = "oppo-debug-mode";

/**
 * Developer debug mode: off by default, toggled with Ctrl+Shift+D and remembered in
 * localStorage. Gates the whole panel so ordinary users never see internal command logs.
 */
function useDevMode(): boolean {
  const [on, setOn] = useState(() => {
    try {
      return localStorage.getItem(DEV_MODE_KEY) === "1";
    } catch {
      return false;
    }
  });
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && (e.key === "D" || e.key === "d")) {
        e.preventDefault();
        setOn((prev) => {
          const next = !prev;
          try {
            localStorage.setItem(DEV_MODE_KEY, next ? "1" : "0");
          } catch {
            /* localStorage unavailable: still toggle for this session */
          }
          return next;
        });
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  return on;
}

function statusOf(entries: DebugEntry[]): { label: string; cls: string } {
  const fails = entries.filter((e) => e.kind === "ipc" && !e.ok).length;
  if (fails > 0) return { label: `${fails} error${fails > 1 ? "s" : ""}`, cls: "fail" };
  return { label: `${entries.length} event${entries.length === 1 ? "" : "s"}`, cls: "" };
}

/**
 * Global docked developer panel. Shows every captured IPC command for the current step (toggle
 * to all steps), newest last, with redacted args + result/error on expand. Mounted once in App;
 * renders nothing unless dev mode is on.
 */
export function DebugPanel({ currentStep }: { currentStep: StepId }) {
  const on = useDevMode();
  const all = useSyncExternalStore(subscribe, getEntries, getEntries);
  const [open, setOpen] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);

  if (!on) return null;

  const view = entriesForView(all, currentStep, showAll);
  const status = statusOf(view);

  const copy = () => {
    try {
      void navigator.clipboard.writeText(JSON.stringify(view, null, 2));
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className={`debug-dock ${open ? "open" : ""}`.trim()}>
      <div className="debug-bar">
        <span className={`debug-dot ${status.cls}`.trim()} />
        <button className="debug-title" onClick={() => setOpen((v) => !v)}>
          Developer debug · {open ? "▾" : "▸"}
        </button>
        <span className="debug-count">{status.label}</span>
        <span className="spacer" />
        <button
          className={`debug-toggle ${showAll ? "on" : ""}`.trim()}
          onClick={() => setShowAll((v) => !v)}
          title="Show all steps, or just the current one"
        >
          {showAll ? "all steps" : "this step"}
        </button>
        <button className="debug-btn" onClick={copy}>
          copy
        </button>
        <button className="debug-btn" onClick={() => clearEntries()}>
          clear
        </button>
      </div>
      {open && (
        <div className="debug-list">
          {view.length === 0 && (
            <div className="debug-empty">No commands captured on this step yet.</div>
          )}
          {view.map((e) =>
            e.kind === "wire" ? (
              <div key={e.seq} className="debug-row wire">
                <button
                  className="debug-row-head"
                  onClick={() => setExpanded((cur) => (cur === e.seq ? null : e.seq))}
                >
                  <span className="debug-icon">{e.direction === "sent" ? "→" : "←"}</span>
                  <span className="debug-cmd">
                    {e.label} {e.direction}
                  </span>
                  <span className="debug-ms">{e.len} B</span>
                </button>
                {expanded === e.seq && (
                  <div className="debug-detail">
                    <div className="debug-detail-label">text</div>
                    <pre>{e.text}</pre>
                    <div className="debug-detail-label">hex</div>
                    <pre>{e.hex}</pre>
                  </div>
                )}
              </div>
            ) : (
              <div key={e.seq} className={`debug-row ${e.ok ? "" : "fail"}`.trim()}>
                <button
                  className="debug-row-head"
                  onClick={() => setExpanded((cur) => (cur === e.seq ? null : e.seq))}
                >
                  <span className={`debug-icon ${e.ok ? "pass" : "fail"}`}>{e.ok ? "✓" : "✕"}</span>
                  <span className="debug-cmd">{e.command}</span>
                  <span className="debug-ms">{Math.round(e.durationMs)} ms</span>
                </button>
                {expanded === e.seq && (
                  <div className="debug-detail">
                    <div className="debug-detail-label">args</div>
                    <pre>{JSON.stringify(e.args, null, 2)}</pre>
                    <div className="debug-detail-label">{e.ok ? "result" : "error"}</div>
                    <pre>{JSON.stringify(e.ok ? e.result : e.error, null, 2)}</pre>
                  </div>
                )}
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}
