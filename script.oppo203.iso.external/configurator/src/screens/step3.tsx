import { Icon } from "../icons";
import { FooterNav } from "../shell/FooterNav";
import type { MonitorMode } from "../state";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 3 — Playback mode. The MONITOR axis of the four-option architecture: how the add-on
// confirms OPPO playback, independent of the routing axis (playercorefactory vs service
// interception) chosen on the Kodi-box step. The pick is written as `playback_monitor_mode`
// and folded into the combined `playback_architecture_preset` by mapping.ts. SVM3 is the
// recommended path for new installs / validation but is NOT yet hardware-validated, so it is
// labelled accordingly — never as proven. The player test (Step 2) reports whether the player
// actually accepts SVM3.
// ============================================================
export function Step3Mode({ go, state, set }: ScreenProps) {
  const pick = (monitorMode: MonitorMode) => set({ monitorMode });
  return (
    <div className="screen">
      <div className="screen-header">
        <div className="screen-num">3</div>
        <h1 className="screen-title">How should playback be confirmed?</h1>
        <p className="screen-subtitle">
          Sending a play command isn&apos;t proof the disc is playing. SVM3 listens to the
          player&apos;s own status so the add-on knows playback really started — and when it
          stops. This is separate from how Kodi hands off (chosen on the Kodi-box step).
        </p>
      </div>
      <div className="grid-2">
        <button
          className={`tile ${state.monitorMode === "svm3" ? "selected" : ""}`.trim()}
          onClick={() => pick("svm3")}
        >
          <div className="tile-icon">
            <Icon name="play" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">SVM3 monitor — recommended for new installs</div>
            <div className="tile-desc">
              Uses OPPO&apos;s verbose mode 3: the add-on watches the player&apos;s UPL/UTC
              status and time-code updates, and only treats playback as confirmed when the
              player reports it. Best feedback; the player test checks your player accepts it.
            </div>
            {state.svm3Supported === true && (
              <div className="model-row-meta" style={{ marginTop: 6 }}>
                ✓ accepted by your player in the control test
              </div>
            )}
            {state.svm3Supported === false && (
              <div className="model-row-meta" style={{ marginTop: 6 }}>
                not detected on your player — Legacy recommended
              </div>
            )}
          </div>
          <Icon name="chevR" size={16} />
        </button>
        <button
          className={`tile ${state.monitorMode === "legacy" ? "selected" : ""}`.trim()}
          onClick={() => pick("legacy")}
        >
          <div className="tile-icon">
            <Icon name="refresh" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">Legacy monitor — maximum compatibility</div>
            <div className="tile-desc">
              The existing hold behaviour (timed / stop-file / status polling). Use this if your
              player or clone doesn&apos;t accept SVM3, or to keep exactly today&apos;s behaviour.
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
      </div>
      <div className="callout info" style={{ marginTop: 18 }}>
        <span className="callout-icon">
          <Icon name="info" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          SVM3 is <strong>recommended for validation / new installs</strong> but not yet
          hardware-validated. Not sure? <strong>Legacy</strong> keeps today&apos;s behaviour and
          you can switch later.
        </div>
      </div>
      <FooterNav go={go} back="step2_test" next="step4_brand" nextLabel="Continue" />
    </div>
  );
}
