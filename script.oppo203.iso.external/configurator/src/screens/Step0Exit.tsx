import { Icon } from "../icons";
import type { ScreenProps } from "./types";

const OPTS = [
  {
    tag: "Simplest",
    title: "Local USB or hard drive on the player",
    desc: "Plug a drive straight into the player. No network involved — sidesteps the entire SMB1 problem.",
  },
  {
    tag: "Direct",
    title: "Direct SMB1 share",
    desc: "A Windows folder or NAS configured for SMB1 / NTLMv1. Reliable when the network is right; needs the old protocol.",
  },
  {
    tag: "Often better",
    title: "NFS share",
    desc: "NFS is often more reliable on OPPO than SMB1 if your NAS supports it.",
  },
  {
    tag: "Heavy",
    title: "SMB1 proxy",
    desc: "Bridge SMB1 through a dedicated Ubuntu VM, or re-share through Windows. Last resort.",
  },
];

export function Step0Exit({ go }: ScreenProps) {
  return (
    <div className="screen">
      <div className="screen-header">
        <h1 className="screen-title">No problem — let's get your player reading files first.</h1>
        <p className="screen-subtitle">
          Your OPPO or clone needs to reach your media on its own first. The player only
          speaks <span className="kbd">SMB1</span> — pick whichever fits your setup.
        </p>
      </div>
      <div className="choice-grid">
        {OPTS.map((o, i) => (
          <div key={i} className="choice-card">
            <div className="choice-card-title">
              <span>{o.title}</span>
              <span className="choice-card-tag">{o.tag}</span>
            </div>
            <div className="choice-card-desc">{o.desc}</div>
          </div>
        ))}
      </div>
      <div className="callout info" style={{ marginTop: 18 }}>
        <span className="callout-icon">
          <Icon name="info" size={13} stroke={2.2} />
        </span>
        <div className="callout-body">
          Once you can browse to an ISO on the player and play it directly, come back and
          we'll continue from here.
        </div>
      </div>
      <div className="row" style={{ marginTop: 18, gap: 10 }}>
        <button className="btn ghost" onClick={() => go("step0_gate")}>
          <Icon name="chevL" size={14} /> Back
        </button>
      </div>
    </div>
  );
}
