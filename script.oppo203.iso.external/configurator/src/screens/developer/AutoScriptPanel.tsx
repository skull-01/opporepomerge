import { useState } from "react";
import { invoke } from "../../ipc";
import { generateAutoexec, type AutoScriptMountType, type AutoScriptOptions } from "../../autoscript/autoscript-gen";
import { autoscriptReadme } from "../../autoscript/readme";
import {
  AUTOSCRIPT_VERBOSE_PUSH_WARNING,
  autoscriptFamily,
  oppo20xAutoscriptFirmwareStatus,
  parseQvrFirmware,
  type FirmwareStatus,
} from "../../autoscript/capability";
import { Transcript, useTranscript } from "./devTranscript";
import { Field } from "./devControls";
import type { DevPanelProps } from "./types";

const FAMILY_LABEL: Record<string, string> = {
  oppo20x_jailbroken: "JB stock OPPO — needs jailbreak + firmware 20X-56+",
  chinoppo_family: "Clone — runs AutoScript without a jailbreak",
  unknown: "Unknown player — set the model in Step 3",
};

function Check({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="row" style={{ gap: 8, cursor: "pointer" }}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="field-label" style={{ margin: 0 }}>{label}</span>
    </label>
  );
}

/**
 * AutoScript helper: build the player's autoexec.sh from a form, preview it live, check the player's
 * readiness (firmware capability + family + telnet/ADB/HTTP reachability), and export a Desktop
 * folder (autoexec.sh + HOW-TO-INSTALL.txt) to copy to a USB drive. The generator is the byte-exact
 * mirror of the add-on (autoscript-gen.ts). The CIFS password is shown in the preview (the user is
 * building the script) but is never persisted. Device readiness is hardware-pending.
 */
export function AutoScriptPanel({ state }: DevPanelProps) {
  const tx = useTranscript();
  const [host, setHost] = useState(state.playerIp);
  const [enableTelnet, setEnableTelnet] = useState(true);
  const [telnetPort, setTelnetPort] = useState("2323");
  const [passwordlessRoot, setPasswordlessRoot] = useState(true);
  const [mountType, setMountType] = useState<AutoScriptMountType>("none");
  const [mountRemote, setMountRemote] = useState("");
  const [mountLocal, setMountLocal] = useState("/tmp/share");
  const [mountOptions, setMountOptions] = useState("");
  const [cifsUser, setCifsUser] = useState("");
  const [cifsPass, setCifsPass] = useState("");
  const [heartbeatPath, setHeartbeatPath] = useState("/tmp/usb/sda1/oppo_autoexec_ran");
  const [enableAdb, setEnableAdb] = useState(false);
  const [adbPort, setAdbPort] = useState("5555");

  const [checking, setChecking] = useState(false);
  const [fwStatus, setFwStatus] = useState<FirmwareStatus | null>(null);
  const [openPorts, setOpenPorts] = useState<number[] | null>(null);
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const opts: AutoScriptOptions = {
    enableTelnet,
    telnetPort: Number(telnetPort) || 2323,
    passwordlessRoot,
    mountType,
    mountRemote,
    mountLocal,
    mountOptions,
    cifsUser,
    cifsPass,
    heartbeatPath,
    enableAdb,
    adbPort: Number(adbPort) || 5555,
  };
  const script = generateAutoexec(opts);
  const family = autoscriptFamily(state.playerModel);
  const port23 = telnetPort.trim() === "23";

  async function checkReadiness() {
    setChecking(true);
    setFwStatus(null);
    setOpenPorts(null);
    tx.push({ dir: "info", text: `Checking AutoScript readiness on ${host}…` });
    try {
      const qvr = await invoke<string>("oppo_query", { host, command: "#QVR" });
      tx.push({ dir: "rx", text: `#QVR ${qvr || "(no reply)"}` });
      setFwStatus(oppo20xAutoscriptFirmwareStatus(parseQvrFirmware(qvr)));
    } catch (e) {
      tx.push({ dir: "err", text: `#QVR ${String(e)}` });
    }
    try {
      const ports = [Number(telnetPort) || 2323, Number(adbPort) || 5555, 436];
      const res = await invoke<{ port: number; open: boolean }[]>("tv_port_probe", { host, ports });
      const open = res.filter((r) => r.open).map((r) => r.port);
      setOpenPorts(open);
      tx.push({ dir: "rx", text: `ports open: ${open.join(", ") || "none"}` });
    } catch (e) {
      tx.push({ dir: "err", text: `port probe ${String(e)}` });
    }
    setChecking(false);
  }

  async function exportBundle() {
    setExportMsg(null);
    try {
      const path = await invoke<string>("export_autoscript_bundle", { script, readme: autoscriptReadme(opts) });
      setExportMsg(`Saved to ${path} — open HOW-TO-INSTALL.txt, then copy autoexec.sh to a FAT32 USB drive's root.`);
    } catch (e) {
      setExportMsg(`Export failed: ${String(e)}`);
    }
  }

  async function copyScript() {
    try {
      await navigator.clipboard.writeText(script);
      setCopied(true);
    } catch (e) {
      setExportMsg(`Copy failed: ${String(e)}`);
    }
  }

  return (
    <div className="stack-lg">
      <section className="card">
        <h3 style={{ marginTop: 0 }}>AutoScript builder</h3>
        <div className="row wrap" style={{ gap: 12, alignItems: "flex-end" }}>
          <Field id="dev-as-host" label="Player IP" value={host} setValue={setHost} width={160} />
          <span className="chip" title="From the configured player model">{FAMILY_LABEL[family]}</span>
        </div>

        <div className="stack" style={{ marginTop: 14 }}>
          <Check label="Start telnet root shell" checked={enableTelnet} onChange={setEnableTelnet} />
          {enableTelnet && <Field id="dev-as-tport" label="Telnet port" value={telnetPort} setValue={setTelnetPort} width={110} />}
          <Check label="Passwordless root" checked={passwordlessRoot} onChange={setPasswordlessRoot} />

          <div className="field" style={{ maxWidth: 160 }}>
            <label className="field-label" htmlFor="dev-as-mount">NAS mount</label>
            <select id="dev-as-mount" className="input" value={mountType} onChange={(e) => setMountType(e.target.value as AutoScriptMountType)}>
              <option value="none">None</option>
              <option value="nfs">NFS</option>
              <option value="cifs">CIFS / SMB</option>
            </select>
          </div>
          {mountType !== "none" && (
            <div className="row wrap" style={{ gap: 12, alignItems: "flex-end" }}>
              <Field id="dev-as-mr" label="Remote share" value={mountRemote} setValue={setMountRemote} width={220}
                placeholder={mountType === "nfs" ? "10.0.1.10:/mnt/media" : "//10.0.1.10/Media"} />
              <Field id="dev-as-ml" label="Mount point" value={mountLocal} setValue={setMountLocal} width={140} />
              <Field id="dev-as-mo" label="Options (optional)" value={mountOptions} setValue={setMountOptions} width={180} />
            </div>
          )}
          {mountType === "cifs" && (
            <div className="row wrap" style={{ gap: 12, alignItems: "flex-end" }}>
              <Field id="dev-as-cu" label="CIFS user" value={cifsUser} setValue={setCifsUser} width={140} />
              <Field id="dev-as-cp" label="CIFS password" value={cifsPass} setValue={setCifsPass} width={160} secret />
            </div>
          )}

          <Check label="Enable ADB over TCP" checked={enableAdb} onChange={setEnableAdb} />
          {enableAdb && <Field id="dev-as-aport" label="ADB port" value={adbPort} setValue={setAdbPort} width={110} />}
          <Field id="dev-as-hb" label="Heartbeat marker path" value={heartbeatPath} setValue={setHeartbeatPath} width={300} />
        </div>

        <div className={`callout ${port23 ? "danger" : "warn"}`} style={{ marginTop: 14 }}>
          <span className="callout-icon">!</span>
          <div className="callout-body">
            {port23
              ? "Port 23 is the OPPO IP-control port — a telnet shell there breaks the add-on's #SVM verbose-push. Use 2323."
              : AUTOSCRIPT_VERBOSE_PUSH_WARNING}
          </div>
        </div>
      </section>

      <section className="card">
        <div className="row-between" style={{ marginBottom: 10 }}>
          <h3 style={{ margin: 0 }}>Generated autoexec.sh</h3>
          <div className="row" style={{ gap: 8 }}>
            <button className="btn outline" onClick={() => void copyScript()}>{copied ? "Copied ✓" : "Copy"}</button>
            <button className="btn" onClick={() => void exportBundle()}>Export to Desktop</button>
          </div>
        </div>
        <div className="dev-transcript" role="document" style={{ maxHeight: 320 }}>
          {script.split("\n").map((line, i) => (
            <div key={i} className="dev-tline dev-rx">{line || " "}</div>
          ))}
        </div>
        {exportMsg && <p className="field-hint" style={{ marginBottom: 0 }} role="status">{exportMsg}</p>}
      </section>

      <section className="card">
        <div className="row-between" style={{ marginBottom: 10 }}>
          <h3 style={{ margin: 0 }}>Readiness check</h3>
          <button className="btn ghost sm" disabled={checking} onClick={() => void checkReadiness()}>
            {checking ? "Checking…" : "Check availability"}
          </button>
        </div>
        <div className="row wrap" style={{ gap: 18 }}>
          <div>
            <div className="field-label">Firmware (AutoScript-capable?)</div>
            <div>{fwStatus ? <FirmwareChip s={fwStatus} /> : <span className="mono">—</span>}</div>
          </div>
          <div>
            <div className="field-label">Ports open (telnet / ADB / HTTP)</div>
            <div className="mono">{openPorts ? (openPorts.join(", ") || "none") : "—"}</div>
          </div>
        </div>
        <span className="field-hint">Reads firmware via #QVR and probes the telnet / ADB / :436 ports — all hardware-pending.</span>
        <div style={{ marginTop: 12 }}>
          <Transcript api={tx} title="AutoScript log" />
        </div>
      </section>
    </div>
  );
}

function FirmwareChip({ s }: { s: FirmwareStatus }) {
  if (s.autoscriptSupported === true) {
    const recommend = s.warnings.includes("oppo20x_autoscript_supported_but_20x_65_0131_recommended");
    return <span className={`chip ${recommend ? "warn" : "success"}`}>{recommend ? `capable — ${s.recommended} recommended` : "capable"}</span>;
  }
  if (s.autoscriptSupported === false) {
    return <span className="chip danger">too old — need {s.minimum}+</span>;
  }
  return <span className="chip warn">firmware unknown</span>;
}
