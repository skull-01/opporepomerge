import { invoke as tauriInvoke } from "@tauri-apps/api/core";
import { record, redact } from "./debug/log";

/**
 * Drop-in wrapper for @tauri-apps/api/core's `invoke` that records every call — command,
 * redacted args, timing, and the result or error — into the debug log for the developer debug
 * view. It is a pure pass-through: identical arguments in, identical value out, the same error
 * rethrown. All wizard call sites import `invoke` from here instead of from the Tauri package,
 * so the panel sees every command without each screen knowing about it.
 */
export async function invoke<T>(command: string, args?: Record<string, unknown>): Promise<T> {
  const ts = Date.now();
  const start = performance.now();
  try {
    const result = await tauriInvoke<T>(command, args);
    record({
      ts,
      command,
      args: redact(args),
      durationMs: performance.now() - start,
      ok: true,
      result: redact(result),
    });
    return result;
  } catch (err) {
    record({
      ts,
      command,
      args: redact(args),
      durationMs: performance.now() - start,
      ok: false,
      error: String(err),
    });
    throw err;
  }
}
