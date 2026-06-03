import { OPPO_HTTP_COMMANDS } from "../../oppo-commands/http-commands";

// Pure helpers for the OPPO console transcript. Kept out of the React component so the
// credential-redaction rule (share logins / tokens must never reach the on-screen log) is unit
// tested rather than asserted by eye.

export type TranscriptDir = "tx" | "rx" | "info" | "err";
export type TranscriptLine = { id: number; dir: TranscriptDir; text: string };

/** True if an OPPO HTTP endpoint is credential-bearing (its query must be redacted + never kept). */
export function isSensitiveEndpoint(endpoint: string): boolean {
  return OPPO_HTTP_COMMANDS.some((c) => c.endpoint === endpoint && c.sensitive === true);
}

/**
 * The GET line shown in the transcript for an HTTP command. For sensitive endpoints the query is
 * replaced with `[redacted]` so a share login/token never reaches the on-screen log.
 */
export function httpRequestLabel(endpoint: string, query: string): string {
  if (!query) return `GET ${endpoint}`;
  return `GET ${endpoint}?${isSensitiveEndpoint(endpoint) ? "[redacted]" : query}`;
}

/** Append lines to the transcript, capping total length so a long session can't grow unbounded. */
export function appendTranscript(
  lines: TranscriptLine[],
  add: TranscriptLine[],
  cap = 300
): TranscriptLine[] {
  const next = [...lines, ...add];
  return next.length > cap ? next.slice(next.length - cap) : next;
}
