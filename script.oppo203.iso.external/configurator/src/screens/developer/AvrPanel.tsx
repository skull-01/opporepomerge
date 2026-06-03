import type { DevPanelProps } from "./types";

/** AVR command console — per-backend palettes (Denon/Marantz, eISCP, Yamaha, Sony audio). Built in PR D-AVR. */
export function AvrPanel(_props: DevPanelProps) {
  return (
    <section className="card">
      <h3 style={{ marginTop: 0 }}>AV receiver console</h3>
      <p className="field-hint" style={{ marginTop: 0 }}>
        Per-backend command palettes and the command/response transcript land in PR D-AVR.
      </p>
    </section>
  );
}
