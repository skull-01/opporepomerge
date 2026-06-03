import { useState } from "react";
import type { ScreenProps } from "../types";
import type { DevTab } from "./types";
import { OppoPanel } from "./OppoPanel";
import { KodiPanel } from "./KodiPanel";
import { TvPanel } from "./TvPanel";
import { AvrPanel } from "./AvrPanel";
import { NasPanel } from "./NasPanel";

// Tab order leads with OPPO (the device the whole add-on drives), then the rest of the chain.
const TABS: readonly { id: DevTab; label: string }[] = [
  { id: "oppo", label: "OPPO" },
  { id: "kodi", label: "Kodi" },
  { id: "tv", label: "TV" },
  { id: "avr", label: "AV receiver" },
  { id: "nas", label: "NAS" },
];

/**
 * Developer Options — a dev surface reachable from the app header (like "Reset all…"),
 * independent of the wizard. Five device sub-sections (OPPO / Kodi / TV / AVR / NAS), each a
 * live view + remote control, for hands-on troubleshooting. The tools fire real commands at
 * real hardware, so the surface leads with a caution; the powerful actions inside each panel
 * (zip upload, restart, raw commands, share login) carry their own inline confirms.
 */
export function DeveloperScreen({ go, state, set }: ScreenProps) {
  const [tab, setTab] = useState<DevTab>("oppo");
  const panelProps = { state, set };

  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">Developer Options</h1>
        <p className="screen-subtitle">
          Advanced device consoles — talk directly to the OPPO, Kodi box, TV, AV receiver, and
          NAS for troubleshooting. These fire real commands at real hardware; use with care.
        </p>
      </div>

      <div className="dev-tabs" role="tablist" aria-label="Developer device sections">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={`dev-tab${tab === t.id ? " active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="dev-panel" role="tabpanel">
        {tab === "oppo" && <OppoPanel {...panelProps} />}
        {tab === "kodi" && <KodiPanel {...panelProps} />}
        {tab === "tv" && <TvPanel {...panelProps} />}
        {tab === "avr" && <AvrPanel {...panelProps} />}
        {tab === "nas" && <NasPanel {...panelProps} />}
      </div>

      <div className="footer-nav">
        <button className="btn ghost" onClick={() => go("step0_gate")}>
          ← Back
        </button>
      </div>
    </div>
  );
}
