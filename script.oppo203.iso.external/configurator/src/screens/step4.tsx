import { useState } from "react";
import { Icon, type IconName } from "../icons";
import { DiagLog, type DiagCheck } from "../shell/DiagLog";
import { FooterNav } from "../shell/FooterNav";
import { BrandIcon } from "../shell/BrandIcon";
import { invoke } from "../ipc";
import { inferBackendFromPorts, probePortList, TV_PROBE_PORTS, type PortResult } from "../probes";
import {
  BUNDLED_TV_DB,
  fetchRemoteTvDb,
  isNewer,
  modelsForBrand,
  modelsForRegion,
  resolveBackend,
  resolvePlatform,
  resolveTier,
  TV_REGIONS,
  type TvDb,
  type TvDbModel,
  type TvRegion,
} from "../tvdb";
import type { ScreenId } from "../steps";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 5 —TV brand
// ============================================================
const TV_BRANDS = [
  { id: "sony",      name: "Sony",      ch: "SONY", color: "#0B0B0C", hint: "Bravia · Google TV" },
  { id: "samsung",   name: "Samsung",   ch: "SI",   color: "#1428A0", hint: "Tizen" },
  { id: "lg",        name: "LG",        ch: "LG",   color: "#A50034", hint: "webOS" },
  { id: "tcl",       name: "TCL",       ch: "TCL",  color: "#C8102E", hint: "Google / Roku" },
  { id: "hisense",   name: "Hisense",   ch: "H",    color: "#00843D", hint: "VIDAA / Google / Roku" },
  { id: "roku",      name: "Roku TV",   ch: "R",    color: "#6F1AB1", hint: "ECP" },
  { id: "vizio",     name: "Vizio",     ch: "V",    color: "#111114", hint: "SmartCast" },
  { id: "panasonic", name: "Panasonic", ch: "P",    color: "#0050A0", hint: "MyHome / FireTV" },
  { id: "other",     name: "Other",     ch: "?",    color: "#6B7280", hint: "or not listed" },
] as const;

export function Step4Brand({ go, state, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Your TV</h1>
        <p className="screen-subtitle">
          Pick your TV's brand. The control method comes from the platform (Google TV →
          ADB, Roku → ECP, webOS → LG, …) — your exact model just helps us confirm.
        </p>
      </div>
      <div className="brand-grid">
        {TV_BRANDS.map((b) => (
          <button
            key={b.id}
            className={`brand-pill ${state.tvBrand === b.id ? "selected" : ""}`.trim()}
            onClick={() => {
              set({ tvBrand: b.id });
              go("step4_model");
            }}
          >
            <BrandIcon slug={b.id} ch={b.ch} color={b.color} fallbackIcon="tv" />
            <div>{b.name}</div>
            <div className="muted" style={{ fontSize: 10.5, fontWeight: 500 }}>{b.hint}</div>
          </button>
        ))}
      </div>
      <FooterNav go={go} back="step2_test" />
    </div>
  );
}

// ============================================================
// STEP 5 —Model
// ============================================================
function tierChipKind(tier: string | null): string {
  if (tier === "preferred") return "success";
  if (tier === "probe") return "accent";
  return "warn";
}

function tierChipLabel(tier: string | null): string {
  if (tier === "preferred") return "preferred path";
  if (tier === "probe") return "probe & confirm";
  if (tier === "fallback") return "fallback path";
  return "manual";
}

export function Step4Model({ go, state, set }: ScreenProps) {
  const [db, setDb] = useState<TvDb>(BUNDLED_TV_DB);
  const [region, setRegion] = useState<TvRegion | null>(state.tvRegion ?? "US");
  const [year, setYear] = useState("2023");
  const [search, setSearch] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const brandName = TV_BRANDS.find((b) => b.id === state.tvBrand)?.name ?? "TV";
  const models = state.tvBrand ? modelsForBrand(db, state.tvBrand) : [];
  const filtered = modelsForRegion(models, region).filter(
    (m) =>
      (!year || String(m.year) === year) &&
      m.name.toLowerCase().includes(search.toLowerCase())
  );

  const pickRegion = (r: TvRegion) => {
    const next = region === r ? null : r;
    setRegion(next);
    set({ tvRegion: next });
  };

  const refresh = async () => {
    setRefreshing(true);
    const remote = await fetchRemoteTvDb();
    if (remote && isNewer(db, remote)) setDb(remote);
    setRefreshing(false);
  };

  const select = (m: TvDbModel) => {
    set({
      tvModel: m.id,
      tvPlatform: resolvePlatform(db, m),
      tvBackend: resolveBackend(db, m),
    });
  };

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Which {brandName} model?</h1>
        <p className="screen-subtitle">
          Region and year just narrow the list — the control method comes from the
          platform.
        </p>
      </div>

      <div className="stack" style={{ gap: 14 }}>
        <div className="row" style={{ gap: 10 }}>
          <div className="field" style={{ flex: 1, maxWidth: 360 }}>
            <input
              className="input text"
              placeholder="Search models…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <span className="spacer" />
          <button className="btn ghost sm" onClick={refresh} disabled={refreshing}>
            <Icon name="download" size={13} /> {refreshing ? "Updating…" : "Update list"}
          </button>
          <button className="btn ghost sm" onClick={() => go("step4_notfound")}>
            <Icon name="search" size={13} /> Can't find my model
          </button>
        </div>
        <div className="row" style={{ gap: 8, alignItems: "center" }}>
          <span className="muted" style={{ fontSize: 12, fontWeight: 500 }}>Region</span>
          <div className="filter-row">
            {TV_REGIONS.map((r) => (
              <button
                key={r}
                className={`filter-pill ${region === r ? "selected" : ""}`.trim()}
                onClick={() => pickRegion(r)}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
        <div className="row" style={{ gap: 8, alignItems: "center" }}>
          <span className="muted" style={{ fontSize: 12, fontWeight: 500 }}>Year</span>
          <div className="filter-row">
            {["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"].map((y) => (
              <button
                key={y}
                className={`filter-pill ${year === y ? "selected" : ""}`.trim()}
                onClick={() => setYear(year === y ? "" : y)}
              >
                {y}
              </button>
            ))}
          </div>
        </div>

        <p className="muted" style={{ fontSize: 11.5, margin: "4px 2px 8px", lineHeight: 1.4 }}>
          TVs are listed by <strong>model family</strong> — every screen size in a family shares the
          same control setup, so pick the family that matches your model name. Your exact size is
          covered even when it isn't spelled out below.
        </p>
        <div className="model-list">
          {filtered.length === 0 && (
            <div className="model-row" style={{ justifyContent: "center", color: "var(--muted)" }}>
              No matches — try adjusting filters or{" "}
              <button className="btn ghost sm" onClick={() => go("step4_notfound")}>
                tell us it's not here
              </button>
            </div>
          )}
          {filtered.map((m) => {
            const backend = resolveBackend(db, m);
            const tier = resolveTier(db, m);
            const fallbacks = m.fallback_backends ?? [];
            return (
              <div
                key={m.id}
                className={`model-row ${state.tvModel === m.id ? "selected" : ""}`.trim()}
                onClick={() => select(m)}
                title={m.region_notes ?? m.notes ?? ""}
              >
                <div>
                  <div>
                    {m.name}{" "}
                    <span className="muted" style={{ fontSize: 11, fontWeight: 500 }}>{m.year}</span>
                  </div>
                  <div className="model-row-meta">
                    {resolvePlatform(db, m) ?? "—"} · backend <code>{backend ?? "—"}</code>
                    {fallbacks.length > 0 && (
                      <>
                        {" "}· fallback <code>{fallbacks.join(", ")}</code>
                      </>
                    )}
                  </div>
                  <div className="model-row-meta">
                    {m.regions.join(" · ")}
                    {m.mapping_confidence && <> · {m.mapping_confidence} confidence</>}
                  </div>
                  {m.sizes && m.sizes.length > 0 && (
                    <div className="model-row-meta">Sizes: {m.sizes.map((s) => `${s}″`).join(" · ")}</div>
                  )}
                </div>
                <span className={`chip ${tierChipKind(tier)}`}>
                  <span className="chip-dot" />
                  {tierChipLabel(tier)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
      <FooterNav
        go={go}
        back="step4_brand"
        next={state.tvModel ? "step4_adb_warn" : null}
        nextLabel="Continue"
      />
    </div>
  );
}

// ============================================================
// STEP 5 —Model not found
// ============================================================
export function Step4NotFound({ go, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">We couldn't find your model.</h1>
        <p className="screen-subtitle">
          That's fine — TVs from 2026+ are deliberately outside our database, and older
          models drift out of it too. You've got two honest paths from here.
        </p>
      </div>
      <div className="grid-2">
        <button className="tile" onClick={() => go("step4_probe")}>
          <div className="tile-icon">
            <Icon name="search" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">
              Probe the TV <span className="tile-badge recommended">Recommended</span>
            </div>
            <div className="tile-desc">
              We test the ports each backend uses (ADB :5555, Roku :8060, Sony IP, …)
              against your real TV and report what answers.
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
        <button
          className="tile"
          onClick={() => {
            set({ tvBackend: "custom_command" });
            go("step4_adb_warn");
          }}
        >
          <div className="tile-icon">
            <Icon name="terminal" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">Choose the method manually</div>
            <div className="tile-desc">
              Pick a backend yourself — including the <code>custom_command</code> escape
              hatch for anything else (Panasonic, Vizio, projectors, CEC scripts).
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
      </div>
      <div className="callout info" style={{ marginTop: 18 }}>
        <span className="callout-icon">
          <Icon name="info" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          A failed probe doesn't mean "unsupported" — usually it just means debugging is
          off or the IP is wrong. Either way, we won't dead-end you.
        </div>
      </div>
      <FooterNav go={go} back="step4_model" />
    </div>
  );
}

// ============================================================
// STEP 5 —Probe
// ============================================================
export function Step4Probe({ go, state, set }: ScreenProps) {
  const ip = state.tvIp || "10.0.1.51";
  const [probing, setProbing] = useState(false);
  const [results, setResults] = useState<PortResult[] | null>(null);

  const backend = results ? inferBackendFromPorts(results) : null;

  const probe = async () => {
    setProbing(true);
    try {
      const r = await invoke<PortResult[]>("tv_port_probe", { host: ip, ports: probePortList() });
      setResults(r);
    } catch {
      setResults([]);
    } finally {
      setProbing(false);
    }
  };

  const checks: DiagCheck[] = TV_PROBE_PORTS.map((entry) => {
    const r = results?.find((x) => x.port === entry.port);
    return {
      status: results === null ? "pending" : r?.open ? "pass" : "fail",
      label: `${entry.label} on :${entry.port}`,
      detail: results === null ? "" : r?.open ? "answered" : "no response",
    };
  });

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Probe your TV</h1>
        <p className="screen-subtitle">
          We'll knock on each backend's port and see what answers. No state-changing
          commands sent.
        </p>
      </div>
      <div className="grid-2" style={{ alignItems: "start" }}>
        <div className="card">
          <h2 className="section-title">Probe target</h2>
          <div className="stack">
            <div className="field">
              <label className="field-label">TV IP</label>
              <input className="input" value={ip} onChange={(e) => set({ tvIp: e.target.value })} />
              <div className="field-hint">Same network as this PC and your Kodi box.</div>
            </div>
            <button className="btn primary" onClick={probe} disabled={probing}>
              <Icon name="search" size={13} /> {probing ? "Probing…" : "Probe the TV"}
            </button>
          </div>
        </div>
        <div className="stack">
          <DiagLog
            title="Port probe"
            checks={checks}
            footer={
              results === null ? (
                <span className="muted">Probe the TV to see which backends answer.</span>
              ) : backend ? (
                <>
                  <strong className="success-text">Looks controllable.</strong> We'll use the{" "}
                  <code>{backend}</code> backend — it answered on the network.
                </>
              ) : (
                <span className="muted">
                  Nothing answered. Check the IP / debugging, or choose a method manually.
                </span>
              )
            }
            footerKind={backend ? "success" : ""}
          />
        </div>
      </div>
      <FooterNav
        go={go}
        back="step4_notfound"
        next={backend ? "step4_test" : null}
        nextLabel={backend ? `Use ${backend}` : "Continue"}
        set={set}
        setKeys={backend ? { tvBackend: backend, tvModel: "probed" } : undefined}
      />
    </div>
  );
}

// ============================================================
// STEP 5 —ADB allow-debugging heads up
// ============================================================
export function Step4AdbWarn(props: ScreenProps) {
  const { go, state } = props;
  // L7: drive the ADB warning off the chosen backend, not a substring of the model id (which
  // over-matched any model containing "q").
  const isAdb = state.tvBackend === "adb";
  if (!isAdb) {
    return <Step4Test {...props} />;
  }
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Heads-up: your TV may ask permission.</h1>
        <p className="screen-subtitle">
          ADB control needs the TV to trust this app the first time we connect. The TV
          (not us) shows the prompt — read it from across the room if you can.
        </p>
      </div>
      <div className="split" style={{ marginTop: 8 }}>
        <div className="tv-mockup">
          <div className="tv-mockup-screen">
            <div className="tv-mockup-text">▼ Allow USB debugging?</div>
            <div className="tv-mockup-text bright">"Always allow from this computer"</div>
            <div className="tv-mockup-text" style={{ fontSize: 10 }}>
              Cancel &nbsp; · &nbsp; OK
            </div>
          </div>
          <div className="stand" />
        </div>
        <div className="stack">
          <div className="callout warn">
            <span className="callout-icon">
              <Icon name="warn" size={13} stroke={2.2} />
            </span>
            <div className="callout-body">
              <strong>Pick "Always allow from this computer"</strong>, not the plain OK. A
              one-time accept can drop on a TV reboot and break silently later.
            </div>
          </div>
          <div className="callout info">
            <span className="callout-icon">
              <Icon name="info" size={13} stroke={2.2} />
            </span>
            <div className="callout-body">
              <strong>No prompt at all?</strong> The dialog only appears if Developer
              Options → USB debugging is already on. If you don't see it, debugging is off
              — enable it and try again.
            </div>
          </div>
          <button className="btn primary lg" onClick={() => go("step4_test")}>
            I'm ready — send the test
          </button>
        </div>
      </div>
      <FooterNav go={go} back="step4_model" />
    </div>
  );
}

// ============================================================
// STEP 5 —Control test
// ============================================================
type TestPhase = "ready" | "running" | "done";
type TestResult = {
  reachable: boolean | null;
  ms: number;
  port: number | null;
  sent: string | null;
  error: string | null;
};

export function Step4Test({ go, state, set }: ScreenProps) {
  const [phase, setPhase] = useState<TestPhase>("ready");
  const [result, setResult] = useState<TestResult | null>(null);

  const backend = state.tvBackend;
  const port =
    backend === "roku_ecp" ? 8060 : backend === "adb" ? 5555 : backend === "sony_bravia" ? 20060 : null;

  async function runTest() {
    setPhase("running");
    const res: TestResult = { reachable: null, ms: 0, port, sent: null, error: null };
    try {
      if (port != null) {
        const p = await invoke<{ reachable: boolean; ms: number }>("ping_host", { host: state.tvIp, port });
        res.reachable = p.reachable;
        res.ms = p.ms;
      }
      if (res.reachable !== false) {
        if (backend === "roku_ecp") {
          await invoke("tv_switch_roku", { host: state.tvIp, key: "VolumeMute" });
          res.sent = "Roku ECP VolumeMute";
        } else if (backend === "adb") {
          await invoke("tv_switch_adb", {
            sshHost: state.kodiIp,
            sshUser: state.sshUser,
            adbPath: "adb",
            tvHost: state.tvIp,
            tvPort: 5555,
            adbCommand: "input keyevent KEYCODE_VOLUME_MUTE",
          });
          res.sent = "adb input keyevent KEYCODE_VOLUME_MUTE";
        }
      }
    } catch (e) {
      res.error = String(e);
    }
    setResult(res);
    setPhase("done");
  }

  const checks: DiagCheck[] =
    phase === "ready"
      ? [
          { status: "pending", label: port != null ? `Reach the TV at ${state.tvIp || "the TV"}:${port}` : "Reach the TV", detail: "" },
          { status: "pending", label: "Send a real mute command", detail: "" },
        ]
      : phase === "running"
        ? [
            { status: "run", label: "Reaching the TV…", detail: "" },
            { status: "pending", label: "Send a real mute command", detail: "" },
          ]
        : [
            result?.reachable === true
              ? { status: "pass", label: `TV reachable at ${state.tvIp}:${result.port}`, detail: `TCP connect ${result.ms} ms` }
              : result?.reachable === false
                ? { status: "fail", label: `No response at ${state.tvIp}:${result?.port}`, detail: "timeout / refused — wrong IP or backend off" }
                : { status: "pass", label: "Reachability not checkable here", detail: `${backend ?? "no backend"} has no plain TCP port` },
            result?.error
              ? { status: "fail", label: "Command failed", detail: result.error }
              : result?.sent
                ? { status: "pass", label: "Real mute command sent", detail: result.sent }
                : { status: "run", label: "No auto-mute for this backend", detail: "press mute on the remote to test by hand" },
          ];

  const done = phase === "done";

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Can we control your TV?</h1>
        <p className="screen-subtitle">
          Quick test — we reach the TV and, where the backend supports it, send a <em>real</em> mute.
          It answers one question: can we drive this TV at all?
        </p>
      </div>
      <div className="grid-2" style={{ alignItems: "start" }}>
        <div className="stack">
          <DiagLog
            title="Basic control test"
            checks={checks}
            footer={
              phase === "ready" ? (
                <span className="muted">Click "Send test signal" when you're ready.</span>
              ) : phase === "running" ? (
                <>Reaching the TV…</>
              ) : (
                <strong>Did your TV react?</strong>
              )
            }
            footerKind={done ? "success" : ""}
          />
          {phase === "ready" && (
            <button className="btn primary lg" onClick={() => void runTest()}>
              <Icon name="play" size={14} /> Send test signal
            </button>
          )}
          {done && (
            <div className="row" style={{ gap: 10 }}>
              <button
                className="btn primary lg"
                onClick={() => {
                  set({ tvVerified: true });
                  go("step5_intro");
                }}
              >
                <Icon name="check" size={14} /> Yes — it reacted
              </button>
              <button className="btn outline" onClick={() => go("step4_fail")}>
                No
              </button>
            </div>
          )}
        </div>
        <div className="tv-mockup">
          <div className="tv-mockup-screen">
            {phase === "running" ? (
              <>
                <div className="tv-mockup-text bright">📡 …</div>
                <div className="tv-mockup-text" style={{ fontSize: 10 }}>
                  reaching · {state.tvModel || "your TV"}
                </div>
              </>
            ) : done ? (
              <>
                <div className="tv-mockup-text bright">— check your TV —</div>
                <div className="tv-mockup-text">{result?.sent ? "did it mute?" : "press mute — did it react?"}</div>
              </>
            ) : (
              <>
                <div className="tv-mockup-text">TV idle</div>
                <div className="tv-mockup-text" style={{ fontSize: 10 }}>
                  {state.tvModel || "—"}
                </div>
              </>
            )}
          </div>
          <div className="stand" />
        </div>
      </div>
      <FooterNav go={go} back="step4_adb_warn" />
    </div>
  );
}

// ============================================================
// STEP 5 —Test failed
// ============================================================
export function Step4Fail({ go, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Let's figure out why.</h1>
        <p className="screen-subtitle">
          An unsupported TV never ends the wizard — even if we can't drive it, you'll
          land on manual switching.
        </p>
      </div>
      <div className="stack">
        <DiagnoseTile
          go={go}
          icon="plug"
          title="Pairing wasn't accepted / debugging off"
          desc="Most common. Re-check the on-TV prompt, or enable Developer Options → USB debugging."
          action="Retry the test"
          target="step4_adb_warn"
        />
        <DiagnoseTile
          go={go}
          icon="network"
          title="Connected, but the command did nothing"
          desc="ADB connected fine but the TV ignored the keycode. We'll flag this and use a fallback for HDMI input later."
          action="Flag as 'input-finding deferred'"
          target="step5_intro"
          tag="advanced"
          onClick={() => set({ tvAdbWeak: true, tvVerified: true })}
        />
        <DiagnoseTile
          go={go}
          icon="cross"
          title="Nothing reached the TV at all"
          desc="Wrong IP, wrong subnet, or guest-WiFi / VLAN split. Try a different backend, or fall back to manual switching."
          action="Drop to manual switching"
          target="step5_intro"
          onClick={() => set({ tvManualSwitch: true, tvVerified: true })}
        />
      </div>
      <FooterNav go={go} back="step4_test" />
    </div>
  );
}

type DiagnoseTileProps = {
  go: (id: ScreenId) => void;
  icon: IconName;
  title: string;
  desc: string;
  action: string;
  target: ScreenId;
  tag?: string;
  onClick?: () => void;
};

function DiagnoseTile({ go, icon, title, desc, action, target, tag, onClick }: DiagnoseTileProps) {
  return (
    <button
      className="tile"
      onClick={() => {
        if (onClick) onClick();
        go(target);
      }}
    >
      <div className="tile-icon">
        <Icon name={icon} size={20} />
      </div>
      <div className="tile-body">
        <div className="tile-title">
          {title} {tag && <span className="tile-badge advanced">{tag}</span>}
        </div>
        <div className="tile-desc">{desc}</div>
      </div>
      <span className="chip accent">
        {action} <Icon name="chevR" size={11} />
      </span>
    </button>
  );
}

