import type { AddonSettings } from "./mapping";

/** Path of the add-on's runtime settings file relative to Kodi userdata/. */
export const ADDON_DATA_SETTINGS_REL = "addon_data/script.oppo203.iso.external/settings.xml";

function xmlEscape(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/**
 * Serialize add-on settings into Kodi's runtime userdata/addon_data settings.xml (v2 format,
 * Kodi 19+). Ids are sorted for a stable, diff-friendly file. This is the file the
 * configurator writes over SFTP/SMB while Kodi is stopped (CONFIGURATOR_HANDOFF.md §7 Q2).
 */
export function serializeSettingsXml(settings: AddonSettings): string {
  const lines = Object.keys(settings)
    .sort()
    .map((id) => `    <setting id="${xmlEscape(id)}">${xmlEscape(settings[id])}</setting>`);
  return (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
    '<settings version="2">\n' +
    lines.join("\n") +
    "\n</settings>\n"
  );
}
