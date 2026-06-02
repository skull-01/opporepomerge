import { useState } from "react";
import { Icon } from "../icons";
import { FooterNav } from "../shell/FooterNav";
import { BrandIcon } from "../shell/BrandIcon";
import { avrAddonBackend } from "../mapping";
import { isAvrChain } from "../steps";
import { invoke } from "../ipc";
import type { PortResult } from "../probes";
import {
  AVR_REGIONS,
  BUNDLED_AVR_DB,
  fetchRemoteAvrDb,
  isNewer,
  modelsForBrand,
  modelsForRegion,
  resolveBackend,
  resolvePlatform,
  type AvrDb,
  type AvrDbModel,
  type AvrRegion,
} from "../avrdb";
import type { ScreenProps } from "./types";

/** A representative "player input" name per add-on backend, shown as the field placeholder. */
function inputPlaceholder(addonBackend: string | null): string {
  switch (addonBackend) {
    case "denon_marantz":
      return "BD";
    case "yamaha_yxc":
      return "hdmi3";
    case "onkyo_eiscp":
    case "pioneer_eiscp":
      return "BD/DVD";
    default:
      return "input";
  }
}

/**
 * The TCP control port to knock on for a Step-6 reachability probe, per resolved add-on
 * backend. null means there is no simple TCP check: Sony's Audio Control API is an
 * authenticated HTTP service (PSK) and custom_command brands have no native driver. Ports
 * mirror resources/lib/avr/avr_presets.py (Denon/Marantz telnet 23, Yamaha YXC HTTP 80,
 * Onkyo/Pioneer eISCP 60128).
 */
function controlProbePort(addonBackend: string | null): number | null {
  switch (addonBackend) {
    case "denon_marantz":
      return 23;
    case "yamaha_yxc":
      return 80;
    case "onkyo_eiscp":
    case "pioneer_eiscp":
      return 60128;
    default:
      return null;
  }
}

// ============================================================
// STEP 7 —AV receiver (optional). The AVR DB is the TV DB's twin: candidate control-path
// mappings (validated:false) surfaced advisorily. The whole step is skippable — AV-receiver
// automation is off by default in the add-on, so the chain works without one.
// ============================================================
const AVR_BRANDS = [
  { id: "denon",   name: "Denon",   ch: "D",    color: "#0B0B0C", hint: "AVR-X · HEOS" },
  { id: "marantz", name: "Marantz", ch: "M",    color: "#16110B", hint: "Cinema · HEOS" },
  { id: "yamaha",  name: "Yamaha",  ch: "Y",    color: "#5B1A8B", hint: "MusicCast · YXC" },
  { id: "onkyo",   name: "Onkyo",   ch: "O",    color: "#7A2230", hint: "eISCP" },
  { id: "pioneer", name: "Pioneer", ch: "P",    color: "#C8102E", hint: "Elite · eISCP" },
  { id: "integra", name: "Integra", ch: "INT",  color: "#1F2937", hint: "eISCP" },
  { id: "sony",    name: "Sony",    ch: "SONY", color: "#0B0B0C", hint: "ES · Audio API" },
  { id: "anthem",  name: "Anthem",  ch: "A",    color: "#B0883B", hint: "MRX · custom" },
  { id: "arcam",   name: "Arcam",   ch: "AR",   color: "#1F3A5F", hint: "custom IP" },
  { id: "nad",     name: "NAD",     ch: "NAD",  color: "#374151", hint: "BluOS · custom" },
] as const;

const AVR_YEARS = ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"];

// ============================================================
// STEP 7 —Ask: do you have a receiver at all?
// ============================================================
export function Step6Ask({ go, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <div className="screen-num">7</div>
        <h1 className="screen-title">Do you use an AV receiver?</h1>
        <p className="screen-subtitle">
          If your sound runs through an AV receiver or processor (player → receiver → TV), pick
          it here so we can note the right control path. No receiver? Skip — the chain works
          without one, and receiver automation is off by default.
        </p>
      </div>
      <div className="grid-2">
        <button className="tile" onClick={() => go("step6_brand")}>
          <div className="tile-icon">
            <Icon name="avr" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">Yes — pick my receiver</div>
            <div className="tile-desc">
              Choose your brand and model. We'll show the candidate control backend for it
              (Denon/Marantz IP, Yamaha YXC, Onkyo/Pioneer/Integra eISCP, Sony Audio API).
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
        <button
          className="tile"
          onClick={() => {
            set({ avrBrand: null, avrModel: null, avrBackend: null, avrReceiverType: null });
            go("test_setup");
          }}
        >
          <div className="tile-icon">
            <Icon name="cross" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">No receiver — skip this step</div>
            <div className="tile-desc">
              Audio goes straight from the player to the TV (or the player handles it). Nothing
              to configure here.
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
          These are <strong>candidate mappings</strong>, not hardware-validated. Most receivers
          need Network Standby / IP Control enabled for reliable control after standby.
        </div>
      </div>
      <FooterNav go={go} back="step5_done" />
    </div>
  );
}

// ============================================================
// STEP 7 —Brand
// ============================================================
export function Step6Brand({ go, state, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Your AV receiver</h1>
        <p className="screen-subtitle">
          Pick the brand. The control path comes from the brand's protocol family — your exact
          model just narrows the list and confirms the candidate backend.
        </p>
      </div>
      <div className="brand-grid">
        {AVR_BRANDS.map((b) => (
          <button
            key={b.id}
            className={`brand-pill ${state.avrBrand === b.id ? "selected" : ""}`.trim()}
            onClick={() => {
              set({ avrBrand: b.id });
              go("step6_model");
            }}
          >
            <BrandIcon slug={b.id} ch={b.ch} color={b.color} fallbackIcon="avr" />
            <div>{b.name}</div>
            <div className="muted" style={{ fontSize: 10.5, fontWeight: 500 }}>{b.hint}</div>
          </button>
        ))}
      </div>
      <FooterNav go={go} back="step6_ask" />
    </div>
  );
}

// ============================================================
// STEP 7 —Model
// ============================================================
export function Step6Model({ go, state, set }: ScreenProps) {
  const [db, setDb] = useState<AvrDb>(BUNDLED_AVR_DB);
  const [region, setRegion] = useState<AvrRegion | null>(state.avrRegion ?? "US");
  const [year, setYear] = useState("");
  const [search, setSearch] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const brandName = AVR_BRANDS.find((b) => b.id === state.avrBrand)?.name ?? "receiver";
  const models = state.avrBrand ? modelsForBrand(db, state.avrBrand) : [];
  const filtered = modelsForRegion(models, region).filter(
    (m) =>
      (!year || String(m.year) === year) &&
      m.name.toLowerCase().includes(search.toLowerCase())
  );

  const pickRegion = (r: AvrRegion) => {
    const next = region === r ? null : r;
    setRegion(next);
    set({ avrRegion: next });
  };

  const refresh = async () => {
    setRefreshing(true);
    const remote = await fetchRemoteAvrDb();
    if (remote && isNewer(db, remote)) setDb(remote);
    setRefreshing(false);
  };

  const select = (m: AvrDbModel) => {
    set({
      avrModel: m.id,
      avrBackend: resolveBackend(db, m),
      avrReceiverType: m.receiver_type,
    });
  };

  const useCustom = () => {
    set({ avrModel: "custom", avrBackend: "custom_command", avrReceiverType: null });
    go("test_setup");
  };

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Which {brandName} receiver?</h1>
        <p className="screen-subtitle">
          Region and year just narrow the list — the control method comes from the protocol
          family. All rows are candidate mappings, not hardware-validated.
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
          <button className="btn ghost sm" onClick={useCustom}>
            <Icon name="terminal" size={13} /> Not listed → custom
          </button>
        </div>
        <div className="row" style={{ gap: 8, alignItems: "center" }}>
          <span className="muted" style={{ fontSize: 12, fontWeight: 500 }}>Region</span>
          <div className="filter-row">
            {AVR_REGIONS.map((r) => (
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
            {AVR_YEARS.map((y) => (
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

        <div className="model-list">
          {filtered.length === 0 && (
            <div className="model-row" style={{ justifyContent: "center", color: "var(--muted)" }}>
              No matches — adjust the filters or{" "}
              <button className="btn ghost sm" onClick={useCustom}>
                use a custom command
              </button>
            </div>
          )}
          {filtered.map((m) => {
            const backend = resolveBackend(db, m);
            const fallbacks = m.fallback_backends ?? [];
            return (
              <div
                key={m.id}
                className={`model-row ${state.avrModel === m.id ? "selected" : ""}`.trim()}
                onClick={() => select(m)}
                title={m.control_notes ?? m.region_notes ?? ""}
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
                    {m.regions.join(" · ")} · {m.receiver_type}
                  </div>
                </div>
                <span className="chip accent">
                  <span className="chip-dot" />
                  candidate
                </span>
              </div>
            );
          })}
        </div>

        {state.avrModel && state.avrModel !== "custom" && (
          <AvrControlCard state={state} set={set} />
        )}
      </div>
      <FooterNav
        go={go}
        back="step6_brand"
        next={state.avrModel ? "test_setup" : null}
        nextLabel="Continue to test"
      />
    </div>
  );
}

// ============================================================
// STEP 7 —Control config (IP + player input). Shown once a real model is picked. This is what
// flows into the add-on settings (avr_backend/avr_host/avr_player_input + avr_control_enabled);
// the mapping in mapping.ts decides whether control is auto-enabled.
// ============================================================
function AvrControlCard({ state, set }: Pick<ScreenProps, "state" | "set">) {
  const addonBackend = avrAddonBackend(state.avrBackend, state.avrBrand);
  const isSony = addonBackend === "sony_audio_api";
  const isCustom = addonBackend === null; // custom_command brands (Anthem/Arcam/NAD)
  const willEnable = !!addonBackend && !isSony && !!state.avrIp && !!state.avrPlayerInput;
  const sonyReady =
    isSony &&
    state.avrSonyAcknowledged &&
    !!state.avrSonyPsk &&
    !!state.avrSonyPlayerInputUri &&
    !!state.avrIp &&
    !!state.avrPlayerInput;
  const ph = inputPlaceholder(addonBackend);
  const probePort = controlProbePort(addonBackend);
  const [probing, setProbing] = useState(false);
  const [reach, setReach] = useState<PortResult | null>(null);
  const runProbe = async () => {
    if (probePort == null || !state.avrIp) return;
    setProbing(true);
    try {
      const r = await invoke<PortResult[]>("tv_port_probe", {
        host: state.avrIp,
        ports: [probePort],
      });
      setReach(r[0] ?? { port: probePort, open: false });
    } catch {
      setReach({ port: probePort, open: false });
    } finally {
      setProbing(false);
    }
  };

  return (
    <div className="card">
      <h2 className="section-title">Receiver control (optional)</h2>
      {isCustom ? (
        <div className="callout info">
          <span className="callout-icon">
            <Icon name="info" size={13} stroke={2.2} />
          </span>
          <div className="callout-body">
            <strong>No native backend yet.</strong> Anthem/Arcam/NAD don't have a first-class
            add-on driver — your selection is recorded, but you'll drive the receiver with the
            add-on's custom command profile. We won't write AVR control settings for it.
          </div>
        </div>
      ) : (
        <>
          <div className="grid-2" style={{ alignItems: "start" }}>
            <div className="field">
              <label className="field-label">Receiver IP</label>
              <input
                className="input"
                value={state.avrIp}
                onChange={(e) => set({ avrIp: e.target.value })}
              />
              <div className="field-hint">
                On your LAN. Enable Network Standby / IP Control on the receiver.
              </div>
            </div>
            <div className="field">
              <label className="field-label">Player input on the receiver</label>
              <input
                className="input"
                placeholder={ph}
                value={state.avrPlayerInput}
                onChange={(e) => set({ avrPlayerInput: e.target.value })}
              />
              <div className="field-hint">
                The receiver input the OPPO is plugged into (e.g. <code>{ph}</code>).
              </div>
            </div>
          </div>
          {!isSony && isAvrChain(state.topology) && (
            <div className="field" style={{ marginTop: 12 }}>
              <label className="field-label">Kodi input on the receiver</label>
              <input
                className="input"
                placeholder="e.g. CBL/SAT"
                value={state.avrKodiInput}
                onChange={(e) => set({ avrKodiInput: e.target.value })}
              />
              <div className="field-hint">
                The receiver input your Kodi box is plugged into — the receiver switches back
                here when playback ends. Leave blank to skip the restore step.
              </div>
            </div>
          )}
          {probePort != null && (
            <div className="row" style={{ gap: 10, alignItems: "center", marginTop: 4 }}>
              <button
                className="btn ghost sm"
                onClick={runProbe}
                disabled={probing || !state.avrIp}
              >
                <Icon name="search" size={13} /> {probing ? "Probing…" : "Test reachability"}
              </button>
              {reach && (
                <span
                  className={reach.open ? "success-text" : "muted"}
                  style={{ fontSize: 12.5 }}
                >
                  {reach.open
                    ? `Port ${probePort} answered — the receiver looks reachable.`
                    : `Port ${probePort} didn't answer — check the IP, that the receiver is powered on, and that Network Standby / IP Control is on.`}
                </span>
              )}
            </div>
          )}
          {isSony ? (
            <>
              <div className="grid-2" style={{ alignItems: "start" }}>
                <div className="field">
                  <label className="field-label">Sony API input URI</label>
                  <input
                    className="input"
                    placeholder="extInput:hdmi?port=2"
                    value={state.avrSonyPlayerInputUri}
                    onChange={(e) => set({ avrSonyPlayerInputUri: e.target.value })}
                  />
                  <div className="field-hint">
                    The Audio Control API addresses inputs by URI (e.g.{" "}
                    <code>extInput:hdmi?port=2</code>), not the plain name above.
                  </div>
                </div>
                <div className="field">
                  <label className="field-label">Pre-Shared Key (PSK)</label>
                  <input
                    className="input"
                    type="password"
                    value={state.avrSonyPsk}
                    onChange={(e) => set({ avrSonyPsk: e.target.value })}
                  />
                  <div className="field-hint">
                    Set on the receiver under IP Control / Authentication. Saved to the add-on
                    settings and handled as a secret.
                  </div>
                </div>
              </div>
              <div className="row" style={{ gap: 10, alignItems: "flex-start", marginTop: 4 }}>
                <button
                  type="button"
                  role="switch"
                  aria-checked={state.avrSonyAcknowledged}
                  className={`toggle ${state.avrSonyAcknowledged ? "on" : ""}`.trim()}
                  style={{ flexShrink: 0, marginTop: 2 }}
                  onClick={() => set({ avrSonyAcknowledged: !state.avrSonyAcknowledged })}
                />
                <span style={{ fontSize: 12.5, color: "var(--text-soft)" }}>
                  I understand the Sony Audio Control API path is <strong>experimental</strong> and
                  unvalidated — enable control on my receiver anyway.
                </span>
              </div>
              {sonyReady ? (
                <div className="callout success">
                  <span className="callout-icon">
                    <Icon name="check" size={13} stroke={2.2} />
                  </span>
                  <div className="callout-body">
                    We'll enable Sony control with <code>sony_audio_api</code>: power on and switch
                    to <code>{state.avrSonyPlayerInputUri}</code> on handoff. Experimental candidate
                    mapping — confirm against your receiver.
                  </div>
                </div>
              ) : (
                <div className="callout warn">
                  <span className="callout-icon">
                    <Icon name="warn" size={13} stroke={2.2} />
                  </span>
                  <div className="callout-body">
                    <strong>Sony stays off until it's complete.</strong> We'll save the backend, IP
                    and input as <code>sony_audio_api</code>, but control needs the IP, player
                    input, the API input URI, the PSK, and the acknowledgement above before we
                    enable it.
                  </div>
                </div>
              )}
            </>
          ) : willEnable ? (
            <div className="callout success">
              <span className="callout-icon">
                <Icon name="check" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                We'll enable AVR control with the <code>{addonBackend}</code> backend: power on
                and switch to <code>{state.avrPlayerInput}</code> on handoff.
                {isAvrChain(state.topology) && state.avrKodiInput && (
                  <> On exit it returns to <code>{state.avrKodiInput}</code>.</>
                )}{" "}
                All candidate mappings — confirm against your receiver.
              </div>
            </div>
          ) : (
            <div className="callout info">
              <span className="callout-icon">
                <Icon name="info" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                Add the receiver IP and player input to enable automatic control with the{" "}
                <code>{addonBackend}</code> backend. Leave them blank to record the receiver
                without enabling control.
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
