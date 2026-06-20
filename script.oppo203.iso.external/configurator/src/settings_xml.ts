import type { AddonSettings } from "./mapping";
import { xmlEscape } from "./xml";

/** Path of the add-on's runtime settings file relative to Kodi userdata/. */
export const ADDON_DATA_SETTINGS_REL = "addon_data/script.oppo203.iso.external/settings.xml";

/**
 * Provenance marker written into the generated settings.xml (ENH-#41 Part C, configurator
 * side). Pairs with the add-on's "managed by the configurator" overwrite warning. Static (no
 * timestamp) so the output stays deterministic and the merge stays idempotent.
 */
const PROVENANCE_COMMENT =
  "<!-- Managed by the OppoKodiAddon Configurator. Changes made directly in Kodi may be " +
  "overwritten the next time the configurator runs. -->";

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
    PROVENANCE_COMMENT +
    "\n" +
    '<settings version="2">\n' +
    lines.join("\n") +
    "\n</settings>\n"
  );
}

/**
 * Parse a Kodi settings.xml document into a flat id->value map. REFUSES (throws) on a malformed
 * document or a non-<settings> root rather than returning a misleading partial object - the same
 * guard mergeSettingsXml uses before it will overwrite a file. Returns {} for empty/whitespace
 * input (no settings written yet), which callers read as "no prior values".
 */
export function parseSettingsXml(xml: string | null): AddonSettings {
  if (!xml || xml.trim() === "") return {};
  return readSettingsDoc(xml, "read it");
}

/**
 * Merge our settings into an existing Kodi settings.xml, PRESERVING any settings the
 * configurator does not own, so applying never silently resets the user's other add-on
 * settings. Our values win for the ids we manage. Returns a fresh file when none exists, and
 * REFUSES (throws) when an existing file is malformed or not a <settings> document rather than
 * clobbering it.
 */
export function mergeSettingsXml(existing: string | null, ours: AddonSettings): string {
  if (!existing || existing.trim() === "") {
    return serializeSettingsXml(ours);
  }
  const merged = readSettingsDoc(existing, "overwrite");
  Object.assign(merged, ours);
  return serializeSettingsXml(merged);
}

/**
 * Shared DOM parse + <settings> validation + id->value extraction. `refusalVerb` tailors the
 * error to the caller ("overwrite" for the merge writer, "read it" for the snapshot reader) so
 * each surfaces an accurate refusal instead of clobbering or trusting a bad file.
 */
function readSettingsDoc(xml: string, refusalVerb: string): AddonSettings {
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  const root = doc.documentElement;
  const malformed = doc.getElementsByTagName("parsererror").length > 0;
  if (malformed || !root || root.nodeName !== "settings") {
    throw new Error(
      `settings.xml is malformed or not a <settings> document; refusing to ${refusalVerb}. ` +
        "Fix or move the file first.",
    );
  }
  const out: AddonSettings = {};
  for (const el of Array.from(root.getElementsByTagName("setting"))) {
    const id = el.getAttribute("id");
    if (id) out[id] = el.textContent ?? "";
  }
  return out;
}
