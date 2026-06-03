import type { DevPanelProps } from "./types";

/** NAS panel — LAN scan, protocol detect, share test-login, live message panel. Built in PR D-NAS. */
export function NasPanel(_props: DevPanelProps) {
  return (
    <section className="card">
      <h3 style={{ marginTop: 0 }}>NAS panel</h3>
      <p className="field-hint" style={{ marginTop: 0 }}>
        LAN scan, protocol detection, share test-login, and the live message panel land in PR
        D-NAS.
      </p>
    </section>
  );
}
