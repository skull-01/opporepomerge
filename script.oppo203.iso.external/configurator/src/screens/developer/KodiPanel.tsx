import type { DevPanelProps } from "./types";

/** Kodi dev tools — version, settings, restart, register, upload-any-version (PR C) + LAN scan (PR E). */
export function KodiPanel(_props: DevPanelProps) {
  return (
    <section className="card">
      <h3 style={{ marginTop: 0 }}>Kodi developer tools</h3>
      <p className="field-hint" style={{ marginTop: 0 }}>
        Add-on version, settings, restart, register-without-restart, and upload-any-version land
        in PR C; the LAN scan for a Kodi box lands in PR E.
      </p>
    </section>
  );
}
