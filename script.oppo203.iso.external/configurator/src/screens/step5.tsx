import { useState, type ReactNode } from "react";
import { Icon } from "../icons";
import { FooterNav } from "../shell/FooterNav";
import { invoke } from "../ipc";
import type { InputAddress } from "../state";
import { planSwitch, type SwitchExtras } from "../step5_switch";
import { isAvrChain, step5NextScreen } from "../steps";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 4 — Input capture intro
// ============================================================
export function Step5Intro({ go, state }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Now the HDMI inputs.</h1>
        <p className="screen-subtitle">
          We need two: <strong>where your player is</strong> (to switch to on handoff) and{" "}
          <strong>where your Kodi box is</strong> (to switch back on exit).{" "}
          {isAvrChain(state.topology)
            ? "In your chain these are inputs on the AV receiver, which does the switching."
            : "Your player and TV are both set up now — good time to pin these down."}
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
          {isAvrChain(state.topology) ? (
            <>
              <strong>Heads-up: we&apos;re about to change your receiver input.</strong> We&apos;ll
              return to your current input when this step ends.
            </>
          ) : (
            <>
              <strong>Heads-up: we&apos;re about to change your TV input.</strong> We&apos;ll return
              to your current input when this step ends.
            </>
          )}
        </div>
      </div>
      <FooterNav
        go={go}
        back="step4_test"
        next={state.tvAdbWeak ? "step5_fallback" : "step5_ask"}
        nextLabel="Capture inputs"
      />
    </div>
  );
}

// ============================================================
// STEP 4 — Ask-first
// ============================================================
type SmartThingsReply = { url: string; body: string };

export function Step5Ask({ go, state, set }: ScreenProps) {
  const [step, setStep] = useState<"oppo" | "kodi">("oppo");
  const [picked, setPicked] = useState<number | null>(null);
  const [confirmed, setConfirmed] = useState(false);

  const [extTemplate, setExtTemplate] = useState("");
  const [stDeviceId, setStDeviceId] = useState("");
  const [stInputId, setStInputId] = useState("");

  const [testing, setTesting] = useState(false);
  const [reply, setReply] = useState<string | null>(null);
  const [stRequest, setStRequest] = useState<SmartThingsReply | null>(null);
  const [error, setError] = useState<string | null>(null);

  const avr = isAvrChain(state.topology);
  const extras: SwitchExtras = {
    externalTemplate: extTemplate,
    smartthingsDeviceId: stDeviceId,
    smartthingsInputId: stInputId,
  };
  // In the AVR chain the receiver switches by its own input string, so a tile isn't required to
  // build the plan; in the TV chain the plan needs the picked HDMI number.
  const plan = picked != null || avr ? planSwitch(state, step, picked ?? 0, extras) : null;

  const resetReplies = () => {
    setReply(null);
    setStRequest(null);
    setError(null);
  };
  const pick = (n: number) => {
    setPicked(n);
    setConfirmed(false);
    resetReplies();
  };
  const next = () => {
    if (step === "oppo") {
      set({ playerInput: picked });
      setStep("kodi");
      setPicked(null);
      setConfirmed(false);
      resetReplies();
    } else {
      set({ kodiInput: picked });
      go("step5_done");
    }
  };

  const runTest = async () => {
    if (!plan || plan.disposition === "manual") return;
    setTesting(true);
    resetReplies();
    try {
      if (plan.disposition === "request") {
        const req = await invoke<SmartThingsReply>(plan.command, plan.args);
        setStRequest(req);
      } else {
        const raw = await invoke<string>(plan.command, plan.args);
        setReply(raw);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setTesting(false);
    }
  };

  const targetName = step === "oppo" ? "OPPO" : "Kodi box";
  const seeName = step === "oppo" ? "the OPPO" : "Kodi";

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">
          Which {avr ? "receiver" : "HDMI"} input is your {targetName} on?
        </h1>
        <p className="screen-subtitle">
          {avr
            ? "We'll ask the receiver to switch to its configured input and show its reply. Confirm visually — receivers rarely report the active input."
            : "Pick it and run the test switch — we'll drive the switch where we can and show the device reply. Not sure? We can find it for you instead."}
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
          <button className="btn outline" onClick={() => go("step5_fallback")}>
            <Icon name="search" size={14} /> Not sure — find it for me
          </button>

          {state.tvBackend === "sony_bravia" && !avr && (
            <div className="field">
              <label className="field-label">Sony TV Pre-Shared Key</label>
              <input
                className="input"
                type="password"
                value={state.tvSonyPsk}
                onChange={(e) => {
                  set({ tvSonyPsk: e.target.value });
                  resetReplies();
                }}
              />
              <div className="field-hint">Set on the TV under IP Control. Needed to test the switch.</div>
            </div>
          )}
          {(state.tvBackend === "lg_command" ||
            state.tvBackend === "samsung_command" ||
            state.tvBackend === "custom_command") &&
            !avr && (
              <div className="field">
                <label className="field-label">TV switch command</label>
                <input
                  className="input"
                  placeholder="e.g. curl -s http://{tv_ip}/..."
                  value={extTemplate}
                  onChange={(e) => {
                    setExtTemplate(e.target.value);
                    resetReplies();
                  }}
                />
                <div className="field-hint">
                  Run on the Kodi box over SSH. Use <code>{"{tv_ip}"}</code> for the TV address.
                </div>
              </div>
            )}
          {state.tvBackend === "smartthings" && !avr && (
            <div className="grid-2" style={{ alignItems: "start" }}>
              <div className="field">
                <label className="field-label">SmartThings device id</label>
                <input
                  className="input"
                  value={stDeviceId}
                  onChange={(e) => {
                    setStDeviceId(e.target.value);
                    resetReplies();
                  }}
                />
              </div>
              <div className="field">
                <label className="field-label">Input id</label>
                <input
                  className="input"
                  placeholder="HDMI1"
                  value={stInputId}
                  onChange={(e) => {
                    setStInputId(e.target.value);
                    resetReplies();
                  }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="stack">
          <div className="tv-mockup">
            <div className="tv-mockup-screen">
              {confirmed && (picked || avr) ? (
                <>
                  <div className="tv-mockup-text bright">
                    {step === "oppo" ? "OPPO M9205 V1" : "Kodi · CoreELEC"}
                  </div>
                  <div className="tv-mockup-text">confirmed{picked ? ` · HDMI ${picked}` : ""}</div>
                </>
              ) : testing ? (
                <div className="tv-mockup-text">switching…</div>
              ) : reply ? (
                <>
                  <div className="tv-mockup-text">switch sent</div>
                  <div className="tv-mockup-text" style={{ fontSize: 10 }}>
                    do you see {seeName}?
                  </div>
                </>
              ) : picked || avr ? (
                <div className="tv-mockup-text">ready to test</div>
              ) : (
                <div className="tv-mockup-text">— pick an input —</div>
              )}
            </div>
            <div className="stand" />
          </div>

          {plan && plan.disposition === "manual" && (
            <div className="callout info">
              <span className="callout-icon">
                <Icon name="info" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                {plan.reason} Switch {avr ? "the receiver" : "your TV"} to the right input yourself,
                then confirm you see {seeName}.
              </div>
            </div>
          )}

          {plan && plan.disposition !== "manual" && (
            <button className="btn primary" onClick={runTest} disabled={testing}>
              <Icon name="play" size={14} />{" "}
              {testing
                ? "Testing…"
                : plan.disposition === "request"
                  ? "Build switch request"
                  : "Test switch"}
            </button>
          )}

          {error && (
            <div className="callout warn">
              <span className="callout-icon">
                <Icon name="warn" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                Switch command failed: <code>{error}</code>. Check the IP/credentials, or switch
                with the remote and confirm below.
              </div>
            </div>
          )}

          {reply && (
            <div className="callout info">
              <span className="callout-icon">
                <Icon name="info" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                Device replied: <code>{reply}</code>. A reply means the command was accepted — it is
                not a guarantee the input changed, so confirm you see {seeName} on screen.
              </div>
            </div>
          )}

          {stRequest && (
            <div className="callout info">
              <span className="callout-icon">
                <Icon name="info" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                SmartThings is a cloud HTTPS call with your bearer token — the add-on fires it
                on-device, the configurator only builds it:
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, marginTop: 6 }}>
                  POST {stRequest.url}
                </div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, marginTop: 2 }}>
                  {stRequest.body}
                </div>
              </div>
            </div>
          )}

          {(picked || avr) && (
            <>
              <div className="row" style={{ gap: 10 }}>
                <button className="btn primary" onClick={() => setConfirmed(true)}>
                  <Icon name="check" size={14} /> Yes, I see {seeName}
                </button>
                <button
                  className="btn outline"
                  onClick={() => {
                    setPicked(null);
                    setConfirmed(false);
                    resetReplies();
                  }}
                >
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
      <FooterNav go={go} back="step5_intro" />
    </div>
  );
}

// ============================================================
// STEP 4 — ADB-weak fallback funnel
// ============================================================
export function Step5Fallback({ go, set }: ScreenProps) {
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
                    set({ playerInput: n, kodiInput: n === 1 ? 2 : 1 });
                    go("step5_done");
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
                set({ playerInput: "cec", kodiInput: 1 });
                go("step5_done");
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
                set({ playerInput: "cycle:2", kodiInput: "cycle:1" });
                go("step5_done");
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
                go("step5_done");
              }}
            >
              Manual switching
            </button>
          }
        />
      </div>
      <FooterNav go={go} back="step5_intro" />
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

export function Step5Done({ go, state }: ScreenProps) {
  const oppoLabel = describeInput(state.playerInput, "3");
  const kodiLabel = describeInput(state.kodiInput, "1");
  const isCycle = typeof state.playerInput === "string" && state.playerInput.startsWith("cycle");
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
                {state.playerInput === "cec" && <> (CEC-asserted)</>}
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
        back="step5_intro"
        next={step5NextScreen(state.topology)}
        nextLabel={
          isAvrChain(state.topology)
            ? "Next: AV receiver"
            : "Next: AV receiver (optional)"
        }
      />
    </div>
  );
}
