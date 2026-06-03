// Minimal i18n scaffold for the configurator. English is the single complete locale today; the
// structure (a keyed catalog + t()) lets call sites be locale-agnostic so additional locales can
// be added later without touching them. Migration is incremental -- components move their
// hardcoded strings to t("...") over time; until then nothing breaks.

/** The English message catalog. Keys are dotted by area (app.* / window.* / ...). */
export const en = {
  "app.title": "Kodi Oppo External Player Configurator",
  "app.versionLine": "{name}-v{version}",
  "window.minimize": "Minimize",
  "window.maximize": "Maximize",
  "window.close": "Close",
} as const;

export type MessageKey = keyof typeof en;
export type Locale = "en";

const CATALOGS: Record<Locale, Partial<Record<MessageKey, string>>> = { en };

let activeLocale: Locale = "en";

/** Switch the active locale. Only "en" ships today; this exists so call sites stay locale-agnostic. */
export function setLocale(locale: Locale): void {
  activeLocale = locale;
}

export function getLocale(): Locale {
  return activeLocale;
}

/**
 * Translate a message key for the active locale, interpolating `{name}` placeholders from `vars`.
 * Falls back to the English catalog, then to the key itself, so a missing translation degrades
 * visibly instead of throwing.
 */
export function t(key: MessageKey, vars?: Record<string, string | number>): string {
  let text: string = CATALOGS[activeLocale][key] ?? en[key] ?? key;
  if (vars) {
    for (const [name, value] of Object.entries(vars)) {
      text = text.split(`{${name}}`).join(String(value));
    }
  }
  return text;
}
