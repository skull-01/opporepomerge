import { useState } from "react";
import { invoke } from "../../ipc";
import { Transcript, useTranscript } from "./devTranscript";
import { Field } from "./devControls";
import type { DevPanelProps } from "./types";

type NasHost = { ip: string; protocols: string[] };

/**
 * NAS panel — sweep the LAN for NAS hosts (identifying the protocol by which service port answers),
 * and test-login to a share for troubleshooting. Credentials are passed to the backend for the
 * login attempt but are NEVER persisted, and the transcript logs only that a password was supplied,
 * never its value. All network I/O is hardware-pending.
 */
export function NasPanel(_props: DevPanelProps) {
  const tx = useTranscript();
  const [baseIp, setBaseIp] = useState("");
  const [scanning, setScanning] = useState(false);
  const [hosts, setHosts] = useState<NasHost[]>([]);

  const [nasHost, setNasHost] = useState("");
  const [share, setShare] = useState("");
  const [protocol, setProtocol] = useState<"smb" | "nfs">("smb");
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [testing, setTesting] = useState(false);

  async function scan() {
    setScanning(true);
    tx.push({
      dir: "info",
      text: `Scanning local subnet${baseIp.trim() ? ` (${baseIp.trim()}/24)` : ""} for NAS hosts…`,
    });
    try {
      const found = await invoke<NasHost[]>("scan_nas_hosts", { baseIp: baseIp.trim() || undefined });
      setHosts(found);
      tx.push({
        dir: "rx",
        text: found.length
          ? `Found ${found.length}: ${found.map((h) => `${h.ip} [${h.protocols.join("/")}]`).join(", ")}`
          : "No NAS hosts answered on the scanned ports.",
      });
    } catch (e) {
      tx.push({ dir: "err", text: `Scan failed: ${String(e)}` });
    } finally {
      setScanning(false);
    }
  }

  async function testLogin() {
    const h = nasHost.trim();
    if (!h || !share.trim()) {
      tx.push({ dir: "err", text: "Host and share are required." });
      return;
    }
    setTesting(true);
    // The transcript never carries the password value — only that one was supplied.
    tx.push({
      dir: "tx",
      text: `${protocol} login ${h}/${share.trim()}${user.trim() ? ` as ${user.trim()}` : ""}${password ? " (password supplied — redacted)" : ""}`,
    });
    try {
      const r = await invoke<string>("nas_test_login", {
        host: h,
        share: share.trim(),
        user: user.trim() || undefined,
        password: password || undefined,
        protocol,
      });
      tx.push({ dir: "rx", text: r });
    } catch (e) {
      tx.push({ dir: "err", text: String(e) });
    } finally {
      setTesting(false);
    }
  }

  return (
    <div className="stack-lg">
      <section className="card">
        <h3 style={{ marginTop: 0 }}>Scan the LAN for NAS hosts</h3>
        <div className="row wrap" style={{ alignItems: "flex-end", gap: 12 }}>
          <Field
            id="dev-nas-base"
            label="Base IP (optional — defaults to this host's subnet)"
            value={baseIp}
            setValue={setBaseIp}
            width={300}
            placeholder="10.0.1.0"
          />
          <button className="btn" disabled={scanning} onClick={() => void scan()}>
            {scanning ? "Scanning…" : "Scan network"}
          </button>
        </div>
        <span className="field-hint">Probes 445/139 (SMB), 2049 (NFS), 548 (AFP), 21 (FTP) across the /24.</span>
        {hosts.length > 0 && (
          <div className="model-list" style={{ marginTop: 12 }}>
            {hosts.map((h) => (
              <button
                key={h.ip}
                className="model-row"
                onClick={() => setNasHost(h.ip)}
                style={{ background: "none", border: "none", font: "inherit", textAlign: "left", cursor: "pointer", width: "100%" }}
              >
                <span className="mono">{h.ip}</span>
                <span className="model-row-meta">{h.protocols.join(" · ")}</span>
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="card">
        <h3 style={{ marginTop: 0 }}>Test a share login</h3>
        <div className="callout warn" style={{ marginBottom: 12 }}>
          <span className="callout-icon">!</span>
          <div className="callout-body">
            Credentials are used only for this attempt — <strong>never saved</strong>, and the log shows only
            that a password was supplied, not its value.
          </div>
        </div>
        <div className="row wrap" style={{ gap: 12, alignItems: "flex-end" }}>
          <Field id="dev-nas-host" label="Host" value={nasHost} setValue={setNasHost} width={160} />
          <Field id="dev-nas-share" label="Share" value={share} setValue={setShare} width={160} placeholder="Media" />
          <div className="field" style={{ maxWidth: 110 }}>
            <label className="field-label" htmlFor="dev-nas-proto">Protocol</label>
            <select id="dev-nas-proto" className="input" value={protocol} onChange={(e) => setProtocol(e.target.value as "smb" | "nfs")}>
              <option value="smb">SMB</option>
              <option value="nfs">NFS</option>
            </select>
          </div>
        </div>
        {protocol === "smb" && (
          <div className="row wrap" style={{ gap: 12, alignItems: "flex-end", marginTop: 4 }}>
            <Field id="dev-nas-user" label="User (optional)" value={user} setValue={setUser} width={160} />
            <Field id="dev-nas-pass" label="Password (optional)" value={password} setValue={setPassword} width={160} secret />
          </div>
        )}
        <div className="row" style={{ marginTop: 12 }}>
          <button className="btn" disabled={testing || !nasHost.trim() || !share.trim()} onClick={() => void testLogin()}>
            {testing ? "Testing…" : "Test login"}
          </button>
        </div>
      </section>

      <Transcript api={tx} title="NAS messages" note="Scan results, login attempts, and errors. Passwords are never shown or saved." />
    </div>
  );
}
