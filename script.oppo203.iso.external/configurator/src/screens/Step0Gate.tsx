import { Icon } from "../icons";
import type { ScreenProps } from "./types";

export function Step0Gate({ go }: ScreenProps) {
  return (
    <div className="screen">
      <div className="intro-hero" style={{ maxWidth: 760 }}>
        <div className="intro-eyebrow">Before we start</div>
        <h1 className="intro-title">Your player needs to reach your media on its own first.</h1>
        <p className="intro-body">
          This wizard sets up the <em>handoff</em> — when you launch a 4K UHD or Blu-ray
          disc image in Kodi, it tells your OPPO or clone player to take over, and
          switches your TV to match. It doesn't set up <em>how</em> your player reaches
          your files. That part needs to be working already.
        </p>
        <div className="grid-2" style={{ width: "100%", marginBottom: 28, alignItems: "stretch" }}>
          <div className="intro-checklist" style={{ marginBottom: 0 }}>
            <h3 className="sub-title" style={{ marginBottom: 10 }}>
              Before continuing, confirm
            </h3>
            <div className="intro-check">You can already browse to an ISO directly on your OPPO/clone.</div>
            <div className="intro-check">It plays from the same media library Kodi uses.</div>
            <div className="intro-check">No new wiring or shares are required to make that happen.</div>
          </div>
          <div className="intro-checklist" style={{ marginBottom: 0 }}>
            <h3 className="sub-title" style={{ marginBottom: 12 }}>
              Ideal preparations before proceeding
            </h3>
            <div className="prep-row">
              <span className="prep-num">1</span>
              <div><strong>Kodi Box</strong> — enable SSH and set a static IP.</div>
            </div>
            <div className="prep-row">
              <span className="prep-num">2</span>
              <div><strong>OPPO / Clone Player</strong> — enable network control and set a static IP.</div>
            </div>
            <div className="prep-row">
              <span className="prep-num">3</span>
              <div><strong>TV</strong> — know the exact model, set a static IP, and identify which HDMI inputs the Kodi box and the OPPO / clone player use.</div>
            </div>
          </div>
        </div>
        <div className="row" style={{ gap: 10 }}>
          <button className="btn primary lg" onClick={() => go("step0_chain")}>
            I can already play ISOs on my player
            <Icon name="chevR" size={14} />
          </button>
          <button className="btn ghost" onClick={() => go("step0_exit")}>
            Not yet
          </button>
        </div>
      </div>
    </div>
  );
}
