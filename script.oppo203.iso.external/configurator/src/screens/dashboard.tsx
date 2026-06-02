import { useEffect, useRef, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { Icon, type IconName } from "../icons";
import { invoke } from "../ipc";
import { parseOppoPowerReply } from "../probes";
import { livenessTargets, type LivenessTarget } from "../dashboard_targets";
import { canStartLiveStream, readOppoStatus, type StatusReadResult } from "../dashboard_status";
import {
  formatEpochAge,
  isStatusFresh,
  type OppoSessionPhase,
  type OppoSessionState,
  type OppoSessionStatus,
} from "../oppo_status";
import { chainNodeViews, type ChainLiveness, type ChainNodeView } from "../dashboard_chain";
import { captureSettingsSnapshot, type SnapshotResult } from "../dashboard_snapshot";
import { diffIsEmpty, type SettingsDiff } from "../settings_diff";
import { foldObservation, type SessionLogEntry } from "../session_log";
import { readDashboardJson, writeDashboardJson } from "../dashboard_store";
import type { ScreenProps } from "./types";

// How often the dashboard re-checks device liveness + session status while it is open.
const POLL_MS = 6000;
// Dashboard appdata file (under the dashboard/ prefix) holding the observed-session history.
const SESSION_LOG_FILE = "session-log.json";
// Most-recent history entries rendered in the card; older ones are retained but collapsed.
const HISTORY_SHOWN = 10;

type LiveStatus = {
  // null while the first probe is still in flight; true/false once known.
  reachable: boolean | null;
  detail: string;
};

// One verbose-mode push frame streamed from the Rust monitor (see lib.rs `LiveFrame`).
type LiveFrame = { seq: number; kind: string; raw: string };

const DEVICE_ICON: Record<LivenessTarget["id"], IconName> = {
  kodi: "kodi",
  player: "player",
  tv: "tv",
  avr: "avr",
};

const FRAME_COLORS: Record<string, string> = {
  upl: "#2563EB",
  utc: "#6B7280",
  status: "#0D9488",
  error: "#DC2626",
  info: "#9CA3AF",
};

function dotColor(reachable: boolean | null): string {
  if (reachable === true) return "#16A34A";
  if (reachable === false) return "#DC2626";
  return "#9CA3AF";
}

function stateBadge(s: OppoSessionState): { label: string; color: string } {
  if (s === "starting") return { label: "in progress", color: "#2563EB" };
  if (s === "failed") return { label: "failed", color: "#DC2626" };
  return { label: "ended", color: "#16A34A" };
}

const PHASE_LABEL: Record<OppoSessionPhase, string> = {
  launching: "launching",
  monitoring: "monitoring",
  ended: "ended",
};

function baseName(path: string): string {
  return path.split(/[\\/]/).pop() || path;
}

async function probeTarget(t: LivenessTarget): Promise<LiveStatus> {
  try {
    if (t.kind === "oppo") {
      const raw = await invoke<string>("oppo_query", { host: t.host, port: t.port, command: "#QPW" });
      const power = parseOppoPowerReply(raw);
      return { reachable: true, detail: power === "unknown" ? "reachable" : `power ${power}` };
    }
    if (t.kind === "oppo-http") {
      // Pure-HTTP install: reachable if the player answers an HTTP/436 request (getmovieplayinfo).
      await invoke<string>("oppo_playback_info", { host: t.host });
      return { reachable: true, detail: "HTTP reachable" };
    }
    const open = await invoke<boolean>("tcp_probe", { host: t.host, port: t.port });
    return { reachable: open, detail: open ? `:${t.port} open` : `:${t.port} no answer` };
  } catch {
    return { reachable: false, detail: "unreachable" };
  }
}

function ConfirmFlag({ on, label }: { on: boolean; label: string }) {
  return (
    <span className="row" style={{ gap: 5, alignItems: "center" }}>
      <Icon name={on ? "check" : "cross"} size={13} style={{ color: on ? "#16A34A" : "#9CA3AF" }} />
      <span className="muted" style={{ fontSize: 12 }}>{label}</span>
    </span>
  );
}

function SessionCard({ result }: { result: StatusReadResult | null }) {
  let body: JSX.Element;
  if (result == null) {
    body = <span className="muted" style={{ fontSize: 12 }}>checking…</span>;
  } else if (!result.supported || result.status == null) {
    body = <span className="muted" style={{ fontSize: 12 }}>{result.note ?? "No session recorded yet."}</span>;
  } else {
    const s: OppoSessionStatus = result.status;
    const badge = stateBadge(s.sessionState);
    const startedAge = formatEpochAge(s.startedAt);
    const updatedAge = formatEpochAge(s.updatedAt);
    const fresh = isStatusFresh(s.updatedAt);
    // Only call a still-"starting" session stale: an ended record is meant to stop refreshing.
    const showStale = fresh === false && s.sessionState === "starting";
    body = (
      <div className="stack-sm">
        <div className="row" style={{ gap: 8, alignItems: "center" }}>
          <span
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: badge.color,
              border: `1px solid ${badge.color}`,
              borderRadius: 6,
              padding: "1px 7px",
            }}
          >
            {badge.label}
          </span>
          {s.phase && (
            <span className="muted" style={{ fontSize: 11, fontFamily: "var(--font-mono)" }}>
              {PHASE_LABEL[s.phase]}
            </span>
          )}
          <span style={{ fontSize: 13 }}>{baseName(s.mediaFile) || "(no media)"}</span>
        </div>
        <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
          {s.architecturePreset} · {s.routingMode} · monitor {s.monitorMode}
        </span>
        {(startedAge || updatedAge) && (
          <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
            {startedAge ? `started ${startedAge}` : ""}
            {startedAge && updatedAge ? " · " : ""}
            {updatedAge ? `updated ${updatedAge}` : ""}
            {showStale ? (
              <span style={{ color: "#DC2626" }}> · stale (add-on may have exited)</span>
            ) : (
              ""
            )}
          </span>
        )}
        <div className="row" style={{ gap: 16 }}>
          <ConfirmFlag on={s.confirmedPlayback} label="playback confirmed" />
          <ConfirmFlag on={s.confirmedProgress} label="progress confirmed" />
        </div>
        {(s.oppoPlaybackState || s.utcTickCount != null || s.stopReason) && (
          <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
            {s.oppoPlaybackState ? `state ${s.oppoPlaybackState}` : ""}
            {s.utcTickCount != null ? ` · ${s.utcTickCount} ticks` : ""}
            {s.stopReason ? ` · ${s.stopReason}` : ""}
          </span>
        )}
      </div>
    );
  }
  return (
    <div className="card">
      <h2 className="section-title">Current session</h2>
      <div className="divider" />
      {body}
      <div className="muted" style={{ fontSize: 11, marginTop: 10 }}>
        The add-on writes this at session start and end, so it is a last/current-session summary,
        not a live progress feed.
      </div>
    </div>
  );
}

const CHAIN_LIVENESS: Record<ChainLiveness, { dot: string; text: string }> = {
  up: { dot: "#16A34A", text: "reachable" },
  down: { dot: "#DC2626", text: "no answer" },
  checking: { dot: "#9CA3AF", text: "checking…" },
  unprobed: { dot: "#9CA3AF", text: "no liveness probe" },
  "no-address": { dot: "#9CA3AF", text: "no address" },
};

function ChainNodeRow({ node, isLast }: { node: ChainNodeView; isLast: boolean }) {
  const live = CHAIN_LIVENESS[node.liveness];
  return (
    <div className="stack-sm" style={{ gap: 4 }}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <div className="row" style={{ gap: 8, alignItems: "center" }}>
          <Icon name={DEVICE_ICON[node.id]} size={16} />
          <span>{node.label}</span>
          {node.host && (
            <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
              {node.host}
            </span>
          )}
        </div>
        <div className="row" style={{ gap: 8, alignItems: "center" }}>
          <span className="muted" style={{ fontSize: 12 }}>{live.text}</span>
          <span
            aria-label={live.text}
            style={{
              width: 9,
              height: 9,
              borderRadius: "50%",
              background: live.dot,
              display: "inline-block",
              flexShrink: 0,
            }}
          />
        </div>
      </div>
      {node.activity && (
        <div className="row" style={{ gap: 6, alignItems: "center", paddingLeft: 24 }}>
          <Icon name="play" size={11} style={{ color: "#2563EB" }} />
          <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
            {node.activity}
          </span>
        </div>
      )}
      {!isLast && (
        <div className="muted" style={{ paddingLeft: 7, fontSize: 12, lineHeight: 1 }}>
          ↓
        </div>
      )}
    </div>
  );
}

function ChainCard({ nodes }: { nodes: ChainNodeView[] }) {
  return (
    <div className="card">
      <h2 className="section-title">Playback chain</h2>
      <div className="divider" />
      <div className="stack-sm">
        {nodes.map((n, i) => (
          <ChainNodeRow key={n.id} node={n} isLast={i === nodes.length - 1} />
        ))}
      </div>
      <div className="muted" style={{ fontSize: 11, marginTop: 10 }}>
        Every hop on the configured chain, in signal order. Liveness is a reachability probe;
        activity comes from the add-on's session, so only the player reports live playback. The
        receiver appears only in an AVR chain.
      </div>
    </div>
  );
}

function fmtWhen(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}

function DiffList({ diff }: { diff: SettingsDiff }) {
  const mono = { fontSize: 12, fontFamily: "var(--font-mono)" } as const;
  return (
    <div className="stack-sm">
      {diff.changed.map((c) => (
        <div key={`c-${c.id}`} style={mono}>
          <span style={{ color: "#2563EB" }}>~ {c.id}</span>
          <span className="muted">: {c.from} → {c.to}</span>
        </div>
      ))}
      {diff.added.map((a) => (
        <div key={`a-${a.id}`} style={mono}>
          <span style={{ color: "#16A34A" }}>+ {a.id}</span>
          <span className="muted">: {a.value}</span>
        </div>
      ))}
      {diff.removed.map((r) => (
        <div key={`r-${r.id}`} style={mono}>
          <span style={{ color: "#DC2626" }}>- {r.id}</span>
          <span className="muted">: {r.value}</span>
        </div>
      ))}
    </div>
  );
}

function SettingsDiffCard({
  result,
  busy,
  supported,
  onSnapshot,
}: {
  result: SnapshotResult | null;
  busy: boolean;
  supported: boolean;
  onSnapshot: () => void;
}) {
  let body: JSX.Element;
  if (!supported) {
    body = (
      <span className="muted" style={{ fontSize: 12 }}>
        Manual mode - connect over SSH (tier A) or SMB (tier B) to snapshot the box's settings.
      </span>
    );
  } else if (result == null) {
    body = (
      <span className="muted" style={{ fontSize: 12 }}>
        Capture the box's current add-on settings to compare against later.
      </span>
    );
  } else if (!result.ok) {
    body = <span className="muted" style={{ fontSize: 12 }}>{result.note}</span>;
  } else if (result.baseline) {
    body = (
      <span className="muted" style={{ fontSize: 12 }}>
        Baseline captured ({result.count} settings). Snapshot again later to see what changed on
        the box.
      </span>
    );
  } else if (diffIsEmpty(result.diff)) {
    body = (
      <span className="muted" style={{ fontSize: 12 }}>
        No changes since the last snapshot ({fmtWhen(result.prevTakenAt)}).
      </span>
    );
  } else {
    body = (
      <div className="stack-sm">
        <span className="muted" style={{ fontSize: 11 }}>
          since {fmtWhen(result.prevTakenAt)}
        </span>
        <DiffList diff={result.diff} />
      </div>
    );
  }
  return (
    <div className="card">
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <h2 className="section-title">Configuration changes</h2>
        <button className="btn outline" onClick={onSnapshot} disabled={busy || !supported}>
          <Icon name="refresh" size={13} /> {busy ? "reading…" : "Snapshot now"}
        </button>
      </div>
      <div className="divider" />
      {body}
      <div className="muted" style={{ fontSize: 11, marginTop: 10 }}>
        Reads the box's <code>settings.xml</code> and compares it to your last snapshot. Secret
        values (PSKs, tokens) are masked, so a secret's change shows only as its key.
      </div>
    </div>
  );
}

function SessionHistoryCard({ entries }: { entries: SessionLogEntry[] }) {
  const shown = entries.slice(-HISTORY_SHOWN).reverse();
  const hidden = entries.length - shown.length;
  return (
    <div className="card">
      <h2 className="section-title">Session history</h2>
      <div className="divider" />
      {entries.length === 0 ? (
        <span className="muted" style={{ fontSize: 12 }}>
          No sessions recorded yet. Sessions the dashboard observes while open are logged here.
        </span>
      ) : (
        <div className="stack-sm">
          {shown.map((e, i) => {
            const badge = stateBadge(e.sessionState);
            return (
              <div
                key={`${e.firstSeenAt}-${i}`}
                className="stack-sm"
                style={{
                  paddingBottom: 6,
                  borderBottom: i < shown.length - 1 ? "1px solid var(--hairline, #00000014)" : "none",
                }}
              >
                <div className="row" style={{ gap: 8, alignItems: "center" }}>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      color: badge.color,
                      border: `1px solid ${badge.color}`,
                      borderRadius: 6,
                      padding: "1px 7px",
                    }}
                  >
                    {badge.label}
                  </span>
                  <span style={{ fontSize: 13 }}>{baseName(e.mediaFile) || "(no media)"}</span>
                  <span
                    className="muted"
                    style={{ fontSize: 11, marginLeft: "auto", fontFamily: "var(--font-mono)" }}
                  >
                    {fmtWhen(e.observedAt)}
                  </span>
                </div>
                <div className="row" style={{ gap: 16, alignItems: "center" }}>
                  <ConfirmFlag on={e.confirmedPlayback} label="playback" />
                  <ConfirmFlag on={e.confirmedProgress} label="progress" />
                  {e.stopReason && (
                    <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
                      {e.stopReason}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
          {hidden > 0 && (
            <span className="muted" style={{ fontSize: 11 }}>
              +{hidden} earlier session{hidden === 1 ? "" : "s"} kept
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export function Dashboard({ go, state }: ScreenProps) {
  const targets = livenessTargets(state);
  // Re-run the poller whenever a probed address or the read tier changes; the effect reads fresh.
  const targetsKey = targets.map((t) => `${t.id}:${t.host}:${t.port}:${t.kind}`).join("|");
  const [statuses, setStatuses] = useState<Record<string, LiveStatus>>({});
  const [session, setSession] = useState<StatusReadResult | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [nonce, setNonce] = useState(0);

  const [snapshot, setSnapshot] = useState<SnapshotResult | null>(null);
  const [snapshotBusy, setSnapshotBusy] = useState(false);
  const snapshotSupported = state.tier === "A" || state.tier === "B";

  const takeSnapshot = async () => {
    setSnapshotBusy(true);
    try {
      setSnapshot(await captureSettingsSnapshot(state, new Date().toISOString()));
    } finally {
      setSnapshotBusy(false);
    }
  };

  // Observed-session history: kept in a ref (read by the poller without re-subscribing) mirrored
  // into state for rendering. Loaded once from appdata; persisted only when the fold changes it.
  const [log, setLog] = useState<SessionLogEntry[]>([]);
  const logRef = useRef<SessionLogEntry[]>([]);
  useEffect(() => {
    let alive = true;
    void readDashboardJson<SessionLogEntry[]>(SESSION_LOG_FILE).then((stored) => {
      if (alive && Array.isArray(stored)) {
        logRef.current = stored;
        setLog(stored);
      }
    });
    return () => {
      alive = false;
    };
  }, []);

  const [streaming, setStreaming] = useState(false);
  const [frames, setFrames] = useState<LiveFrame[]>([]);
  const [streamErr, setStreamErr] = useState<string | null>(null);
  const streamingRef = useRef(false);
  useEffect(() => {
    streamingRef.current = streaming;
  }, [streaming]);
  // The live stream auto-starts once the first status read clears the dual-subscriber gate. These
  // refs keep that to a single attempt and let a manual Stop stick (no immediate auto-restart).
  const autoStartedRef = useRef(false);
  const userStoppedRef = useRef(false);

  useEffect(() => {
    let alive = true;
    const list = livenessTargets(state);
    const runAll = async () => {
      setChecking(true);
      const [entries, sess] = await Promise.all([
        Promise.all(list.map(async (t) => [t.id, await probeTarget(t)] as const)),
        readOppoStatus(state),
      ]);
      if (!alive) return;
      setStatuses(Object.fromEntries(entries));
      setSession(sess);
      // Fold the just-read session into the local history; persist only on a real change so the
      // idle 6s polls that re-read an unchanged status file do not churn the appdata file.
      if (sess.status) {
        const next = foldObservation(logRef.current, sess.status, new Date().toISOString());
        if (next !== logRef.current) {
          logRef.current = next;
          setLog(next);
          void writeDashboardJson(SESSION_LOG_FILE, next).catch(() => {});
        }
      }
      setLastChecked(new Date().toLocaleTimeString());
      setChecking(false);
      // Safety: if the add-on starts a session while we're streaming, drop our verbose
      // connection so the two don't fight over the player's device-global verbose mode.
      if (streamingRef.current && sess.status?.sessionState === "starting") {
        streamingRef.current = false;
        void invoke("stop_oppo_live_monitor").catch(() => {});
        setStreaming(false);
        setStreamErr("Stopped: the add-on started a playback session.");
      }
      // Auto-start the live stream once the first read clears the dual-subscriber gate, so the
      // dashboard begins streaming on open without a manual click. Only one attempt, and never
      // after a manual Stop or while the add-on owns the session.
      if (
        !autoStartedRef.current &&
        !userStoppedRef.current &&
        !streamingRef.current &&
        canStartLiveStream(sess.status).allowed
      ) {
        autoStartedRef.current = true;
        streamingRef.current = true;
        setStreamErr(null);
        setFrames([]);
        try {
          await invoke("start_oppo_live_monitor", { host: state.playerIp, port: 23 });
          if (!alive) return;
          setStreaming(true);
        } catch (e) {
          if (!alive) return;
          streamingRef.current = false;
          setStreamErr(`Could not start: ${String(e)}`);
          setStreaming(false);
        }
      }
    };
    void runAll();
    const h = setInterval(() => void runAll(), POLL_MS);
    return () => {
      alive = false;
      clearInterval(h);
    };
  }, [targetsKey, state.tier, state.sshUser, state.kodiPlatform, state.smbSharePath, nonce]);

  // Subscribe to the Rust live stream once; stop the monitor on unmount (restores verbose mode).
  useEffect(() => {
    let alive = true;
    let unlisten: (() => void) | undefined;
    void listen<LiveFrame>("oppo-live", (e) => {
      setFrames((f) => [...f.slice(-99), e.payload]);
    }).then((u) => {
      if (alive) unlisten = u;
      else u();
    });
    return () => {
      alive = false;
      if (unlisten) unlisten();
      void invoke("stop_oppo_live_monitor").catch(() => {});
    };
  }, []);

  const gate = canStartLiveStream(session?.status ?? null);
  // Full-chain view: every node in topology order, fed the probe map + parsed session we already
  // poll. LiveStatus carries { reachable } so it is accepted directly as the probe shape.
  const chainViews = chainNodeViews(state, statuses, session?.status ?? null);

  const startStream = async () => {
    if (!gate.allowed) {
      setStreamErr(gate.reason);
      return;
    }
    // A manual Start clears the "user stopped" latch so the stream behaves normally again.
    userStoppedRef.current = false;
    setStreamErr(null);
    setFrames([]);
    try {
      await invoke("start_oppo_live_monitor", { host: state.playerIp, port: 23 });
      setStreaming(true);
    } catch (e) {
      setStreamErr(`Could not start: ${String(e)}`);
      setStreaming(false);
    }
  };

  const stopStream = async () => {
    // Remember the user stopped on purpose so the auto-start does not immediately reopen it.
    userStoppedRef.current = true;
    try {
      await invoke("stop_oppo_live_monitor");
    } catch {
      // best-effort
    }
    setStreaming(false);
  };

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Live dashboard.</h1>
        <p className="screen-subtitle">
          A quick health view of your configured chain. The configurator pings each device it has
          an address for and reads the add-on's last session, every few seconds, while this screen
          is open.
        </p>
      </div>

      <div className="card">
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <h2 className="section-title">Devices</h2>
          <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
            {checking ? "checking…" : lastChecked ? `checked ${lastChecked}` : ""}
          </span>
        </div>
        <div className="divider" />
        <div className="stack-sm">
          {targets.map((t) => {
            const s = statuses[t.id];
            return (
              <div
                key={t.id}
                className="row"
                style={{ justifyContent: "space-between", alignItems: "center" }}
              >
                <div className="row" style={{ gap: 8, alignItems: "center" }}>
                  <Icon name={DEVICE_ICON[t.id]} size={16} />
                  <span>{t.label}</span>
                  <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
                    {t.host}
                  </span>
                </div>
                <div className="row" style={{ gap: 8, alignItems: "center" }}>
                  <span className="muted" style={{ fontSize: 12 }}>
                    {s?.detail ?? "…"}
                  </span>
                  <span
                    aria-label={
                      s?.reachable == null ? "checking" : s.reachable ? "reachable" : "unreachable"
                    }
                    style={{
                      width: 9,
                      height: 9,
                      borderRadius: "50%",
                      background: dotColor(s?.reachable ?? null),
                      display: "inline-block",
                      flexShrink: 0,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <SessionCard result={session} />

      <SessionHistoryCard entries={log} />

      <ChainCard nodes={chainViews} />

      <SettingsDiffCard
        result={snapshot}
        busy={snapshotBusy}
        supported={snapshotSupported}
        onSnapshot={takeSnapshot}
      />

      <div className="card">
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <h2 className="section-title">Live stream (verbose mode 3)</h2>
          {streaming ? (
            <button className="btn outline" onClick={stopStream}>
              <Icon name="cross" size={13} /> Stop
            </button>
          ) : (
            <button className="btn outline" onClick={startStream} disabled={!gate.allowed}>
              <Icon name="play" size={13} /> Start
            </button>
          )}
        </div>
        <div className="divider" />
        {!gate.allowed && (
          <div className="callout warn" style={{ width: "100%", marginBottom: 10 }}>
            <span className="callout-icon">
              <Icon name="warn" size={13} stroke={2.2} />
            </span>
            <div className="callout-body">{gate.reason}</div>
          </div>
        )}
        {streamErr && (
          <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>{streamErr}</div>
        )}
        <div
          style={{
            maxHeight: 180,
            overflowY: "auto",
            fontFamily: "var(--font-mono)",
            fontSize: 11.5,
            lineHeight: 1.6,
          }}
        >
          {frames.length === 0 ? (
            <span className="muted">
              {streaming ? "waiting for the player to push frames…" : "not streaming"}
            </span>
          ) : (
            frames.map((f) => (
              <div key={f.seq} style={{ color: FRAME_COLORS[f.kind] }}>
                {f.raw}
              </div>
            ))
          )}
        </div>
        <div className="muted" style={{ fontSize: 11, marginTop: 10 }}>
          Opens the configurator's own <code>#SVM 3</code> connection to the player and restores
          the prior verbose mode on stop. Starts automatically when the dashboard opens; disabled
          (and dropped) while the add-on owns a session, so the two never drive the player's
          device-global verbose mode at once.
        </div>
      </div>

      <div className="callout info" style={{ width: "100%", marginBottom: 14 }}>
        <span className="callout-icon">
          <Icon name="info" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          This is a network-reachability check, not a full health report — each device is listed
          once the wizard has stored an address and a backend with a plain TCP control port (the
          TV appears after Step 4 captures its IP on a Roku ECP / ADB / Sony backend). Software-verified:
          liveness, session status, and the live stream depend on the real devices answering.
        </div>
      </div>

      <div className="row" style={{ gap: 10 }}>
        <button className="btn outline" onClick={() => setNonce((n) => n + 1)} disabled={checking}>
          <Icon name="refresh" size={14} /> Re-check now
        </button>
        <button className="btn outline" onClick={() => go("test_success")}>
          <Icon name="chevL" size={14} /> Back
        </button>
      </div>
    </div>
  );
}
