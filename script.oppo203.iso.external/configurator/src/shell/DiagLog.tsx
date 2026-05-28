import type { ReactNode } from "react";

export type DiagStatus = "pass" | "fail" | "warn" | "run" | "pending";

export type DiagCheck = {
  status: DiagStatus;
  label: string;
  detail?: string;
};

type Props = {
  title: string;
  checks: DiagCheck[];
  footer?: ReactNode;
  footerKind?: "success" | "fail" | "";
  output?: string;
};

export function DiagLog({ title, checks, footer, footerKind, output }: Props) {
  const anyRunning = checks.some((c) => c.status === "run");
  const allPass = checks.every((c) => c.status === "pass");
  const anyFail = checks.some((c) => c.status === "fail");
  const headerDotClass = anyFail ? "fail" : anyRunning || !allPass ? "running" : "";
  const headerText = anyFail
    ? "Failed"
    : anyRunning
      ? "Running…"
      : allPass
        ? "All checks passed"
        : "Idle";

  return (
    <div className="diag">
      <div className="diag-header">
        <span className={`diag-header-dot ${headerDotClass}`.trim()} />
        <strong style={{ color: "var(--text)", fontWeight: 600 }}>{title}</strong>
        <span className="spacer" />
        <span>{headerText}</span>
      </div>
      <div className="diag-list">
        {checks.map((c, i) => (
          <div key={i} className={`diag-row ${c.status === "pending" ? "diag-pending" : ""}`.trim()}>
            <span className={`diag-icon ${c.status}`}>
              {c.status === "pass"
                ? "✓"
                : c.status === "fail"
                  ? "✕"
                  : c.status === "warn"
                    ? "!"
                    : c.status === "pending"
                      ? "·"
                      : ""}
            </span>
            <span className="diag-label">{c.label}</span>
            <span className="diag-detail">{c.detail}</span>
          </div>
        ))}
      </div>
      {output && <pre className="diag-output">{output}</pre>}
      {footer && <div className={`diag-footer ${footerKind ?? ""}`.trim()}>{footer}</div>}
    </div>
  );
}
