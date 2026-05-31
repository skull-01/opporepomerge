import { FooterNav } from "../shell/FooterNav";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 3 — Playback mode (placeholder). The legacy vs SVM3 choice is added in a later PR;
// for now this is a minimal pass-through that routes Player -> Playback mode -> TV.
// ============================================================
export function Step3Mode({ go }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Playback mode</h1>
        <p className="screen-subtitle">
          How the add-on confirms OPPO playback — configured next.
        </p>
      </div>
      <div className="card">
        <h3 className="sub-title">Playback mode</h3>
      </div>
      <FooterNav go={go} back="step2_test" next="step4_brand" nextLabel="Continue" />
    </div>
  );
}
