import { useState } from "react";
import { Transcript, runAndLog, useTranscript } from "./devTranscript";
import { Field, PingRow } from "./devControls";
import type { DevPanelProps } from "./types";

/**
 * CEC ownership-claim test — the HDMI-switching behaviour check. The configurator sends no CEC
 * frames itself; it triggers each device's NATIVE CEC active-source claim and the operator watches
 * the TV. Waking the OPPO makes it assert active source (TV -> player); Kodi's CECActivateSource
 * builtin asserts Kodi's (TV -> Kodi box). Real device I/O via the shared transcript; the actual
 * HDMI switch is observed on the TV (CEC exposes no telemetry to read back).
 */
export function CecPanel({ state }: DevPanelProps) {
  const tx = useTranscript();
  const [oppoIp, setOppoIp] = useState(state.playerIp);
  const [kodiIp, setKodiIp] = useState(state.kodiIp);

  const wakeOppo = (action: string, label: string) =>
    void runAndLog(tx, `OPPO ${label}`, "oppo_power", { host: oppoIp, action });
  const claimKodi = () =>
    void runAndLog(tx, "Kodi CECActivateSource", "kodi_cec_activate", { host: kodiIp, user: state.sshUser });

  return (
    <div className="dev-split">
      <div className="stack-lg">
        <section className="card">
          <h3 style={{ marginTop: 0 }}>CEC ownership claim — HDMI-switching behaviour test</h3>
          <div className="callout info" style={{ marginBottom: 0 }}>
            <span className="callout-icon">i</span>
            <div className="callout-body">
              The configurator sends <strong>no CEC frames</strong>. Each device claims the TV by
              asserting itself as the CEC <em>active source</em>: waking the OPPO should switch the TV
              to the player; Kodi's <span className="mono">CECActivateSource</span> should switch it
              back. Enable CEC on the TV <strong>and</strong> both devices, then claim each and{" "}
              <strong>watch the TV</strong>.
            </div>
          </div>
        </section>

        <section className="card">
          <h3 style={{ marginTop: 0 }}>OPPO (player) → claim the TV</h3>
          <Field id="dev-cec-oppo-ip" label="OPPO IP" value={oppoIp} setValue={setOppoIp} width={220} />
          <PingRow label="OPPO" host={oppoIp} port={23} />
          <div className="row wrap" style={{ gap: 10, marginTop: 12 }}>
            <button className="btn" onClick={() => wakeOppo("eject", "#EJT (wake clone)")}>
              Wake clone (#EJT)
            </button>
            <button className="btn outline" onClick={() => wakeOppo("on", "#PON (power on)")}>
              Power on (#PON)
            </button>
          </div>
          <span className="field-hint">
            On wake the OPPO asserts CEC active source → the TV should switch to the OPPO's input. The
            M9205 clone wakes with #EJT; a genuine OPPO with #PON.
          </span>
        </section>

        <section className="card">
          <h3 style={{ marginTop: 0 }}>Kodi box → claim the TV back</h3>
          <Field id="dev-cec-kodi-ip" label="Kodi box IP" value={kodiIp} setValue={setKodiIp} width={220} />
          <PingRow label="Kodi box" host={kodiIp} port={8080} />
          <div className="row" style={{ marginTop: 12 }}>
            <button className="btn" onClick={() => claimKodi()}>
              Claim TV (Kodi CECActivateSource)
            </button>
          </div>
          <span className="field-hint">
            Runs Kodi's <span className="mono">CECActivateSource</span> builtin over SSH (
            {state.sshUser}@{kodiIp || "the box"}) → the TV should switch back to the Kodi box.
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
