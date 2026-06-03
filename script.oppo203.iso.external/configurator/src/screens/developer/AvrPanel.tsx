import { useState } from "react";
import { Transcript, runAndLog, useTranscript } from "./devTranscript";
import { BackendTabs, Field, RawRow } from "./devControls";
import type { DevPanelProps } from "./types";

type Backend = "denon" | "eiscp" | "yamaha" | "sony";

const BACKENDS: readonly { id: Backend; label: string }[] = [
  { id: "denon", label: "Denon / Marantz" },
  { id: "eiscp", label: "Onkyo / Pioneer (eISCP)" },
  { id: "yamaha", label: "Yamaha" },
  { id: "sony", label: "Sony audio" },
];

// Input-select presets per backend — fired via the existing avr_switch_* commands, which select an
// input (Denon SI / eISCP SLI / Yamaha setInput / Sony setPlayContent). The raw box takes the same
// per-backend input token, so anything not listed can still be sent.
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

/**
 * AVR command console — every receiver backend available for experimentation. Each fires through
 * the existing avr_switch_* commands (input select: Denon SI :23, Onkyo/Pioneer eISCP SLI :60128,
 * Yamaha setInput :80, Sony audio setPlayContent REST), with a per-backend input palette + a raw
 * input-token box and the shared command/response transcript. All control is hardware-pending.
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

  return (
    <div className="stack-lg">
      <section className="card">
        <h3 style={{ marginTop: 0 }}>AV receiver console</h3>
        <Field id="dev-avr-ip" label="AVR IP" value={avrIp} setValue={setAvrIp} width={280} />

        <BackendTabs tabs={BACKENDS} active={backend} onPick={setBackend} label="AVR backend" />

        {backend === "denon" && (
          <div className="stack">
            <div className="filter-row">
              {DENON_INPUTS.map((i) => (
                <button key={i} className="filter-pill" onClick={() => fireDenon(i)}>{i}</button>
              ))}
            </div>
            <RawRow id="dev-avr-denon" label="Raw input (after SI)" placeholder="BD" value={rawDenon} setValue={setRawDenon} onSend={() => fireDenon(rawDenon.trim())} />
          </div>
        )}

        {backend === "eiscp" && (
          <div className="stack">
            <div className="filter-row">
              {EISCP_INPUTS.map((i) => (
                <button key={i.code} className="filter-pill" title={`SLI${i.code}`} onClick={() => fireEiscp(i.code)}>{i.label}</button>
              ))}
            </div>
            <RawRow id="dev-avr-eiscp" label="Raw input code (2 hex digits)" placeholder="10" value={rawEiscp} setValue={setRawEiscp} onSend={() => fireEiscp(rawEiscp.trim())} />
          </div>
        )}

        {backend === "yamaha" && (
          <div className="stack">
            <div className="filter-row">
              {YAMAHA_INPUTS.map((i) => (
                <button key={i} className="filter-pill" onClick={() => fireYamaha(i)}>{i}</button>
              ))}
            </div>
            <RawRow id="dev-avr-yamaha" label="Raw input name" placeholder="hdmi1" value={rawYamaha} setValue={setRawYamaha} onSend={() => fireYamaha(rawYamaha.trim())} />
          </div>
        )}

        {backend === "sony" && (
          <div className="stack">
            <Field id="dev-avr-psk" label="Pre-shared key (PSK, optional)" value={psk} setValue={setPsk} width={220} secret />
            <div className="filter-row">
              {SONY_URIS.map((u) => (
                <button key={u.uri} className="filter-pill" title={u.uri} onClick={() => fireSony(u.uri)}>{u.label}</button>
              ))}
            </div>
            <RawRow id="dev-avr-sony" label="Raw input URI" placeholder="extInput:hdmi?port=1" value={rawSony} setValue={setRawSony} onSend={() => fireSony(rawSony.trim())} />
          </div>
        )}
      </section>

      <Transcript api={tx} title="AVR transcript" note="Receivers reply per command (or echo) — this is a command/response log, not a continuous telemetry feed." />
    </div>
  );
}
