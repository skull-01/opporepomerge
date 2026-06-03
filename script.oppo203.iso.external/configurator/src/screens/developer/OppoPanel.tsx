import type { DevPanelProps } from "./types";

/** OPPO command console — TCP (#XXX) + HTTP (436) palettes and a live transcript. Built in PR B-OPPO. */
export function OppoPanel(_props: DevPanelProps) {
  return (
    <section className="card">
      <h3 style={{ marginTop: 0 }}>OPPO console</h3>
      <p className="field-hint" style={{ marginTop: 0 }}>
        TCP and HTTP command palettes plus the live transcript land in PR B-OPPO.
      </p>
    </section>
  );
}
