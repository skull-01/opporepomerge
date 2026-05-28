import type { CSSProperties } from "react";

export type IconName =
  | "media"
  | "kodi"
  | "tv"
  | "player"
  | "avr"
  | "hdmi"
  | "play"
  | "check"
  | "cross"
  | "chevR"
  | "chevL"
  | "chevD"
  | "refresh"
  | "search"
  | "info"
  | "warn"
  | "spark"
  | "folder"
  | "file"
  | "terminal"
  | "network"
  | "download"
  | "plug"
  | "remote"
  | "arrows"
  | "bolt"
  | "power"
  | "close"
  | "min"
  | "max";

type Props = {
  name: IconName;
  size?: number;
  stroke?: number;
  style?: CSSProperties;
};

export function Icon({ name, size = 16, stroke = 1.8, style }: Props) {
  const p = {
    fill: "none",
    stroke: "currentColor",
    strokeWidth: stroke,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  const paths: Record<IconName, JSX.Element> = {
    media: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2" {...p} />
        <path d="M3 9h18M7 13h3M7 16h7" {...p} />
      </>
    ),
    kodi: (
      <>
        <rect x="3" y="4" width="18" height="13" rx="2" {...p} />
        <path d="M3 17l3 3h12l3-3M9 8l5 3-5 3z" {...p} />
      </>
    ),
    tv: (
      <>
        <rect x="3" y="5" width="18" height="13" rx="2" {...p} />
        <path d="M8 21h8M12 18v3" {...p} />
      </>
    ),
    player: (
      <>
        <rect x="2" y="8" width="20" height="9" rx="1.5" {...p} />
        <circle cx="17.5" cy="12.5" r="2" {...p} />
        <path d="M6 12h7M6 14h5" {...p} />
      </>
    ),
    avr: (
      <>
        <rect x="2" y="6" width="20" height="12" rx="1.5" {...p} />
        <circle cx="7" cy="12" r="2" {...p} />
        <circle cx="13" cy="12" r="2" {...p} />
        <path d="M18 10v4" {...p} />
      </>
    ),
    hdmi: (
      <>
        <path d="M8 4h8l2 3v10l-2 3H8l-2-3V7z M9 8h6M9 11h6" {...p} />
      </>
    ),
    play: <path d="M8 5l11 7-11 7z" {...p} />,
    check: <path d="M5 12.5l4.5 4.5L19 6" {...p} />,
    cross: <path d="M6 6l12 12M18 6L6 18" {...p} />,
    chevR: <path d="M9 6l6 6-6 6" {...p} />,
    chevL: <path d="M15 6l-6 6 6 6" {...p} />,
    chevD: <path d="M6 9l6 6 6-6" {...p} />,
    refresh: (
      <path
        d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5"
        {...p}
      />
    ),
    search: (
      <>
        <circle cx="11" cy="11" r="6" {...p} />
        <path d="M20 20l-4-4" {...p} />
      </>
    ),
    info: (
      <>
        <circle cx="12" cy="12" r="9" {...p} />
        <path d="M12 11v6M12 7.5v.1" {...p} />
      </>
    ),
    warn: <path d="M12 3l10 17H2z M12 10v5M12 18v.1" {...p} />,
    spark: (
      <path
        d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"
        {...p}
      />
    ),
    folder: (
      <path
        d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
        {...p}
      />
    ),
    file: <path d="M7 3h8l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z M14 3v5h5" {...p} />,
    terminal: (
      <>
        <rect x="3" y="4" width="18" height="16" rx="2" {...p} />
        <path d="M7 9l3 3-3 3M13 15h4" {...p} />
      </>
    ),
    network: (
      <>
        <circle cx="12" cy="12" r="9" {...p} />
        <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" {...p} />
      </>
    ),
    download: <path d="M12 4v12M6 11l6 6 6-6M4 20h16" {...p} />,
    plug: <path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0z M12 18v4" {...p} />,
    remote: (
      <>
        <rect x="7" y="2" width="10" height="20" rx="3" {...p} />
        <circle cx="12" cy="7" r="1.2" {...p} />
        <path d="M9.5 12h5M9.5 15h5M9.5 18h5" {...p} />
      </>
    ),
    arrows: <path d="M4 12h16M4 12l4-4M4 12l4 4M20 12l-4-4M20 12l-4 4" {...p} />,
    bolt: <path d="M13 2L4 14h7l-1 8 9-12h-7z" {...p} />,
    power: <path d="M12 3v9M5.6 7.6a9 9 0 1 0 12.8 0" {...p} />,
    close: <path d="M6 6l12 12M18 6L6 18" {...p} />,
    min: <path d="M6 12h12" {...p} />,
    max: <rect x="5" y="5" width="14" height="14" rx="0" {...p} />,
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      style={{ display: "inline-block", flexShrink: 0, ...style }}
    >
      {paths[name]}
    </svg>
  );
}
