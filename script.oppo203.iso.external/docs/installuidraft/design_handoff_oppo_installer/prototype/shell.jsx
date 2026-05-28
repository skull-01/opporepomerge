// shell.jsx — Windows chrome, chain diagram, progress indicators
// Exports to window: WinShell, Chain, Progress, Icon

const STEPS = [
  { id: "step0",      label: "Prerequisite",  short: "0",   num: "0",   chain: "media" },
  { id: "step1",      label: "Kodi box",       short: "1",   num: "1",   chain: "kodi" },
  { id: "step2",      label: "TV",             short: "2",   num: "2",   chain: "tv" },
  { id: "step3",      label: "Player",         short: "3",   num: "3",   chain: "player" },
  { id: "step3_5",    label: "Inputs",         short: "3.5", num: "3.5", chain: "tv-player" },
  { id: "test",       label: "Full test",      short: "T",   num: "✓",   chain: "all" },
];

// Map a screen id to a step id (so branch screens still highlight their parent step)
const SCREEN_TO_STEP = {
  // Step 0
  step0_gate: "step0",
  step0_exit: "step0",
  // Step 1
  step1_intro: "step1",
  step1_tierA: "step1",
  step1_tierB: "step1",
  step1_tierC: "step1",
  // Step 2
  step2_brand: "step2",
  step2_model: "step2",
  step2_notfound: "step2",
  step2_probe: "step2",
  step2_adb_warn: "step2",
  step2_test: "step2",
  step2_fail: "step2",
  // Step 3
  step3_brand: "step3",
  step3_test: "step3",
  step3_fail: "step3",
  // Step 3.5
  step35_intro: "step3_5",
  step35_ask: "step3_5",
  step35_fallback: "step3_5",
  step35_done: "step3_5",
  // Test
  test_setup: "test",
  test_confirm: "test",
  test_success: "test",
};

// Icon system — minimal, line-based, recognizable
function Icon({ name, size = 16, stroke = 1.8 }) {
  const s = size;
  const sw = stroke;
  const p = { fill: "none", stroke: "currentColor", strokeWidth: sw, strokeLinecap: "round", strokeLinejoin: "round" };
  const paths = {
    media:   <><rect x="3" y="5" width="18" height="14" rx="2" {...p} /><path d="M3 9h18M7 13h3M7 16h7" {...p} /></>,
    kodi:    <><rect x="3" y="4" width="18" height="13" rx="2" {...p} /><path d="M3 17l3 3h12l3-3M9 8l5 3-5 3z" {...p} /></>,
    tv:      <><rect x="3" y="5" width="18" height="13" rx="2" {...p} /><path d="M8 21h8M12 18v3" {...p} /></>,
    player:  <><rect x="2" y="8" width="20" height="9" rx="1.5" {...p} /><circle cx="17.5" cy="12.5" r="2" {...p} /><path d="M6 12h7M6 14h5" {...p} /></>,
    avr:     <><rect x="2" y="6" width="20" height="12" rx="1.5" {...p} /><circle cx="7" cy="12" r="2" {...p} /><circle cx="13" cy="12" r="2" {...p} /><path d="M18 10v4" {...p} /></>,
    hdmi:    <><path d="M8 4h8l2 3v10l-2 3H8l-2-3V7z M9 8h6M9 11h6" {...p} /></>,
    play:    <><path d="M8 5l11 7-11 7z" {...p} /></>,
    check:   <><path d="M5 12.5l4.5 4.5L19 6" {...p} /></>,
    cross:   <><path d="M6 6l12 12M18 6L6 18" {...p} /></>,
    chevR:   <><path d="M9 6l6 6-6 6" {...p} /></>,
    chevL:   <><path d="M15 6l-6 6 6 6" {...p} /></>,
    chevD:   <><path d="M6 9l6 6 6-6" {...p} /></>,
    refresh: <><path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5" {...p} /></>,
    search:  <><circle cx="11" cy="11" r="6" {...p} /><path d="M20 20l-4-4" {...p} /></>,
    info:    <><circle cx="12" cy="12" r="9" {...p} /><path d="M12 11v6M12 7.5v.1" {...p} /></>,
    warn:    <><path d="M12 3l10 17H2z M12 10v5M12 18v.1" {...p} /></>,
    spark:   <><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" {...p} /></>,
    folder:  <><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" {...p} /></>,
    file:    <><path d="M7 3h8l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z M14 3v5h5" {...p} /></>,
    terminal:<><rect x="3" y="4" width="18" height="16" rx="2" {...p} /><path d="M7 9l3 3-3 3M13 15h4" {...p} /></>,
    network: <><circle cx="12" cy="12" r="9" {...p} /><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" {...p} /></>,
    download:<><path d="M12 4v12M6 11l6 6 6-6M4 20h16" {...p} /></>,
    plug:    <><path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0z M12 18v4" {...p} /></>,
    remote:  <><rect x="7" y="2" width="10" height="20" rx="3" {...p} /><circle cx="12" cy="7" r="1.2" {...p} /><path d="M9.5 12h5M9.5 15h5M9.5 18h5" {...p} /></>,
    arrows:  <><path d="M4 12h16M4 12l4-4M4 12l4 4M20 12l-4-4M20 12l-4 4" {...p} /></>,
    bolt:    <><path d="M13 2L4 14h7l-1 8 9-12h-7z" {...p} /></>,
    power:   <><path d="M12 3v9M5.6 7.6a9 9 0 1 0 12.8 0" {...p} /></>,
    close:   <><path d="M6 6l12 12M18 6L6 18" {...p} /></>,
    min:     <><path d="M6 12h12" {...p} /></>,
    max:     <><rect x="5" y="5" width="14" height="14" rx="0" {...p} /></>,
  };
  return <svg width={s} height={s} viewBox="0 0 24 24" style={{display:'inline-block',flexShrink:0}}>{paths[name] || null}</svg>;
}

// ============================================================
// Windows-style chrome
// ============================================================
function WinShell({ children, title = "OPPO Installer" }) {
  return (
    <div className="win">
      <div className="titlebar">
        <div className="titlebar-title">
          <span className="titlebar-title-icon">O</span>
          <span>{title}</span>
        </div>
        <div className="titlebar-spacer" />
        <div className="titlebar-btns">
          <button className="titlebar-btn" tabIndex={-1}><Icon name="min" size={10} stroke={1.5}/></button>
          <button className="titlebar-btn" tabIndex={-1}><Icon name="max" size={10} stroke={1.5}/></button>
          <button className="titlebar-btn close" tabIndex={-1}><Icon name="close" size={10} stroke={1.5}/></button>
        </div>
      </div>
      <div className="win-body">{children}</div>
    </div>
  );
}

// ============================================================
// Chain diagram — persistent topology view
// activeChain: "media" | "kodi" | "tv" | "player" | "tv-player" | "all"
// ============================================================
function Chain({ active, completed = {} }) {
  // active is the current chain target; completed is { media, kodi, tv, player } booleans
  const nodes = [
    { id: "media",  icon: "media",  label: "Media",   sub: "prereq" },
    { id: "kodi",   icon: "kodi",   label: "Kodi box",sub: "10.0.1.42" },
    { id: "tv",     icon: "tv",     label: "TV",      sub: "TCL Q9" },
    { id: "player", icon: "player", label: "Player",  sub: "M9205 V1" },
  ];

  const isActive = (id) => active === id || (active === "all" && id !== "media") || (active === "tv-player" && (id === "tv" || id === "player"));
  const isDone = (id) => {
    if (active === "all") return completed[id];
    if (id === "media" && completed.media) return true;
    // active node not done
    if (isActive(id)) return false;
    return !!completed[id];
  };

  const edgeState = (a, b) => {
    if (active === "tv-player" && a === "tv" && b === "player") return "bidir";
    if (isActive(a) && completed[b]) return "active";
    if (isActive(b) && completed[a]) return "active";
    if (completed[a] && completed[b]) return "done";
    return "";
  };

  return (
    <div className="chain">
      {nodes.map((n, i) => (
        <React.Fragment key={n.id}>
          <div className={`chain-node ${isActive(n.id) ? "active" : ""} ${isDone(n.id) ? "done" : ""} ${n.id === "media" && completed.media && !isActive(n.id) ? "gated" : ""}`}>
            <div className="chain-icon"><Icon name={n.icon} size={20} /></div>
            <div className="chain-node-label">{n.label}</div>
          </div>
          {i < nodes.length - 1 && (
            <div className={`chain-edge ${edgeState(n.id, nodes[i+1].id)}`}>
              <div className="chain-edge-line" />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

// ============================================================
// Progress indicator — 3 variants
// ============================================================
function Progress({ variant, current, onJump }) {
  // current = step id ("step0", "step1", ...)
  const currentIdx = STEPS.findIndex((s) => s.id === current);
  if (variant === "stepper") {
    return (
      <div className="stepper">
        {STEPS.map((s, i) => (
          <React.Fragment key={s.id}>
            <button
              className={`stepper-item ${i < currentIdx ? "done" : ""} ${i === currentIdx ? "active" : ""}`}
              onClick={() => onJump && onJump(s.id)}
              style={{background:'none',border:'none',padding:0,cursor:'pointer'}}
            >
              <span className={`stepper-dot ${i < currentIdx ? "done" : ""} ${i === currentIdx ? "active" : ""}`}>
                <span className="num">{s.num}</span>
              </span>
              <span className="stepper-label">{s.label}</span>
            </button>
            {i < STEPS.length - 1 && <span className={`stepper-sep ${i < currentIdx ? "done" : ""}`} />}
          </React.Fragment>
        ))}
      </div>
    );
  }
  if (variant === "minimal") {
    const pct = ((currentIdx + 1) / STEPS.length) * 100;
    return (
      <div className="minimal-progress">
        <strong>{STEPS[currentIdx]?.label || "—"}</strong>
        <span>· Step {currentIdx + 1} of {STEPS.length}</span>
        <div className="bar"><div className="bar-fill" style={{width: pct + "%"}} /></div>
      </div>
    );
  }
  return null; // sidebar handled separately
}

function Sidebar({ current, onJump }) {
  const currentIdx = STEPS.findIndex((s) => s.id === current);
  return (
    <div className="sidebar">
      <div className="sidebar-title">Setup steps</div>
      {STEPS.map((s, i) => (
        <button
          key={s.id}
          className={`sidebar-step ${i < currentIdx ? "done" : ""} ${i === currentIdx ? "active" : ""}`}
          onClick={() => onJump && onJump(s.id)}
          style={{background:'none',border:'none',width:'100%',textAlign:'left',fontFamily:'inherit'}}
        >
          <span className="sidebar-step-dot">{i < currentIdx ? "✓" : s.num}</span>
          <span>{s.label}</span>
        </button>
      ))}
    </div>
  );
}

// ============================================================
// Header (chain + progress) — shown above content
// ============================================================
function AppHeader({ progressVariant, screenId, completed, chainActive, onJump }) {
  const stepId = SCREEN_TO_STEP[screenId] || "step0";
  return (
    <div className="app-header">
      {progressVariant === "stepper" && <Progress variant="stepper" current={stepId} onJump={onJump} />}
      {progressVariant === "minimal" && <Progress variant="minimal" current={stepId} onJump={onJump} />}
      <Chain active={chainActive} completed={completed} />
    </div>
  );
}

Object.assign(window, { WinShell, AppHeader, Sidebar, Chain, Progress, Icon, STEPS, SCREEN_TO_STEP });
