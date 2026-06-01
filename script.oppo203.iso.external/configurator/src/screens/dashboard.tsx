import { useEffect, useRef, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { Icon, type IconName } from "../icons";
import { invoke } from "../ipc";
import { parseOppoPowerReply } from "../probes";
import { livenessTargets, type LivenessTarget } from "../dashboard_targets";
import { canStartLiveStream, readOppoStatus, type StatusReadResult } from "../dashboard_status";
import type { OppoSessionState, OppoSessionStatus } from "../oppo_status";
import type { ScreenProps } from "./types";

// How often the dashboard re-checks device liveness + session status while it is open.
const POLL_MS = 6000;

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
          <span style={{ fontSize: 13 }}>{baseName(s.mediaFile) || "(no media)"}</span>
        </div>
        <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
          {s.architecturePreset} · {s.routingMode} · monitor {s.monitorMode}
        </span>
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

export function Dashboard({ go, state }: ScreenProps) {
  const targets = livenessTargets(state);
  // Re-run the poller whenever a probed address or the read tier changes; the effect reads fresh.
  const targetsKey = targets.map((t) => `${t.id}:${t.host}:${t.port}:${t.kind}`).join("|");
  const [statuses, setStatuses] = useState<Record<string, LiveStatus>>({});
  const [session, setSession] = useState<StatusReadResult | null>(null);
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [nonce, setNonce] = useState(0);

  const [streaming, setStreaming] = useState(false);
  const [frames, setFrames] = useState<LiveFrame[]>([]);
  const [streamErr, setStreamErr] = useState<string | null>(null);
  const streamingRef = useRef(false);
  useEffect(() => {
    streamingRef.current = streaming;
  }, [streaming]);

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

  const startStream = async () => {
    if (!gate.allowed) {
      setStreamErr(gate.reason);
      return;
    }
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
          the prior verbose mode on stop. Disabled while the add-on owns a session, so the two
          never drive the player's device-global verbose mode at once.
        </div>
      </div>

      <div className="callout info" style={{ width: "100%", marginBottom: 14 }}>
        <span className="callout-icon">
          <Icon name="info" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          This is a network-reachability check, not a full health report — the TV isn't listed
          because the wizard doesn't store a TV address. Software-verified: liveness, session
          status, and the live stream depend on the real devices answering.
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
