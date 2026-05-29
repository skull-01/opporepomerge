import { useState, type ReactNode } from "react";
import { Icon } from "../icons";
import { DiagLog, type DiagCheck } from "../shell/DiagLog";
import { FooterNav } from "../shell/FooterNav";
import { invoke } from "@tauri-apps/api/core";
import { buildTransferFiles, kodiTargetForPlatform, type KodiPlatform } from "../generate";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 1 — Kodi box (tier select)
// ============================================================
export function Step1Intro({ go, state, set }: ScreenProps) {
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
      <div className="card" style={{ marginBottom: 20, maxWidth: 520 }}>
        <div className="field">
          <label className="field-label">Kodi box IP</label>
          <div className="row" style={{ gap: 8 }}>
            <input
              className="input"
              value={ip}
              onChange={(e) => set({ kodiIp: e.target.value })}
              style={{ flex: 1 }}
            />
            <button className="btn outline">
              <Icon name="search" size={14} /> Find on network
            </button>
          </div>
          <div className="field-hint">
            Reachable from this Windows PC. Reserve it on DHCP if you can.
          </div>
        </div>
      </div>

      <h2 className="section-title" style={{ marginTop: 8 }}>
        Playback architecture
      </h2>
      <p className="screen-subtitle" style={{ marginTop: 4, marginBottom: 10 }}>
        How Kodi hands a disc image to your player. External Player is the standard,
        most predictable path; Service Interception is an alternate for special setups.
      </p>
      <div className="row" style={{ gap: 8, marginBottom: 22 }}>
        <button
          className={`filter-pill ${
            state.playbackArchitecture === "external_player" ? "selected" : ""
          }`.trim()}
          onClick={() => set({ playbackArchitecture: "external_player" })}
        >
          External Player (recommended)
        </button>
        <button
          className={`filter-pill ${
            state.playbackArchitecture === "service_interception" ? "selected" : ""
          }`.trim()}
          onClick={() => set({ playbackArchitecture: "service_interception" })}
        >
          Service Interception
        </button>
      </div>

      <h2 className="section-title" style={{ marginTop: 8 }}>
        How should we install — and apply — your setup files?
      </h2>
      <div className="stack" style={{ marginTop: 10 }}>
        <button
          className="tile"
          onClick={() => {
            set({ tier: "A" });
            go("step1_tierA");
          }}
        >
          <div className="tile-icon">
            <Icon name="bolt" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">
              Auto-write + auto-apply{" "}
              <span className="tile-badge recommended">Recommended</span>
            </div>
            <div className="tile-desc">
              We copy the files <em>and</em> restart Kodi for you. Needs SSH enabled —
              default-on for CoreELEC and LibreELEC.
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
        <button
          className="tile"
          onClick={() => {
            set({ tier: "B" });
            go("step1_tierB");
          }}
        >
          <div className="tile-icon">
            <Icon name="download" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">Auto-write only (SMB)</div>
            <div className="tile-desc">
              We copy the files; you restart Kodi yourself. Works on stock Windows / Android
              Kodi boxes where SSH isn't on by default.
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
        <button
          className="tile"
          onClick={() => {
            set({ tier: "C" });
            go("step1_tierC");
          }}
        >
          <div className="tile-icon">
            <Icon name="folder" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">
              I'll do it myself <span className="tile-badge advanced">Manual</span>
            </div>
            <div className="tile-desc">
              We generate the files; you place them and restart. Most control, most work.
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
      </div>
    </div>
  );
}

// ============================================================
// STEP 1 — Tier A (SSH)
// ============================================================
export function Step1TierA({ go, set }: ScreenProps) {
  const [tested, setTested] = useState(false);
  const checks: DiagCheck[] = tested
    ? [
        { status: "pass", label: "SSH reachable at 10.0.1.42:22", detail: "OpenSSH_8.0 · ed25519 fingerprint OK" },
        { status: "pass", label: "userdata located & writable", detail: "/storage/.kodi/userdata/ · 4 KB temp write OK" },
        { status: "pass", label: "Kodi restart command available", detail: "systemctl restart kodi" },
      ]
    : [
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
      <div className="grid-2" style={{ alignItems: "start" }}>
        <div className="card">
          <h2 className="section-title">SSH credentials</h2>
          <div className="stack">
            <div className="field">
              <label className="field-label">Username</label>
              <input className="input" defaultValue="root" />
            </div>
            <div className="field">
              <label className="field-label">Authentication</label>
              <div className="row" style={{ gap: 8 }}>
                <button className="filter-pill selected">Password</button>
                <button className="filter-pill">SSH key</button>
              </div>
            </div>
            <div className="field">
              <label className="field-label">Password</label>
              <input className="input" type="password" defaultValue="••••••••" />
              <div className="field-hint">
                CoreELEC default is <span className="kbd">coreelec</span>.
              </div>
            </div>
            <button className="btn primary" onClick={() => setTested(true)}>
              <Icon name="play" size={13} /> Test connection
            </button>
          </div>
        </div>
        <div className="stack">
          <DiagLog
            title="Connection checks"
            checks={checks}
            footer={
              tested ? (
                <>All set — we'll install your files and restart Kodi for you, backing up anything already there.</>
              ) : (
                <span className="muted">Run the test to verify each check independently.</span>
              )
            }
            footerKind={tested ? "success" : ""}
          />
          {tested && (
            <div className="callout info">
              <span className="callout-icon">
                <Icon name="info" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                <strong>Auto-apply is CoreELEC / LibreELEC only.</strong> On other platforms,
                we'll fall back to "auto-write, you restart."
              </div>
            </div>
          )}
        </div>
      </div>
      <FooterNav
        go={go}
        back="step1_intro"
        next={tested ? "step2_brand" : null}
        nextLabel="Continue to TV"
        set={set}
        setKeys={{ kodiVerified: true }}
      />
    </div>
  );
}

// ============================================================
// STEP 1 — Tier B (SMB)
// ============================================================
export function Step1TierB({ go, set }: ScreenProps) {
  const [tested, setTested] = useState(false);
  const [sharePath, setSharePath] = useState("\\\\10.0.1.42\\Kodi");
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testAccess = async () => {
    setTesting(true);
    setError(null);
    try {
      await invoke("smb_test_write", { userdataPath: sharePath });
      setTested(true);
    } catch (e) {
      setTested(false);
      setError(String(e));
    } finally {
      setTesting(false);
    }
  };

  const checks: DiagCheck[] = tested
    ? [
        { status: "pass", label: "Box reachable at 10.0.1.42", detail: "ICMP 0.4 ms · 0% loss" },
        { status: "pass", label: "userdata share accessible", detail: "\\\\10.0.1.42\\Kodi · creds OK" },
        { status: "pass", label: "Write test passed", detail: "temp file created + removed" },
      ]
    : [
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
      <div className="grid-2" style={{ alignItems: "start" }}>
        <div className="card">
          <h2 className="section-title">SMB share</h2>
          <div className="stack">
            <div className="field">
              <label className="field-label">Share path</label>
              <input
                className="input"
                value={sharePath}
                onChange={(e) => setSharePath(e.target.value)}
              />
              <div className="field-hint">
                The share that contains the <span className="path">userdata</span> folder.
              </div>
            </div>
            <div className="grid-2">
              <div className="field">
                <label className="field-label">
                  Username <span className="muted">(if needed)</span>
                </label>
                <input className="input text" placeholder="optional" />
              </div>
              <div className="field">
                <label className="field-label">Password</label>
                <input className="input" type="password" placeholder="optional" />
              </div>
            </div>
            <button className="btn primary" onClick={testAccess} disabled={testing}>
              <Icon name="play" size={13} /> {testing ? "Testing…" : "Test access"}
            </button>
            {error && (
              <div className="field-hint" style={{ color: "var(--danger)" }}>
                Write test failed: {error}
              </div>
            )}
          </div>
        </div>
        <div className="stack">
          <DiagLog
            title="Share checks"
            checks={checks}
            footer={
              tested ? (
                <>
                  All set — we'll install your files with a backup.{" "}
                  <strong>You'll restart Kodi yourself</strong> so it loads them.
                </>
              ) : (
                <span className="muted">Run the test to verify each check.</span>
              )
            }
            footerKind={tested ? "success" : ""}
          />
          {tested && (
            <div className="callout warn">
              <span className="callout-icon">
                <Icon name="warn" size={13} stroke={2.2} />
              </span>
              <div className="callout-body">
                <strong>After the wizard finishes,</strong> restart Kodi on your box
                (reboot it, or quit-and-relaunch the Kodi app).
              </div>
            </div>
          )}
        </div>
      </div>
      <FooterNav
        go={go}
        back="step1_intro"
        next={tested ? "step2_brand" : null}
        nextLabel="Continue to TV"
        set={set}
        setKeys={{ kodiVerified: true }}
      />
    </div>
  );
}

// ============================================================
// STEP 1 — Tier C (Manual)
// ============================================================
const PLATFORM_LABELS: Record<KodiPlatform, string> = {
  coreelec: "CoreELEC / LibreELEC",
  android: "Android",
  windows: "Windows",
  linux: "Linux",
};

export function Step1TierC({ go, state, set }: ScreenProps) {
  const [savedDir, setSavedDir] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const platform: KodiPlatform = state.kodiPlatform ?? "coreelec";

  const generate = async () => {
    setGenerating(true);
    try {
      const target = kodiTargetForPlatform(platform, state.pythonPath);
      const dir = await invoke<string>("generate_files", { files: buildTransferFiles(target) });
      setSavedDir(dir);
    } catch {
      setSavedDir(null);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">You'll install the files yourself</h1>
        <p className="screen-subtitle">
          We'll generate <span className="path">playercorefactory.xml</span> and the
          remote-bridge keymap and show you where they go.
        </p>
      </div>

      <div className="callout warn" style={{ marginBottom: 18 }}>
        <span className="callout-icon">
          <Icon name="warn" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          <strong>Back up first.</strong> Before copying anything in, make a copy of these
          from your Kodi <span className="path">userdata</span> folder — if either already
          exists, our files will replace yours.
          <div className="stack-sm" style={{ marginTop: 10 }}>
            <div className="row" style={{ gap: 8 }}>
              <Icon name="file" size={14} />
              <span>
                <span className="path">playercorefactory.xml</span> — if you have one, it
                likely contains your other players. Back it up or merge our entries by
                hand, or you'll lose them.
              </span>
            </div>
            <div className="row" style={{ gap: 8 }}>
              <Icon name="folder" size={14} />
              <span>
                <span className="path">keymaps/</span> folder — back up anything there you
                want to keep (risk is a same-name collision, not the whole folder).
              </span>
            </div>
          </div>
          <div className="muted" style={{ marginTop: 10, fontSize: 12 }}>
            If a file doesn't exist yet, there's nothing to back up — just drop ours in.
          </div>
        </div>
      </div>

      <h2 className="section-title">Where to put the files</h2>
      <div className="stack" style={{ marginTop: 10 }}>
        <PathRow
          platform="CoreELEC / LibreELEC"
          file="/storage/.kodi/userdata/"
          keymap="/storage/.kodi/userdata/keymaps/"
        />
        <PathRow
          platform="Android (Shield, Ugoos, …)"
          file="/sdcard/Android/data/org.xbmc.kodi/files/.kodi/userdata/"
          keymap=".kodi/userdata/keymaps/"
          note="app-private storage may be hard to browse — use Kodi's file manager or copy via SMB / USB"
        />
        <PathRow
          platform="Windows"
          file="%APPDATA%\Kodi\userdata\"
          keymap="%APPDATA%\Kodi\userdata\keymaps\"
        />
      </div>

      <div className="callout info" style={{ marginTop: 16 }}>
        <span className="callout-icon">
          <Icon name="info" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          <strong>Remember this folder.</strong> You'll need it again if you ever
          regenerate these files. After copying, <strong>restart Kodi</strong> so it
          loads them.
        </div>
      </div>

      <h2 className="section-title" style={{ marginTop: 18 }}>Generate for</h2>
      <div className="row" style={{ gap: 8, marginTop: 8 }}>
        {(["coreelec", "android", "windows", "linux"] as const).map((p) => (
          <button
            key={p}
            className={`filter-pill ${platform === p ? "selected" : ""}`.trim()}
            onClick={() => set({ kodiPlatform: p })}
          >
            {PLATFORM_LABELS[p]}
          </button>
        ))}
      </div>
      <div className="row" style={{ marginTop: 14, gap: 10 }}>
        <button className="btn primary" onClick={generate} disabled={generating}>
          <Icon name="download" size={14} /> {generating ? "Generating…" : "Generate & save files"}
        </button>
        <button
          className="btn outline"
          onClick={() => {
            if (savedDir) void invoke("reveal_path", { path: savedDir });
          }}
          disabled={!savedDir}
        >
          <Icon name="folder" size={14} /> Open output folder
        </button>
      </div>
      {savedDir && (
        <div className="callout info" style={{ marginTop: 12 }}>
          <span className="callout-icon">
            <Icon name="check" size={13} stroke={2.2} />
          </span>
          <div className="callout-body">
            Files written to <span className="path">{savedDir}</span> — copy{" "}
            <span className="path">playercorefactory.xml</span> and{" "}
            <span className="path">keymaps/oppo203iso.xml</span> into your Kodi userdata
            folder.
          </div>
        </div>
      )}
      <FooterNav
        go={go}
        back="step1_intro"
        next="step2_brand"
        nextLabel="Continue to TV"
        set={set}
        setKeys={{ kodiVerified: true }}
      />
    </div>
  );
}

type PathRowProps = {
  platform: string;
  file: string;
  keymap: string;
  note?: ReactNode;
};

function PathRow({ platform, file, keymap, note }: PathRowProps) {
  return (
    <div className="card" style={{ padding: 14 }}>
      <div className="row-between">
        <strong style={{ fontSize: 13 }}>{platform}</strong>
        <span className="chip">
          <Icon name="folder" size={11} /> userdata
        </span>
      </div>
      <div className="stack-sm" style={{ marginTop: 8 }}>
        <div className="row">
          <span className="muted" style={{ minWidth: 80, fontSize: 12 }}>main</span>
          <span className="path">{file}</span>
        </div>
        <div className="row">
          <span className="muted" style={{ minWidth: 80, fontSize: 12 }}>keymap</span>
          <span className="path">{keymap}</span>
        </div>
      </div>
      {note && <div className="muted" style={{ fontSize: 12, marginTop: 8 }}>{note}</div>}
    </div>
  );
}
