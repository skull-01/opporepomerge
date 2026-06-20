import { useEffect, useState } from "react";
import { Transcript, runAndLog, useTranscript } from "./devTranscript";
import { Field, PingRow } from "./devControls";
import { invoke } from "../../ipc";
import type { DevPanelProps } from "./types";

type SshKeyInfo = { public_key: string; path: string; exists: boolean };

/**
 * CEC ownership-claim test — the HDMI-switching behaviour check. The configurator sends no CEC
 * frames itself; it triggers each device's NATIVE CEC active-source claim and the operator watches
 * the TV. The OPPO asserts active source when it powers on (One Touch Play), so from standby a wake
 * switches the TV to it — but when it's ALREADY ON a wake is a no-op, hence the power-cycle / play
 * "force claim" options. Kodi's CECActivateSource (over key-only SSH) claims the TV back; the SSH
 * helper sets up that key auth first. The actual HDMI switch is observed on the TV (CEC has no
 * telemetry to read back).
 */
export function CecPanel({ state }: DevPanelProps) {
  const tx = useTranscript();
  const [oppoIp, setOppoIp] = useState(state.playerIp);
  const [kodiIp, setKodiIp] = useState(state.kodiIp);
  const [busy, setBusy] = useState(false);
  const [testPath, setTestPath] = useState("");

  const [sshKey, setSshKey] = useState<SshKeyInfo | null>(null);
  const [sshOk, setSshOk] = useState<boolean | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    void loadKey(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const wakeOppo = (action: string, label: string) =>
    void runAndLog(tx, `OPPO ${label}`, "oppo_power", { host: oppoIp, action });

  const playOppo = () =>
    void runAndLog(tx, "OPPO #PLA (play → assert active source)", "oppo_query", {
      host: oppoIp,
      command: "#PLA",
      port: 23,
    });

  const playTestFile = () => {
    if (!testPath.trim()) {
      tx.push({ dir: "err", text: "Enter an OPPO-visible file path first." });
      return;
    }
    void runAndLog(tx, `play test file (/playnormalfile) ${testPath.trim()}`, "oppo_http_play", {
      host: oppoIp,
      oppoPath: testPath.trim(),
    });
  };

  async function powerCycleOppo() {
    setBusy(true);
    tx.push({ dir: "tx", text: "OPPO power cycle: #POF → wait 4s → #PON" });
    try {
      await invoke("oppo_power", { host: oppoIp, action: "off" });
      tx.push({ dir: "info", text: "#POF sent — waiting 4s for standby…" });
      await new Promise<void>((resolve) => setTimeout(resolve, 4000));
      const r = await invoke<string>("oppo_power", { host: oppoIp, action: "on" });
      tx.push({ dir: "rx", text: `#PON: ${r || "(sent)"} — the power-on should re-assert CEC active source` });
    } catch (e) {
      tx.push({ dir: "err", text: String(e) });
    } finally {
      setBusy(false);
    }
  }

  const claimKodi = () =>
    void runAndLog(tx, "Kodi CECActivateSource", "kodi_cec_activate", { host: kodiIp, user: state.sshUser });

  async function loadKey(generate: boolean) {
    try {
      const k = await invoke<SshKeyInfo>("ssh_public_key", { generate });
      setSshKey(k);
      if (generate && k.exists) tx.push({ dir: "info", text: `generated ${k.path}` });
    } catch (e) {
      tx.push({ dir: "err", text: `ssh key: ${String(e)}` });
    }
  }

  async function testSsh() {
    setSshOk(null);
    try {
      await invoke("ssh_test", { host: kodiIp, user: state.sshUser });
      setSshOk(true);
      tx.push({ dir: "rx", text: `SSH key auth OK to ${state.sshUser}@${kodiIp}` });
    } catch (e) {
      setSshOk(false);
      tx.push({ dir: "err", text: `SSH: ${String(e)}` });
    }
  }

  const installCmd = sshKey?.exists
    ? `type "${sshKey.path}" | ssh ${state.sshUser}@${kodiIp || "<box-ip>"} "mkdir -p /storage/.ssh; cat >> /storage/.ssh/authorized_keys; chmod 600 /storage/.ssh/authorized_keys"`
    : "";

  async function copyInstall() {
    try {
      await navigator.clipboard.writeText(installCmd);
      setCopied(true);
    } catch (e) {
      tx.push({ dir: "err", text: `copy: ${String(e)}` });
    }
  }

  return (
    <div className="dev-split">
      <div className="stack-lg">
        <section className="card">
          <h3 style={{ marginTop: 0 }}>CEC ownership claim — HDMI-switching behaviour test</h3>
          <div className="callout info" style={{ marginBottom: 0 }}>
            <span className="callout-icon">i</span>
            <div className="callout-body">
              The configurator sends <strong>no CEC frames</strong>. Each device claims the TV by
              asserting itself as the CEC <em>active source</em>. Enable CEC on the TV{" "}
              <strong>and</strong> both devices, claim each, and <strong>watch the TV</strong>.
            </div>
          </div>
        </section>

        <section className="card">
          <h3 style={{ marginTop: 0 }}>OPPO (player) → claim the TV</h3>
          <Field id="dev-cec-oppo-ip" label="OPPO IP" value={oppoIp} setValue={setOppoIp} width={220} />
          <PingRow label="OPPO" host={oppoIp} port={23} />

          <h4 className="dev-subhead" style={{ marginTop: 14 }}>From standby</h4>
          <div className="row wrap" style={{ gap: 10 }}>
            <button className="btn" disabled={busy} onClick={() => wakeOppo("eject", "#EJT (wake clone)")}>
              Wake clone (#EJT)
            </button>
            <button className="btn outline" disabled={busy} onClick={() => wakeOppo("on", "#PON (power on)")}>
              Power on (#PON)
            </button>
          </div>

          <h4 className="dev-subhead" style={{ marginTop: 14 }}>Already on — force it to claim the TV</h4>
          <div className="row wrap" style={{ gap: 10 }}>
            <button className="btn" disabled={busy} onClick={() => void powerCycleOppo()}>
              {busy ? "Cycling…" : "Power cycle (#POF → #PON)"}
            </button>
            <button className="btn outline" disabled={busy} onClick={() => playOppo()}>
              Play (#PLA)
            </button>
          </div>
          <span className="field-hint">
            One Touch Play fires on power-<em>up</em>, so an already-on OPPO won't re-claim the TV from a
            plain wake. The power cycle re-fires it; Play asserts active source via playback. If neither
            switches the TV, the M9205 clone doesn't assert CEC active source.
          </span>

          <h4 className="dev-subhead" style={{ marginTop: 14 }}>Play a real file (test CEC-on-play)</h4>
          <div className="row" style={{ gap: 6 }}>
            <input
              className="input mono"
              placeholder="smb://10.0.1.10/Media/test.mkv — an OPPO-visible path"
              value={testPath}
              spellCheck={false}
              onChange={(e) => setTestPath(e.target.value)}
              style={{ flex: 1 }}
            />
            <button className="btn" onClick={() => playTestFile()}>Play test file</button>
          </div>
          <span className="field-hint">
            Fires the OPPO's <span className="mono">/playnormalfile</span> over the HTTP API — the same call
            the add-on's handoff makes (activate → signin → play). There is <strong>no direct CEC command</strong>;
            playing real content is the trigger, so if the OPPO asserts CEC on play, the TV switches to it.
          </span>
        </section>

        <section className="card">
          <h3 style={{ marginTop: 0 }}>Kodi box → claim the TV back</h3>
          <Field id="dev-cec-kodi-ip" label="Kodi box IP" value={kodiIp} setValue={setKodiIp} width={220} />
          <PingRow label="Kodi box" host={kodiIp} port={8080} />

          <div className="callout warn" style={{ marginTop: 12 }}>
            <span className="callout-icon">!</span>
            <div className="callout-body">
              <strong>Authorize SSH first.</strong> The Kodi claim runs over <strong>key-only</strong> SSH
              (no password) — get key auth working before it'll succeed.
            </div>
          </div>
          <div className="row wrap" style={{ gap: 10, marginTop: 10 }}>
            <button className="btn" onClick={() => void testSsh()}>Test SSH</button>
            {sshKey && !sshKey.exists && (
              <button className="btn outline" onClick={() => void loadKey(true)}>Generate a key</button>
            )}
            {sshOk === true && <span className="success-text" role="status">✓ key auth OK</span>}
            {sshOk === false && <span className="danger-text" role="status">✗ not authorized — set up below</span>}
          </div>

          {sshKey?.exists && (
            <div className="stack-sm" style={{ marginTop: 10 }}>
              <div className="field-label">Your public key ({sshKey.path})</div>
              <div className="dev-transcript" style={{ maxHeight: 70 }}>
                <div className="dev-tline mono" style={{ wordBreak: "break-all" }}>{sshKey.public_key}</div>
              </div>
              <div className="field-label" style={{ marginTop: 6 }}>
                Run once in a terminal (enter the box password — CoreELEC default <span className="mono">coreelec</span>), then Test SSH:
              </div>
              <div className="row" style={{ gap: 6 }}>
                <input className="input mono" readOnly value={installCmd} spellCheck={false} style={{ flex: 1 }} />
                <button className="btn outline" onClick={() => void copyInstall()}>{copied ? "Copied ✓" : "Copy"}</button>
              </div>
            </div>
          )}

          <div className="row" style={{ marginTop: 14 }}>
            <button className="btn" onClick={() => claimKodi()}>
              Claim TV (Kodi CECActivateSource)
            </button>
          </div>
          <span className="field-hint">
            Runs Kodi's <span className="mono">CECActivateSource</span> builtin over SSH ({state.sshUser}@
            {kodiIp || "the box"}) → the TV should switch back to the Kodi box.
          </span>
        </section>
      </div>
      <div className="dev-split-aside">
        <Transcript
          api={tx}
          title="CEC test transcript"
          note="CEC has no telemetry — this logs what was sent + the device reply. The HDMI switch itself is what you watch on the TV."
        />
      </div>
    </div>
  );
}
