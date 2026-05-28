// screens-2.jsx — Step 3 (Player), Step 3.5 (Input capture), Full Setup Test

// ============================================================
// STEP 3 — Player brand + model + IP + test
// ============================================================
const PLAYER_BRANDS = [
  { id: "oppo",      name: "OPPO",       ch: "O",  posture: "stock",   models: ["UDP-203", "UDP-205"] },
  { id: "chinoppo",  name: "Chinoppo",   ch: "C",  posture: "wake-rewrite", models: ["M9201","M9203","M9205 V1","M9205C","M9200","M9205","M9702"] },
  { id: "magnetar",  name: "Magnetar",   ch: "M",  posture: "warning", models: ["UDP800","UDP900"] },
  { id: "reavon",    name: "Reavon",     ch: "R",  posture: "warning", models: ["UBR-X100","UBR-X110","UBR-X200"] },
  { id: "cineultra", name: "CineUltra",  ch: "CU", posture: "wake-rewrite", models: ["V203","V204"] },
  { id: "ipuk",      name: "iPUK",       ch: "iP", posture: "wake-rewrite", models: ["UHD8592"] },
  { id: "giec",      name: "Giec",       ch: "G",  posture: "wake-rewrite", models: ["BDP-G5300"] },
  { id: "other",     name: "Other / clone", ch: "?", posture: "stock",      models: ["Conservative default","Chinoppo eject-to-wake"] },
];

function Step3Brand({ go, state, set }) {
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
      <div className="brand-grid" style={{marginBottom:18}}>
        {PLAYER_BRANDS.map((b) => (
          <button key={b.id}
            className={`brand-pill ${state.playerBrand === b.id ? "selected" : ""}`}
            onClick={() => set({playerBrand: b.id, playerModel: null})}>
            <div className="brand-logo">{b.ch}</div>
            <div>{b.name}</div>
            <div className="muted" style={{fontSize:10.5, fontWeight:500}}>
              {b.posture === "stock" ? "stock wake" : b.posture === "wake-rewrite" ? "eject-to-wake" : "warning-only"}
            </div>
          </button>
        ))}
      </div>

      {selected && (
        <div className="grid-2" style={{alignItems:'start'}}>
          <div className="card">
            <h2 className="section-title">{selected.name} models</h2>
            <div className="filter-row" style={{gap:8}}>
              {selected.models.map((m) => (
                <button key={m}
                  className={`filter-pill ${state.playerModel === m ? "selected" : ""}`}
                  onClick={() => set({playerModel: m})}>
                  {m}
                </button>
              ))}
            </div>
            <div className="divider" />
            <div className="field">
              <label className="field-label">Player IP</label>
              <input className="input" defaultValue="10.0.1.77" onChange={(e)=>set({playerIp:e.target.value})} />
              <div className="field-hint">Port 23 — IP control. Reserve it on DHCP.</div>
            </div>
          </div>

          {selected.posture === "warning" ? (
            <div className="callout warn">
              <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
              <div className="callout-body">
                <strong>{selected.name} is warning-only.</strong> Commands are <em>not</em>
                mutated; we won't claim hardware compatibility until a tester report exists.
                You can continue — the rest of the setup still works.
              </div>
            </div>
          ) : selected.posture === "wake-rewrite" ? (
            <div className="callout info">
              <span className="callout-icon"><Icon name="bolt" size={13} stroke={2.2}/></span>
              <div className="callout-body">
                <strong>Clone wake quirk handled.</strong> {selected.name} models can be
                asleep and won't answer until woken. We'll wake with <code>#EJT</code>
                (eject-to-wake) before any other command.
              </div>
            </div>
          ) : (
            <div className="callout info">
              <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
              <div className="callout-body">
                <strong>Stock OPPO behavior.</strong> Wake is plain <code>#PON</code>;
                <code>#POW</code> and <code>#PLA</code> are passed through unchanged.
              </div>
            </div>
          )}
        </div>
      )}

      <FooterNav go={go} back="step2_test"
        next={state.playerBrand && state.playerModel ? "step3_test" : null}
        nextLabel="Continue to control test" />
    </div>
  );
}

// ============================================================
// STEP 3 — Wake & confirm test
// ============================================================
function Step3Test({ go, state, set }) {
  const [phase, setPhase] = React.useState("ready"); // ready | running | pass | fail
  const isClone = ["chinoppo","cineultra","ipuk","giec"].includes(state.playerBrand);
  const wakeCmd = isClone ? "#EJT" : "#PON";

  React.useEffect(() => {
    if (phase === "running") {
      const t = setTimeout(() => setPhase("pass"), 2200);
      return () => clearTimeout(t);
    }
  }, [phase]);

  const baseChecks = (running) => [
    { status: running ? "pass" : "pending", label: `TCP :23 reachable`, detail: running ? `10.0.1.77 · 0.6 ms` : "" },
    { status: running ? (phase === "pass" ? "pass" : "run") : "pending", label: `Wake with ${wakeCmd}`, detail: running ? `command transmitted` : "" },
    { status: phase === "pass" ? "pass" : "pending", label: "Query #QPW (status)", detail: phase === "pass" ? `reply: @QPW ON` : "" },
    { status: phase === "pass" ? "pass" : "pending", label: "Confirm: player reports ON", detail: phase === "pass" ? "two-way IP control verified" : "" },
  ];

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">{isClone ? "Power on your player first." : "Test IP control."}</h1>
        <p className="screen-subtitle">
          {isClone
            ? <>Clones can be asleep and won't answer until woken. Make sure your player is plugged in and in <strong>standby</strong> — not switched off at the wall — then we'll wake it and confirm control.</>
            : <>We'll send a query the player <em>answers</em>, not a blind state-changing command. Two-way control or nothing.</>}
        </p>
      </div>

      <div className="grid-2" style={{alignItems:'start'}}>
        <div className="stack">
          <DiagLog
            title={isClone ? "Wake → confirm" : "IP control"}
            checks={baseChecks(phase !== "ready")}
            footer={phase === "pass"
              ? <><strong className="success-text">Two-way IP control confirmed.</strong> Player answered to <code>#QPW</code> with <code>ON</code> after wake.</>
              : phase === "running"
                ? <>Waking and querying — clones can take a few seconds to come up.</>
                : <span className="muted">Click "Wake &amp; confirm" when the player is in standby.</span>}
            footerKind={phase === "pass" ? "success" : ""}
          />
          <div className="row" style={{gap:10}}>
            {phase === "ready" && (
              <button className="btn primary lg" onClick={() => setPhase("running")}>
                <Icon name="bolt" size={14}/> Wake &amp; confirm
              </button>
            )}
            {phase === "pass" && (
              <button className="btn primary lg" onClick={() => { set({playerVerified:true}); go("step35_intro"); }}>
                Continue — capture HDMI inputs <Icon name="chevR" size={14}/>
              </button>
            )}
            <button className="btn outline" onClick={() => go("step3_fail")}>
              Test didn't work
            </button>
          </div>
        </div>
        <div className="stack">
          <div className="player-mockup">
            <span className={`player-mockup-led ${phase === "ready" ? "standby" : ""}`} />
            <div className="player-mockup-screen">
              {phase === "ready" ? "STANDBY" : phase === "running" ? "WAKE…" : "ON  ·  READY"}
            </div>
          </div>
          <div className="callout info">
            <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
            <div className="callout-body">
              <strong>Quick Start</strong> may need to be on so the player stays reachable
              in standby. Plain "off at the wall" doesn't count — the network stack must
              stay alive to receive the wake.
            </div>
          </div>
        </div>
      </div>
      <FooterNav go={go} back="step3_brand" />
    </div>
  );
}

// ============================================================
// STEP 3 — Test failed (cheapest-first hints)
// ============================================================
function Step3Fail({ go }) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Player didn't respond.</h1>
        <p className="screen-subtitle">Ordered cheapest-first — the most common cause is at the top.</p>
      </div>
      <div className="stack">
        <HintTile num="1" title='"IP Control" isn\u2019t enabled'
          desc="Setup → Device Setup → IP Control / Network Control → On. Wording varies by firmware. By far the most common cause." />
        <HintTile num="2" title="Wrong IP, or it changed"
          desc="Confirm in the player's network settings; reserve it on DHCP so it doesn't drift." />
        <HintTile num="3" title="Not on the same network"
          desc="Player and Kodi box must share the LAN/subnet — no guest WiFi, no VLAN split. (Your TV is irrelevant here — it had its own test.)" />
        <HintTile num="4" title="Standby, not off at the wall (clones)"
          desc="Plain power-off kills the network stack; the player can't receive a wake. Switch it to standby instead." />
      </div>
      <FooterNav go={go} back="step3_test" next="step3_test" nextLabel="Retry the test" />
    </div>
  );
}
function HintTile({ num, title, desc }) {
  return (
    <div className="tile" style={{cursor:'default'}}>
      <div className="tile-icon" style={{background:'var(--surface-2)', color:'var(--text-soft)', fontFamily:'var(--font-display)', fontWeight:700}}>{num}</div>
      <div className="tile-body">
        <div className="tile-title">{title}</div>
        <div className="tile-desc">{desc}</div>
      </div>
    </div>
  );
}

// ============================================================
// STEP 3.5 — Input capture intro
// ============================================================
function Step35Intro({ go, state }) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Now the HDMI inputs.</h1>
        <p className="screen-subtitle">
          We need two: <strong>where your player is</strong> (to switch to on handoff)
          and <strong>where your Kodi box is</strong> (to switch back on exit). The player
          is awake now — good time to do this.
        </p>
      </div>
      <div className="card">
        <h3 className="sub-title">Plan</h3>
        <div className="stack-sm">
          <div className="row" style={{gap:10}}>
            <span className="kbd" style={{minWidth:24, textAlign:'center'}}>1</span>
            <span>Capture the <strong>OPPO's HDMI input</strong> — the one we switch to.</span>
          </div>
          <div className="row" style={{gap:10}}>
            <span className="kbd" style={{minWidth:24, textAlign:'center'}}>2</span>
            <span>Capture the <strong>Kodi box's HDMI input</strong> — the return target.</span>
          </div>
        </div>
        <div className="divider" />
        <div className="row" style={{gap:8}}>
          <span className="chip success"><Icon name="check" size={11}/> Backend: <code>{state.tvBackend || "roku_ecp"}</code></span>
          {state.tvAdbWeak && <span className="chip warn"><Icon name="warn" size={11}/> ADB-weak — fallback path</span>}
          {state.tvManualSwitch && <span className="chip warn">Manual switching</span>}
        </div>
      </div>
      <div className="callout warn" style={{marginTop:14}}>
        <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
        <div className="callout-body">
          <strong>Heads-up: we're about to change your TV input.</strong> We'll return to
          your current input when this step ends.
        </div>
      </div>
      <FooterNav go={go} back="step3_test" next={state.tvAdbWeak ? "step35_fallback" : "step35_ask"} nextLabel="Capture inputs" />
    </div>
  );
}

// ============================================================
// STEP 3.5 — Ask-first (addressable backend)
// ============================================================
function Step35Ask({ go, state, set }) {
  const [step, setStep] = React.useState("oppo"); // oppo | kodi | done
  const [picked, setPicked] = React.useState(null);
  const [confirmed, setConfirmed] = React.useState(false);

  const pick = (n) => { setPicked(n); setConfirmed(false); };
  const next = () => {
    if (step === "oppo") {
      set({oppoInput: picked});
      setStep("kodi"); setPicked(null); setConfirmed(false);
    } else {
      set({kodiInput: picked});
      go("step35_done");
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

      <div className="grid-2" style={{alignItems:'start'}}>
        <div className="stack">
          <div className="hdmi-grid">
            {[1,2,3,4].map((n) => (
              <button key={n}
                className={`hdmi-tile ${picked === n ? "selected" : ""}`}
                onClick={() => pick(n)}>
                <div className="hdmi-tile-num">{n}</div>
                <div className="hdmi-tile-label">HDMI {n}</div>
              </button>
            ))}
          </div>
          <button className="btn outline" onClick={() => go("step35_fallback")}>
            <Icon name="search" size={14}/> Not sure — find it for me
          </button>
        </div>

        <div className="stack">
          <div className="tv-mockup">
            <div className="tv-mockup-screen">
              {picked && confirmed ? (
                <>
                  <div className="tv-mockup-text bright">{step === "oppo" ? "OPPO M9205 V1" : "Kodi · CoreELEC"}</div>
                  <div className="tv-mockup-text">on HDMI {picked}</div>
                </>
              ) : picked ? (
                <>
                  <div className="tv-mockup-text">switched to HDMI {picked}</div>
                  <div className="tv-mockup-text" style={{fontSize:10}}>do you see {step === "oppo" ? "your player" : "Kodi"}?</div>
                </>
              ) : (
                <>
                  <div className="tv-mockup-text">— pick an input —</div>
                </>
              )}
            </div>
            <div className="stand"/>
          </div>
          {picked && (
            <>
              <div className="callout info">
                <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
                <div className="callout-body">
                  Sent <code>switch-to HDMI{picked}</code> via <code>{state.tvBackend || "roku_ecp"}</code>.
                  Do you see {step === "oppo" ? "the OPPO" : "Kodi"} on screen?
                </div>
              </div>
              <div className="row" style={{gap:10}}>
                <button className="btn primary" onClick={() => { setConfirmed(true); }}>
                  <Icon name="check" size={14}/> Yes, that's it
                </button>
                <button className="btn outline" onClick={() => setPicked(null)}>
                  No — pick a different one
                </button>
              </div>
              {confirmed && (
                <button className="btn primary lg" onClick={next}>
                  {step === "oppo" ? "Next: Kodi box input" : "All inputs captured"}
                  <Icon name="chevR" size={14}/>
                </button>
              )}
            </>
          )}
        </div>
      </div>
      <FooterNav go={go} back="step35_intro" />
    </div>
  );
}

// ============================================================
// STEP 3.5 — ADB-weak fallback funnel
// ============================================================
function Step35Fallback({ go, set }) {
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
        <FallbackRung num="1" status="active" title="Ask the number"
          desc="Tell us the HDMI number and we'll fire KEYCODE_TV_INPUT_HDMI_N. Stores a real HDMI number."
          action={
            <div className="row" style={{gap:6}}>
              {[1,2,3,4].map((n) =>
                <button key={n} className="filter-pill" onClick={() => { set({oppoInput:n, kodiInput: n === 1 ? 2 : 1}); go("step35_done"); }}>HDMI {n}</button>
              )}
            </div>
          } />
        <FallbackRung num="2" status="next" title="CEC One-Touch-Play"
          desc="Wake the OPPO so it asserts active source over CEC; the TV follows. Stores 'OPPO = CEC-asserted input' — no number needed."
          action={<button className="btn outline sm" onClick={() => { set({oppoInput:"cec", kodiInput: 1}); go("step35_done"); }}>Use CEC fallback</button>} />
        <FallbackRung num="3" status="next" title="Blind-cycle (last resort)"
          desc="Send the input-advance key; you tell us when the OPPO appears. Stores the lossy record — 'input after N advances' — flagged as brittle internally."
          action={<button className="btn outline sm" onClick={() => { set({oppoInput:"cycle:2", kodiInput: "cycle:1"}); go("step35_done"); }}>Cycle now</button>} />
        <FallbackRung num="4" status="exit" title="None of the above worked"
          desc="Switch inputs with your TV remote yourself. The add-on simply won't try to drive the TV."
          action={<button className="btn ghost sm" onClick={() => { set({tvManualSwitch:true}); go("step35_done"); }}>Manual switching</button>} />
      </div>
      <FooterNav go={go} back="step35_intro" />
    </div>
  );
}
function FallbackRung({ num, status, title, desc, action }) {
  return (
    <div className="tile" style={{cursor:'default', alignItems:'center'}}>
      <div className="tile-icon" style={{
        background: status === "active" ? "var(--accent-soft)" : "var(--surface-2)",
        color: status === "active" ? "var(--accent)" : "var(--muted)",
        fontWeight:700, fontFamily:'var(--font-display)'
      }}>{num}</div>
      <div className="tile-body">
        <div className="tile-title">{title} {status === "active" && <span className="chip accent" style={{marginLeft:6}}>Try this first</span>}</div>
        <div className="tile-desc">{desc}</div>
      </div>
      <div>{action}</div>
    </div>
  );
}

// ============================================================
// STEP 3.5 — Done
// ============================================================
function Step35Done({ go, state }) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Inputs captured.</h1>
        <p className="screen-subtitle">We'll use these for handoff and return-on-exit. You can edit them later in the add-on settings.</p>
      </div>
      <div className="grid-2">
        <div className="card">
          <h3 className="sub-title">Switch to</h3>
          <div className="row" style={{gap:14, marginTop:8}}>
            <div className="tile-icon"><Icon name="player" size={20}/></div>
            <div>
              <div style={{fontSize:14, fontWeight:600}}>OPPO {state.playerModel || "M9205 V1"}</div>
              <div className="muted" style={{fontSize:12, fontFamily:'var(--font-mono)', marginTop:2}}>
                HDMI {typeof state.oppoInput === "number" ? state.oppoInput : state.oppoInput || "3"}
                {state.oppoInput === "cec" && <> (CEC-asserted)</>}
                {typeof state.oppoInput === "string" && state.oppoInput.startsWith("cycle") && <> (blind-cycle · brittle)</>}
              </div>
            </div>
          </div>
        </div>
        <div className="card">
          <h3 className="sub-title">Return to</h3>
          <div className="row" style={{gap:14, marginTop:8}}>
            <div className="tile-icon"><Icon name="kodi" size={20}/></div>
            <div>
              <div style={{fontSize:14, fontWeight:600}}>Kodi box</div>
              <div className="muted" style={{fontSize:12, fontFamily:'var(--font-mono)', marginTop:2}}>
                HDMI {typeof state.kodiInput === "number" ? state.kodiInput : state.kodiInput || "1"}
              </div>
            </div>
          </div>
        </div>
      </div>
      {(typeof state.oppoInput === "string" && state.oppoInput.startsWith("cycle")) && (
        <div className="callout warn" style={{marginTop:14}}>
          <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
          <div className="callout-body">
            <strong>Blind-cycle is brittle.</strong> If your TV's input order ever shifts
            (added device, reordered ports), the return-target may land somewhere unexpected.
            Edit it manually in the add-on if that happens.
          </div>
        </div>
      )}
      <FooterNav go={go} back="step35_intro" next="test_setup" nextLabel="Run the full setup test" />
    </div>
  );
}

// ============================================================
// FULL SETUP TEST — copy disc + 3-question confirmation + success
// ============================================================
function TestSetup({ go, state, set }) {
  // mode: null (pick) | "disc" (use our bundled test ISO) | "own" (use your own file)
  const [mode, setMode] = React.useState(state.testMode || null);
  const [copied, setCopied] = React.useState(false);

  const pick = (m) => { setMode(m); set({testMode: m}); };

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Full setup test.</h1>
        <p className="screen-subtitle">
          End to end: handoff, TV switch, play, and Kodi-remote menu control. You pick
          how to test — use our bundled disc, or use one of your own files if you have a
          UHD ISO already in your library.
        </p>
      </div>

      {mode === null && (
        <div className="grid-2">
          <button className="tile" onClick={() => pick("disc")}>
            <div className="tile-icon"><Icon name="download" size={20}/></div>
            <div className="tile-body">
              <div className="tile-title">
                Use our test disc <span className="tile-badge recommended">Recommended</span>
              </div>
              <div className="tile-desc">
                We made a small UHD ISO ourselves — playable, with a navigable menu, named
                to trigger Kodi's eligibility rules. We'll copy it into your library so
                both Kodi and your player can see it.
              </div>
            </div>
            <Icon name="chevR" size={16}/>
          </button>
          <button className="tile" onClick={() => pick("own")}>
            <div className="tile-icon"><Icon name="folder" size={20}/></div>
            <div className="tile-body">
              <div className="tile-title">Use one of your own files</div>
              <div className="tile-desc">
                Open Kodi on your box, browse to any UHD ISO you already have, and press
                Play. Faster — but only works if you've got a UHD-tagged disc image in
                your library already.
              </div>
            </div>
            <Icon name="chevR" size={16}/>
          </button>
        </div>
      )}

      {mode !== null && (
        <div className="grid-2" style={{alignItems:'start'}}>
          {mode === "disc" && (
            <div className="card">
              <div className="row-between" style={{marginBottom:10}}>
                <h2 className="section-title" style={{margin:0}}>Where should we put the test disc?</h2>
                <button className="btn ghost sm" onClick={() => { setMode(null); setCopied(false); }}>
                  <Icon name="chevL" size={12}/> Change
                </button>
              </div>
              <div className="stack">
                <div className="field">
                  <label className="field-label">Save location</label>
                  <div className="row" style={{gap:8}}>
                    <input className="input" defaultValue="\\nas\Movies\_test\" style={{flex:1}} />
                    <button className="btn outline sm"><Icon name="folder" size={13}/> Browse…</button>
                  </div>
                </div>
                <div className="callout warn">
                  <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
                  <div className="callout-body">
                    Must be on the media library <strong>both Kodi and your player use</strong> —
                    not just a folder on this PC. If your library is a NAS or shared folder,
                    point here to that share.
                  </div>
                </div>
                {!copied ? (
                  <button className="btn primary" onClick={() => setCopied(true)}>
                    <Icon name="download" size={13}/> Copy test disc
                  </button>
                ) : (
                  <DiagLog
                    title="Copying test disc"
                    checks={[
                      { status:"pass", label:"OPPO-Installer-Test-2160p.iso", detail:"4.2 GB · copied OK" },
                      { status:"pass", label:"Path eligibility tag", detail:"contains '2160p' · disc-style" },
                      { status:"pass", label:"Reachable from Kodi box", detail:"confirmed via SFTP read" },
                    ]}
                    footer={<>Copied. <strong>Rescan your Kodi library</strong> so the test file appears, then play it from Kodi.</>}
                    footerKind="success"
                  />
                )}
              </div>
            </div>
          )}

          {mode === "own" && (
            <div className="card">
              <div className="row-between" style={{marginBottom:10}}>
                <h2 className="section-title" style={{margin:0}}>Now go to Kodi and play an ISO.</h2>
                <button className="btn ghost sm" onClick={() => setMode(null)}>
                  <Icon name="chevL" size={12}/> Change
                </button>
              </div>
              <div className="stack">
                <div className="stack-sm">
                  <InstructionStep n="1" title="Open Kodi on your box"
                    desc={<>That's your <span className="path">{state.kodiIp || "10.0.1.42"}</span> machine — not this Windows PC.</>} />
                  <InstructionStep n="2" title="Find any UHD ISO in your library"
                    desc={<>Filename should contain <span className="kbd">2160p</span>, <span className="kbd">UHD</span>, or <span className="kbd">4K</span> — that's what trips the eligibility rule. A <span className="path">BDMV/</span> folder works too.</>} />
                  <InstructionStep n="3" title="Press Play"
                    desc={<>Kodi should hand off to your player instead of starting playback itself. Your TV should switch. The disc menu should appear.</>} />
                  <InstructionStep n="4" title="Come back here when you're done"
                    desc={<>We'll ask three quick yes/no questions about what happened.</>} />
                </div>
                <div className="callout info">
                  <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
                  <div className="callout-body">
                    <strong>Nothing tagged UHD in your library?</strong> Switch to our test
                    disc instead — we'll copy one that's correctly tagged.
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="stack">
            <div className="card">
              <h3 className="sub-title">What this verifies</h3>
              <div className="stack-sm" style={{marginTop:8}}>
                <ChainCheckRow icon="kodi" label="Kodi launches the file" detail="playercorefactory.xml routes it" />
                <ChainCheckRow icon="tv"   label="TV switches input" detail="HDMI {state.oppoInput}" actualState={state} />
                <ChainCheckRow icon="player" label="Player picks it up" detail="and starts the disc menu" />
                <ChainCheckRow icon="remote" label="Kodi remote drives the menu" detail="remote-bridge keymap loaded" />
              </div>
            </div>
            {mode === "own" && (
              <div className="card" style={{padding:14}}>
                <div className="row" style={{gap:10}}>
                  <span className="chip"><Icon name="kodi" size={11}/> Kodi box</span>
                  <span className="muted" style={{fontSize:12}}>→</span>
                  <span className="chip accent"><Icon name="play" size={11}/> Play any UHD ISO</span>
                </div>
                <div className="muted" style={{fontSize:11.5, marginTop:8, fontFamily:'var(--font-mono)'}}>
                  we wait here · no commands sent until you tell us how it went
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <FooterNav go={go} back="step35_done"
        next={mode === "disc" && copied ? "test_confirm" : mode === "own" ? "test_confirm" : null}
        nextLabel={mode === "own" ? "I played one — how did it go?" : "I rescanned and played it — how did it go?"} />
    </div>
  );
}

function InstructionStep({ n, title, desc }) {
  return (
    <div className="row" style={{gap:12, alignItems:'flex-start', padding:'6px 0'}}>
      <span style={{
        minWidth:22, height:22, borderRadius:'50%',
        background:'var(--accent-soft)', color:'var(--accent)',
        display:'inline-flex', alignItems:'center', justifyContent:'center',
        fontSize:11, fontWeight:700, fontFamily:'var(--font-display)',
        flexShrink:0, marginTop:1,
      }}>{n}</span>
      <div style={{flex:1}}>
        <div style={{fontSize:13.5, fontWeight:600, color:'var(--text)', marginBottom:2}}>{title}</div>
        <div style={{fontSize:12.5, color:'var(--muted)', lineHeight:1.5}}>{desc}</div>
      </div>
    </div>
  );
}
function ChainCheckRow({ icon, label, detail, actualState }) {
  // detail may reference state values
  let d = detail;
  if (actualState && detail.includes("{state.oppoInput}")) {
    d = detail.replace("{state.oppoInput}", actualState.oppoInput || "3");
  }
  return (
    <div className="row" style={{gap:10}}>
      <span style={{color:'var(--muted)'}}><Icon name={icon} size={16}/></span>
      <span style={{flex:1, fontSize:13}}>{label}</span>
      <span className="muted" style={{fontSize:11.5, fontFamily:'var(--font-mono)'}}>{d}</span>
    </div>
  );
}

// ============================================================
// TEST — 3-question confirmation
// ============================================================
function TestConfirm({ go }) {
  const [answers, setAnswers] = React.useState({ play: null, switch: null, menu: null });
  const allAnswered = answers.play !== null && answers.switch !== null && answers.menu !== null;
  const allYes = answers.play === true && answers.switch === true && answers.menu === true;
  const nextScreen = allAnswered
    ? (allYes ? "test_success"
       : answers.play === false ? "step3_test"
       : answers.switch === false ? "step2_test"
       : "step1_intro")
    : null;
  const nextLabel = !allAnswered ? null
    : allYes ? "See the summary"
    : answers.play === false ? "Fix routing → Step 3"
    : answers.switch === false ? "Fix TV → Step 2"
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
          n="1" label="Did the test disc start playing on your player?"
          owner="Step 3 · Player / playercorefactory routing"
          value={answers.play} onChange={(v) => setAnswers({...answers, play:v})} />
        <Question
          n="2" label="Did your TV switch to the player's input?"
          owner="Step 2 · TV / Step 3.5 input capture"
          value={answers.switch} onChange={(v) => setAnswers({...answers, switch:v})} />
        <Question
          n="3" label="Can you navigate the disc menu with your Kodi remote?"
          owner="Step 1 · keymap not loaded / Kodi not restarted"
          value={answers.menu} onChange={(v) => setAnswers({...answers, menu:v})} />
      </div>
      {allAnswered && !allYes && (
        <div className="callout warn" style={{marginTop:18}}>
          <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
          <div className="callout-body">
            We'll send you back to the step that owns the failing piece — your other
            answers stay intact.
          </div>
        </div>
      )}
      {allAnswered && allYes && (
        <div className="callout success" style={{marginTop:18}}>
          <span className="callout-icon"><Icon name="check" size={13} stroke={2.2}/></span>
          <div className="callout-body">
            <strong>Setup verified end to end.</strong> Continue to the summary.
          </div>
        </div>
      )}
      <FooterNav go={go} back="test_setup" next={nextScreen} nextLabel={nextLabel || "Continue"} />
    </div>
  );
}
function Question({ n, label, owner, value, onChange }) {
  return (
    <div className={`tile ${value !== null ? "selected" : ""}`} style={{cursor:'default'}}>
      <div className="tile-icon" style={{
        background: value === true ? "var(--success-soft)" : value === false ? "var(--danger-soft)" : "var(--surface-2)",
        color: value === true ? "var(--success)" : value === false ? "var(--danger)" : "var(--muted)",
        fontWeight:700, fontFamily:'var(--font-display)'
      }}>
        {value === true ? "✓" : value === false ? "✕" : n}
      </div>
      <div className="tile-body">
        <div className="tile-title">{label}</div>
        <div className="tile-desc">
          {value === false
            ? <>Failure routes to → <strong>{owner}</strong></>
            : <>Failure would route to → {owner}</>}
        </div>
      </div>
      <div className="row" style={{gap:6}}>
        <button className={`filter-pill ${value === true ? "selected" : ""}`} onClick={() => onChange(true)}>Yes</button>
        <button className={`filter-pill ${value === false ? "selected" : ""}`} onClick={() => onChange(false)}>No</button>
      </div>
    </div>
  );
}

// ============================================================
// TEST — Success summary
// ============================================================
function TestSuccess({ go, state }) {
  return (
    <div className="screen">
      <div className="intro-hero">
        <div className="intro-eyebrow"><Icon name="check" size={12} stroke={2.4}/>&nbsp;&nbsp;Setup verified, end to end</div>
        <h1 className="intro-title">Your chain works.</h1>
        <p className="intro-body">
          Kodi hands off, your TV switches, the player picks up, and your Kodi remote
          drives the disc menu. Nothing else to do here — you can close this app.
        </p>

        <div className="card" style={{width:'100%', marginBottom:16}}>
          <h3 className="sub-title">Your chain</h3>
          <div style={{marginTop:10}}>
            <Chain active="all" completed={{media:true, kodi:true, tv:true, player:true}} />
          </div>
          <div className="divider" />
          <div className="stack-sm">
            <SummaryRow label="Kodi box" value={`${state.kodiIp || "10.0.1.42"} · ${state.tier === "A" ? "Auto-write + auto-apply" : state.tier === "B" ? "Auto-write (SMB)" : "Manual"}`} />
            <SummaryRow label="TV"        value={`${state.tvModel || "TCL 65Q9"} · backend ${state.tvBackend || "adb"}${state.tvAdbWeak ? " (input fallback)" : ""}`} />
            <SummaryRow label="Player"    value={`${state.playerBrand === "chinoppo" ? "Chinoppo" : "OPPO"} ${state.playerModel || "M9205 V1"} · ${state.playerIp || "10.0.1.77"}`} />
            <SummaryRow label="Switch to" value={`HDMI ${state.oppoInput || 3}`} />
            <SummaryRow label="Return to" value={`HDMI ${state.kodiInput || 1}`} />
          </div>
        </div>

        <div className="row" style={{gap:10}}>
          <button className="btn primary lg" onClick={() => go("step0_gate")}>
            <Icon name="check" size={14}/> Done
          </button>
          <button className="btn outline"><Icon name="download" size={14}/> Save setup report (.txt)</button>
        </div>

        <div className="muted" style={{fontSize:11.5, marginTop:18, fontFamily:'var(--font-mono)'}}>
          software-verified · hardware validation not claimed
        </div>
      </div>
    </div>
  );
}
function SummaryRow({ label, value }) {
  return (
    <div className="row" style={{gap:12, padding:'4px 0'}}>
      <span className="muted" style={{minWidth:90, fontSize:12, fontWeight:500}}>{label}</span>
      <span style={{fontSize:13, fontFamily:'var(--font-mono)'}}>{value}</span>
    </div>
  );
}

Object.assign(window, {
  Step3Brand, Step3Test, Step3Fail,
  Step35Intro, Step35Ask, Step35Fallback, Step35Done,
  TestSetup, TestConfirm, TestSuccess,
});
