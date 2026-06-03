import type { WizardState } from "../../state";

/** The device sub-sections of the Developer Options console, in tab order. */
export type DevTab = "oppo" | "kodi" | "tv" | "avr" | "nas" | "autoscript";

/**
 * Props each device panel receives. Panels read the configured device IPs / backends from the
 * wizard state and may write transient dev-only fields back via `set`; they never advance the
 * wizard (no `go`), since Developer Options is a side surface, not a numbered step.
 */
export type DevPanelProps = {
  state: WizardState;
  set: (patch: Partial<WizardState>) => void;
};
