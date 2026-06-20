import { STEPS, type StepId } from "../steps";

type Props = {
  current: StepId;
  onJump: (id: StepId) => void;
};

export function Sidebar({ current, onJump }: Props) {
  const currentIdx = STEPS.findIndex((s) => s.id === current);
  return (
    <div className="sidebar">
      <div className="sidebar-title">Setup steps</div>
      {STEPS.map((s, i) => {
        const done = i < currentIdx;
        const active = i === currentIdx;
        return (
          <button
            key={s.id}
            className={`sidebar-step ${done ? "done" : ""} ${active ? "active" : ""}`.trim()}
            onClick={() => onJump(s.id)}
            style={{ background: "none", border: "none", width: "100%", textAlign: "left", fontFamily: "inherit" }}
          >
            <span className="sidebar-step-dot">{done ? "✓" : s.num}</span>
            <span>{s.label}</span>
          </button>
        );
      })}
    </div>
  );
}
