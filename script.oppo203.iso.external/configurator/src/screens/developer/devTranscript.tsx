import { useRef, useState } from "react";
import { invoke } from "../../ipc";

// Shared live-transcript model + UI for the Developer Options device consoles (TV / AVR / NAS).
// The OPPO console predates this and keeps its own copy; everything else reuses these.

export type TranscriptDir = "tx" | "rx" | "info" | "err";
export type TranscriptLine = { id: number; dir: TranscriptDir; text: string };

const DIR_PREFIX: Record<TranscriptDir, string> = { tx: "▶ ", rx: "◀ ", info: "• ", err: "✗ " };

/** Append lines, capping total length so a long session can't grow unbounded (keeps the newest). */
export function appendTranscript(
  lines: TranscriptLine[],
  add: TranscriptLine[],
  cap = 300
): TranscriptLine[] {
  const next = [...lines, ...add];
  return next.length > cap ? next.slice(next.length - cap) : next;
}

export type TranscriptApi = {
  lines: TranscriptLine[];
  push: (...entries: Array<{ dir: TranscriptDir; text: string }>) => void;
  clear: () => void;
};

export function useTranscript(): TranscriptApi {
  const [lines, setLines] = useState<TranscriptLine[]>([]);
  const idRef = useRef(0);
  const push = (...entries: Array<{ dir: TranscriptDir; text: string }>) => {
    const withIds = entries.map((e) => ({ id: idRef.current++, ...e }));
    setLines((cur) => appendTranscript(cur, withIds));
  };
  const clear = () => setLines([]);
  return { lines, push, clear };
}

/**
 * Fire a Tauri command, logging the request line and then the reply (or error) into the transcript.
 * Object replies are JSON-stringified. Errors are caught and shown — the console never throws at the
 * user. All device I/O behind these commands is best-effort and hardware-pending.
 */
export async function runAndLog(
  api: TranscriptApi,
  txText: string,
  command: string,
  args?: Record<string, unknown>
): Promise<void> {
  api.push({ dir: "tx", text: txText });
  try {
    const r = await invoke<unknown>(command, args);
    api.push({ dir: "rx", text: typeof r === "string" ? r || "(no reply)" : JSON.stringify(r) });
  } catch (e) {
    api.push({ dir: "err", text: String(e) });
  }
}

export function Transcript({
  api,
  title = "Live transcript",
  note,
}: {
  api: TranscriptApi;
  title?: string;
  note?: string;
}) {
  return (
    <section className="card">
      <div className="row-between" style={{ marginBottom: 10 }}>
        <h3 style={{ margin: 0 }}>{title}</h3>
        <button className="btn ghost sm" onClick={api.clear} disabled={!api.lines.length}>
          Clear
        </button>
      </div>
      {note && (
        <div className="callout info" style={{ marginBottom: 10 }}>
          <span className="callout-icon">i</span>
          <div className="callout-body">{note}</div>
        </div>
      )}
      <div className="dev-transcript" role="log">
        {api.lines.length === 0 ? (
          <div className="dev-tline dev-info">No activity yet.</div>
        ) : (
          api.lines.map((l) => (
            <div key={l.id} className={`dev-tline dev-${l.dir}`}>
              {DIR_PREFIX[l.dir]}
              {l.text}
            </div>
          ))
        )}
      </div>
    </section>
  );
}
