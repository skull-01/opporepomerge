import { useState, type ReactNode } from "react";
import { Icon } from "../icons";
import { FooterNav } from "../shell/FooterNav";
import type { InputAddress } from "../state";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 4 — Input capture intro
// ============================================================
export function Step4Intro({ go, state }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Now the HDMI inputs.</h1>
        <p className="screen-subtitle">
          We need two: <strong>where your player is</strong> (to switch to on handoff) and{" "}
          <strong>where your Kodi box is</strong> (to switch back on exit). Your player and
          TV are both set up now — good time to pin these down.
        </p>
      </div>
      <div className="card">
        <h3 className="sub-title">Plan</h3>
        <div className="stack-sm">
          <div className="row" style={{ gap: 10 }}>
            <span className="kbd" style={{ minWidth: 24, textAlign: "center" }}>1</span>
            <span>
              Capture the <strong>OPPO's HDMI input</strong> — the one we switch to.
            </span>
          </div>
          <div className="row" style={{ gap: 10 }}>
            <span className="kbd" style={{ minWidth: 24, textAlign: "center" }}>2</span>
            <span>
              Capture the <strong>Kodi box's HDMI input</strong> — the return target.
            </span>
          </div>
        </div>
        <div className="divider" />
        <div className="row" style={{ gap: 8 }}>
          <span className="chip success">
            <Icon name="check" size={11} /> Backend: <code>{state.tvBackend || "roku_ecp"}</code>
          </span>
          {state.tvAdbWeak && (
            <span className="chip warn">
              <Icon name="warn" size={11} /> ADB-weak — fallback path
            </span>
          )}
          {state.tvManualSwitch && <span className="chip warn">Manual switching</span>}
        </div>
      </div>
      <div className="callout warn" style={{ marginTop: 14 }}>
        <span className="callout-icon">
          <Icon name="warn" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          <strong>Heads-up: we're about to change your TV input.</strong> We'll return to
          your current input when this step ends.
        </div>
      </div>
      <FooterNav
        go={go}
        back="step3_test"
        next={state.tvAdbWeak ? "step4_fallback" : "step4_ask"}
        nextLabel="Capture inputs"
      />
    </div>
  );
}

// ============================================================
// STEP 4 — Ask-first
// ============================================================
export function Step4Ask({ go, state, set }: ScreenProps) {
  const [step, setStep] = useState<"oppo" | "kodi">("oppo");
  const [picked, setPicked] = useState<number | null>(null);
  const [confirmed, setConfirmed] = useState(false);

  const pick = (n: number) => {
    setPicked(n);
    setConfirmed(false);
  };
  const next = () => {
    if (step === "oppo") {
      set({ oppoInput: picked });
      setStep("kodi");
      setPicked(null);
      setConfirmed(false);
    } else {
      set({ kodiInput: picked });
      go("step4_done");
    }
  };

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">
          Which HDMI input is your {step === "oppo" ? "OPPO" : "Kodi box"} on?
        </h1>
        <p className="screen-subtitle">
          If you know, pick it and we'll switch to it and confirm. If you don't, we can
          find it for you instead.
        </p>
      </div>

      <div className="grid-2" style={{ alignItems: "start" }}>
        <div className="stack">
          <div className="hdmi-grid">
            {[1, 2, 3, 4].map((n) => (
              <button
                key={n}
                className={`hdmi-tile ${picked === n ? "selected" : ""}`.trim()}
                onClick={() => pick(n)}
              >
                <div className="hdmi-tile-num">{n}</div>
                <div className="hdmi-tile-label">HDMI {n}</div>
              </button>
            ))}
          </div>
          <button className="btn outline" onClick={() => go("step4_fallback")}>
            <Icon name="search" size={14} /> Not sure — find it for me
          </button>
        </div>

        <div className="stack">
          <div className="tv-mockup">
            <div className="tv-mockup-screen">
              {picked && confirmed ? (
                <>
                  <div className="tv-mockup-text bright">
                    {step === "oppo" ? "OPPO M9205 V1" : "Kodi · CoreELEC"}
                  </div>
                  <div className="tv-mockup-text">on HDMI {picked}</div>
                </>
              ) : picked ? (
                <>
                  <div className="tv-mockup-text">switched to HDMI {picked}</div>
                  <div className="tv-mockup-text" style={{ fontSize: 10 }}>
                    do you see {step === "oppo" ? "your player" : "Kodi"}?
                  </div>
                </>
              ) : (
                <div className="tv-mockup-text">— pick an input —</div>
              )}
            </div>
            <div className="stand" />
          </div>
          {picked && (
            <>
              <div className="callout info">
                <span className="callout-icon">
                  <Icon name="info" size={13} stroke={2.2} />
                </span>
                <div className="callout-body">
                  Sent <code>switch-to HDMI{picked}</code> via{" "}
                  <code>{state.tvBackend || "roku_ecp"}</code>. Do you see{" "}
                  {step === "oppo" ? "the OPPO" : "Kodi"} on screen?
                </div>
              </div>
              <div className="row" style={{ gap: 10 }}>
                <button className="btn primary" onClick={() => setConfirmed(true)}>
                  <Icon name="check" size={14} /> Yes, that's it
                </button>
                <button className="btn outline" onClick={() => setPicked(null)}>
                  No — pick a different one
                </button>
              </div>
              {confirmed && (
                <button className="btn primary lg" onClick={next}>
                  {step === "oppo" ? "Next: Kodi box input" : "All inputs captured"}
                  <Icon name="chevR" size={14} />
                </button>
              )}
            </>
          )}
        </div>
      </div>
      <FooterNav go={go} back="step4_intro" />
    </div>
  );
}

// ============================================================
// STEP 4 — ADB-weak fallback funnel
// ============================================================
export function Step4Fallback({ go, set }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Let's find it together.</h1>
        <p className="screen-subtitle">
          Your TV connected but ignores discrete HDMI keys. We'll walk three fallbacks,
          most-reliable first. Each rung confirms before we move on.
        </p>
      </div>
      <div className="stack">
        <FallbackRung
          num="1"
          status="active"
          title="Ask the number"
          desc="Tell us the HDMI number and we'll fire KEYCODE_TV_INPUT_HDMI_N. Stores a real HDMI number."
          action={
            <div className="row" style={{ gap: 6 }}>
              {[1, 2, 3, 4].map((n) => (
                <button
                  key={n}
                  className="filter-pill"
                  onClick={() => {
                    set({ oppoInput: n, kodiInput: n === 1 ? 2 : 1 });
                    go("step4_done");
                  }}
                >
                  HDMI {n}
                </button>
              ))}
            </div>
          }
        />
        <FallbackRung
          num="2"
          status="next"
          title="CEC One-Touch-Play"
          desc="Wake the OPPO so it asserts active source over CEC; the TV follows. Stores 'OPPO = CEC-asserted input' — no number needed."
          action={
            <button
              className="btn outline sm"
              onClick={() => {
                set({ oppoInput: "cec", kodiInput: 1 });
                go("step4_done");
              }}
            >
              Use CEC fallback
            </button>
          }
        />
        <FallbackRung
          num="3"
          status="next"
          title="Blind-cycle (last resort)"
          desc="Send the input-advance key; you tell us when the OPPO appears. Stores the lossy record — 'input after N advances' — flagged as brittle internally."
          action={
            <button
              className="btn outline sm"
              onClick={() => {
                set({ oppoInput: "cycle:2", kodiInput: "cycle:1" });
                go("step4_done");
              }}
            >
              Cycle now
            </button>
          }
        />
        <FallbackRung
          num="4"
          status="exit"
          title="None of the above worked"
          desc="Switch inputs with your TV remote yourself. The add-on simply won't try to drive the TV."
          action={
            <button
              className="btn ghost sm"
              onClick={() => {
                set({ tvManualSwitch: true });
                go("step4_done");
              }}
            >
              Manual switching
            </button>
          }
        />
      </div>
      <FooterNav go={go} back="step4_intro" />
    </div>
  );
}

type RungStatus = "active" | "next" | "exit";

function FallbackRung({
  num,
  status,
  title,
  desc,
  action,
}: {
  num: string;
  status: RungStatus;
  title: string;
  desc: string;
  action: ReactNode;
}) {
  return (
    <div className="tile" style={{ cursor: "default", alignItems: "center" }}>
      <div
        className="tile-icon"
        style={{
          background: status === "active" ? "var(--accent-soft)" : "var(--surface-2)",
          color: status === "active" ? "var(--accent)" : "var(--muted)",
          fontWeight: 700,
          fontFamily: "var(--font-display)",
        }}
      >
        {num}
      </div>
      <div className="tile-body">
        <div className="tile-title">
          {title}{" "}
          {status === "active" && (
            <span className="chip accent" style={{ marginLeft: 6 }}>
              Try this first
            </span>
          )}
        </div>
        <div className="tile-desc">{desc}</div>
      </div>
      <div>{action}</div>
    </div>
  );
}

// ============================================================
// STEP 4 — Done
// ============================================================
function describeInput(input: InputAddress, fallback: string) {
  if (input == null) return fallback;
  return typeof input === "number" ? String(input) : input;
}

export function Step4Done({ go, state }: ScreenProps) {
  const oppoLabel = describeInput(state.oppoInput, "3");
  const kodiLabel = describeInput(state.kodiInput, "1");
  const isCycle = typeof state.oppoInput === "string" && state.oppoInput.startsWith("cycle");
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Inputs captured.</h1>
        <p className="screen-subtitle">
          We'll use these for handoff and return-on-exit. You can edit them later in the
          add-on settings.
        </p>
      </div>
      <div className="grid-2">
        <div className="card">
          <h3 className="sub-title">Switch to</h3>
          <div className="row" style={{ gap: 14, marginTop: 8 }}>
            <div className="tile-icon">
              <Icon name="player" size={20} />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>
                OPPO {state.playerModel || "M9205 V1"}
              </div>
              <div
                className="muted"
                style={{ fontSize: 12, fontFamily: "var(--font-mono)", marginTop: 2 }}
              >
                HDMI {oppoLabel}
                {state.oppoInput === "cec" && <> (CEC-asserted)</>}
                {isCycle && <> (blind-cycle · brittle)</>}
              </div>
            </div>
          </div>
        </div>
        <div className="card">
          <h3 className="sub-title">Return to</h3>
          <div className="row" style={{ gap: 14, marginTop: 8 }}>
            <div className="tile-icon">
              <Icon name="kodi" size={20} />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>Kodi box</div>
              <div
                className="muted"
                style={{ fontSize: 12, fontFamily: "var(--font-mono)", marginTop: 2 }}
              >
                HDMI {kodiLabel}
              </div>
            </div>
          </div>
        </div>
      </div>
      {isCycle && (
        <div className="callout warn" style={{ marginTop: 14 }}>
          <span className="callout-icon">
            <Icon name="warn" size={13} stroke={2.2} />
          </span>
          <div className="callout-body">
            <strong>Blind-cycle is brittle.</strong> If your TV's input order ever shifts
            (added device, reordered ports), the return-target may land somewhere
            unexpected. Edit it manually in the add-on if that happens.
          </div>
        </div>
      )}
      <FooterNav
        go={go}
        back="step4_intro"
        next="step5_ask"
        nextLabel="Next: AV receiver (optional)"
      />
    </div>
  );
}
