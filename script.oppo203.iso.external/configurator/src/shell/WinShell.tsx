import type { ReactNode } from "react";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { Icon } from "../icons";
import { t } from "../i18n";

type Props = {
  title?: string;
  children: ReactNode;
};

export function WinShell({ title = t("app.title"), children }: Props) {
  return (
    <div className="win">
      <div className="titlebar" data-tauri-drag-region="">
        <div className="titlebar-title">
          <span className="titlebar-title-icon">O</span>
          <span>{title}</span>
        </div>
        <div className="titlebar-spacer" />
        <div className="titlebar-btns">
          <button
            className="titlebar-btn"
            tabIndex={-1}
            aria-label={t("window.minimize")}
            onClick={() => {
              void getCurrentWindow().minimize();
            }}
          >
            <Icon name="min" size={10} stroke={1.5} />
          </button>
          <button
            className="titlebar-btn"
            tabIndex={-1}
            aria-label={t("window.maximize")}
            onClick={() => {
              void getCurrentWindow().toggleMaximize();
            }}
          >
            <Icon name="max" size={10} stroke={1.5} />
          </button>
          <button
            className="titlebar-btn close"
            tabIndex={-1}
            aria-label={t("window.close")}
            onClick={() => {
              void getCurrentWindow().close();
            }}
          >
            <Icon name="close" size={10} stroke={1.5} />
          </button>
        </div>
      </div>
      <div className="win-body">{children}</div>
    </div>
  );
}
