import { useState } from "react";
import { Transcript, runAndLog, useTranscript } from "./devTranscript";
import type { DevPanelProps } from "./types";

type Backend = "roku" | "adb" | "sony" | "external" | "smartthings";

const BACKENDS: readonly { id: Backend; label: string }[] = [
  { id: "roku", label: "Roku ECP" },
  { id: "adb", label: "ADB" },
  { id: "sony", label: "Sony Bravia" },
  { id: "external", label: "LG / Samsung / custom" },
  { id: "smartthings", label: "SmartThings" },
];

// Illustrative presets — the raw box is the real tool for anything not listed.
const ROKU_KEYS = [
  "Home", "Back", "Up", "Down", "Left", "Right", "Select", "Play", "Rev", "Fwd",
  "InstantReplay", "Info", "VolumeUp", "VolumeDown", "VolumeMute", "PowerOff",
  "InputHDMI1", "InputHDMI2", "InputHDMI3", "InputHDMI4",
];

const ADB_PRESETS: readonly { label: string; cmd: string }[] = [
  { label: "Home", cmd: "input keyevent KEYCODE_HOME" },
  { label: "Up", cmd: "input keyevent KEYCODE_DPAD_UP" },
  { label: "Down", cmd: "input keyevent KEYCODE_DPAD_DOWN" },
  { label: "Left", cmd: "input keyevent KEYCODE_DPAD_LEFT" },
  { label: "Right", cmd: "input keyevent KEYCODE_DPAD_RIGHT" },
  { label: "OK", cmd: "input keyevent KEYCODE_DPAD_CENTER" },
  { label: "Back", cmd: "input keyevent KEYCODE_BACK" },
  { label: "Power", cmd: "input keyevent KEYCODE_POWER" },
];

const SONY_IRCC: readonly { label: string; code: string }[] = [
  { label: "Home", code: "AAAAAQAAAAEAAAAVAw==" },
  { label: "Up", code: "AAAAAQAAAAEAAAB0Aw==" },
  { label: "Down", code: "AAAAAQAAAAEAAAB1Aw==" },
  { label: "Left", code: "AAAAAQAAAAEAAAA0Aw==" },
  { label: "Right", code: "AAAAAQAAAAEAAAAzAw==" },
  { label: "Confirm", code: "AAAAAQAAAAEAAABlAw==" },
  { label: "Return", code: "AAAAAgAAAJcAAAACAw==" },
  { label: "Power off", code: "AAAAAQAAAAEAAAAvAw==" },
  { label: "Input", code: "AAAAAQAAAAEAAAAlAw==" },
  { label: "HDMI 1", code: "AAAAAgAAABoAAABaAw==" },
  { label: "HDMI 2", code: "AAAAAgAAABoAAABbAw==" },
];

const EXTERNAL_PRESETS: readonly { label: string; template: string }[] = [
  { label: "Samsung → HDMI", template: "samsungctl --host {tv_ip} --method websocket KEY_HDMI" },
  { label: "Samsung power", template: "samsungctl --host {tv_ip} --method websocket KEY_POWER" },
];

/**
 * TV command console — every backend available for experimentation regardless of the configured
 * one. Roku/ADB/external accept arbitrary keys/commands directly; Sony Bravia exposes the HDMI-port
 * REST switch plus generic IRCC remote keys; SmartThings builds its cloud request for display (the
 * add-on fires it over HTTPS). TVs expose no telemetry feed, so the transcript is a command/response
 * log + reachability — stated honestly. All control is hardware-pending.
 */
export function TvPanel({ state }: DevPanelProps) {
  const tx = useTranscript();
  const [backend, setBackend] = useState<Backend>("roku");
  const [tvIp, setTvIp] = useState(state.tvIp || "");
  const [psk, setPsk] = useState(state.tvSonyPsk || "");
  const [adbPath, setAdbPath] = useState("adb");
  const [tvPort, setTvPort] = useState("5555");
  const [rawRoku, setRawRoku] = useState("");
  const [rawAdb, setRawAdb] = useState("");
  const [rawIrcc, setRawIrcc] = useState("");
  const [rawTemplate, setRawTemplate] = useState("");
  const [stDevice, setStDevice] = useState(state.tvSmartThingsDeviceId || "");
  const [stInput, setStInput] = useState(state.tvSmartThingsOppoInputId || "");

  const sshUser = state.sshUser;
  const kodiIp = state.kodiIp;

  const fireRoku = (key: string) => void runAndLog(tx, `roku ${key}`, "tv_switch_roku", { host: tvIp, key });
  const fireAdb = (cmd: string) =>
    void runAndLog(tx, `adb ${cmd}`, "tv_switch_adb", {
      sshHost: kodiIp,
      sshUser,
      adbPath,
      tvHost: tvIp,
      tvPort: Number(tvPort) || 5555,
      adbCommand: cmd,
    });
  const fireSonyPort = (port: number) =>
    void runAndLog(tx, `bravia HDMI ${port}`, "tv_switch_sony_bravia", { host: tvIp, psk, port });
  const fireIrcc = (code: string, label?: string) =>
    void runAndLog(tx, `bravia IRCC ${label ?? code}`, "tv_sony_bravia_ircc", { host: tvIp, psk, code });
  const fireExternal = (template: string) =>
    void runAndLog(tx, `external: ${template}`, "tv_switch_external", { sshHost: kodiIp, sshUser, template, tvIp });
  const buildSt = () =>
    void runAndLog(tx, `smartthings setInputSource ${stInput}`, "smartthings_switch_request", {
      deviceId: stDevice,
      inputId: stInput,
    });

  return (
    <div className="dev-split">
      <div className="stack-lg">
      <section className="card">
        <h3 style={{ marginTop: 0 }}>TV console</h3>
        <div className="field" style={{ maxWidth: 280 }}>
          <label className="field-label" htmlFor="dev-tv-ip">TV IP</label>
          <input id="dev-tv-ip" className="input" value={tvIp} spellCheck={false} onChange={(e) => setTvIp(e.target.value)} />
        </div>

        <div className="dev-tabs" role="tablist" aria-label="TV backend" style={{ marginTop: 16 }}>
          {BACKENDS.map((b) => (
            <button
              key={b.id}
              role="tab"
              aria-selected={backend === b.id}
              className={`dev-tab${backend === b.id ? " active" : ""}`}
              onClick={() => setBackend(b.id)}
            >
              {b.label}
            </button>
          ))}
        </div>

        {backend === "roku" && (
          <div className="stack">
            <div className="filter-row">
              {ROKU_KEYS.map((k) => (
                <button key={k} className="filter-pill" onClick={() => fireRoku(k)}>{k}</button>
              ))}
            </div>
            <RawRow id="dev-tv-roku" placeholder="Select" label="Raw ECP key" value={rawRoku} setValue={setRawRoku} onSend={() => fireRoku(rawRoku.trim())} />
          </div>
        )}

        {backend === "adb" && (
          <div className="stack">
            <div className="row wrap">
              <Field id="dev-tv-adbpath" label="adb path" value={adbPath} setValue={setAdbPath} width={140} />
              <Field id="dev-tv-adbport" label="adb port" value={tvPort} setValue={setTvPort} width={100} />
            </div>
            <span className="field-hint">Runs on the Kodi box ({sshUser}@{kodiIp}) over SSH → adb to the TV.</span>
            <div className="filter-row">
              {ADB_PRESETS.map((p) => (
                <button key={p.label} className="filter-pill" title={p.cmd} onClick={() => fireAdb(p.cmd)}>{p.label}</button>
              ))}
            </div>
            <RawRow id="dev-tv-adb" placeholder="input keyevent KEYCODE_HOME" label="Raw adb shell command" value={rawAdb} setValue={setRawAdb} onSend={() => fireAdb(rawAdb.trim())} />
          </div>
        )}

        {backend === "sony" && (
          <div className="stack">
            <Field id="dev-tv-psk" label="Pre-shared key (PSK)" value={psk} setValue={setPsk} width={220} secret />
            <div>
              <div className="field-label" style={{ marginBottom: 6 }}>HDMI port (REST setPlayContent)</div>
              <div className="filter-row">
                {[1, 2, 3, 4].map((n) => (
                  <button key={n} className="filter-pill" onClick={() => fireSonyPort(n)}>HDMI {n}</button>
                ))}
              </div>
            </div>
            <div>
              <div className="field-label" style={{ marginBottom: 6 }}>IRCC remote keys</div>
              <div className="filter-row">
                {SONY_IRCC.map((c) => (
                  <button key={c.label} className="filter-pill" title={c.code} onClick={() => fireIrcc(c.code, c.label)}>{c.label}</button>
                ))}
              </div>
            </div>
            <RawRow id="dev-tv-ircc" placeholder="base64 IRCC code" label="Raw IRCC code" value={rawIrcc} setValue={setRawIrcc} onSend={() => fireIrcc(rawIrcc.trim())} />
          </div>
        )}

        {backend === "external" && (
          <div className="stack">
            <span className="field-hint">Runs the command on the Kodi box ({sshUser}@{kodiIp}) over SSH; <span className="mono">{"{tv_ip}"}</span> is substituted.</span>
            <div className="filter-row">
              {EXTERNAL_PRESETS.map((p) => (
                <button key={p.label} className="filter-pill" title={p.template} onClick={() => fireExternal(p.template)}>{p.label}</button>
              ))}
            </div>
            <RawRow id="dev-tv-ext" placeholder="samsungctl --host {tv_ip} ... / curl ..." label="Raw command template" value={rawTemplate} setValue={setRawTemplate} onSend={() => fireExternal(rawTemplate.trim())} />
          </div>
        )}

        {backend === "smartthings" && (
          <div className="stack">
            <span className="field-hint">Builds the cloud request for display — the add-on fires it over HTTPS (no TLS client here).</span>
            <Field id="dev-tv-stdev" label="Device id" value={stDevice} setValue={setStDevice} width={280} />
            <Field id="dev-tv-stinput" label="Input id" value={stInput} setValue={setStInput} width={220} />
            <div className="row">
              <button className="btn" disabled={!stDevice.trim() || !stInput.trim()} onClick={buildSt}>Build setInputSource request</button>
            </div>
          </div>
        )}
      </section>
      </div>
      <div className="dev-split-aside">
        <Transcript api={tx} title="TV transcript" note="TVs expose no telemetry feed — this is a command/response log plus reachability, not a live device view." />
      </div>
    </div>
  );
}

function Field({
  id, label, value, setValue, width, secret,
}: {
  id: string; label: string; value: string; setValue: (v: string) => void; width?: number; secret?: boolean;
}) {
  return (
    <div className="field" style={{ maxWidth: width }}>
      <label className="field-label" htmlFor={id}>{label}</label>
      <input id={id} className="input" type={secret ? "password" : "text"} value={value} spellCheck={false} onChange={(e) => setValue(e.target.value)} />
    </div>
  );
}

function RawRow({
  id, label, placeholder, value, setValue, onSend,
}: {
  id: string; label: string; placeholder: string; value: string; setValue: (v: string) => void; onSend: () => void;
}) {
  return (
    <div className="field">
      <label className="field-label" htmlFor={id}>{label}</label>
      <div className="row">
        <input
          id={id}
          className="input mono"
          placeholder={placeholder}
          value={value}
          spellCheck={false}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") onSend(); }}
        />
        <button className="btn" disabled={!value.trim()} onClick={onSend}>Send</button>
      </div>
    </div>
  );
}
