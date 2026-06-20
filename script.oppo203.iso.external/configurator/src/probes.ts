import type { TvBackend } from "./state";

export type PortResult = { port: number; open: boolean };

/** Ports probed per TV backend, in priority order (first open wins). */
export const TV_PROBE_PORTS: { port: number; backend: TvBackend; label: string }[] = [
  { port: 8060, backend: "roku_ecp", label: "Roku ECP" },
  { port: 5555, backend: "adb", label: "ADB" },
  { port: 20060, backend: "sony_bravia", label: "Sony IP control" },
];

export function probePortList(): number[] {
  return TV_PROBE_PORTS.map((p) => p.port);
}

/** Infer the most likely backend from the open ports (probe order = priority). */
export function inferBackendFromPorts(results: PortResult[]): TvBackend | null {
  for (const entry of TV_PROBE_PORTS) {
    if (results.some((r) => r.port === entry.port && r.open)) return entry.backend;
  }
  return null;
}

/**
 * Parse an OPPO #QPW reply ("@QPW OK ON") into on / off / unknown. Token-aware rather than a
 * loose substring scan: an "@QPW ER" error reply, or anything that does not end in a known
 * power value, parses to "unknown" (so a failed/error reply is never read as a power state).
 */
export function parseOppoPowerReply(raw: string): "on" | "off" | "unknown" {
  const tokens = raw.trim().toUpperCase().split(/\s+/);
  if (tokens.includes("ER")) return "unknown";
  const value = tokens[tokens.length - 1] ?? "";
  if (value === "ON") return "on";
  if (value === "OFF") return "off";
  return "unknown";
}

/**
 * Parse an OPPO #QVM reply ("@QVM OK 2") into the current verbose mode "0".."3", or null when
 * the reply is an error or unparseable. Used to restore the player's mode after an SVM3
 * capability probe (so the probe leaves verbose mode exactly as it found it).
 */
export function parseOppoVerboseMode(raw: string): "0" | "1" | "2" | "3" | null {
  const tokens = raw.trim().toUpperCase().split(/\s+/);
  if (tokens.includes("ER")) return null;
  for (let i = tokens.length - 1; i >= 0; i--) {
    const t = tokens[i];
    if (t === "0" || t === "1" || t === "2" || t === "3") return t;
  }
  return null;
}

/**
 * Whether an OPPO #SVM 3 reply indicates the command was accepted ("@SVM OK 3" / "OK 3"). An
 * error ("@SVM ER") or empty/garbage reply is treated as not accepted, so the configurator
 * never claims SVM3 support the player did not actually confirm.
 */
export function parseSvm3Accepted(raw: string): boolean {
  const tokens = raw.trim().toUpperCase().split(/\s+/);
  if (tokens.includes("ER")) return false;
  return tokens.includes("OK");
}
