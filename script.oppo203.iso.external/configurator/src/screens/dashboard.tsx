import { useEffect, useState } from "react";
import { Icon, type IconName } from "../icons";
import { invoke } from "../ipc";
import { parseOppoPowerReply } from "../probes";
import { livenessTargets, type LivenessTarget } from "../dashboard_targets";
import type { ScreenProps } from "./types";

// How often the dashboard re-checks device liveness while it is open.
const POLL_MS = 6000;

type LiveStatus = {
  // null while the first probe is still in flight; true/false once known.
  reachable: boolean | null;
  detail: string;
};

const DEVICE_ICON: Record<LivenessTarget["id"], IconName> = {
  kodi: "kodi",
  player: "player",
  avr: "avr",
};

function dotColor(reachable: boolean | null): string {
  if (reachable === true) return "#16A34A";
  if (reachable === false) return "#DC2626";
  return "#9CA3AF";
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

export function Dashboard({ go, state }: ScreenProps) {
  const targets = livenessTargets(state);
  // Re-run the poller whenever a probed address changes; the effect reads state fresh.
  const targetsKey = targets.map((t) => `${t.id}:${t.host}:${t.port}:${t.kind}`).join("|");
  const [statuses, setStatuses] = useState<Record<string, LiveStatus>>({});
  const [lastChecked, setLastChecked] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    let alive = true;
    const list = livenessTargets(state);
    const runAll = async () => {
      setChecking(true);
      const entries = await Promise.all(
        list.map(async (t) => [t.id, await probeTarget(t)] as const)
      );
      if (!alive) return;
      setStatuses(Object.fromEntries(entries));
      setLastChecked(new Date().toLocaleTimeString());
      setChecking(false);
    };
    void runAll();
    const h = setInterval(() => void runAll(), POLL_MS);
    return () => {
      alive = false;
      clearInterval(h);
    };
  }, [targetsKey, nonce]);

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Live dashboard.</h1>
        <p className="screen-subtitle">
          A quick health view of your configured chain. The configurator pings each device it
          has an address for, every few seconds, while this screen is open.
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

      <div className="callout info" style={{ width: "100%", marginBottom: 14 }}>
        <span className="callout-icon">
          <Icon name="info" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          This is a network-reachability check, not a full health report — the TV isn't listed
          because the wizard doesn't store a TV address. Software-verified: liveness depends on
          the real devices answering.
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
