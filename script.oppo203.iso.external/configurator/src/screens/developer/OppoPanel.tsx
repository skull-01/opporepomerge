import { useEffect, useRef, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { invoke } from "../../ipc";
import {
  OPPO_TCP_CATEGORY_LABELS,
  OPPO_TCP_COMMANDS,
  type OppoTcpCategory,
} from "../../oppo-commands/tcp-commands";
import {
  OPPO_HTTP_CATEGORY_LABELS,
  OPPO_HTTP_COMMANDS,
  type OppoHttpCategory,
} from "../../oppo-commands/http-commands";
import {
  appendTranscript,
  httpRequestLabel,
  type TranscriptDir,
  type TranscriptLine,
} from "./oppoConsole";
import type { DevPanelProps } from "./types";

// One verbose-mode push frame streamed from the Rust monitor (see lib.rs `LiveFrame`).
type LiveFrame = { seq: number; kind: string; raw: string };

const TCP_CATEGORIES = Array.from(
  new Set(OPPO_TCP_COMMANDS.map((c) => c.category))
) as OppoTcpCategory[];
const HTTP_CATEGORIES = Array.from(
  new Set(OPPO_HTTP_COMMANDS.map((c) => c.category))
) as OppoHttpCategory[];

const DIR_PREFIX: Record<TranscriptDir, string> = { tx: "▶ ", rx: "◀ ", info: "• ", err: "✗ " };

/**
 * OPPO command console: a TCP (#XXX) palette + the landed HTTP (port 436) catalog, each fired at
 * the player, with a live transcript that can be fed by either the verbose-push stream (TCP) or an
 * HTTP poll. All device I/O is best-effort and hardware-pending; credential-bearing HTTP endpoints
 * are redacted in the transcript (see oppoConsole.ts) and never persisted.
 */
export function OppoPanel({ state }: DevPanelProps) {
  const [host, setHost] = useState(state.playerIp);
  const [palette, setPalette] = useState<"tcp" | "http">("tcp");
  const [rawTcp, setRawTcp] = useState("");
  const [httpEndpoint, setHttpEndpoint] = useState("/getmovieplayinfo");
  const [httpQuery, setHttpQuery] = useState("");
  const [busy, setBusy] = useState(false);

  const [lines, setLines] = useState<TranscriptLine[]>([]);
  const idRef = useRef(0);

  const [monitorKind, setMonitorKind] = useState<"tcp" | "http">("tcp");
  const [live, setLive] = useState(false);
  const liveTokenRef = useRef<number | null>(null);
  const pollRef = useRef<number | null>(null);

  const selected = OPPO_HTTP_COMMANDS.find((c) => c.endpoint === httpEndpoint);
  const pollSeconds = Math.max(2, Number(state.oppoHttpRefreshSeconds) || 5);

  function push(...entries: Array<{ dir: TranscriptDir; text: string }>) {
    const withIds = entries.map((e) => ({ id: idRef.current++, ...e }));
    setLines((cur) => appendTranscript(cur, withIds));
  }

  // Subscribe once to the Rust verbose-push stream; append each frame while a TCP monitor runs.
  useEffect(() => {
    let alive = true;
    let unlisten: (() => void) | undefined;
    void listen<LiveFrame>("oppo-live", (e) => {
      push({ dir: "rx", text: `live: ${e.payload.raw}` });
    }).then((u) => {
      if (alive) unlisten = u;
      else u();
    });
    return () => {
      alive = false;
      if (unlisten) unlisten();
    };
  }, []);

  // Stop any live feed on unmount (restores the player's verbose mode; clears the poll timer).
  useEffect(() => {
    return () => {
      if (pollRef.current !== null) window.clearInterval(pollRef.current);
      if (liveTokenRef.current !== null) {
        void invoke("stop_oppo_live_monitor", { token: liveTokenRef.current }).catch(() => {});
      }
    };
  }, []);

  async function fireTcp(command: string) {
    const cmd = command.trim();
    if (!cmd) return;
    setBusy(true);
    push({ dir: "tx", text: cmd });
    try {
      const resp = await invoke<string>("oppo_query", { host, command: cmd, port: 23 });
      push({ dir: "rx", text: resp || "(no reply)" });
    } catch (e) {
      push({ dir: "err", text: String(e) });
    } finally {
      setBusy(false);
    }
  }

  async function fireHttp() {
    const q = httpQuery.trim();
    setBusy(true);
    push({ dir: "tx", text: httpRequestLabel(httpEndpoint, q) });
    try {
      const body = await invoke<string>("oppo_http_get", {
        host,
        endpoint: httpEndpoint,
        query: q || undefined,
      });
      push({ dir: "rx", text: body || "(empty body)" });
    } catch (e) {
      push({ dir: "err", text: String(e) });
    } finally {
      setBusy(false);
    }
  }

  async function startMonitor() {
    if (live) return;
    if (monitorKind === "tcp") {
      try {
        const token = await invoke<number>("start_oppo_live_monitor", { host, port: 23 });
        liveTokenRef.current = token;
        setLive(true);
        push({ dir: "info", text: "verbose-push monitor started (#SVM 3)" });
      } catch (e) {
        push({ dir: "err", text: `could not start verbose monitor: ${String(e)}` });
      }
    } else {
      setLive(true);
      push({ dir: "info", text: `HTTP poll started (every ${pollSeconds}s)` });
      const tick = async () => {
        try {
          const info = await invoke<string>("oppo_playback_info", { host });
          push({ dir: "rx", text: `getmovieplayinfo: ${info || "(empty)"}` });
        } catch (e) {
          push({ dir: "err", text: `getmovieplayinfo: ${String(e)}` });
        }
        try {
          const g = await invoke<string>("oppo_http_get", { host, endpoint: "/getglobalinfo" });
          push({ dir: "rx", text: `getglobalinfo: ${g || "(empty)"}` });
        } catch (e) {
          push({ dir: "err", text: `getglobalinfo: ${String(e)}` });
        }
      };
      void tick();
      pollRef.current = window.setInterval(() => void tick(), pollSeconds * 1000);
    }
  }

  async function stopMonitor() {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
    if (liveTokenRef.current !== null) {
      await invoke("stop_oppo_live_monitor", { token: liveTokenRef.current }).catch(() => {});
      liveTokenRef.current = null;
    }
    if (live) push({ dir: "info", text: "monitor stopped" });
    setLive(false);
  }

  function switchMonitorKind(kind: "tcp" | "http") {
    if (kind === monitorKind) return;
    void stopMonitor();
    setMonitorKind(kind);
  }

  return (
    <div className="stack-lg">
      <section className="card">
        <h3 style={{ marginTop: 0 }}>OPPO console</h3>
        <div className="field" style={{ maxWidth: 280 }}>
          <label className="field-label" htmlFor="dev-oppo-host">
            Player IP
          </label>
          <input
            id="dev-oppo-host"
            className="input"
            value={host}
            onChange={(e) => setHost(e.target.value)}
            spellCheck={false}
          />
          <span className="field-hint">
            TCP control on :23, HTTP app-API on :436. Defaults to the configured player.
          </span>
        </div>

        <div className="dev-tabs" role="tablist" aria-label="Command palette" style={{ marginTop: 16 }}>
          <button
            role="tab"
            aria-selected={palette === "tcp"}
            className={`dev-tab${palette === "tcp" ? " active" : ""}`}
            onClick={() => setPalette("tcp")}
          >
            TCP (#XXX)
          </button>
          <button
            role="tab"
            aria-selected={palette === "http"}
            className={`dev-tab${palette === "http" ? " active" : ""}`}
            onClick={() => setPalette("http")}
          >
            HTTP (:436)
          </button>
        </div>

        {palette === "tcp" ? (
          <div className="stack">
            {TCP_CATEGORIES.map((cat) => (
              <div key={cat}>
                <div className="field-label" style={{ marginBottom: 6 }}>
                  {OPPO_TCP_CATEGORY_LABELS[cat]}
                </div>
                <div className="filter-row">
                  {OPPO_TCP_COMMANDS.filter((c) => c.category === cat).map((c) => (
                    <button
                      key={c.command}
                      className="filter-pill"
                      title={c.command}
                      disabled={busy}
                      onClick={() => void fireTcp(c.command)}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <div className="field" style={{ marginTop: 4 }}>
              <label className="field-label" htmlFor="dev-oppo-raw">
                Raw command
              </label>
              <div className="row">
                <input
                  id="dev-oppo-raw"
                  className="input mono"
                  placeholder="#QPL"
                  value={rawTcp}
                  spellCheck={false}
                  onChange={(e) => setRawTcp(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") void fireTcp(rawTcp);
                  }}
                />
                <button className="btn" disabled={busy || !rawTcp.trim()} onClick={() => void fireTcp(rawTcp)}>
                  Send
                </button>
              </div>
              <span className="field-hint">Any documented or undocumented command, sent verbatim over TCP:23.</span>
            </div>
          </div>
        ) : (
          <div className="stack">
            <div className="field">
              <label className="field-label" htmlFor="dev-oppo-ep">
                Endpoint
              </label>
              <select
                id="dev-oppo-ep"
                className="input"
                value={httpEndpoint}
                onChange={(e) => setHttpEndpoint(e.target.value)}
              >
                {HTTP_CATEGORIES.map((cat) => (
                  <optgroup key={cat} label={OPPO_HTTP_CATEGORY_LABELS[cat]}>
                    {OPPO_HTTP_COMMANDS.filter((c) => c.category === cat).map((c) => (
                      <option key={c.endpoint} value={c.endpoint}>
                        {c.endpoint}
                        {c.control ? " ⚠" : ""}
                        {c.sensitive ? " 🔒" : ""}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
            <div className="field">
              <label className="field-label" htmlFor="dev-oppo-q">
                Query {selected?.needsParams ? "(required)" : "(optional)"}
              </label>
              <div className="row">
                <input
                  id="dev-oppo-q"
                  className="input mono"
                  placeholder="key=Up  ·  path=%2Fmnt%2Fusb"
                  value={httpQuery}
                  spellCheck={false}
                  onChange={(e) => setHttpQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") void fireHttp();
                  }}
                />
                <button className="btn" disabled={busy} onClick={() => void fireHttp()}>
                  Send GET
                </button>
              </div>
              <span className="field-hint">
                ⚠ state-changing · 🔒 credential-bearing (redacted in the log, never saved). Percent-encode
                spaces as %20.
              </span>
            </div>
          </div>
        )}
      </section>

      <section className="card">
        <div className="row-between" style={{ marginBottom: 10 }}>
          <h3 style={{ margin: 0 }}>Live transcript</h3>
          <button className="btn ghost sm" onClick={() => setLines([])} disabled={!lines.length}>
            Clear
          </button>
        </div>
        <div className="row" style={{ marginBottom: 10 }}>
          <div className="dev-tabs" role="tablist" aria-label="Monitor source" style={{ marginBottom: 0, borderBottom: "none" }}>
            <button
              role="tab"
              aria-selected={monitorKind === "tcp"}
              className={`dev-tab${monitorKind === "tcp" ? " active" : ""}`}
              onClick={() => switchMonitorKind("tcp")}
            >
              TCP push (#SVM 3)
            </button>
            <button
              role="tab"
              aria-selected={monitorKind === "http"}
              className={`dev-tab${monitorKind === "http" ? " active" : ""}`}
              onClick={() => switchMonitorKind("http")}
            >
              HTTP poll
            </button>
          </div>
          <span className="spacer" />
          {live ? (
            <button className="btn danger" onClick={() => void stopMonitor()}>
              Stop
            </button>
          ) : (
            <button className="btn" onClick={() => void startMonitor()}>
              Start
            </button>
          )}
        </div>
        <div className="callout warn" style={{ marginBottom: 10 }}>
          <span className="callout-icon">!</span>
          <div className="callout-body">
            TCP push sets the player's <strong>device-global</strong> verbose mode (#SVM) and allows only
            one live stream at a time — shared with the dashboard. HTTP poll needs the app API awake.
          </div>
        </div>
        <div className="dev-transcript" role="log">
          {lines.length === 0 ? (
            <div className="dev-tline dev-info">No activity yet — fire a command or start the monitor.</div>
          ) : (
            lines.map((l) => (
              <div key={l.id} className={`dev-tline dev-${l.dir}`}>
                {DIR_PREFIX[l.dir]}
                {l.text}
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
