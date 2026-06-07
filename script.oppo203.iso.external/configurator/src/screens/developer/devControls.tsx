import { useState } from "react";
import { invoke } from "../../ipc";

// Small shared form controls for the Developer Options device consoles (AVR / NAS).

export function Field({
  id,
  label,
  value,
  setValue,
  width,
  secret,
  placeholder,
}: {
  id: string;
  label: string;
  value: string;
  setValue: (v: string) => void;
  width?: number;
  secret?: boolean;
  placeholder?: string;
}) {
  return (
    <div className="field" style={{ maxWidth: width }}>
      <label className="field-label" htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        className="input"
        type={secret ? "password" : "text"}
        value={value}
        placeholder={placeholder}
        spellCheck={false}
        onChange={(e) => setValue(e.target.value)}
      />
    </div>
  );
}

export function RawRow({
  id,
  label,
  placeholder,
  value,
  setValue,
  onSend,
}: {
  id: string;
  label: string;
  placeholder: string;
  value: string;
  setValue: (v: string) => void;
  onSend: () => void;
}) {
  return (
    <div className="field">
      <label className="field-label" htmlFor={id}>
        {label}
      </label>
      <div className="row">
        <input
          id={id}
          className="input mono"
          placeholder={placeholder}
          value={value}
          spellCheck={false}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") onSend();
          }}
        />
        <button className="btn" disabled={!value.trim()} onClick={onSend}>
          Send
        </button>
      </div>
    </div>
  );
}

type PingPhase = "idle" | "running" | "ok" | "fail";

/**
 * A reachability ping for a device console: enter the IP, probe its control port, show the real
 * result + measured latency (✓ reachable · N ms / ✗ no response). `port` is null for backends with
 * no plain TCP control port (e.g. SmartThings / LG), and the row says so honestly.
 */
export function PingRow({ label, host, port }: { label: string; host: string; port: number | null }) {
  const [phase, setPhase] = useState<PingPhase>("idle");
  const [text, setText] = useState("");
  async function ping() {
    const h = host.trim();
    if (!h) {
      setPhase("fail");
      setText("Enter an IP first.");
      return;
    }
    if (port == null) {
      setPhase("fail");
      setText("No plain TCP control port for this backend.");
      return;
    }
    setPhase("running");
    setText("");
    try {
      const r = await invoke<{ reachable: boolean; ms: number; port: number }>("ping_host", {
        host: h,
        port,
      });
      if (r.reachable) {
        setPhase("ok");
        setText(`reachable at ${h}:${r.port} · ${r.ms} ms`);
      } else {
        setPhase("fail");
        setText(`no response from ${h}:${r.port} (timeout / refused)`);
      }
    } catch (e) {
      setPhase("fail");
      setText(String(e));
    }
  }
  return (
    <div className="row" style={{ alignItems: "center", gap: 10, marginTop: 4 }}>
      <button className="btn outline" disabled={phase === "running"} onClick={() => void ping()}>
        {phase === "running" ? "Pinging…" : `Ping ${label}`}
      </button>
      {text && (
        <span
          className={phase === "ok" ? "success-text" : phase === "fail" ? "danger-text" : "field-hint"}
          style={{ margin: 0 }}
          role="status"
        >
          {phase === "ok" ? "✓ " : phase === "fail" ? "✗ " : ""}
          {text}
        </span>
      )}
    </div>
  );
}

export function BackendTabs<T extends string>({
  tabs,
  active,
  onPick,
  label = "Backend",
}: {
  tabs: readonly { id: T; label: string }[];
  active: T;
  onPick: (t: T) => void;
  label?: string;
}) {
  return (
    <div className="dev-tabs" role="tablist" aria-label={label} style={{ marginTop: 16 }}>
      {tabs.map((t) => (
        <button
          key={t.id}
          role="tab"
          aria-selected={active === t.id}
          className={`dev-tab${active === t.id ? " active" : ""}`}
          onClick={() => onPick(t.id)}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
