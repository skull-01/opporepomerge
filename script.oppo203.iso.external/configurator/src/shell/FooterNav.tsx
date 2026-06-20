import { Icon } from "../icons";
import type { WizardState } from "../state";
import type { ScreenId } from "../steps";

type Props = {
  go: (id: ScreenId) => void;
  back?: ScreenId | null;
  next?: ScreenId | null;
  nextLabel?: string;
  set?: (patch: Partial<WizardState>) => void;
  setKeys?: Partial<WizardState>;
};

export function FooterNav({ go, back, next, nextLabel = "Continue", set, setKeys }: Props) {
  return (
    <div className="footer-nav">
      <div className="row" style={{ gap: 10 }}>
        {back && (
          <button className="btn ghost" onClick={() => go(back)}>
            <Icon name="chevL" size={14} /> Back
          </button>
        )}
        <span className="spacer" />
        {next && (
          <button
            className="btn primary"
            onClick={() => {
              if (set && setKeys) set(setKeys);
              go(next);
            }}
          >
            {nextLabel} <Icon name="chevR" size={14} />
          </button>
        )}
      </div>
    </div>
  );
}
