// app.jsx — Main app: routing, state, tweaks panel

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  aesthetic: "a",
  mode: "light",
  progress: "stepper",
}/*EDITMODE-END*/;

// Map each screen id to which chain node should be "active"
const SCREEN_TO_CHAIN = {
  step0_gate: "media", step0_exit: "media",
  step1_intro: "kodi", step1_tierA: "kodi", step1_tierB: "kodi", step1_tierC: "kodi",
  step2_brand: "tv", step2_model: "tv", step2_notfound: "tv", step2_probe: "tv",
  step2_adb_warn: "tv", step2_test: "tv", step2_fail: "tv",
  step3_brand: "player", step3_test: "player", step3_fail: "player",
  step35_intro: "tv-player", step35_ask: "tv-player",
  step35_fallback: "tv-player", step35_done: "tv-player",
  test_setup: "all", test_confirm: "all", test_success: "all",
};

// Map state flags to chain-completed nodes
function computeCompleted(state, screenId) {
  return {
    media: screenId !== "step0_gate", // gate accepted means media prereq is acknowledged
    kodi:  !!state.kodiVerified,
    tv:    !!state.tvVerified,
    player:!!state.playerVerified,
  };
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [screen, setScreen] = React.useState("step0_gate");
  const [state, setState] = React.useState({
    kodiIp: "10.0.1.42",
    tier: null,
    kodiVerified: false,
    tvBrand: null,
    tvModel: null,
    tvBackend: null,
    tvVerified: false,
    tvAdbWeak: false,
    tvManualSwitch: false,
    playerBrand: null,
    playerModel: null,
    playerIp: "10.0.1.77",
    playerVerified: false,
    oppoInput: null,
    kodiInput: null,
  });

  React.useEffect(() => {
    document.body.className = `theme-${t.aesthetic} mode-${t.mode}`;
  }, [t.aesthetic, t.mode]);

  const set = React.useCallback((patch) => setState((s) => ({ ...s, ...patch })), []);
  const go = React.useCallback((id) => {
    if (id) {
      setScreen(id);
      // scroll content back to top
      requestAnimationFrame(() => {
        const c = document.querySelector(".content-inner, .app-content");
        if (c) c.scrollTop = 0;
      });
    }
  }, []);

  // step id (for sidebar + progress)
  const stepId = SCREEN_TO_STEP[screen] || "step0";

  const renderScreen = () => {
    const props = { go, state, set };
    switch (screen) {
      case "step0_gate":   return <Step0Gate   {...props} />;
      case "step0_exit":   return <Step0Exit   {...props} />;
      case "step1_intro":  return <Step1Intro  {...props} />;
      case "step1_tierA":  return <Step1TierA  {...props} />;
      case "step1_tierB":  return <Step1TierB  {...props} />;
      case "step1_tierC":  return <Step1TierC  {...props} />;
      case "step2_brand":  return <Step2Brand  {...props} />;
      case "step2_model":  return <Step2Model  {...props} />;
      case "step2_notfound":return <Step2NotFound {...props} />;
      case "step2_probe":  return <Step2Probe  {...props} />;
      case "step2_adb_warn":return <Step2AdbWarn {...props} />;
      case "step2_test":   return <Step2Test   {...props} />;
      case "step2_fail":   return <Step2Fail   {...props} />;
      case "step3_brand":  return <Step3Brand  {...props} />;
      case "step3_test":   return <Step3Test   {...props} />;
      case "step3_fail":   return <Step3Fail   {...props} />;
      case "step35_intro": return <Step35Intro {...props} />;
      case "step35_ask":   return <Step35Ask   {...props} />;
      case "step35_fallback":return <Step35Fallback {...props} />;
      case "step35_done":  return <Step35Done  {...props} />;
      case "test_setup":   return <TestSetup   {...props} />;
      case "test_confirm": return <TestConfirm {...props} />;
      case "test_success": return <TestSuccess {...props} />;
      default:             return <Step0Gate   {...props} />;
    }
  };

  const completed = computeCompleted(state, screen);
  const chainActive = SCREEN_TO_CHAIN[screen] || "media";
  const useSidebar = t.progress === "sidebar";

  // Find first screen of a step (for sidebar jumps)
  const stepFirstScreen = (stepId) => {
    if (stepId === "step0") return "step0_gate";
    if (stepId === "step1") return "step1_intro";
    if (stepId === "step2") return "step2_brand";
    if (stepId === "step3") return "step3_brand";
    if (stepId === "step3_5") return "step35_intro";
    if (stepId === "test") return "test_setup";
    return "step0_gate";
  };
  const onJumpStep = (sid) => go(stepFirstScreen(sid));

  return (
    <React.Fragment>
      <WinShell title="OPPO Installer · setup wizard">
        {/* Header: chain + progress (unless sidebar) */}
        <div className="app-header">
          {!useSidebar && t.progress === "stepper" && <Progress variant="stepper" current={stepId} onJump={onJumpStep} />}
          {!useSidebar && t.progress === "minimal" && <Progress variant="minimal" current={stepId} onJump={onJumpStep} />}
          <Chain active={chainActive} completed={completed} />
        </div>

        {useSidebar ? (
          <div className="app-content with-sidebar">
            <Sidebar current={stepId} onJump={onJumpStep} />
            <div className="content-inner">{renderScreen()}</div>
          </div>
        ) : (
          <div className="app-content">{renderScreen()}</div>
        )}
      </WinShell>

      <TweaksPanel title="Design tweaks">
        <TweakSection label="Aesthetic" />
        <TweakRadio label="Direction" value={t.aesthetic}
          options={[
            {value:"a", label:"A · Warm Paper"},
            {value:"b", label:"B · Dim Lounge"},
            {value:"c", label:"C · Living Room"},
          ]}
          onChange={(v) => setTweak("aesthetic", v)} />
        <TweakRadio label="Mode" value={t.mode}
          options={[
            {value:"light", label:"Light"},
            {value:"dark", label:"Dark"},
          ]}
          onChange={(v) => setTweak("mode", v)} />
        <TweakSection label="Progress indicator" />
        <TweakRadio label="Style" value={t.progress}
          options={[
            {value:"stepper", label:"Stepper"},
            {value:"sidebar", label:"Sidebar"},
            {value:"minimal", label:"Minimal"},
          ]}
          onChange={(v) => setTweak("progress", v)} />
        <TweakSection label="Navigate" />
        <ScreenJumper screen={screen} go={go} />
      </TweaksPanel>
    </React.Fragment>
  );
}

// Quick screen jumper for the tweaks panel — useful for design review without walking the flow
function ScreenJumper({ screen, go }) {
  const groups = [
    { label: "Step 0 · Prereq",   screens: [
      {id:"step0_gate", name:"Gate"},
      {id:"step0_exit", name:"Exit branch"},
    ]},
    { label: "Step 1 · Kodi box", screens: [
      {id:"step1_intro", name:"Tier select"},
      {id:"step1_tierA", name:"Tier A · SSH"},
      {id:"step1_tierB", name:"Tier B · SMB"},
      {id:"step1_tierC", name:"Tier C · Manual"},
    ]},
    { label: "Step 2 · TV", screens: [
      {id:"step2_brand", name:"Brand"},
      {id:"step2_model", name:"Model"},
      {id:"step2_notfound", name:"Not found"},
      {id:"step2_probe", name:"Probe"},
      {id:"step2_adb_warn", name:"ADB heads-up"},
      {id:"step2_test", name:"Control test"},
      {id:"step2_fail", name:"Test failed"},
    ]},
    { label: "Step 3 · Player", screens: [
      {id:"step3_brand", name:"Brand + IP"},
      {id:"step3_test", name:"Wake & confirm"},
      {id:"step3_fail", name:"Test failed"},
    ]},
    { label: "Step 3.5 · Inputs", screens: [
      {id:"step35_intro", name:"Intro"},
      {id:"step35_ask", name:"Ask-first"},
      {id:"step35_fallback", name:"ADB-weak fallback"},
      {id:"step35_done", name:"Captured"},
    ]},
    { label: "Test", screens: [
      {id:"test_setup", name:"Copy disc"},
      {id:"test_confirm", name:"3 questions"},
      {id:"test_success", name:"All verified"},
    ]},
  ];
  return (
    <div style={{display:'flex', flexDirection:'column', gap:8, padding:'4px 0'}}>
      {groups.map((g) => (
        <div key={g.label}>
          <div style={{fontSize:10, fontWeight:600, textTransform:'uppercase', letterSpacing:'0.06em', color:'#888', marginBottom:4}}>{g.label}</div>
          <div style={{display:'flex', flexWrap:'wrap', gap:4}}>
            {g.screens.map((s) => (
              <button key={s.id}
                onClick={() => go(s.id)}
                style={{
                  padding:'3px 8px', borderRadius:6, fontSize:11, cursor:'pointer',
                  border:'1px solid '+(screen === s.id ? 'var(--accent,#666)' : 'rgba(127,127,127,0.3)'),
                  background: screen === s.id ? 'var(--accent,#666)' : 'transparent',
                  color: screen === s.id ? 'white' : 'inherit',
                  fontFamily: 'inherit',
                }}>
                {s.name}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
