import { useState } from "react";
import { Transcript, runAndLog, useTranscript } from "./devTranscript";
import { BackendTabs, Field, PingRow, RawRow } from "./devControls";
import type { DevPanelProps } from "./types";

type Backend = "denon" | "eiscp" | "yamaha" | "sony";

const BACKENDS: readonly { id: Backend; label: string }[] = [
  { id: "denon", label: "Denon / Marantz" },
  { id: "eiscp", label: "Onkyo / Pioneer (eISCP)" },
  { id: "yamaha", label: "Yamaha" },
  { id: "sony", label: "Sony audio" },
];

// Input-select presets per backend — fired via the existing avr_switch_* commands, which select an
// input (Denon SI / eISCP SLI / Yamaha setInput / Sony setPlayContent). The "other input" box takes
// the same per-backend input token, so anything not listed can still be selected.
const DENON_INPUTS = ["BD", "DVD", "GAME", "MPLAY", "CD", "TV", "SAT/CBL", "AUX1", "TUNER", "NET", "PHONO"];
const EISCP_INPUTS: readonly { label: string; code: string }[] = [
  { label: "BD/DVD (10)", code: "10" },
  { label: "CBL/SAT (01)", code: "01" },
  { label: "GAME (02)", code: "02" },
  { label: "CD (23)", code: "23" },
  { label: "TUNER (24)", code: "24" },
  { label: "STRM-BOX (11)", code: "11" },
  { label: "NET (2B)", code: "2B" },
  { label: "USB (29)", code: "29" },
];
const YAMAHA_INPUTS = ["hdmi1", "hdmi2", "hdmi3", "hdmi4", "av1", "av2", "audio1", "optical1", "bd_dvd", "tuner", "net_radio"];
const SONY_URIS: readonly { label: string; uri: string }[] = [
  { label: "HDMI 1", uri: "extInput:hdmi?port=1" },
  { label: "HDMI 2", uri: "extInput:hdmi?port=2" },
  { label: "HDMI 3", uri: "extInput:hdmi?port=3" },
  { label: "HDMI 4", uri: "extInput:hdmi?port=4" },
];

// Raw-command presets per backend — arbitrary protocol commands (power / volume / mute / query),
// distinct from input-select. Fired through avr_raw_send: Denon line-ASCII over telnet (:23),
// Onkyo/Pioneer eISCP payload framed over :60128, Yamaha MusicCast API path over HTTP (:80).
type RawPreset = { label: string; cmd: string };
const DENON_RAW: readonly RawPreset[] = [
  { label: "Power On", cmd: "PWON" },
  { label: "Standby", cmd: "PWSTANDBY" },
  { label: "Vol +", cmd: "MVUP" },
  { label: "Vol −", cmd: "MVDOWN" },
  { label: "Mute On", cmd: "MUON" },
  { label: "Mute Off", cmd: "MUOFF" },
  { label: "Power?", cmd: "PW?" },
];
const EISCP_RAW: readonly RawPreset[] = [
  { label: "Power On", cmd: "!1PWR01" },
  { label: "Power Off", cmd: "!1PWR00" },
  { label: "Vol +", cmd: "!1MVLUP" },
  { label: "Vol −", cmd: "!1MVLDOWN" },
  { label: "Mute On", cmd: "!1AMT01" },
  { label: "Mute Off", cmd: "!1AMT00" },
  { label: "Power?", cmd: "!1PWRQSTN" },
];
const YAMAHA_RAW: readonly RawPreset[] = [
  { label: "Power On", cmd: "/YamahaExtendedControl/v1/main/setPower?power=on" },
  { label: "Standby", cmd: "/YamahaExtendedControl/v1/main/setPower?power=standby" },
  { label: "Vol +", cmd: "/YamahaExtendedControl/v1/main/setVolume?volume=up" },
  { label: "Vol −", cmd: "/YamahaExtendedControl/v1/main/setVolume?volume=down" },
  { label: "Mute On", cmd: "/YamahaExtendedControl/v1/main/setMute?enable=true" },
  { label: "Mute Off", cmd: "/YamahaExtendedControl/v1/main/setMute?enable=false" },
  { label: "Status", cmd: "/YamahaExtendedControl/v1/main/getStatus" },
];

const RAW_PLACEHOLDER: Record<Backend, string> = {
  denon: "PWON",
  eiscp: "!1PWR01",
  yamaha: "/YamahaExtendedControl/v1/main/getStatus",
  sony: "",
};
const RAW_HINT: Record<Backend, string> = {
  denon: "Line-ASCII command over telnet (:23); a CR is appended. e.g. MV505, SITV, PW?",
  eiscp: "eISCP payload (must start with !); framed with the ISCP header over :60128.",
  yamaha: "MusicCast/YXC API path over HTTP (:80); must be an absolute /… path.",
  sony: "",
};

/**
 * AVR command console — every receiver backend available for experimentation. Two modes per
 * backend: an input-select palette (Denon SI :23, Onkyo/Pioneer eISCP SLI :60128, Yamaha setInput
 * :80, Sony audio setPlayContent REST) and a raw-command console (avr_raw_send) for arbitrary
 * power/volume/mute/query commands. Sony's REST API has no line protocol, so its raw surface stays
 * the setPlayContent URI box. All control is hardware-pending; the shared command/response
 * transcript logs each exchange.
 */
export function AvrPanel({ state }: DevPanelProps) {
  const tx = useTranscript();
  const [backend, setBackend] = useState<Backend>("denon");
  const [avrIp, setAvrIp] = useState(state.avrIp || "");
  const [psk, setPsk] = useState(state.avrSonyPsk || "");
  const [rawDenon, setRawDenon] = useState("");
  const [rawEiscp, setRawEiscp] = useState("");
  const [rawYamaha, setRawYamaha] = useState("");
  const [rawSony, setRawSony] = useState("");
  const [cmdDenon, setCmdDenon] = useState("");
  const [cmdEiscp, setCmdEiscp] = useState("");
  const [cmdYamaha, setCmdYamaha] = useState("");

  const fireDenon = (input: string) =>
    void runAndLog(tx, `denon SI${input}`, "avr_switch_denon", { host: avrIp, input });
  const fireEiscp = (code: string) =>
    void runAndLog(tx, `eiscp SLI${code}`, "avr_switch_eiscp", { host: avrIp, inputCode: code });
  const fireYamaha = (input: string) =>
    void runAndLog(tx, `yamaha setInput ${input}`, "avr_switch_yamaha", { host: avrIp, input });
  const fireSony = (uri: string) =>
    void runAndLog(tx, `sony setPlayContent ${uri}`, "avr_switch_sony_audio", {
      host: avrIp,
      inputUri: uri,
      psk: psk.trim() || undefined,
    });
  const fireRaw = (b: Backend, command: string) => {
    if (!command) return;
    void runAndLog(tx, `${b} raw » ${command}`, "avr_raw_send", { backend: b, host: avrIp, command });
  };

  return (
    <div className="dev-split">
      <div className="stack-lg">
      <section className="card">
        <h3 style={{ marginTop: 0 }}>AV receiver console</h3>
        <Field id="dev-avr-ip" label="AVR IP" value={avrIp} setValue={setAvrIp} width={280} />
        <PingRow
          label="AVR"
          host={avrIp}
          port={backend === "denon" ? 23 : backend === "eiscp" ? 60128 : 80}
        />

        <BackendTabs tabs={BACKENDS} active={backend} onPick={setBackend} label="AVR backend" />

        {backend === "denon" && (
          <div className="stack">
            <h4 className="dev-subhead">Input select (SI)</h4>
            <div className="filter-row">
              {DENON_INPUTS.map((i) => (
                <button key={i} className="filter-pill" onClick={() => fireDenon(i)}>{i}</button>
              ))}
            </div>
            <RawRow id="dev-avr-denon" label="Other input (after SI)" placeholder="BD" value={rawDenon} setValue={setRawDenon} onSend={() => fireDenon(rawDenon.trim())} />
            <h4 className="dev-subhead">Raw command</h4>
            <div className="filter-row">
              {DENON_RAW.map((r) => (
                <button key={r.cmd} className="filter-pill" title={r.cmd} onClick={() => fireRaw("denon", r.cmd)}>{r.label}</button>
              ))}
            </div>
            <RawRow id="dev-avr-denon-raw" label="Raw command" placeholder={RAW_PLACEHOLDER.denon} value={cmdDenon} setValue={setCmdDenon} onSend={() => fireRaw("denon", cmdDenon.trim())} />
            <p className="dev-hint">{RAW_HINT.denon}</p>
          </div>
        )}

        {backend === "eiscp" && (
          <div className="stack">
            <h4 className="dev-subhead">Input select (SLI)</h4>
            <div className="filter-row">
              {EISCP_INPUTS.map((i) => (
                <button key={i.code} className="filter-pill" title={`SLI${i.code}`} onClick={() => fireEiscp(i.code)}>{i.label}</button>
              ))}
            </div>
            <RawRow id="dev-avr-eiscp" label="Other input code (2 hex digits)" placeholder="10" value={rawEiscp} setValue={setRawEiscp} onSend={() => fireEiscp(rawEiscp.trim())} />
            <h4 className="dev-subhead">Raw command</h4>
            <div className="filter-row">
              {EISCP_RAW.map((r) => (
                <button key={r.cmd} className="filter-pill" title={r.cmd} onClick={() => fireRaw("eiscp", r.cmd)}>{r.label}</button>
              ))}
            </div>
            <RawRow id="dev-avr-eiscp-raw" label="Raw eISCP payload" placeholder={RAW_PLACEHOLDER.eiscp} value={cmdEiscp} setValue={setCmdEiscp} onSend={() => fireRaw("eiscp", cmdEiscp.trim())} />
            <p className="dev-hint">{RAW_HINT.eiscp}</p>
          </div>
        )}

        {backend === "yamaha" && (
          <div className="stack">
            <h4 className="dev-subhead">Input select</h4>
            <div className="filter-row">
              {YAMAHA_INPUTS.map((i) => (
                <button key={i} className="filter-pill" onClick={() => fireYamaha(i)}>{i}</button>
              ))}
            </div>
            <RawRow id="dev-avr-yamaha" label="Other input name" placeholder="hdmi1" value={rawYamaha} setValue={setRawYamaha} onSend={() => fireYamaha(rawYamaha.trim())} />
            <h4 className="dev-subhead">Raw command</h4>
            <div className="filter-row">
              {YAMAHA_RAW.map((r) => (
                <button key={r.cmd} className="filter-pill" title={r.cmd} onClick={() => fireRaw("yamaha", r.cmd)}>{r.label}</button>
              ))}
            </div>
            <RawRow id="dev-avr-yamaha-raw" label="Raw MusicCast path" placeholder={RAW_PLACEHOLDER.yamaha} value={cmdYamaha} setValue={setCmdYamaha} onSend={() => fireRaw("yamaha", cmdYamaha.trim())} />
            <p className="dev-hint">{RAW_HINT.yamaha}</p>
          </div>
        )}

        {backend === "sony" && (
          <div className="stack">
            <Field id="dev-avr-psk" label="Pre-shared key (PSK, optional)" value={psk} setValue={setPsk} width={220} secret />
            <h4 className="dev-subhead">setPlayContent</h4>
            <div className="filter-row">
              {SONY_URIS.map((u) => (
                <button key={u.uri} className="filter-pill" title={u.uri} onClick={() => fireSony(u.uri)}>{u.label}</button>
              ))}
            </div>
            <RawRow id="dev-avr-sony" label="Raw input URI" placeholder="extInput:hdmi?port=1" value={rawSony} setValue={setRawSony} onSend={() => fireSony(rawSony.trim())} />
            <p className="dev-hint">Sony's Audio Control API is JSON-RPC (no line protocol), so this setPlayContent URI box is its raw surface.</p>
          </div>
        )}
      </section>
      </div>
      <div className="dev-split-aside">
        <Transcript api={tx} title="AVR transcript" note="Receivers reply per command (or echo) — this is a command/response log, not a continuous telemetry feed." />
      </div>
    </div>
  );
}
