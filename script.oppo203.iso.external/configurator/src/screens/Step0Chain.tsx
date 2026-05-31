import { Icon } from "../icons";
import type { Topology } from "../state";
import type { ScreenProps } from "./types";

// ============================================================
// STEP 0 — Playback chain. The user picks their physical topology up front so the rest of the
// wizard can adapt its copy and the settings it writes. Soft default: each chain keeps later
// escape hatches (the optional receiver step in the TV chain, the manual/TV fallback in the
// AVR chain), so a wrong pick here is never a dead end.
// ============================================================
export function Step0Chain({ go, state, set }: ScreenProps) {
  const pick = (topology: Topology) => {
    set({ topology });
    go("step1_intro");
  };
  return (
    <div className="screen">
      <div className="screen-header">
        <div className="screen-num">0</div>
        <h1 className="screen-title">How is your home theater wired?</h1>
        <p className="screen-subtitle">
          Pick the chain that matches your gear. It changes which steps we show and how the
          add-on hands off on playback — you can still adjust the details later.
        </p>
      </div>
      <div className="grid-2">
        <button
          className={`tile ${state.topology === "kodi_tv_player" ? "selected" : ""}`.trim()}
          onClick={() => pick("kodi_tv_player")}
        >
          <div className="tile-icon">
            <Icon name="tv" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">Kodi · TV · OPPO</div>
            <div className="tile-desc">
              Your player plugs straight into the TV. On handoff we switch the TV to the
              player&apos;s HDMI input, and back to Kodi on exit. No AV receiver in the path.
            </div>
          </div>
          <Icon name="chevR" size={16} />
        </button>
        <button
          className={`tile ${state.topology === "kodi_avr_tv_player" ? "selected" : ""}`.trim()}
          onClick={() => pick("kodi_avr_tv_player")}
        >
          <div className="tile-icon">
            <Icon name="avr" size={20} />
          </div>
          <div className="tile-body">
            <div className="tile-title">Kodi · AVR · TV · OPPO</div>
            <div className="tile-desc">
              Your player plugs into an AV receiver. The receiver switches its input between
              the player and Kodi on handoff; the TV stays on one fixed input. We&apos;ll set
              up the receiver in step 5.
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
          Not sure? Pick <strong>Kodi · TV · OPPO</strong> — it&apos;s the common case, and
          you can still add a receiver later.
        </div>
      </div>
    </div>
  );
}
