import { useState } from "react";
import { Icon } from "../icons";
import { invoke } from "@tauri-apps/api/core";
import { DiagLog, type DiagCheck } from "../shell/DiagLog";
import { FooterNav } from "../shell/FooterNav";
import { BrandIcon } from "../shell/BrandIcon";
import { parseOppoPowerReply } from "../probes";
import { PLAYER_BRANDS, isWakeRewriteBrand } from "../players";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 2 — Player brand + model + IP
// ============================================================
export function Step2Brand({ go, state, set }: ScreenProps) {
  const selected = PLAYER_BRANDS.find((b) => b.id === state.playerBrand);
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Your OPPO or clone</h1>
        <p className="screen-subtitle">
          Brand → model. We use this to pick the right wake command and posture — not a
          control backend (that's always IP control on port 23).
        </p>
      </div>

      <h3 className="sub-title">Brand</h3>
      <div className="brand-grid" style={{ marginBottom: 18 }}>
        {PLAYER_BRANDS.map((b) => (
          <button
            key={b.id}
            className={`brand-pill ${state.playerBrand === b.id ? "selected" : ""}`.trim()}
            onClick={() => set({ playerBrand: b.id, playerModel: null })}
          >
            <BrandIcon slug={b.id} ch={b.ch} color={b.color} fallbackIcon="player" />
            <div>{b.name}</div>
            <div className="muted" style={{ fontSize: 10.5, fontWeight: 500 }}>
              {b.posture === "stock"
                ? "stock wake"
                : b.posture === "wake-rewrite"
                  ? "eject-to-wake"
                  : "warning-only"}
            </div>
          </button>
        ))}
      </div>

      {selected && (
        <div className="grid-2" style={{ alignItems: "start" }}>
          <div className="card">
            <h2 className="section-title">{selected.name} models</h2>
            <div className="filter-row" style={{ gap: 8 }}>
              {selected.models.map((m) => (
                <button
                  key={m.label}
                  className={`filter-pill ${state.playerModel === m.label ? "selected" : ""}`.trim()}
                  onClick={() => set({ playerModel: m.label })}
                >
                  {m.label}
                </button>
              ))}
            </div>
            <div className="divider" />
            <div className="field">
              <label className="field-label">Player IP</label>
              <input
                className="input"
                defaultValue="10.0.1.77"
                onChange={(e) => set({ playerIp: e.target.value })}
              />
              <div className="field-hint">Port 23 — IP control. Reserve it on DHCP.</div>
            </div>
          </div>

          {selected.posture === "warning" ? (
            <div className="callout warn">
              <span className="callout-icon">
                <Icon name="warn" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                <strong>{selected.name} is warning-only.</strong> Commands are <em>not</em>{" "}
                mutated; we won't claim hardware compatibility until a tester report
                exists. You can continue — the rest of the setup still works.
              </div>
            </div>
          ) : selected.posture === "wake-rewrite" ? (
            <div className="callout info">
              <span className="callout-icon">
                <Icon name="bolt" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                <strong>Clone wake quirk handled.</strong> {selected.name} models can be
                asleep and won't answer until woken. We'll wake with <code>#EJT</code>{" "}
                (eject-to-wake) before any other command.
              </div>
            </div>
          ) : (
            <div className="callout info">
              <span className="callout-icon">
                <Icon name="info" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                <strong>Stock OPPO behavior.</strong> Wake is plain <code>#PON</code>;{" "}
                <code>#POW</code> and <code>#PLA</code> are passed through unchanged.
              </div>
            </div>
          )}
        </div>
      )}

      <FooterNav
        go={go}
        back="step1_intro"
        next={state.playerBrand && state.playerModel ? "step2_test" : null}
        nextLabel="Continue to control test"
      />
    </div>
  );
}

// ============================================================
// STEP 2 — Wake & confirm test
// ============================================================
type WakePhase = "ready" | "running" | "pass" | "fail";

export function Step2Test({ go, state, set }: ScreenProps) {
  const [phase, setPhase] = useState<WakePhase>("ready");
  const [reply, setReply] = useState("");
  const isClone = isWakeRewriteBrand(state.playerBrand);
  const wakeCmd = isClone ? "#EJT" : "#PON";

  const wakeAndConfirm = async () => {
    setPhase("running");
    setReply("");
    try {
      await invoke("oppo_query", { host: state.playerIp, port: 23, command: wakeCmd });
      const raw = await invoke<string>("oppo_query", {
        host: state.playerIp,
        port: 23,
        command: "#QPW",
      });
      setReply(raw);
      // Pass only when the player actually reports power ON. A non-empty reply that is OFF or
      // an "@QPW ER" error must NOT count as confirmed two-way control.
      setPhase(parseOppoPowerReply(raw) === "on" ? "pass" : "fail");
    } catch {
      setPhase("fail");
    }
  };

  const power = parseOppoPowerReply(reply);
  const gotReply = reply.trim() !== "";
  const baseChecks: DiagCheck[] = [
    {
      // TCP was reachable if any reply came back, even one that didn't confirm power.
      status: phase === "pass" || gotReply ? "pass" : phase === "fail" ? "fail" : "pending",
      label: "TCP :23 reachable",
      detail: phase !== "ready" ? state.playerIp : "",
    },
    {
      status:
        phase === "pass" ? "pass" : phase === "running" ? "run" : phase === "fail" ? "fail" : "pending",
      label: `Wake with ${wakeCmd}`,
      detail: phase !== "ready" ? `${wakeCmd} sent` : "",
    },
    {
      status: phase === "pass" ? "pass" : gotReply ? "fail" : "pending",
      label: "Query #QPW (status)",
      detail: gotReply ? `reply: ${reply}` : "",
    },
    {
      status: phase === "pass" ? "pass" : gotReply ? "fail" : "pending",
      label:
        phase === "pass"
          ? "Confirm: player powered ON"
          : gotReply
            ? `Confirm: player reported ${power.toUpperCase()} (not ON)`
            : "Confirm: player powered ON",
      detail: phase === "pass" ? "two-way IP control verified" : "",
    },
  ];

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">
          {isClone ? "Power on your player first." : "Test IP control."}
        </h1>
        <p className="screen-subtitle">
          {isClone ? (
            <>
              Clones can be asleep and won't answer until woken. Make sure your player is
              plugged in and in <strong>standby</strong> — not switched off at the wall —
              then we'll wake it and confirm control.
            </>
          ) : (
            <>
              We'll send a query the player <em>answers</em>, not a blind state-changing
              command. Two-way control or nothing.
            </>
          )}
        </p>
      </div>

      <div className="grid-2" style={{ alignItems: "start" }}>
        <div className="stack">
          <DiagLog
            title={isClone ? "Wake → confirm" : "IP control"}
            checks={baseChecks}
            footer={
              phase === "pass" ? (
                <>
                  <strong className="success-text">Two-way IP control confirmed.</strong>{" "}
                  Player answered to <code>#QPW</code> with <code>ON</code> after wake.
                </>
              ) : phase === "running" ? (
                <>Waking and querying — clones can take a few seconds to come up.</>
              ) : (
                <span className="muted">Click "Wake &amp; confirm" when the player is in standby.</span>
              )
            }
            footerKind={phase === "pass" ? "success" : ""}
          />
          <div className="row" style={{ gap: 10 }}>
            {phase === "ready" && (
              <button className="btn primary lg" onClick={wakeAndConfirm}>
                <Icon name="bolt" size={14} /> Wake &amp; confirm
              </button>
            )}
            {phase === "pass" && (
              <button
                className="btn primary lg"
                onClick={() => {
                  set({ playerVerified: true });
                  go("step3_brand");
                }}
              >
                Continue — set up your TV <Icon name="chevR" size={14} />
              </button>
            )}
            <button className="btn outline" onClick={() => go("step2_fail")}>
              Test didn't work
            </button>
          </div>
        </div>
        <div className="stack">
          <div className="player-mockup">
            <span className={`player-mockup-led ${phase === "ready" ? "standby" : ""}`.trim()} />
            <div className="player-mockup-screen">
              {phase === "ready" ? "STANDBY" : phase === "running" ? "WAKE…" : "ON  ·  READY"}
            </div>
          </div>
          <div className="callout info">
            <span className="callout-icon">
              <Icon name="info" size={13} stroke={2.2} />
            </span>
            <div className="callout-body">
              <strong>Quick Start</strong> may need to be on so the player stays reachable
              in standby. Plain "off at the wall" doesn't count — the network stack must
              stay alive to receive the wake.
            </div>
          </div>
        </div>
      </div>
      <FooterNav go={go} back="step2_brand" />
    </div>
  );
}

// ============================================================
// STEP 2 — Test failed
// ============================================================
export function Step2Fail({ go }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Player didn't respond.</h1>
        <p className="screen-subtitle">
          Ordered cheapest-first — the most common cause is at the top.
        </p>
      </div>
      <div className="stack">
        <HintTile
          num="1"
          title={'"IP Control" isn’t enabled'}
          desc="Setup → Device Setup → IP Control / Network Control → On. Wording varies by firmware. By far the most common cause."
        />
        <HintTile
          num="2"
          title="Wrong IP, or it changed"
          desc="Confirm in the player's network settings; reserve it on DHCP so it doesn't drift."
        />
        <HintTile
          num="3"
          title="Not on the same network"
          desc="Player and Kodi box must share the LAN/subnet — no guest WiFi, no VLAN split. (Your TV is irrelevant here — it had its own test.)"
        />
        <HintTile
          num="4"
          title="Standby, not off at the wall (clones)"
          desc="Plain power-off kills the network stack; the player can't receive a wake. Switch it to standby instead."
        />
      </div>
      <FooterNav go={go} back="step2_test" next="step2_test" nextLabel="Retry the test" />
    </div>
  );
}

function HintTile({ num, title, desc }: { num: string; title: string; desc: string }) {
  return (
    <div className="tile" style={{ cursor: "default" }}>
      <div
        className="tile-icon"
        style={{
          background: "var(--surface-2)",
          color: "var(--text-soft)",
          fontFamily: "var(--font-display)",
          fontWeight: 700,
        }}
      >
        {num}
      </div>
      <div className="tile-body">
        <div className="tile-title">{title}</div>
        <div className="tile-desc">{desc}</div>
      </div>
    </div>
  );
}
