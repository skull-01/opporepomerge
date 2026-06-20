// screens-1.jsx — Step 0 (gate + exit), Step 1 (intro + tier A/B/C), Step 2 (TV)

// ============================================================
// STEP 0 — Prerequisite gate
// ============================================================
function Step0Gate({ go }) {
  return (
    <div className="screen">
      <div className="intro-hero">
        <div className="intro-eyebrow">Before we start</div>
        <h1 className="intro-title">Your player needs to reach your media on its own first.</h1>
        <p className="intro-body">
          This wizard sets up the <em>handoff</em> — when you launch a 4K UHD or Blu-ray
          disc image in Kodi, it tells your OPPO or clone player to take over, and
          switches your TV to match. It doesn't set up <em>how</em> your player reaches
          your files. That part needs to be working already.
        </p>
        <div className="intro-checklist">
          <h3 className="sub-title" style={{marginBottom:10}}>Before continuing, confirm</h3>
          <div className="intro-check">You can already browse to an ISO directly on your OPPO/clone.</div>
          <div className="intro-check">It plays from the same media library Kodi uses.</div>
          <div className="intro-check">No new wiring or shares are required to make that happen.</div>
        </div>
        <div className="row" style={{gap:10}}>
          <button className="btn primary lg" onClick={() => go("step1_intro")}>
            I can already play ISOs on my player
            <Icon name="chevR" size={14} />
          </button>
          <button className="btn ghost" onClick={() => go("step0_exit")}>
            Not yet
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// STEP 0 — Exit branch (media-source help, not a dead-end)
// ============================================================
function Step0Exit({ go }) {
  const opts = [
    { tag: "Simplest", title: "Local USB or hard drive on the player",
      desc: "Plug a drive straight into the player. No network involved — sidesteps the entire SMB1 problem." },
    { tag: "Direct",   title: "Direct SMB1 share",
      desc: "A Windows folder or NAS configured for SMB1 / NTLMv1. Reliable when the network is right; needs the old protocol." },
    { tag: "Often better", title: "NFS share",
      desc: "NFS is often more reliable on OPPO than SMB1 if your NAS supports it." },
    { tag: "Heavy",    title: "SMB1 proxy",
      desc: "Bridge SMB1 through a dedicated Ubuntu VM, or re-share through Windows. Last resort." },
  ];
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">No problem — let's get your player reading files first.</h1>
        <p className="screen-subtitle">
          Your OPPO or clone needs to reach your media on its own first. The player only
          speaks <span className="kbd">SMB1</span> — pick whichever fits your setup.
        </p>
      </div>
      <div className="choice-grid">
        {opts.map((o, i) => (
          <button key={i} className="choice-card">
            <div className="choice-card-title">
              <span>{o.title}</span>
              <span className="choice-card-tag">{o.tag}</span>
            </div>
            <div className="choice-card-desc">{o.desc}</div>
          </button>
        ))}
      </div>
      <div className="callout info" style={{marginTop:18}}>
        <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
        <div className="callout-body">
          Once you can browse to an ISO on the player and play it directly,
          come back and we'll continue from here.
        </div>
      </div>
      <div className="row" style={{marginTop:18, gap:10}}>
        <button className="btn outline"><Icon name="file" size={14}/> Open setup guide</button>
        <button className="btn ghost" onClick={() => go("step0_gate")}><Icon name="chevL" size={14}/> Back</button>
      </div>
    </div>
  );
}

// ============================================================
// STEP 1 — Kodi box (tier select)
// ============================================================
function Step1Intro({ go, state, set }) {
  const ip = state.kodiIp || "10.0.1.42";
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Your Kodi box</h1>
        <p className="screen-subtitle">
          Kodi runs on a separate device from this app. Enter its IP so we can deliver
          your setup files, then choose how they should be installed.
        </p>
      </div>
      <div className="card" style={{marginBottom:20, maxWidth:520}}>
        <div className="field">
          <label className="field-label">Kodi box IP</label>
          <div className="row" style={{gap:8}}>
            <input className="input" value={ip} onChange={(e)=>set({kodiIp: e.target.value})} style={{flex:1}} />
            <button className="btn outline"><Icon name="search" size={14}/> Find on network</button>
          </div>
          <div className="field-hint">Reachable from this Windows PC. Reserve it on DHCP if you can.</div>
        </div>
      </div>

      <h2 className="section-title" style={{marginTop:8}}>How should we install — and apply — your setup files?</h2>
      <div className="stack" style={{marginTop:10}}>
        <button className="tile" onClick={()=>{set({tier:"A"}); go("step1_tierA");}}>
          <div className="tile-icon"><Icon name="bolt" size={20}/></div>
          <div className="tile-body">
            <div className="tile-title">
              Auto-write + auto-apply <span className="tile-badge recommended">Recommended</span>
            </div>
            <div className="tile-desc">
              We copy the files <em>and</em> restart Kodi for you. Needs SSH enabled —
              default-on for CoreELEC and LibreELEC.
            </div>
          </div>
          <Icon name="chevR" size={16}/>
        </button>
        <button className="tile" onClick={()=>{set({tier:"B"}); go("step1_tierB");}}>
          <div className="tile-icon"><Icon name="download" size={20}/></div>
          <div className="tile-body">
            <div className="tile-title">Auto-write only (SMB)</div>
            <div className="tile-desc">
              We copy the files; you restart Kodi yourself. Works on stock Windows / Android
              Kodi boxes where SSH isn't on by default.
            </div>
          </div>
          <Icon name="chevR" size={16}/>
        </button>
        <button className="tile" onClick={()=>{set({tier:"C"}); go("step1_tierC");}}>
          <div className="tile-icon"><Icon name="folder" size={20}/></div>
          <div className="tile-body">
            <div className="tile-title">I'll do it myself <span className="tile-badge advanced">Manual</span></div>
            <div className="tile-desc">
              We generate the files; you place them and restart. Most control, most work.
            </div>
          </div>
          <Icon name="chevR" size={16}/>
        </button>
      </div>
    </div>
  );
}

// ============================================================
// Reusable diagnostic-log component
// ============================================================
function DiagLog({ title, checks, footer, footerKind, output }) {
  // checks: { label, detail, status: 'pass'|'fail'|'warn'|'run'|'pending' }
  const anyRunning = checks.some((c) => c.status === "run");
  const allPass = checks.every((c) => c.status === "pass");
  const anyFail = checks.some((c) => c.status === "fail");
  const headerDotClass = anyFail ? "fail" : anyRunning ? "running" : allPass ? "" : "running";
  const headerText = anyFail ? "Failed" : anyRunning ? "Running…" : allPass ? "All checks passed" : "Idle";
  return (
    <div className="diag">
      <div className="diag-header">
        <span className={`diag-header-dot ${headerDotClass}`} />
        <strong style={{color:'var(--text)', fontWeight:600}}>{title}</strong>
        <span className="spacer" />
        <span>{headerText}</span>
      </div>
      <div className="diag-list">
        {checks.map((c, i) => (
          <div key={i} className={`diag-row ${c.status === "pending" ? "diag-pending" : ""}`}>
            <span className={`diag-icon ${c.status}`}>
              {c.status === "pass" ? "✓" : c.status === "fail" ? "✕" : c.status === "warn" ? "!" : c.status === "pending" ? "·" : ""}
            </span>
            <span className="diag-label">{c.label}</span>
            <span className="diag-detail">{c.detail}</span>
          </div>
        ))}
      </div>
      {output && <pre className="diag-output">{output}</pre>}
      {footer && <div className={`diag-footer ${footerKind || ""}`}>{footer}</div>}
    </div>
  );
}

// ============================================================
// STEP 1 — Tier A (SSH)
// ============================================================
function Step1TierA({ go, state, set }) {
  const [tested, setTested] = React.useState(false);
  const checks = tested ? [
    { status: "pass", label: "SSH reachable at 10.0.1.42:22", detail: "OpenSSH_8.0 · ed25519 fingerprint OK" },
    { status: "pass", label: "userdata located & writable", detail: "/storage/.kodi/userdata/ · 4 KB temp write OK" },
    { status: "pass", label: "Kodi restart command available", detail: "systemctl restart kodi" },
  ] : [
    { status: "pending", label: "SSH reachable at 10.0.1.42:22", detail: "" },
    { status: "pending", label: "userdata located & writable", detail: "" },
    { status: "pending", label: "Kodi restart command available", detail: "" },
  ];
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Auto-write + auto-apply (SSH)</h1>
        <p className="screen-subtitle">
          One login handles both copying the files and restarting Kodi. SFTP-write + SSH-restart
          on the same credentials — not SMB plus a separate hop.
        </p>
      </div>
      <div className="grid-2" style={{alignItems:'start'}}>
        <div className="card">
          <h2 className="section-title">SSH credentials</h2>
          <div className="stack">
            <div className="field">
              <label className="field-label">Username</label>
              <input className="input" defaultValue="root" />
            </div>
            <div className="field">
              <label className="field-label">Authentication</label>
              <div className="row" style={{gap:8}}>
                <button className="filter-pill selected">Password</button>
                <button className="filter-pill">SSH key</button>
              </div>
            </div>
            <div className="field">
              <label className="field-label">Password</label>
              <input className="input" type="password" defaultValue="••••••••" />
              <div className="field-hint">CoreELEC default is <span className="kbd">coreelec</span>.</div>
            </div>
            <button className="btn primary" onClick={() => setTested(true)}>
              <Icon name="play" size={13}/> Test connection
            </button>
          </div>
        </div>
        <div className="stack">
          <DiagLog
            title="Connection checks"
            checks={checks}
            footer={tested
              ? <>All set — we'll install your files and restart Kodi for you, backing up anything already there.</>
              : <span className="muted">Run the test to verify each check independently.</span>}
            footerKind={tested ? "success" : ""}
          />
          {tested && (
            <div className="callout info">
              <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
              <div className="callout-body">
                <strong>Auto-apply is CoreELEC / LibreELEC only.</strong> On other platforms,
                we'll fall back to "auto-write, you restart."
              </div>
            </div>
          )}
        </div>
      </div>
      <FooterNav go={go} back="step1_intro" next={tested ? "step2_brand" : null} nextLabel="Continue to TV" set={set} setKeys={{kodiVerified: true}} />
    </div>
  );
}

// ============================================================
// STEP 1 — Tier B (SMB)
// ============================================================
function Step1TierB({ go, state, set }) {
  const [tested, setTested] = React.useState(false);
  const checks = tested ? [
    { status: "pass", label: "Box reachable at 10.0.1.42", detail: "ICMP 0.4 ms · 0% loss" },
    { status: "pass", label: "userdata share accessible", detail: "\\\\10.0.1.42\\Kodi · creds OK" },
    { status: "pass", label: "Write test passed", detail: "temp file created + removed" },
  ] : [
    { status: "pending", label: "Box reachable at 10.0.1.42", detail: "" },
    { status: "pending", label: "userdata share accessible", detail: "" },
    { status: "pending", label: "Write test passed", detail: "" },
  ];
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Auto-write only (SMB)</h1>
        <p className="screen-subtitle">
          We'll copy the files for you. You'll restart Kodi yourself afterwards — SMB
          can't reload Kodi on its own.
        </p>
      </div>
      <div className="grid-2" style={{alignItems:'start'}}>
        <div className="card">
          <h2 className="section-title">SMB share</h2>
          <div className="stack">
            <div className="field">
              <label className="field-label">Share path</label>
              <input className="input" defaultValue="\\10.0.1.42\Kodi" />
              <div className="field-hint">The share that contains the <span className="path">userdata</span> folder.</div>
            </div>
            <div className="grid-2">
              <div className="field">
                <label className="field-label">Username <span className="muted">(if needed)</span></label>
                <input className="input text" placeholder="optional" />
              </div>
              <div className="field">
                <label className="field-label">Password</label>
                <input className="input" type="password" placeholder="optional" />
              </div>
            </div>
            <button className="btn primary" onClick={() => setTested(true)}>
              <Icon name="play" size={13}/> Test access
            </button>
          </div>
        </div>
        <div className="stack">
          <DiagLog
            title="Share checks"
            checks={checks}
            footer={tested
              ? <>All set — we'll install your files with a backup. <strong>You'll restart Kodi yourself</strong> so it loads them.</>
              : <span className="muted">Run the test to verify each check.</span>}
            footerKind={tested ? "success" : ""}
          />
          {tested && (
            <div className="callout warn">
              <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
              <div className="callout-body">
                <strong>After the wizard finishes,</strong> restart Kodi on your box
                (reboot it, or quit-and-relaunch the Kodi app).
              </div>
            </div>
          )}
        </div>
      </div>
      <FooterNav go={go} back="step1_intro" next={tested ? "step2_brand" : null} nextLabel="Continue to TV" set={set} setKeys={{kodiVerified: true}} />
    </div>
  );
}

// ============================================================
// STEP 1 — Tier C (Manual)
// ============================================================
function Step1TierC({ go, state, set }) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">You'll install the files yourself</h1>
        <p className="screen-subtitle">
          We'll generate <span className="path">playercorefactory.xml</span> and the
          remote-bridge keymap and show you where they go.
        </p>
      </div>

      <div className="callout warn" style={{marginBottom:18}}>
        <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
        <div className="callout-body">
          <strong>Back up first.</strong> Before copying anything in, make a copy of these
          from your Kodi <span className="path">userdata</span> folder — if either already
          exists, our files will replace yours.
          <div className="stack-sm" style={{marginTop:10}}>
            <div className="row" style={{gap:8}}>
              <Icon name="file" size={14}/>
              <span><span className="path">playercorefactory.xml</span> — if you have one, it likely contains your other players. Back it up or merge our entries by hand, or you'll lose them.</span>
            </div>
            <div className="row" style={{gap:8}}>
              <Icon name="folder" size={14}/>
              <span><span className="path">keymaps/</span> folder — back up anything there you want to keep (risk is a same-name collision, not the whole folder).</span>
            </div>
          </div>
          <div className="muted" style={{marginTop:10, fontSize:12}}>
            If a file doesn't exist yet, there's nothing to back up — just drop ours in.
          </div>
        </div>
      </div>

      <h2 className="section-title">Where to put the files</h2>
      <div className="stack" style={{marginTop:10}}>
        <PathRow platform="CoreELEC / LibreELEC"
          file="/storage/.kodi/userdata/" keymap="/storage/.kodi/userdata/keymaps/" />
        <PathRow platform="Android (Shield, Ugoos, …)"
          file="/sdcard/Android/data/org.xbmc.kodi/files/.kodi/userdata/"
          keymap=".kodi/userdata/keymaps/"
          note="app-private storage may be hard to browse — use Kodi's file manager or copy via SMB / USB" />
        <PathRow platform="Windows"
          file="%APPDATA%\Kodi\userdata\" keymap="%APPDATA%\Kodi\userdata\keymaps\" />
      </div>

      <div className="callout info" style={{marginTop:16}}>
        <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
        <div className="callout-body">
          <strong>Remember this folder.</strong> You'll need it again if you ever
          regenerate these files. After copying, <strong>restart Kodi</strong> so it
          loads them.
        </div>
      </div>

      <div className="row" style={{marginTop:18, gap:10}}>
        <button className="btn primary"><Icon name="download" size={14}/> Generate &amp; save files</button>
        <button className="btn outline"><Icon name="folder" size={14}/> Open output folder</button>
      </div>
      <FooterNav go={go} back="step1_intro" next="step2_brand" nextLabel="Continue to TV"
        set={set} setKeys={{kodiVerified: true}} />
    </div>
  );
}

function PathRow({ platform, file, keymap, note }) {
  return (
    <div className="card" style={{padding:14}}>
      <div className="row-between">
        <strong style={{fontSize:13}}>{platform}</strong>
        <span className="chip"><Icon name="folder" size={11}/> userdata</span>
      </div>
      <div className="stack-sm" style={{marginTop:8}}>
        <div className="row"><span className="muted" style={{minWidth:80, fontSize:12}}>main</span><span className="path">{file}</span></div>
        <div className="row"><span className="muted" style={{minWidth:80, fontSize:12}}>keymap</span><span className="path">{keymap}</span></div>
      </div>
      {note && <div className="muted" style={{fontSize:12, marginTop:8}}>{note}</div>}
    </div>
  );
}

// ============================================================
// STEP 2 — TV brand
// ============================================================
const TV_BRANDS = [
  { id: "sony",     name: "Sony",     ch: "S",  hint: "Bravia · Google TV" },
  { id: "samsung",  name: "Samsung",  ch: "Sa", hint: "Tizen" },
  { id: "lg",       name: "LG",       ch: "LG", hint: "webOS" },
  { id: "tcl",      name: "TCL",      ch: "T",  hint: "Google / Roku" },
  { id: "hisense",  name: "Hisense",  ch: "H",  hint: "VIDAA / Google / Roku" },
  { id: "roku",     name: "Roku TV",  ch: "R",  hint: "ECP" },
  { id: "vizio",    name: "Vizio",    ch: "V",  hint: "SmartCast" },
  { id: "panasonic",name: "Panasonic",ch: "P",  hint: "MyHome / FireTV" },
  { id: "other",    name: "Other",    ch: "?",  hint: "or not listed" },
];

function Step2Brand({ go, state, set }) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Your TV</h1>
        <p className="screen-subtitle">
          Pick your TV's brand. The control method comes from the platform (Google TV →
          ADB, Roku → ECP, webOS → LG, …) — your exact model just helps us confirm.
        </p>
      </div>
      <div className="brand-grid">
        {TV_BRANDS.map((b) => (
          <button key={b.id}
            className={`brand-pill ${state.tvBrand === b.id ? "selected" : ""}`}
            onClick={() => { set({tvBrand: b.id}); go("step2_model"); }}>
            <div className="brand-logo">{b.ch}</div>
            <div>{b.name}</div>
            <div className="muted" style={{fontSize:10.5, fontWeight:500}}>{b.hint}</div>
          </button>
        ))}
      </div>
      <FooterNav go={go} back="step1_intro" />
    </div>
  );
}

// ============================================================
// STEP 2 — Model
// ============================================================
function Step2Model({ go, state, set }) {
  const [year, setYear] = React.useState("2023");
  const [size, setSize] = React.useState("65\"");
  const [search, setSearch] = React.useState("");
  const allModels = [
    { id: "55q9-2023",  name: "55Q9 (2023)",  year: "2023", size: "55\"", platform: "Google TV", tier: "probe", backend: "adb" },
    { id: "65q9-2023",  name: "65Q9 (2023)",  year: "2023", size: "65\"", platform: "Google TV", tier: "probe", backend: "adb" },
    { id: "75q9-2023",  name: "75Q9 (2023)",  year: "2023", size: "75\"", platform: "Google TV", tier: "probe", backend: "adb" },
    { id: "65q10-2024", name: "65Q10 Pro",    year: "2024", size: "65\"", platform: "Google TV", tier: "probe", backend: "adb" },
    { id: "65q7-2022",  name: "65Q7",         year: "2022", size: "65\"", platform: "Google TV", tier: "probe", backend: "adb" },
    { id: "55r5-2022",  name: "55R5 (Roku)",  year: "2022", size: "55\"", platform: "Roku TV",   tier: "probe", backend: "roku_ecp" },
  ];
  const filtered = allModels.filter((m) =>
    (!year || m.year === year) && (!size || m.size === size) &&
    (m.name.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Which TCL model?</h1>
        <p className="screen-subtitle">Year and size are just to narrow the list — the control method comes from the platform.</p>
      </div>

      <div className="stack" style={{gap:14}}>
        <div className="row" style={{gap:10}}>
          <div className="field" style={{flex:1, maxWidth:360}}>
            <input className="input text" placeholder="Search models…" value={search} onChange={(e)=>setSearch(e.target.value)} />
          </div>
          <span className="spacer" />
          <button className="btn ghost sm" onClick={() => go("step2_notfound")}>
            <Icon name="search" size={13}/> Can't find my model
          </button>
        </div>
        <div className="row" style={{gap:8, alignItems:'center'}}>
          <span className="muted" style={{fontSize:12, fontWeight:500}}>Year</span>
          <div className="filter-row">
            {["2025","2024","2023","2022","2021","2020","2019","2018"].map((y) =>
              <button key={y} className={`filter-pill ${year===y?"selected":""}`} onClick={()=>setYear(year===y?"":y)}>{y}</button>
            )}
          </div>
        </div>
        <div className="row" style={{gap:8, alignItems:'center'}}>
          <span className="muted" style={{fontSize:12, fontWeight:500}}>Size</span>
          <div className="filter-row">
            {["43\"","50\"","55\"","65\"","75\"","85\""].map((s) =>
              <button key={s} className={`filter-pill ${size===s?"selected":""}`} onClick={()=>setSize(size===s?"":s)}>{s}</button>
            )}
          </div>
        </div>

        <div className="model-list">
          {filtered.length === 0 && (
            <div className="model-row" style={{justifyContent:'center', color:'var(--muted)'}}>No matches — try adjusting filters or <button className="btn ghost sm" onClick={()=>go("step2_notfound")}>tell us it's not here</button></div>
          )}
          {filtered.map((m) => (
            <div key={m.id}
              className={`model-row ${state.tvModel === m.id ? "selected" : ""}`}
              onClick={() => { set({tvModel: m.id, tvPlatform: m.platform, tvBackend: m.backend}); }}>
              <div>
                <div>{m.name}</div>
                <div className="model-row-meta">{m.platform} · backend <code>{m.backend}</code></div>
              </div>
              <span className={`chip ${m.tier === "probe" ? "success" : "warn"}`}>
                <span className="chip-dot"/>
                {m.tier === "probe" ? "probe & confirm" : "bring-your-own command"}
              </span>
            </div>
          ))}
        </div>
      </div>
      <FooterNav go={go} back="step2_brand" next={state.tvModel ? "step2_adb_warn" : null} nextLabel="Continue" />
    </div>
  );
}

// ============================================================
// STEP 2 — Model not found / probe
// ============================================================
function Step2NotFound({ go, set }) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">We couldn't find your model.</h1>
        <p className="screen-subtitle">
          That's fine — TVs from 2026+ are deliberately outside our database, and older
          models drift out of it too. You've got two honest paths from here.
        </p>
      </div>
      <div className="grid-2">
        <button className="tile" onClick={() => go("step2_probe")}>
          <div className="tile-icon"><Icon name="search" size={20}/></div>
          <div className="tile-body">
            <div className="tile-title">Probe the TV <span className="tile-badge recommended">Recommended</span></div>
            <div className="tile-desc">
              We test the ports each backend uses (ADB :5555, Roku :8060, Sony IP, …)
              against your real TV and report what answers.
            </div>
          </div>
          <Icon name="chevR" size={16}/>
        </button>
        <button className="tile" onClick={() => { set({tvBackend:"custom_command"}); go("step2_adb_warn"); }}>
          <div className="tile-icon"><Icon name="terminal" size={20}/></div>
          <div className="tile-body">
            <div className="tile-title">Choose the method manually</div>
            <div className="tile-desc">
              Pick a backend yourself — including the <code>custom_command</code> escape
              hatch for anything else (Panasonic, Vizio, projectors, CEC scripts).
            </div>
          </div>
          <Icon name="chevR" size={16}/>
        </button>
      </div>
      <div className="callout info" style={{marginTop:18}}>
        <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
        <div className="callout-body">
          A failed probe doesn't mean "unsupported" — usually it just means debugging is
          off or the IP is wrong. Either way, we won't dead-end you.
        </div>
      </div>
      <FooterNav go={go} back="step2_model" />
    </div>
  );
}

function Step2Probe({ go, state, set }) {
  const [probed, setProbed] = React.useState(false);
  const checks = probed ? [
    { status: "pass", label: "Roku ECP on :8060",         detail: "200 OK · TCL · 55R5 · firmware 12.5" },
    { status: "fail", label: "ADB on :5555",              detail: "connection refused (debugging off?)" },
    { status: "fail", label: "Sony IP control on :20060", detail: "no response" },
    { status: "fail", label: "Samsung SmartThings",       detail: "skipped — no token configured" },
  ] : [
    { status: "pending", label: "Roku ECP on :8060",         detail: "" },
    { status: "pending", label: "ADB on :5555",              detail: "" },
    { status: "pending", label: "Sony IP control on :20060", detail: "" },
    { status: "pending", label: "Samsung SmartThings",       detail: "" },
  ];
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Probe your TV</h1>
        <p className="screen-subtitle">We'll knock on each backend's port and see what answers. No state-changing commands sent.</p>
      </div>
      <div className="grid-2" style={{alignItems:'start'}}>
        <div className="card">
          <h2 className="section-title">Probe target</h2>
          <div className="stack">
            <div className="field">
              <label className="field-label">TV IP</label>
              <input className="input" defaultValue="10.0.1.51" />
              <div className="field-hint">Same network as this PC and your Kodi box.</div>
            </div>
            <button className="btn primary" onClick={() => setProbed(true)}>
              <Icon name="search" size={13}/> Probe the TV
            </button>
          </div>
        </div>
        <div className="stack">
          <DiagLog
            title="Port probe"
            checks={checks}
            footer={probed
              ? <><strong className="success-text">Looks like a Roku TV.</strong> We'll use the <code>roku_ecp</code> backend — input switching and confirm are clean here.</>
              : <span className="muted">Probe the TV to see which backends answer.</span>}
            footerKind={probed ? "success" : ""}
          />
        </div>
      </div>
      <FooterNav go={go} back="step2_notfound" next={probed ? "step2_test" : null} nextLabel="Use Roku ECP" set={set} setKeys={{tvBackend:"roku_ecp", tvModel:"probed-roku"}} />
    </div>
  );
}

// ============================================================
// STEP 2 — ADB allow-debugging heads up
// ============================================================
function Step2AdbWarn({ go, state }) {
  const isAdb = state.tvBackend === "adb" || (state.tvModel || "").includes("q");
  if (!isAdb) {
    // skip past for non-ADB backends
    return <Step2Test go={go} state={state} />;
  }
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Heads-up: your TV may ask permission.</h1>
        <p className="screen-subtitle">
          ADB control needs the TV to trust this app the first time we connect. The TV (not
          us) shows the prompt — read it from across the room if you can.
        </p>
      </div>
      <div className="split" style={{marginTop:8}}>
        <div className="tv-mockup">
          <div className="tv-mockup-screen">
            <div className="tv-mockup-text">▼ Allow USB debugging?</div>
            <div className="tv-mockup-text bright">"Always allow from this computer"</div>
            <div className="tv-mockup-text" style={{fontSize:10}}>Cancel &nbsp; · &nbsp; OK</div>
          </div>
          <div className="stand"/>
        </div>
        <div className="stack">
          <div className="callout warn">
            <span className="callout-icon"><Icon name="warn" size={13} stroke={2.2}/></span>
            <div className="callout-body">
              <strong>Pick "Always allow from this computer"</strong>, not the plain OK. A
              one-time accept can drop on a TV reboot and break silently later.
            </div>
          </div>
          <div className="callout info">
            <span className="callout-icon"><Icon name="info" size={13} stroke={2.2}/></span>
            <div className="callout-body">
              <strong>No prompt at all?</strong> The dialog only appears if Developer
              Options → USB debugging is already on. If you don't see it, debugging is off
              — enable it and try again.
            </div>
          </div>
          <button className="btn primary lg" onClick={() => go("step2_test")}>
            I'm ready — send the test
          </button>
        </div>
      </div>
      <FooterNav go={go} back="step2_model" />
    </div>
  );
}

// ============================================================
// STEP 2 — Control test (the basic-control gate)
// ============================================================
function Step2Test({ go, state, set }) {
  const [phase, setPhase] = React.useState("ready"); // ready | sending | sent
  React.useEffect(() => {
    if (phase === "sending") {
      const t = setTimeout(() => setPhase("sent"), 1500);
      return () => clearTimeout(t);
    }
  }, [phase]);
  const send = () => setPhase("sending");

  const checks =
    phase === "sending" ? [
      { status: "pass", label: "ADB connected to 10.0.1.51:5555", detail: "RSA pairing accepted" },
      { status: "run",  label: "Send KEYCODE_VOLUME_MUTE",        detail: "test command (no input change)" },
      { status: "pending", label: "Confirm with you",             detail: "waiting for you" },
    ] :
    phase === "sent" ? [
      { status: "pass", label: "ADB connected to 10.0.1.51:5555", detail: "RSA pairing accepted" },
      { status: "pass", label: "Send KEYCODE_VOLUME_MUTE",        detail: "command transmitted · 124 ms" },
      { status: "run",  label: "Did your TV mute / unmute?",      detail: "waiting for your answer" },
    ] : [
      { status: "pending", label: "ADB connected to 10.0.1.51:5555", detail: "" },
      { status: "pending", label: "Send KEYCODE_VOLUME_MUTE",        detail: "" },
      { status: "pending", label: "Confirm with you",                detail: "" },
    ];

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Can we control your TV?</h1>
        <p className="screen-subtitle">
          Quick test — we'll send a mute blip. No inputs change, no OPPO wake. Just answers
          one question: <em>can we drive this TV at all?</em>
        </p>
      </div>
      <div className="grid-2" style={{alignItems:'start'}}>
        <div className="stack">
          <DiagLog
            title="Basic control test"
            checks={checks}
            footer={phase === "ready"
              ? <span className="muted">Click "Send test signal" when you're ready.</span>
              : phase === "sending"
                ? <>Listen for the mute click or watch the on-screen indicator.</>
                : <strong>Did your TV react?</strong>}
            footerKind={phase === "sent" ? "success" : ""}
          />
          {phase === "ready" && (
            <button className="btn primary lg" onClick={send}>
              <Icon name="play" size={14}/> Send test signal
            </button>
          )}
          {phase === "sent" && (
            <div className="row" style={{gap:10}}>
              <button className="btn primary lg" onClick={() => { set({tvVerified:true}); go("step3_brand"); }}>
                <Icon name="check" size={14}/> Yes — it reacted
              </button>
              <button className="btn outline" onClick={() => go("step2_fail")}>
                No
              </button>
            </div>
          )}
        </div>
        <div className="tv-mockup">
          <div className="tv-mockup-screen">
            {phase === "sending" ? (
              <>
                <div className="tv-mockup-text bright">🔇 MUTE</div>
                <div className="tv-mockup-text" style={{fontSize:10}}>sent · {state.tvModel || "your TV"}</div>
              </>
            ) : phase === "sent" ? (
              <>
                <div className="tv-mockup-text bright">— check your TV —</div>
                <div className="tv-mockup-text">did you hear it?</div>
              </>
            ) : (
              <>
                <div className="tv-mockup-text">TV idle</div>
                <div className="tv-mockup-text" style={{fontSize:10}}>{state.tvModel || "—"}</div>
              </>
            )}
          </div>
          <div className="stand"/>
        </div>
      </div>
      <FooterNav go={go} back="step2_adb_warn" />
    </div>
  );
}

// ============================================================
// STEP 2 — Test failed (diagnose by cause)
// ============================================================
function Step2Fail({ go, state, set }) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Let's figure out why.</h1>
        <p className="screen-subtitle">An unsupported TV never ends the wizard — even if we can't drive it, you'll land on manual switching.</p>
      </div>
      <div className="stack">
        <DiagnoseTile go={go} icon="plug" title="Pairing wasn't accepted / debugging off"
          desc="Most common. Re-check the on-TV prompt, or enable Developer Options → USB debugging."
          action="Retry the test" target="step2_adb_warn" />
        <DiagnoseTile go={go} icon="network" title="Connected, but the command did nothing"
          desc="ADB connected fine but the TV ignored the keycode. We'll flag this and use a fallback for HDMI input later."
          action="Flag as 'input-finding deferred'" target="step3_brand" tag="advanced"
          onClick={() => set({tvAdbWeak: true, tvVerified: true})} />
        <DiagnoseTile go={go} icon="cross" title="Nothing reached the TV at all"
          desc="Wrong IP, wrong subnet, or guest-WiFi / VLAN split. Try a different backend, or fall back to manual switching."
          action="Drop to manual switching" target="step3_brand"
          onClick={() => set({tvManualSwitch: true, tvVerified: true})} />
      </div>
      <FooterNav go={go} back="step2_test" />
    </div>
  );
}
function DiagnoseTile({ go, icon, title, desc, action, target, tag, onClick }) {
  return (
    <button className="tile" onClick={() => { if (onClick) onClick(); go(target); }}>
      <div className="tile-icon"><Icon name={icon} size={20}/></div>
      <div className="tile-body">
        <div className="tile-title">{title} {tag && <span className="tile-badge advanced">{tag}</span>}</div>
        <div className="tile-desc">{desc}</div>
      </div>
      <span className="chip accent">{action} <Icon name="chevR" size={11}/></span>
    </button>
  );
}

// ============================================================
// Shared footer nav
// ============================================================
function FooterNav({ go, back, next, nextLabel = "Continue", set, setKeys }) {
  return (
    <div className="footer-nav" style={{marginTop:'auto', paddingTop:24}}>
      <div className="row" style={{gap:10}}>
        {back && <button className="btn ghost" onClick={() => go(back)}><Icon name="chevL" size={14}/> Back</button>}
        <span className="spacer" />
        {next && (
          <button className="btn primary" onClick={() => { if (set && setKeys) set(setKeys); go(next); }}>
            {nextLabel} <Icon name="chevR" size={14}/>
          </button>
        )}
      </div>
    </div>
  );
}

Object.assign(window, {
  Step0Gate, Step0Exit,
  Step1Intro, Step1TierA, Step1TierB, Step1TierC,
  Step2Brand, Step2Model, Step2NotFound, Step2Probe, Step2AdbWarn, Step2Test, Step2Fail,
  DiagLog, FooterNav,
});
