import { Fragment } from "react";
import { STEPS, type StepId } from "../steps";

type Props = {
  variant: "stepper" | "minimal";
  current: StepId;
  onJump: (id: StepId) => void;
};

export function Progress({ variant, current, onJump }: Props) {
  const currentIdx = STEPS.findIndex((s) => s.id === current);

  if (variant === "stepper") {
    return (
      <div className="stepper">
        {STEPS.map((s, i) => {
          const done = i < currentIdx;
          const active = i === currentIdx;
          return (
            <Fragment key={s.id}>
              <button
                className={`stepper-item ${done ? "done" : ""} ${active ? "active" : ""}`.trim()}
                onClick={() => onJump(s.id)}
                style={{ background: "none", border: "none", padding: 0, cursor: "pointer" }}
              >
                <span className={`stepper-dot ${done ? "done" : ""} ${active ? "active" : ""}`.trim()}>
                  <span className="num">{s.num}</span>
                </span>
                <span className="stepper-label">{s.label}</span>
              </button>
              {i < STEPS.length - 1 && <span className={`stepper-sep ${done ? "done" : ""}`.trim()} />}
            </Fragment>
          );
        })}
      </div>
    );
  }

  const pct = ((currentIdx + 1) / STEPS.length) * 100;
  return (
    <div className="minimal-progress">
      <strong>{STEPS[currentIdx]?.label ?? "—"}</strong>
      <span>
        · Step {currentIdx + 1} of {STEPS.length}
      </span>
      <div className="bar">
        <div className="bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
