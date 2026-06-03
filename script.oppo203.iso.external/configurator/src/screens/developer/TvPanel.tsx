import type { DevPanelProps } from "./types";

/** TV command console — per-backend palettes (Roku/ADB/Sony/Samsung/LG/SmartThings/custom). Built in PR D-TV. */
export function TvPanel(_props: DevPanelProps) {
  return (
    <section className="card">
      <h3 style={{ marginTop: 0 }}>TV console</h3>
      <p className="field-hint" style={{ marginTop: 0 }}>
        Per-backend command palettes and the command/response transcript land in PR D-TV.
      </p>
    </section>
  );
}
