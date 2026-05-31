import { useState, type ReactNode } from "react";
import { Icon, type IconName } from "../icons";
import { Chain } from "../shell/Chain";
import { DiagLog } from "../shell/DiagLog";
import { FooterNav } from "../shell/FooterNav";
import { applyToKodi, type ApplyResult } from "../apply";
import { isAvrChain, type ScreenId } from "../steps";
import type { ScreenProps } from "./types";

// ============================================================
// TEST — Setup (copy disc OR play your own)
// ============================================================
type TestMode = "disc" | "own" | null;

export function TestSetup({ go, state, set }: ScreenProps) {
  const [mode, setMode] = useState<TestMode>(state.testMode);
  const [copied, setCopied] = useState(false);

  const pick = (m: "disc" | "own") => {
    setMode(m);
    set({ testMode: m });
  };

  const nextScreen: ScreenId | null =
    (mode === "disc" && copied) || mode === "own" ? "test_confirm" : null;
  const nextLabel =
    mode === "own"
      ? "I played one — how did it go?"
      : "I rescanned and played it — how did it go?";

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Full setup test.</h1>
        <p className="screen-subtitle">
          End to end: handoff, TV switch, play, and Kodi-remote menu control. You pick how
          to test — use our bundled disc, or use one of your own files if you have a UHD
          ISO already in your library.
        </p>
      </div>

      {mode === null && (
        <div className="grid-2">
          <button className="tile" onClick={() => pick("disc")}>
            <div className="tile-icon">
              <Icon name="download" size={20} />
            </div>
            <div className="tile-body">
              <div className="tile-title">
                Use our test disc{" "}
                <span className="tile-badge recommended">Recommended</span>
              </div>
              <div className="tile-desc">
                We made a small UHD ISO ourselves — playable, with a navigable menu, named
                to trigger Kodi's eligibility rules. We'll copy it into your library so
                both Kodi and your player can see it.
              </div>
            </div>
            <Icon name="chevR" size={16} />
          </button>
          <button className="tile" onClick={() => pick("own")}>
            <div className="tile-icon">
              <Icon name="folder" size={20} />
            </div>
            <div className="tile-body">
              <div className="tile-title">Use one of your own files</div>
              <div className="tile-desc">
                Open Kodi on your box, browse to any UHD ISO you already have, and press
                Play. Faster — but only works if you've got a UHD-tagged disc image in
                your library already.
              </div>
            </div>
            <Icon name="chevR" size={16} />
          </button>
        </div>
      )}

      {mode !== null && (
        <div className="grid-2" style={{ alignItems: "start" }}>
          {mode === "disc" && (
            <div className="card">
              <div className="row-between" style={{ marginBottom: 10 }}>
                <h2 className="section-title" style={{ margin: 0 }}>
                  Where should we put the test disc?
                </h2>
                <button
                  className="btn ghost sm"
                  onClick={() => {
                    setMode(null);
                    setCopied(false);
                  }}
                >
                  <Icon name="chevL" size={12} /> Change
                </button>
              </div>
              <div className="stack">
                <div className="field">
                  <label className="field-label">Save location</label>
                  <div className="row" style={{ gap: 8 }}>
                    <input
                      className="input"
                      defaultValue="\\nas\Movies\_test\"
                      style={{ flex: 1 }}
                    />
                    <button className="btn outline sm">
                      <Icon name="folder" size={13} /> Browse…
                    </button>
                  </div>
                </div>
                <div className="callout warn">
                  <span className="callout-icon">
                    <Icon name="warn" size={13} stroke={2.2} />
                  </span>
                  <div className="callout-body">
                    Must be on the media library{" "}
                    <strong>both Kodi and your player use</strong> — not just a folder on
                    this PC. If your library is a NAS or shared folder, point here to that
                    share.
                  </div>
                </div>
                {!copied ? (
                  <button className="btn primary" onClick={() => setCopied(true)}>
                    <Icon name="download" size={13} /> Copy test disc
                  </button>
                ) : (
                  <DiagLog
                    title="Copying test disc"
                    checks={[
                      { status: "pass", label: "OPPO-Installer-Test-2160p.iso", detail: "4.2 GB · copied OK" },
                      { status: "pass", label: "Path eligibility tag", detail: "contains '2160p' · disc-style" },
                      { status: "pass", label: "Reachable from Kodi box", detail: "confirmed via SFTP read" },
                    ]}
                    footer={
                      <>
                        Copied. <strong>Rescan your Kodi library</strong> so the test file
                        appears, then play it from Kodi.
                      </>
                    }
                    footerKind="success"
                  />
                )}
              </div>
            </div>
          )}

          {mode === "own" && (
            <div className="card">
              <div className="row-between" style={{ marginBottom: 10 }}>
                <h2 className="section-title" style={{ margin: 0 }}>
                  Now go to Kodi and play an ISO.
                </h2>
                <button className="btn ghost sm" onClick={() => setMode(null)}>
                  <Icon name="chevL" size={12} /> Change
                </button>
              </div>
              <div className="stack">
                <div className="stack-sm">
                  <InstructionStep
                    n="1"
                    title="Open Kodi on your box"
                    desc={
                      <>
                        That's your{" "}
                        <span className="path">{state.kodiIp || "10.0.1.42"}</span>{" "}
                        machine — not this Windows PC.
                      </>
                    }
                  />
                  <InstructionStep
                    n="2"
                    title="Find any UHD ISO in your library"
                    desc={
                      <>
                        Filename should contain <span className="kbd">2160p</span>,{" "}
                        <span className="kbd">UHD</span>, or <span className="kbd">4K</span>{" "}
                        — that's what trips the eligibility rule. A{" "}
                        <span className="path">BDMV/</span> folder works too.
                      </>
                    }
                  />
                  <InstructionStep
                    n="3"
                    title="Press Play"
                    desc={
                      <>
                        Kodi should hand off to your player instead of starting playback
                        itself. Your TV should switch. The disc menu should appear.
                      </>
                    }
                  />
                  <InstructionStep
                    n="4"
                    title="Come back here when you're done"
                    desc={<>We'll ask three quick yes/no questions about what happened.</>}
                  />
                </div>
                <div className="callout info">
                  <span className="callout-icon">
                    <Icon name="info" size={13} stroke={2.2} />
                  </span>
                  <div className="callout-body">
                    <strong>Nothing tagged UHD in your library?</strong> Switch to our
                    test disc instead — we'll copy one that's correctly tagged.
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="stack">
            <div className="card">
              <h3 className="sub-title">What this verifies</h3>
              <div className="stack-sm" style={{ marginTop: 8 }}>
                <ChainCheckRow
                  icon="kodi"
                  label="Kodi launches the file"
                  detail="playercorefactory.xml routes it"
                />
                <ChainCheckRow
                  icon="tv"
                  label="TV switches input"
                  detail={`HDMI ${state.playerInput ?? 3}`}
                />
                <ChainCheckRow
                  icon="player"
                  label="Player picks it up"
                  detail="and starts the disc menu"
                />
                <ChainCheckRow
                  icon="remote"
                  label="Kodi remote drives the menu"
                  detail="remote-bridge keymap loaded"
                />
              </div>
            </div>
            {mode === "own" && (
              <div className="card" style={{ padding: 14 }}>
                <div className="row" style={{ gap: 10 }}>
                  <span className="chip">
                    <Icon name="kodi" size={11} /> Kodi box
                  </span>
                  <span className="muted" style={{ fontSize: 12 }}>→</span>
                  <span className="chip accent">
                    <Icon name="play" size={11} /> Play any UHD ISO
                  </span>
                </div>
                <div
                  className="muted"
                  style={{ fontSize: 11.5, marginTop: 8, fontFamily: "var(--font-mono)" }}
                >
                  we wait here · no commands sent until you tell us how it went
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <FooterNav
        go={go}
        back="step5_ask"
        next={nextScreen}
        nextLabel={nextLabel}
      />
    </div>
  );
}

function InstructionStep({ n, title, desc }: { n: string; title: string; desc: ReactNode }) {
  return (
    <div className="row" style={{ gap: 12, alignItems: "flex-start", padding: "6px 0" }}>
      <span
        style={{
          minWidth: 22,
          height: 22,
          borderRadius: "50%",
          background: "var(--accent-soft)",
          color: "var(--accent)",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 11,
          fontWeight: 700,
          fontFamily: "var(--font-display)",
          flexShrink: 0,
          marginTop: 1,
        }}
      >
        {n}
      </span>
      <div style={{ flex: 1 }}>
        <div
          style={{ fontSize: 13.5, fontWeight: 600, color: "var(--text)", marginBottom: 2 }}
        >
          {title}
        </div>
        <div style={{ fontSize: 12.5, color: "var(--muted)", lineHeight: 1.5 }}>{desc}</div>
      </div>
    </div>
  );
}

function ChainCheckRow({ icon, label, detail }: { icon: IconName; label: string; detail: string }) {
  return (
    <div className="row" style={{ gap: 10 }}>
      <span style={{ color: "var(--muted)" }}>
        <Icon name={icon} size={16} />
      </span>
      <span style={{ flex: 1, fontSize: 13 }}>{label}</span>
      <span
        className="muted"
        style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}
      >
        {detail}
      </span>
    </div>
  );
}

// ============================================================
// TEST — 3-question confirmation
// ============================================================
type Answer = boolean | null;
type Answers = { play: Answer; switch: Answer; menu: Answer };

export function TestConfirm({ go }: ScreenProps) {
  const [answers, setAnswers] = useState<Answers>({ play: null, switch: null, menu: null });
  const allAnswered =
    answers.play !== null && answers.switch !== null && answers.menu !== null;
  const allYes = answers.play === true && answers.switch === true && answers.menu === true;
  const nextScreen: ScreenId | null = !allAnswered
    ? null
    : allYes
      ? "test_success"
      : answers.play === false
        ? "step2_test"
        : answers.switch === false
          ? "step3_test"
          : "step1_intro";
  const nextLabel = !allAnswered
    ? undefined
    : allYes
      ? "See the summary"
      : answers.play === false
        ? "Fix routing → Step 2"
        : answers.switch === false
          ? "Fix TV → Step 3"
          : "Fix keymap → Step 1";

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">How did that go?</h1>
        <p className="screen-subtitle">
          Three honest yes/no questions. Any "no" routes you straight to the step that
          owns that piece — no detective work.
        </p>
      </div>
      <div className="stack">
        <Question
          n="1"
          label="Did the test disc start playing on your player?"
          owner="Step 2 · Player / playercorefactory routing"
          value={answers.play}
          onChange={(v) => setAnswers({ ...answers, play: v })}
        />
        <Question
          n="2"
          label="Did your TV switch to the player's input?"
          owner="Step 3 · TV / Step 4 input capture"
          value={answers.switch}
          onChange={(v) => setAnswers({ ...answers, switch: v })}
        />
        <Question
          n="3"
          label="Can you navigate the disc menu with your Kodi remote?"
          owner="Step 1 · keymap not loaded / Kodi not restarted"
          value={answers.menu}
          onChange={(v) => setAnswers({ ...answers, menu: v })}
        />
      </div>
      {allAnswered && !allYes && (
        <div className="callout warn" style={{ marginTop: 18 }}>
          <span className="callout-icon">
            <Icon name="warn" size={13} stroke={2.2} />
          </span>
          <div className="callout-body">
            We'll send you back to the step that owns the failing piece — your other
            answers stay intact.
          </div>
        </div>
      )}
      {allAnswered && allYes && (
        <div className="callout success" style={{ marginTop: 18 }}>
          <span className="callout-icon">
            <Icon name="check" size={13} stroke={2.2} />
          </span>
          <div className="callout-body">
            <strong>Setup verified end to end.</strong> Continue to the summary.
          </div>
        </div>
      )}
      <FooterNav go={go} back="test_setup" next={nextScreen} nextLabel={nextLabel} />
    </div>
  );
}

function Question({
  n,
  label,
  owner,
  value,
  onChange,
}: {
  n: string;
  label: string;
  owner: string;
  value: Answer;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className={`tile ${value !== null ? "selected" : ""}`.trim()} style={{ cursor: "default" }}>
      <div
        className="tile-icon"
        style={{
          background:
            value === true
              ? "var(--success-soft)"
              : value === false
                ? "var(--danger-soft)"
                : "var(--surface-2)",
          color:
            value === true
              ? "var(--success)"
              : value === false
                ? "var(--danger)"
                : "var(--muted)",
          fontWeight: 700,
          fontFamily: "var(--font-display)",
        }}
      >
        {value === true ? "✓" : value === false ? "✕" : n}
      </div>
      <div className="tile-body">
        <div className="tile-title">{label}</div>
        <div className="tile-desc">
          {value === false ? (
            <>
              Failure routes to → <strong>{owner}</strong>
            </>
          ) : (
            <>Failure would route to → {owner}</>
          )}
        </div>
      </div>
      <div className="row" style={{ gap: 6 }}>
        <button
          className={`filter-pill ${value === true ? "selected" : ""}`.trim()}
          onClick={() => onChange(true)}
        >
          Yes
        </button>
        <button
          className={`filter-pill ${value === false ? "selected" : ""}`.trim()}
          onClick={() => onChange(false)}
        >
          No
        </button>
      </div>
    </div>
  );
}

// ============================================================
// TEST — Success summary
// ============================================================
export function TestSuccess({ go, state }: ScreenProps) {
  const [applying, setApplying] = useState(false);
  const [result, setResult] = useState<ApplyResult | null>(null);

  const apply = async () => {
    setApplying(true);
    setResult(await applyToKodi(state));
    setApplying(false);
  };

  const applyLabel =
    state.tier === "A"
      ? "Apply to Kodi (SSH + restart)"
      : state.tier === "B"
        ? "Apply to Kodi (SMB)"
        : "Generate files to copy";

  return (
    <div className="screen">
      <div className="intro-hero">
        <div className="intro-eyebrow">
          <Icon name="check" size={12} stroke={2.4} />
          &nbsp;&nbsp;Setup verified, end to end
        </div>
        <h1 className="intro-title">Your chain works.</h1>
        <p className="intro-body">
          Kodi hands off, your TV switches, the player picks up, and your Kodi remote
          drives the disc menu. Nothing else to do here — you can close this app.
        </p>

        <div className="card" style={{ width: "100%", marginBottom: 16 }}>
          <h3 className="sub-title">Your chain</h3>
          <div style={{ marginTop: 10 }}>
            <Chain active="all" completed={{ media: true, kodi: true, tv: true, player: true }} />
          </div>
          <div className="divider" />
          <div className="stack-sm">
            <SummaryRow
              label="Kodi box"
              value={`${state.kodiIp || "10.0.1.42"} · ${
                state.tier === "A"
                  ? "Auto-write + auto-apply"
                  : state.tier === "B"
                    ? "Auto-write (SMB)"
                    : "Manual"
              }`}
            />
            <SummaryRow
              label="TV"
              value={`${state.tvModel || "TCL 65Q9"} · backend ${state.tvBackend || "adb"}${
                state.tvAdbWeak ? " (input fallback)" : ""
              }`}
            />
            <SummaryRow
              label="Player"
              value={`${state.playerBrand === "chinoppo" ? "Chinoppo" : "OPPO"} ${
                state.playerModel || "M9205 V1"
              } · ${state.playerIp || "10.0.1.77"}`}
            />
            {state.avrBrand && (
              <SummaryRow
                label="Receiver"
                value={`${state.avrBrand} · backend ${state.avrBackend ?? "—"}`}
              />
            )}
            <SummaryRow
              label="Switch to"
              value={
                isAvrChain(state.topology)
                  ? `Receiver ${state.avrPlayerInput || "input"}`
                  : `HDMI ${state.playerInput ?? 3}`
              }
            />
            <SummaryRow
              label="Return to"
              value={
                isAvrChain(state.topology)
                  ? `Receiver ${state.avrKodiInput || "input"}`
                  : `HDMI ${state.kodiInput ?? 1}`
              }
            />
          </div>
        </div>

        {result && (
          <div
            className={`callout ${result.ok ? "success" : "warn"}`}
            style={{ width: "100%", marginBottom: 14 }}
          >
            <span className="callout-icon">
              <Icon name={result.ok ? "check" : "warn"} size={13} stroke={2.2} />
            </span>
            <div className="callout-body">{result.detail}</div>
          </div>
        )}

        <div className="row" style={{ gap: 10 }}>
          <button className="btn primary lg" onClick={apply} disabled={applying}>
            <Icon name="download" size={14} /> {applying ? "Applying…" : applyLabel}
          </button>
          <button className="btn outline" onClick={() => go("step0_gate")}>
            <Icon name="check" size={14} /> Done
          </button>
        </div>

        <div
          className="muted"
          style={{ fontSize: 11.5, marginTop: 18, fontFamily: "var(--font-mono)" }}
        >
          software-verified · hardware validation not claimed
        </div>
      </div>
    </div>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="row" style={{ gap: 12, padding: "4px 0" }}>
      <span className="muted" style={{ minWidth: 90, fontSize: 12, fontWeight: 500 }}>
        {label}
      </span>
      <span style={{ fontSize: 13, fontFamily: "var(--font-mono)" }}>{value}</span>
    </div>
  );
}
