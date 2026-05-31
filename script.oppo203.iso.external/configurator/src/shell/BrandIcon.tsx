import { useState } from "react";
import { Icon, type IconName } from "../icons";
import {
  siSony,
  siSamsung,
  siLg,
  siRoku,
  siPanasonic,
  siOppo,
  type SimpleIcon,
} from "simple-icons";

// Real brand marks for the brands Simple Icons carries (CC0 SVGs; trademarks remain with their
// owners — used here only to identify the user's actual device, not to imply endorsement).
// Any brand not in this map (clones, niche AV brands, "Other") falls back to a colored monogram.
const BRAND_ICONS: Record<string, SimpleIcon> = {
  sony: siSony,
  samsung: siSamsung,
  lg: siLg,
  roku: siRoku,
  panasonic: siPanasonic,
  oppo: siOppo,
};

// Some brand marks are near-white (Sony's is #FFFFFF) and vanish on the white chip the
// colored marks need. Detect a light mark by perceived luminance so it gets a dark chip.
function markIsLight(hex: string): boolean {
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  return 0.299 * r + 0.587 * g + 0.114 * b > 200;
}

type Props = {
  /** Brand id; when it matches a Simple Icons slug the real logo is shown. */
  slug: string;
  /** Monogram text for the fallback badge. */
  ch: string;
  /** Brand color for the fallback badge background. */
  color: string;
  /** Generic device glyph shown when the brand has no real logo (e.g. clones). */
  fallbackIcon?: IconName;
};

export function BrandIcon({ slug, ch, color, fallbackIcon }: Props) {
  const icon = BRAND_ICONS[slug];
  // If the bundled icon ever fails to render, drop to the fallback rather than show nothing.
  const [broke, setBroke] = useState(false);

  if (!icon || broke) {
    // No real brand mark: prefer a generic device glyph, else the colored monogram.
    if (fallbackIcon) {
      return (
        <div className="brand-logo" style={{ background: color }}>
          <Icon name={fallbackIcon} size={18} />
        </div>
      );
    }
    const fontSize = ch.length > 2 ? 10 : ch.length > 1 ? 11 : 14;
    return (
      <div className="brand-logo" style={{ background: color, fontSize }}>
        {ch}
      </div>
    );
  }

  return (
    <div className={`brand-logo brand-logo-mark${markIsLight(icon.hex) ? " brand-logo-mark-dark" : ""}`}>
      <svg
        role="img"
        aria-label={icon.title}
        viewBox="0 0 24 24"
        width="20"
        height="20"
        fill={`#${icon.hex}`}
        onError={() => setBroke(true)}
      >
        <path d={icon.path} />
      </svg>
    </div>
  );
}
