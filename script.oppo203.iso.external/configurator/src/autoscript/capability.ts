// Configurator mirror of the add-on's AutoScript firmware-capability gating
// (resources/lib/kodi/settings_reader.py). The add-on is the source of truth; the thresholds + the
// supported/blocked decisions are pinned both sides (autoscript.test.ts / test_autoscript_consistency.py).

export const OPPO20X_AUTOSCRIPT_MIN_FIRMWARE = "20X-56";
export const OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE = "20X-65-0131";
export const OPPO20X_AUTOSCRIPT_UNSUPPORTED_NOTE =
  "20X-54-1127 and older/pre-56 firmware are not supported for AutoScript-based NAS playback.";

export const AUTOSCRIPT_VERBOSE_PUSH_WARNING =
  "AutoScript shell handlers that replace the OPPO port-23 protocol can break #SVM 2 verbose-push " +
  "status parsing. Keep the stock TCP/IP control surface available or disable verbose-push hold mode.";

/** Clone models that run AutoScript without a jailbreak (mirror of CHINOPPO_NAS_PLAYBACK_MODELS). */
export const CHINOPPO_NAS_PLAYBACK_MODELS: readonly string[] = [
  "M9200", "M9201", "M9203", "M9205", "M9205-V1", "M9205C", "M9702",
  "CineUltra-V203", "CineUltra-V204", "IPUK-UHD8592", "GIEC-BDP-G5300",
  "M9205-V2", "M9205-V3", "M9205-V4", "M9702-Plus", "VenPro-V203",
];

/** Mirror of `_firmware_major_build`: the numeric 20X build component (65 for 20X-65-0131). */
export function firmwareMajorBuild(firmware: string | null | undefined): number | null {
  if (firmware == null) return null;
  let text = String(firmware).trim().toUpperCase().replace(/_/g, "-");
  if (!text) return null;
  if (text.startsWith("20X-")) text = text.slice(4);
  const head = text.split("-")[0]?.trim() ?? "";
  // Python int() is strict — reject any non-integer head (parseInt would be too lenient).
  if (!/^[+-]?\d+$/.test(head)) return null;
  const n = Number(head);
  return Number.isFinite(n) ? n : null;
}

export type FirmwareStatus = {
  firmware: string;
  minimum: string;
  recommended: string;
  autoscriptSupported: boolean | null;
  warnings: string[];
  blockers: string[];
};

/** Mirror of `oppo20x_autoscript_firmware_status`: build >= 56 supported, >= 65 recommended. */
export function oppo20xAutoscriptFirmwareStatus(firmware: string | null | undefined): FirmwareStatus {
  const build = firmwareMajorBuild(firmware);
  const result: FirmwareStatus = {
    firmware: firmware == null ? "" : String(firmware).trim(),
    minimum: OPPO20X_AUTOSCRIPT_MIN_FIRMWARE,
    recommended: OPPO20X_AUTOSCRIPT_RECOMMENDED_FIRMWARE,
    autoscriptSupported: null,
    warnings: [],
    blockers: [],
  };
  if (build === null) {
    result.warnings.push("oppo20x_firmware_unknown");
    return result;
  }
  if (build < 56) {
    result.autoscriptSupported = false;
    result.blockers.push("oppo20x_firmware_below_20x_56");
    result.warnings.push(OPPO20X_AUTOSCRIPT_UNSUPPORTED_NOTE);
    return result;
  }
  result.autoscriptSupported = true;
  if (build < 65) {
    result.warnings.push("oppo20x_autoscript_supported_but_20x_65_0131_recommended");
  }
  return result;
}

export type AutoScriptFamily = "oppo20x_jailbroken" | "chinoppo_family" | "unknown";

/** Coarse family classification for the readiness UI: clone model → clone family; else JB stock OPPO. */
export function autoscriptFamily(model: string | null | undefined): AutoScriptFamily {
  const m = String(model ?? "").trim();
  if (!m) return "unknown";
  const upper = m.toUpperCase();
  if (CHINOPPO_NAS_PLAYBACK_MODELS.some((c) => c.toUpperCase() === upper)) return "chinoppo_family";
  if (/UDP-?20[35]/.test(upper)) return "oppo20x_jailbroken";
  return "unknown";
}

/**
 * Pull the firmware string from a #QVR reply ("OK UDP20X-65-0131" / "@QVR OK UDP20X-65-0131") into
 * the "20X-65-0131" form firmwareMajorBuild expects (drops the UDP prefix). "" if none found.
 */
export function parseQvrFirmware(reply: string | null | undefined): string {
  const m = /(?:UDP)?(20X-[A-Z0-9-]+)/.exec(String(reply ?? "").toUpperCase());
  return m ? m[1] : "";
}
