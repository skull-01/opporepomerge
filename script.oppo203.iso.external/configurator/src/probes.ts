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

/** Parse an OPPO #QPW reply ("@QPW OK ON") into on / off / unknown. */
export function parseOppoPowerReply(raw: string): "on" | "off" | "unknown" {
  const upper = raw.toUpperCase();
  if (upper.includes("OFF")) return "off";
  if (upper.includes("ON")) return "on";
  return "unknown";
}
