import { useState } from "react";
import { Icon } from "../icons";
import { invoke } from "../ipc";
import { DiagLog, type DiagCheck } from "../shell/DiagLog";
import { FooterNav } from "../shell/FooterNav";
import { BrandIcon } from "../shell/BrandIcon";
import { parseOppoPowerReply, parseOppoVerboseMode, parseSvm3Accepted } from "../probes";
import { deriveRewrite, parseOppoPlayingPath } from "../nas_path";
import { PLAYER_BRANDS, hwModelFor, isWakeRewriteBrand } from "../players";
import { BUNDLED_PLAYERS_DB, modelWakeCommand, playerModelByHw } from "../playersdb";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 3 —Player brand + model + IP
// ============================================================
export function Step2Brand({ go, state, set }: ScreenProps) {
  const selected = PLAYER_BRANDS.find((b) => b.id === state.playerBrand);
  const selectedModel =
    state.playerBrand && state.playerModel
      ? playerModelByHw(BUNDLED_PLAYERS_DB, hwModelFor(state.playerBrand, state.playerModel) ?? "")
      : null;
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
            {selectedModel && (
              <div className="model-row-meta" style={{ marginTop: 8 }}>
                markets {selectedModel.regions.join(" · ")} · wake{" "}
                <code>{selectedModel.wake_command}</code> ·{" "}
                {selectedModel.hardware_class.replace(/_/g, " ")}
                {selectedModel.nas_playback_candidate && <> · NAS-playback candidate</>}
              </div>
            )}
            <div className="divider" />
            <div className="field">
              <label className="field-label">Player IP</label>
              <input
                className="input"
                value={state.playerIp}
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
                asleep and won't answer until woken.{" "}
                {selectedModel ? (
                  <>
                    We'll wake with <code>{selectedModel.wake_command}</code>{" "}
                    {selectedModel.wake_command === "#EJT"
                      ? "(eject-to-wake)"
                      : "(power-on — this model drives CEC over the network)"}{" "}
                    before any other command.
                  </>
                ) : (
                  <>We'll use the right wake command for the model you pick first.</>
                )}
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

      {selected && selectedModel && <OppoNasPathCard state={state} set={set} />}

      <FooterNav
        go={go}
        back="step0_chain"
        next={state.playerBrand && state.playerModel ? "step2_test" : null}
        nextLabel="Continue to control test"
      />
    </div>
  );
}

// ============================================================
// STEP 3 —Wake & confirm test
// ============================================================
type WakePhase = "ready" | "running" | "pass" | "fail";
type Svm3Phase = "idle" | "running" | "supported" | "unsupported";

export function Step2Test({ go, state, set }: ScreenProps) {
  const [phase, setPhase] = useState<WakePhase>("ready");
  const [reply, setReply] = useState("");
  const [svm3Phase, setSvm3Phase] = useState<Svm3Phase>("idle");
  const isClone = isWakeRewriteBrand(state.playerBrand);
  // Wake command is PER-MODEL (e.g. M9205 family -> #PON, M9702/M9702-Plus -> #EJT),
  // not brand-level. This command is actually sent to the player below, so it must
  // match the selected model -- a brand heuristic would eject-wake an M9205.
  const selectedModel =
    state.playerBrand && state.playerModel
      ? playerModelByHw(BUNDLED_PLAYERS_DB, hwModelFor(state.playerBrand, state.playerModel) ?? "")
      : null;
  const wakeCmd = modelWakeCommand(selectedModel);

  // Capability probe for OPPO verbose mode 3, reusing the same oppo_query command as the power
  // test (no new Rust command). It queries the current mode (#QVM), tries #SVM 3, then restores
  // the previous mode so it leaves the player untouched. The result recommends the Playback-mode
  // default at Step 3; it never fails the power test (legacy works regardless).
  const probeSvm3 = async () => {
    setSvm3Phase("running");
    try {
      const qvm = await invoke<string>("oppo_query", {
        host: state.playerIp,
        port: 23,
        command: "#QVM",
      });
      const previousMode = parseOppoVerboseMode(qvm);
      const svm = await invoke<string>("oppo_query", {
        host: state.playerIp,
        port: 23,
        command: "#SVM 3",
      });
      const ok = parseSvm3Accepted(svm);
      if (previousMode) {
        await invoke("oppo_query", {
          host: state.playerIp,
          port: 23,
          command: `#SVM ${previousMode}`,
        });
      }
      // Record the probe result, but don't override an explicit Pure HTTP (http) choice -- the
      // default preset is Pure HTTP, and the player test only recommends svm3-vs-legacy.
      set(
        state.monitorMode === "http"
          ? { svm3Supported: ok }
          : { svm3Supported: ok, monitorMode: ok ? "svm3" : "legacy" },
      );
      setSvm3Phase(ok ? "supported" : "unsupported");
    } catch {
      set(state.monitorMode === "http" ? { svm3Supported: false } : { svm3Supported: false, monitorMode: "legacy" });
      setSvm3Phase("unsupported");
    }
  };

  const wakeAndConfirm = async () => {
    setPhase("running");
    setReply("");
    setSvm3Phase("idle");
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
      if (parseOppoPowerReply(raw) === "on") {
        setPhase("pass");
        void probeSvm3();
      } else {
        setPhase("fail");
      }
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
                  go("step3_mode");
                }}
              >
                Continue — set up your TV <Icon name="chevR" size={14} />
              </button>
            )}
            <button className="btn outline" onClick={() => go("step2_fail")}>
              Test didn't work
            </button>
          </div>
          {svm3Phase !== "idle" && (
            <div className={`callout ${svm3Phase === "supported" ? "info" : ""}`.trim()}>
              <span className="callout-icon">
                <Icon name={svm3Phase === "supported" ? "spark" : "info"} size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                {svm3Phase === "running" ? (
                  <>Checking SVM3 (verbose mode 3) support…</>
                ) : svm3Phase === "supported" ? (
                  <>
                    <strong>SVM3 supported.</strong> Your player accepts verbose mode 3 — we&apos;ll
                    recommend the SVM3 monitor at the next step. You can still choose Legacy.
                  </>
                ) : (
                  <>
                    <strong>SVM3 not detected.</strong> Your player didn&apos;t accept verbose mode
                    3, so the next step defaults to the Legacy monitor. Two-way control still works.
                  </>
                )}
              </div>
            </div>
          )}
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
// STEP 3 —Test failed
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

// ============================================================
// OPPO media-path capture (Phase 1b; http_handoff path rewrite, issue #173)
// ============================================================
function OppoNasPathCard({ state, set }: Pick<ScreenProps, "state" | "set">) {
  const [kodiPath, setKodiPath] = useState("");
  const [oppoPath, setOppoPath] = useState("");
  const [busy, setBusy] = useState<"" | "kodi" | "oppo">("");
  const [note, setNote] = useState("");
  const [manual, setManual] = useState(false);

  const captureKodi = async () => {
    setBusy("kodi");
    setNote("");
    try {
      const p = await invoke<string | null>("kodi_now_playing", {
        host: state.kodiIp,
        user: state.sshUser,
      });
      if (p) setKodiPath(p);
      else setNote("Kodi reported nothing playing — start the file in Kodi, then capture.");
    } catch (e) {
      setNote(`Kodi query failed: ${String(e)}`);
    }
    setBusy("");
  };

  const readOppo = async () => {
    setBusy("oppo");
    setNote("");
    try {
      const raw = await invoke<string>("oppo_playback_info", { host: state.playerIp });
      const found = parseOppoPlayingPath(raw);
      if (found) setOppoPath(found);
      else setNote("Couldn't read a path from the OPPO — type the path it shows for this file.");
    } catch (e) {
      setNote(`OPPO read failed: ${String(e)}`);
    }
    setBusy("");
  };

  const rewrite = deriveRewrite(kodiPath, oppoPath);
  const saved =
    rewrite !== null && state.oppoPathFrom === rewrite.from && state.oppoPathTo === rewrite.to;

  return (
    <div className="card" style={{ marginTop: 18 }}>
      <h2 className="section-title">OPPO media path (http_handoff launch)</h2>
      <p className="muted" style={{ fontSize: 12.5, marginTop: -2 }}>
        Play one file <strong>both</strong> ways and we map the path the OPPO needs. Only used by
        the <code>http_handoff</code> launch — skip it for the other modes.
      </p>

      <div className="field">
        <label className="field-label">Path as Kodi sees it</label>
        <div className="row" style={{ gap: 8 }}>
          <input
            className="input"
            value={kodiPath}
            placeholder="smb://10.0.1.10/Movies/Film.iso"
            onChange={(e) => setKodiPath(e.target.value)}
          />
          <button className="btn outline" disabled={busy !== ""} onClick={captureKodi}>
            {busy === "kodi" ? "Reading…" : "Capture from Kodi"}
          </button>
        </div>
        <div className="field-hint">Play the file in Kodi, then capture — read live over SSH.</div>
      </div>

      <div className="field">
        <label className="field-label">Path as the OPPO sees it</label>
        <div className="row" style={{ gap: 8 }}>
          <input
            className="input"
            value={oppoPath}
            placeholder="MyNAS/Movies/Film.iso"
            onChange={(e) => setOppoPath(e.target.value)}
          />
          <button className="btn outline" disabled={busy !== ""} onClick={readOppo}>
            {busy === "oppo" ? "Reading…" : "Read from OPPO"}
          </button>
        </div>
        <div className="field-hint">
          SMB <code>smb://host/share/…</code> · NFS <code>nfs://host/export/…</code> — the OPPO
          uses its own share label, not the IP.
        </div>
      </div>

      {note && (
        <div className="callout warn" style={{ marginTop: 4 }}>
          <div className="callout-body">{note}</div>
        </div>
      )}

      {rewrite ? (
        <div className="callout info" style={{ marginTop: 8 }}>
          <div className="callout-body">
            Rewrite <code>{rewrite.from}</code> → <code>{rewrite.to}</code>
            <div className="row" style={{ gap: 8, marginTop: 8 }}>
              <button
                className="btn primary"
                onClick={() => set({ oppoPathFrom: rewrite.from, oppoPathTo: rewrite.to })}
              >
                Use this mapping
              </button>
              {saved && <span className="success-text">Saved.</span>}
            </div>
          </div>
        </div>
      ) : kodiPath.trim() && oppoPath.trim() ? (
        <div className="muted" style={{ fontSize: 12, marginTop: 8 }}>
          Those paths don't share a common tail — are they the same file?
        </div>
      ) : null}

      <button
        className="btn outline"
        style={{ marginTop: 10, fontSize: 12 }}
        onClick={() => setManual((m) => !m)}
      >
        {manual ? "Hide manual entry" : "Enter the prefixes manually"}
      </button>
      {manual && (
        <div className="grid-2" style={{ marginTop: 8 }}>
          <div className="field">
            <label className="field-label">oppo_http_path_from</label>
            <input
              className="input"
              value={state.oppoPathFrom}
              placeholder="smb://10.0.1.10/Movies/"
              onChange={(e) => set({ oppoPathFrom: e.target.value })}
            />
          </div>
          <div className="field">
            <label className="field-label">oppo_http_path_to</label>
            <input
              className="input"
              value={state.oppoPathTo}
              placeholder="MyNAS/Movies/"
              onChange={(e) => set({ oppoPathTo: e.target.value })}
            />
          </div>
        </div>
      )}
    </div>
  );
}
