import { useState } from "react";
import { Icon } from "../icons";
import { FooterNav } from "../shell/FooterNav";
import { BrandIcon } from "../shell/BrandIcon";
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

// ============================================================
// STEP 5 — AV receiver (optional). The AVR DB is the TV DB's twin: candidate control-path
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

const AVR_YEARS = ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"];

// ============================================================
// STEP 5 — Ask: do you have a receiver at all?
// ============================================================
export function Step5Ask({ go, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <div className="screen-num">5</div>
        <h1 className="screen-title">Do you use an AV receiver?</h1>
        <p className="screen-subtitle">
          If your sound runs through an AV receiver or processor (player → receiver → TV), pick
          it here so we can note the right control path. No receiver? Skip — the chain works
          without one, and receiver automation is off by default.
        </p>
      </div>
      <div className="grid-2">
        <button className="tile" onClick={() => go("step5_brand")}>
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
      <FooterNav go={go} back="step4_done" />
    </div>
  );
}

// ============================================================
// STEP 5 — Brand
// ============================================================
export function Step5Brand({ go, state, set }: ScreenProps) {
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
              go("step5_model");
            }}
          >
            <BrandIcon slug={b.id} ch={b.ch} color={b.color} fallbackIcon="avr" />
            <div>{b.name}</div>
            <div className="muted" style={{ fontSize: 10.5, fontWeight: 500 }}>{b.hint}</div>
          </button>
        ))}
      </div>
      <FooterNav go={go} back="step5_ask" />
    </div>
  );
}

// ============================================================
// STEP 5 — Model
// ============================================================
export function Step5Model({ go, state, set }: ScreenProps) {
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
      </div>
      <FooterNav
        go={go}
        back="step5_brand"
        next={state.avrModel ? "test_setup" : null}
        nextLabel="Continue to test"
      />
    </div>
  );
}
