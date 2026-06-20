import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import { recordWire } from "./log";

/** Payload of a Rust `debug-wire` event (see src-tauri/src/lib.rs `WireEvent`). */
type WirePayload = {
  direction: "sent" | "recv";
  label: string;
  host: string;
  port: number;
  hex: string;
  text: string;
  len: number;
};

/**
 * Subscribe to raw wire-transcript events emitted by the Rust commands — currently only the OPPO
 * IP-control path (`oppo_query`) — and record them in the debug log so the developer panel can
 * show the actual bytes sent/received. Returns the Tauri unlisten fn.
 *
 * Only the no-secret OPPO control bytes are emitted Rust-side; secret-bearing payloads (the
 * generated settings.xml passed to deploy/SSH commands) are deliberately never sent, since the
 * panel's key-based redactor cannot sanitize a raw byte stream.
 */
export function startWireListener(): Promise<UnlistenFn> {
  return listen<WirePayload>("debug-wire", (event) => {
    const p = event.payload;
    recordWire({
      ts: Date.now(),
      direction: p.direction,
      label: p.label,
      host: p.host,
      port: p.port,
      hex: p.hex,
      text: p.text,
      len: p.len,
    });
  });
}
