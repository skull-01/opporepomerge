import { useState } from "react";
import { Icon } from "../icons";
import { FooterNav } from "../shell/FooterNav";
import { invoke } from "../ipc";
import { parseOppoPowerReply, type PortResult } from "../probes";
import type { InputAddress } from "../state";
import { planSwitch, type SwitchExtras } from "../step5_switch";
import {
  autoFindMethod,
  autoFindProbePorts,
  sweepCommandFor,
  SWEEP_INPUTS,
} from "../step5_autofind";
import { isAvrChain, step5NextScreen } from "../steps";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 6 —Input capture intro
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
// STEP 6 —Ask-first
// ============================================================
type SmartThingsReply = { url: string; body: string };

export function Step5Ask({ go, state, set }: ScreenProps) {
  const [step, setStep] = useState<"oppo" | "kodi">("oppo");
  const [picked, setPicked] = useState<number | null>(null);
  const [confirmed, setConfirmed] = useState(false);

  const [testing, setTesting] = useState(false);
  const [reply, setReply] = useState<string | null>(null);
  const [stRequest, setStRequest] = useState<SmartThingsReply | null>(null);
  const [error, setError] = useState<string | null>(null);

  const avr = isAvrChain(state.topology);
  // The external command and SmartThings input id are per-target: the test for this step reads the
  // OPPO-side or Kodi-side persisted field, so the same values feed both the test and the add-on.
  const extras: SwitchExtras = {
    externalTemplate: step === "oppo" ? state.tvOppoCommand : state.tvKodiCommand,
    smartthingsDeviceId: state.tvSmartThingsDeviceId,
    smartthingsInputId:
      step === "oppo" ? state.tvSmartThingsOppoInputId : state.tvSmartThingsKodiInputId,
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
                <label className="field-label">
                  {step === "oppo" ? "Switch-to-OPPO command" : "Switch-to-Kodi command"}
                </label>
                <input
                  className="input"
                  placeholder="e.g. curl -s http://{tv_ip}/..."
                  value={step === "oppo" ? state.tvOppoCommand : state.tvKodiCommand}
                  onChange={(e) => {
                    set(
                      step === "oppo"
                        ? { tvOppoCommand: e.target.value }
                        : { tvKodiCommand: e.target.value },
                    );
                    resetReplies();
                  }}
                />
                <div className="field-hint">
                  Run on the Kodi box over SSH. Use <code>{"{tv_ip}"}</code> for the TV address.
                </div>
              </div>
            )}
          {state.tvBackend === "smartthings" && !avr && (
            <>
              <div className="field">
                <label className="field-label">SmartThings token</label>
                <input
                  className="input"
                  type="password"
                  value={state.tvSmartThingsToken}
                  onChange={(e) => {
                    set({ tvSmartThingsToken: e.target.value });
                    resetReplies();
                  }}
                />
                <div className="field-hint">Personal access token with device control scope.</div>
              </div>
              <div className="grid-2" style={{ alignItems: "start" }}>
                <div className="field">
                  <label className="field-label">SmartThings device id</label>
                  <input
                    className="input"
                    value={state.tvSmartThingsDeviceId}
                    onChange={(e) => {
                      set({ tvSmartThingsDeviceId: e.target.value });
                      resetReplies();
                    }}
                  />
                </div>
                <div className="field">
                  <label className="field-label">
                    {step === "oppo" ? "OPPO input id" : "Kodi input id"}
                  </label>
                  <input
                    className="input"
                    placeholder="HDMI1"
                    value={
                      step === "oppo"
                        ? state.tvSmartThingsOppoInputId
                        : state.tvSmartThingsKodiInputId
                    }
                    onChange={(e) => {
                      set(
                        step === "oppo"
                          ? { tvSmartThingsOppoInputId: e.target.value }
                          : { tvSmartThingsKodiInputId: e.target.value },
                      );
                      resetReplies();
                    }}
                  />
                </div>
              </div>
            </>
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
// STEP 6 —Auto-find inputs (driven sweep where the backend allows, manual otherwise)
// ============================================================
type Reachability = { tvOpen: boolean | null; oppoPower: "on" | "off" | "unknown" | null };

export function Step5Fallback({ go, state, set }: ScreenProps) {
  const method = autoFindMethod(state);

  const [scanning, setScanning] = useState(false);
  const [reach, setReach] = useState<Reachability>({ tvOpen: null, oppoPower: null });
  const [sweepIdx, setSweepIdx] = useState(0);
  const [sweepBusy, setSweepBusy] = useState(false);
  const [sweepErr, setSweepErr] = useState<string | null>(null);
  const [foundOppo, setFoundOppo] = useState<number | null>(null);

  const scan = async () => {
    setScanning(true);
    setSweepErr(null);
    const ports = autoFindProbePorts(state);
    let tvOpen: boolean | null = null;
    let oppoPower: "on" | "off" | "unknown" | null = null;
    try {
      if (state.tvIp && ports.length > 0) {
        const r = await invoke<PortResult[]>("tv_port_probe", { host: state.tvIp, ports });
        tvOpen = r.some((p) => p.open);
      }
    } catch {
      tvOpen = false;
    }
    try {
      if (state.playerIp) {
        const raw = await invoke<string>("oppo_query", {
          host: state.playerIp,
          port: 23,
          command: "#QPW",
        });
        oppoPower = parseOppoPowerReply(raw);
      }
    } catch {
      oppoPower = null;
    }
    setReach({ tvOpen, oppoPower });
    setScanning(false);
  };

  const sweepHdmi = SWEEP_INPUTS[sweepIdx];
  const fireSweep = async () => {
    const cmd = sweepCommandFor(state, sweepHdmi);
    if (!cmd) return;
    setSweepBusy(true);
    setSweepErr(null);
    try {
      await invoke<string>(cmd.command, cmd.args);
    } catch (e) {
      setSweepErr(String(e));
    } finally {
      setSweepBusy(false);
    }
  };
  const confirmOppoHere = () => {
    setFoundOppo(sweepHdmi);
    set({ playerInput: sweepHdmi, kodiInput: sweepHdmi === 1 ? 2 : 1 });
  };
  const notHere = () => {
    setSweepErr(null);
    setSweepIdx((i) => (i + 1) % SWEEP_INPUTS.length);
  };

  const manualEntry = (
    <div className="card">
      <h3 className="sub-title">Enter it manually</h3>
      <div className="tile-desc" style={{ marginBottom: 8 }}>
        Pick the HDMI number your {isAvrChain(state.topology) ? "receiver" : "TV"} shows for the
        OPPO. We store it as a real input number; the Kodi box takes another.
      </div>
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
    </div>
  );

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Let's find it together.</h1>
        <p className="screen-subtitle">
          {method === "sweep"
            ? "No TV protocol reports the active input, so we switch to each HDMI in turn and you tell us when the OPPO appears — a real, driven sweep."
            : "This backend can't drive discrete HDMI inputs from here, so we'll confirm what we can reach and then take the input number from you."}
        </p>
      </div>

      <div className="stack">
        <div className="card">
          <div className="row" style={{ gap: 10, alignItems: "center" }}>
            <button className="btn outline sm" onClick={scan} disabled={scanning}>
              <Icon name="search" size={13} /> {scanning ? "Scanning…" : "Scan reachability"}
            </button>
            {reach.tvOpen != null && (
              <span className={reach.tvOpen ? "success-text" : "muted"} style={{ fontSize: 12.5 }}>
                TV control port {reach.tvOpen ? "answered" : "didn't answer"}
              </span>
            )}
            {reach.oppoPower != null && (
              <span className="muted" style={{ fontSize: 12.5 }}>
                · OPPO {reach.oppoPower === "unknown" ? "reachable" : `power ${reach.oppoPower}`}
              </span>
            )}
          </div>
          {reach.oppoPower === "off" && (
            <div className="field-hint" style={{ marginTop: 6 }}>
              The OPPO reports power off — turn it on so you can see it on the TV during the sweep.
            </div>
          )}
        </div>

        {method === "sweep" ? (
          foundOppo != null ? (
            <div className="callout success">
              <span className="callout-icon">
                <Icon name="check" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                Found the OPPO on <code>HDMI {foundOppo}</code>. We stored it as the handoff input
                and set the Kodi box to <code>HDMI {foundOppo === 1 ? 2 : 1}</code> — adjust on the
                next screen if that's not right.
                <div style={{ marginTop: 10 }}>
                  <button className="btn primary" onClick={() => go("step5_done")}>
                    Looks right — continue <Icon name="chevR" size={14} />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card">
              <h3 className="sub-title">Sweep · trying HDMI {sweepHdmi}</h3>
              <div className="tile-desc" style={{ marginBottom: 10 }}>
                We'll switch your TV to <code>HDMI {sweepHdmi}</code>. Watch the screen — if you see
                the OPPO, confirm it; otherwise we move to the next input.
              </div>
              <div className="row" style={{ gap: 10 }}>
                <button className="btn primary" onClick={fireSweep} disabled={sweepBusy}>
                  <Icon name="play" size={14} /> {sweepBusy ? "Switching…" : `Switch to HDMI ${sweepHdmi}`}
                </button>
                <button className="btn outline" onClick={confirmOppoHere}>
                  <Icon name="check" size={14} /> I see the OPPO
                </button>
                <button className="btn ghost" onClick={notHere}>
                  Not here — next
                </button>
              </div>
              {sweepErr && (
                <div className="callout warn" style={{ marginTop: 10 }}>
                  <span className="callout-icon">
                    <Icon name="warn" size={13} stroke={2.2} />
                  </span>
                  <div className="callout-body">
                    Switch failed: <code>{sweepErr}</code>. Check the TV IP / reachability above, or
                    enter the number manually below.
                  </div>
                </div>
              )}
            </div>
          )
        ) : null}

        {manualEntry}

        <div className="tile" style={{ cursor: "default", alignItems: "center" }}>
          <div className="tile-body">
            <div className="tile-title">None of this worked</div>
            <div className="tile-desc">
              Switch inputs with your remote yourself — the add-on won't try to drive the TV.
            </div>
          </div>
          <button
            className="btn ghost sm"
            onClick={() => {
              set({ tvManualSwitch: true });
              go("step5_done");
            }}
          >
            Manual switching
          </button>
        </div>
      </div>
      <FooterNav go={go} back="step5_intro" />
    </div>
  );
}

// ============================================================
// STEP 6 —Done
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
