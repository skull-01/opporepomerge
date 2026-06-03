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
