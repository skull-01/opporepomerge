import type { StepId } from "../steps";

type BaseEntry = {
  seq: number;
  ts: number;
  step: StepId | null;
};

/** One captured IPC round-trip (the `invoke` wrapper), shown in the debug view (Ctrl+Shift+D). */
export type IpcEntry = BaseEntry & {
  kind: "ipc";
  command: string;
  args: unknown;
  durationMs: number;
  ok: boolean;
  result?: unknown;
  error?: string;
};

/**
 * One raw frame on a command's underlying wire (currently the OPPO IP-control TCP path),
 * pushed from Rust as a `debug-wire` event. Only the no-secret OPPO path emits these.
 */
export type WireEntry = BaseEntry & {
  kind: "wire";
  direction: "sent" | "recv";
  label: string;
  host: string;
  port: number;
  hex: string;
  text: string;
  len: number;
};

export type DebugEntry = IpcEntry | WireEntry;

const MAX_ENTRIES = 500;
const MAX_STRING = 2000;
// Keys whose values may carry secrets (Sony PSK, SmartThings tokens, passwords, NAS creds).
// Matched case-insensitively against the key NAME; the value is replaced wholesale so a secret
// never reaches the panel or a copy/paste of it.
const SENSITIVE_KEY = /psk|token|password|secret|credential/i;

/**
 * Whether a key or setting-id name may carry a secret (Sony PSK, SmartThings token, password,
 * NAS credential). The single home for that policy - shared by the debug redactor below and the
 * dashboard settings-snapshot diff, so a secret value never reaches the UI or the snapshot on disk.
 */
export function isSensitiveKey(name: string): boolean {
  return SENSITIVE_KEY.test(name);
}

let entries: DebugEntry[] = [];
let seq = 0;
let currentStep: StepId | null = null;
const listeners = new Set<() => void>();

/**
 * Deep-copy `value`, blanking secret-bearing fields and truncating long strings (generated
 * settings.xml / playercorefactory blobs passed to deploy_* commands). Never throws; bounded
 * by depth so an unexpected cycle cannot run away.
 */
export function redact(value: unknown, keyHint = "", depth = 0): unknown {
  if (isSensitiveKey(keyHint)) return "[redacted]";
  if (depth > 8) return "[…]";
  if (typeof value === "string") {
    return value.length > MAX_STRING
      ? `${value.slice(0, MAX_STRING)}…[+${value.length - MAX_STRING} chars]`
      : value;
  }
  if (Array.isArray(value)) return value.map((v) => redact(v, "", depth + 1));
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = redact(v, k, depth + 1);
    }
    return out;
  }
  return value;
}

function emit(): void {
  for (const fn of listeners) fn();
}

/** Tag subsequent entries with the wizard step the user is on (App sets this on navigation). */
export function setCurrentStep(step: StepId | null): void {
  currentStep = step;
}

/** Append a captured IPC call: assigns the sequence number, stamps the current step, notifies. */
export function record(e: Omit<IpcEntry, "seq" | "step" | "kind">): void {
  const entry: IpcEntry = { ...e, kind: "ipc", seq, step: currentStep };
  seq += 1;
  entries = [...entries, entry].slice(-MAX_ENTRIES);
  emit();
}

/** Append a raw wire frame (from a `debug-wire` event): same seq/step/ring-buffer as record(). */
export function recordWire(e: Omit<WireEntry, "seq" | "step" | "kind">): void {
  const entry: WireEntry = { ...e, kind: "wire", seq, step: currentStep };
  seq += 1;
  entries = [...entries, entry].slice(-MAX_ENTRIES);
  emit();
}

export function getEntries(): readonly DebugEntry[] {
  return entries;
}

export function clearEntries(): void {
  entries = [];
  emit();
}

/** Subscribe to log changes (drives useSyncExternalStore). Returns an unsubscribe fn. */
export function subscribe(fn: () => void): () => void {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

/** The panel's filter: the active step only, or everything. Order is preserved (newest last). */
export function entriesForView(
  all: readonly DebugEntry[],
  step: StepId | null,
  showAll: boolean,
): DebugEntry[] {
  if (showAll || step == null) return [...all];
  return all.filter((e) => e.step === step);
}

/** Test seam: reset module state so cases do not bleed into each other. */
export function __resetForTest(): void {
  entries = [];
  seq = 0;
  currentStep = null;
  listeners.clear();
}
