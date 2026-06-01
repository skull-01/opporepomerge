import { useEffect, useRef, useState, type ReactNode } from "react";
import { listen } from "@tauri-apps/api/event";
import { Icon, type IconName } from "../icons";
import { invoke } from "../ipc";
import { Chain } from "../shell/Chain";
import { FooterNav } from "../shell/FooterNav";
import { applyToKodi, installAddonToKodi, type ApplyResult } from "../apply";
import { isAvrChain, type ScreenId } from "../steps";
import {
  foldSvm3Frame,
  INITIAL_SVM3_CONFIRM,
  type LiveFrame,
  type Svm3Confirm,
} from "../svm3_confirm";
import type { ScreenProps } from "./types";

// One copy-progress frame emitted by the Rust `copy_to_share` command (see lib.rs `CopyProgress`).
type CopyProgress = { bytes_copied: number; total: number; percent: number };

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  const units = ["KB", "MB", "GB", "TB"];
  let v = n / 1024;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v.toFixed(1)} ${units[i]}`;
}

// ============================================================
// TEST — Setup (copy disc OR play your own)
// ============================================================
type TestMode = "disc" | "own" | null;
type CopyPhase = "idle" | "copying" | "done" | "error";

export function TestSetup({ go, state, set }: ScreenProps) {
  const [mode, setMode] = useState<TestMode>(state.testMode);
  const [copied, setCopied] = useState(false);

  // Test-ISO copy (Phase 4.2; D-2 = the operator supplies the source disc/ISO).
  const [sourcePath, setSourcePath] = useState("");
  const [destPath, setDestPath] = useState("\\\\nas\\Movies\\_test\\test-uhd-2160p.iso");
  const [copyPhase, setCopyPhase] = useState<CopyPhase>("idle");
  const [progress, setProgress] = useState<CopyProgress | null>(null);
  const [copyErr, setCopyErr] = useState<string | null>(null);
  // Track copy-in-flight in a ref so the progress listener (subscribed once) only updates the bar
  // while our own copy is running.
  const copyingRef = useRef(false);

  useEffect(() => {
    let alive = true;
    let unlisten: (() => void) | undefined;
    void listen<CopyProgress>("copy-progress", (e) => {
      if (copyingRef.current) setProgress(e.payload);
    }).then((u) => {
      if (alive) unlisten = u;
      else u();
    });
    return () => {
      alive = false;
      if (unlisten) unlisten();
    };
  }, []);

  const startCopy = async () => {
    setCopyErr(null);
    setProgress(null);
    setCopyPhase("copying");
    copyingRef.current = true;
    try {
      await invoke<{ dest: string; bytes_copied: number }>("copy_to_share", {
        sourcePath,
        destPath,
      });
      setCopyPhase("done");
      setCopied(true);
    } catch (e) {
      setCopyErr(String(e));
      setCopyPhase("error");
    } finally {
      copyingRef.current = false;
    }
  };

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
          to test — copy a UHD ISO you supply onto the shared library, or play one you
          already have there.
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
                Copy a test ISO to the share{" "}
                <span className="tile-badge recommended">Recommended</span>
              </div>
              <div className="tile-desc">
                Point us at a UHD ISO <strong>you supply</strong> (named to trigger Kodi's
                eligibility rules) and we'll copy it onto the library both Kodi and your
                player can see.
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
                  <label className="field-label">Test ISO on this PC</label>
                  <input
                    className="input"
                    value={sourcePath}
                    placeholder="C:\Users\you\Downloads\test-uhd-2160p.iso"
                    onChange={(e) => setSourcePath(e.target.value)}
                    disabled={copyPhase === "copying"}
                  />
                  <div className="field-hint">
                    The UHD-tagged disc image <strong>you supply</strong> — name it with{" "}
                    <code>2160p</code> or <code>UHD</code> so Kodi's eligibility rule trips.
                  </div>
                </div>
                <div className="field">
                  <label className="field-label">Destination on the shared library</label>
                  <input
                    className="input"
                    value={destPath}
                    placeholder="\\nas\Movies\_test\test-uhd-2160p.iso"
                    onChange={(e) => setDestPath(e.target.value)}
                    disabled={copyPhase === "copying"}
                  />
                </div>
                <div className="callout warn">
                  <span className="callout-icon">
                    <Icon name="warn" size={13} stroke={2.2} />
                  </span>
                  <div className="callout-body">
                    Must be on the media library{" "}
                    <strong>both Kodi and your player use</strong> — not just a folder on
                    this PC. If your library is a NAS or shared folder, point here to that
                    share (a local path or a <code>\\server\share</code> UNC path).
                  </div>
                </div>

                {copyPhase !== "idle" && (
                  <CopyProgressBar phase={copyPhase} progress={progress} error={copyErr} />
                )}

                <div className="row" style={{ gap: 8 }}>
                  <button
                    className="btn primary"
                    onClick={startCopy}
                    disabled={copyPhase === "copying" || !sourcePath.trim() || !destPath.trim()}
                  >
                    <Icon name="download" size={13} />{" "}
                    {copyPhase === "copying"
                      ? "Copying…"
                      : copyPhase === "done"
                        ? "Copy again"
                        : "Copy to the share"}
                  </button>
                </div>
                {copyPhase === "done" && (
                  <div className="callout info">
                    <span className="callout-icon">
                      <Icon name="info" size={13} stroke={2.2} />
                    </span>
                    <div className="callout-body">
                      Copied. Now <strong>rescan your Kodi library</strong> so it appears, then
                      play it from Kodi.
                    </div>
                  </div>
                )}
                <div
                  className="muted"
                  style={{ fontSize: 11, fontFamily: "var(--font-mono)" }}
                >
                  placeholder wiring · you supply the disc · software-verified, not
                  hardware-validated
                </div>
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
                    <strong>Nothing tagged UHD in your library?</strong> Switch to the copy
                    option instead — point us at a UHD ISO you supply and we'll copy it onto
                    the share.
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
                  we only watch the player's status feed · no control commands sent
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {mode !== null && (
        <Svm3ConfirmCard playerIp={state.playerIp} svm3={state.monitorMode === "svm3"} />
      )}

      <FooterNav
        go={go}
        back="step6_ask"
        next={nextScreen}
        nextLabel={nextLabel}
      />
    </div>
  );
}

function CopyProgressBar({
  phase,
  progress,
  error,
}: {
  phase: CopyPhase;
  progress: CopyProgress | null;
  error: string | null;
}) {
  const pct = phase === "done" ? 100 : (progress?.percent ?? 0);
  const barColor = phase === "error" ? "var(--danger)" : "var(--accent)";
  return (
    <div className="stack-sm">
      <div
        style={{
          height: 8,
          borderRadius: 5,
          background: "var(--surface-2)",
          overflow: "hidden",
        }}
      >
        <div
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
          style={{
            width: `${pct}%`,
            height: "100%",
            background: barColor,
            transition: "width 120ms linear",
          }}
        />
      </div>
      <div
        className="muted"
        style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}
      >
        {phase === "error" ? (
          <span style={{ color: "var(--danger)" }}>Copy failed: {error}</span>
        ) : phase === "done" ? (
          "100% — copy complete"
        ) : progress ? (
          `${pct}% · ${formatBytes(progress.bytes_copied)}${
            progress.total > 0 ? ` of ${formatBytes(progress.total)}` : ""
          }`
        ) : (
          "starting…"
        )}
      </div>
    </div>
  );
}

// Colors for the live verbose-mode frame tail, matching the dashboard's stream view.
const FRAME_COLORS: Record<string, string> = {
  upl: "#2563EB",
  utc: "#6B7280",
  status: "#0D9488",
  error: "#DC2626",
  info: "#9CA3AF",
};

// Live SVM3 confirmation: opens the configurator's own verbose-mode-3 connection to the player and
// confirms playback from real `@UPL PLAY` / advancing `@UTC` frames, instead of a manual yes/no.
// Read-only and opt-in; stops on unmount so it restores the player's prior verbose mode. Reuses the
// same start/stop_oppo_live_monitor commands + oppo-live event the dashboard streams.
function Svm3ConfirmCard({ playerIp, svm3 }: { playerIp: string; svm3: boolean }) {
  const [streaming, setStreaming] = useState(false);
  const [frames, setFrames] = useState<LiveFrame[]>([]);
  const [verdict, setVerdict] = useState<Svm3Confirm>(INITIAL_SVM3_CONFIRM);
  const [err, setErr] = useState<string | null>(null);
  const verdictRef = useRef<Svm3Confirm>(INITIAL_SVM3_CONFIRM);

  useEffect(() => {
    let alive = true;
    let unlisten: (() => void) | undefined;
    void listen<LiveFrame>("oppo-live", (e) => {
      setFrames((f) => [...f.slice(-29), e.payload]);
      const next = foldSvm3Frame(verdictRef.current, e.payload);
      verdictRef.current = next;
      setVerdict(next);
    }).then((u) => {
      if (alive) unlisten = u;
      else u();
    });
    return () => {
      alive = false;
      if (unlisten) unlisten();
      // Always release the player's verbose mode when leaving the screen.
      void invoke("stop_oppo_live_monitor").catch(() => {});
    };
  }, []);

  const start = async () => {
    setErr(null);
    setFrames([]);
    verdictRef.current = INITIAL_SVM3_CONFIRM;
    setVerdict(INITIAL_SVM3_CONFIRM);
    try {
      await invoke("start_oppo_live_monitor", { host: playerIp, port: 23 });
      setStreaming(true);
    } catch (e) {
      setErr(`Could not start: ${String(e)}`);
      setStreaming(false);
    }
  };

  const stop = async () => {
    try {
      await invoke("stop_oppo_live_monitor");
    } catch {
      // best-effort
    }
    setStreaming(false);
  };

  return (
    <div className="card" style={{ marginTop: 14 }}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <h3 className="sub-title" style={{ margin: 0 }}>
          Live playback confirmation (SVM3)
        </h3>
        {streaming ? (
          <button className="btn outline sm" onClick={stop}>
            <Icon name="cross" size={13} /> Stop watching
          </button>
        ) : (
          <button className="btn outline sm" onClick={start}>
            <Icon name="play" size={13} /> Watch the player
          </button>
        )}
      </div>
      <p className="muted" style={{ fontSize: 12.5, marginTop: 6 }}>
        We open a read-only verbose-mode-3 connection to <code>{playerIp}</code> and confirm
        playback from what the player reports — <code>@UPL PLAY</code> plus an advancing{" "}
        <code>@UTC</code> time code — not a guess.
      </p>

      {!svm3 && (
        <div className="callout warn" style={{ marginTop: 4 }}>
          <span className="callout-icon">
            <Icon name="warn" size={13} stroke={2.2} />
          </span>
          <div className="callout-body">
            Your playback mode is <strong>Legacy</strong>, not SVM3. You can still watch the live
            feed here, but the add-on won't use it to confirm playback at runtime.
          </div>
        </div>
      )}

      <div className="row" style={{ gap: 18, marginTop: 10 }}>
        <ConfirmBadge on={verdict.confirmedPlayback} label="playback confirmed" />
        <ConfirmBadge on={verdict.confirmedProgress} label="progress advancing" />
        <span className="muted" style={{ fontSize: 11.5, fontFamily: "var(--font-mono)" }}>
          {verdict.playbackState ? `state ${verdict.playbackState}` : "state —"}
          {verdict.utcTicks > 0 ? ` · ${verdict.utcTicks} ticks` : ""}
        </span>
      </div>

      {err && (
        <div className="muted" style={{ fontSize: 12, marginTop: 8, color: "var(--danger)" }}>
          {err}
        </div>
      )}

      <div
        style={{
          maxHeight: 132,
          overflowY: "auto",
          marginTop: 10,
          fontFamily: "var(--font-mono)",
          fontSize: 11.5,
          lineHeight: 1.6,
        }}
      >
        {frames.length === 0 ? (
          <span className="muted">
            {streaming ? "waiting for the player to push frames…" : "not watching"}
          </span>
        ) : (
          frames.map((f) => (
            <div key={f.seq} style={{ color: FRAME_COLORS[f.kind] }}>
              {f.raw}
            </div>
          ))
        )}
      </div>

      <div
        className="muted"
        style={{ fontSize: 11, marginTop: 10, fontFamily: "var(--font-mono)" }}
      >
        read-only · restores the player's prior verbose mode on stop · software-verified, not
        hardware-validated
      </div>
    </div>
  );
}

function ConfirmBadge({ on, label }: { on: boolean; label: string }) {
  return (
    <span className="row" style={{ gap: 5, alignItems: "center" }}>
      <Icon name={on ? "check" : "cross"} size={13} style={{ color: on ? "#16A34A" : "#9CA3AF" }} />
      <span className="muted" style={{ fontSize: 12 }}>
        {label}
      </span>
    </span>
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

export function TestConfirm({ go, state }: ScreenProps) {
  const [answers, setAnswers] = useState<Answers>({ play: null, switch: null, menu: null });
  // Report the six-option pieces this test exercises, separately — the routing axis, how
  // playback is confirmed (the Step 3 monitor choice), and the TV/AVR switcher.
  const routingLabel =
    state.playbackArchitecture === "service_interception"
      ? "Service interception"
      : state.playbackArchitecture === "http_handoff"
        ? "HTTP handoff (community NAS)"
        : "Playercorefactory";
  const svm3 = state.monitorMode === "svm3";
  const tvAvrLabel = isAvrChain(state.topology)
    ? `AV receiver${state.avrBackend ? ` · ${state.avrBackend}` : ""}`
    : state.tvBackend
      ? `TV · ${state.tvBackend}`
      : "none";
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
          ? "step4_test"
          : "step1_intro";
  const nextLabel = !allAnswered
    ? undefined
    : allYes
      ? "See the summary"
      : answers.play === false
        ? "Fix routing → Step 3"
        : answers.switch === false
          ? "Fix TV → Step 5"
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

      <div className="card" style={{ marginBottom: 14 }}>
        <h3 className="sub-title">What this test covers</h3>
        <div className="model-row-meta" style={{ marginTop: 4 }}>
          Kodi route · <strong>{routingLabel}</strong>
        </div>
        <div className="model-row-meta" style={{ marginTop: 4 }}>
          Playback confirmation ·{" "}
          <strong>
            {svm3
              ? "SVM3 — the player reports playback (UPL/UTC)"
              : "Legacy — timed / polled hold"}
          </strong>
        </div>
        <div className="model-row-meta" style={{ marginTop: 4 }}>
          TV / AVR · <strong>{tvAvrLabel}</strong>
        </div>
      </div>

      {svm3 && (
        <div className="callout info" style={{ marginBottom: 14 }}>
          <span className="callout-icon">
            <Icon name="info" size={13} stroke={2.2} />
          </span>
          <div className="callout-body">
            With SVM3 the add-on treats playback as confirmed only once the player itself
            reports it — it writes <code>oppo203iso-status.json</code> recording confirmed
            playback and progress. A disc that plays but isn&apos;t reported as confirmed means
            the player isn&apos;t sending status, not that playback failed.
          </div>
        </div>
      )}

      <div className="stack">
        <Question
          n="1"
          label="Did the test disc start playing on your player?"
          owner="Step 3 · Player / playercorefactory routing"
          value={answers.play}
          onChange={(v) => setAnswers({ ...answers, play: v })}
        />
        <Question
          n="2"
          label="Did your TV switch to the player's input?"
          owner="Step 5 · TV / Step 6 input capture"
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
    const install = await installAddonToKodi(state);
    if (!install.ok) {
      setResult(install);
      setApplying(false);
      return;
    }
    const applied = await applyToKodi(state);
    setResult({ ok: applied.ok, detail: `${install.detail} ${applied.detail}` });
    setApplying(false);
  };

  const applyLabel =
    state.tier === "A"
      ? "Install add-on + apply (SSH + restart)"
      : state.tier === "B"
        ? "Install add-on + apply (SMB)"
        : "Bundle add-on + generate files";

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
          <button className="btn outline" onClick={() => go("dashboard")}>
            <Icon name="network" size={14} /> Live dashboard
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
