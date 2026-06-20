// @vitest-environment happy-dom
import { describe, expect, it } from "vitest";
import {
  ADDON_DATA_SETTINGS_REL,
  mergeSettingsXml,
  parseSettingsXml,
  serializeSettingsXml,
} from "./settings_xml";

describe("serializeSettingsXml", () => {
  it("emits Kodi v2 settings with sorted ids", () => {
    const xml = serializeSettingsXml({ tv_backend: "adb", oppo_ip: "10.0.1.77" });
    expect(xml).toContain('<settings version="2">');
    expect(xml).toContain('<setting id="oppo_ip">10.0.1.77</setting>');
    expect(xml).toContain('<setting id="tv_backend">adb</setting>');
    expect(xml.indexOf('id="oppo_ip"')).toBeLessThan(xml.indexOf('id="tv_backend"'));
  });

  it("escapes XML metacharacters in values", () => {
    const xml = serializeSettingsXml({ cmd: 'a & b < c > "d"' });
    expect(xml).toContain("a &amp; b &lt; c &gt; &quot;d&quot;");
  });

  it("exposes the addon_data settings path", () => {
    expect(ADDON_DATA_SETTINGS_REL).toBe("addon_data/script.oppo203.iso.external/settings.xml");
  });

  it("writes the configurator provenance marker (ENH-#41 Part C)", () => {
    const xml = serializeSettingsXml({ oppo_ip: "10.0.1.77" });
    expect(xml).toContain("Managed by the OppoKodiAddon Configurator");
  });
});

describe("mergeSettingsXml", () => {
  it("returns a fresh file when none exists", () => {
    const xml = mergeSettingsXml(null, { oppo_ip: "10.0.1.77" });
    expect(xml).toContain('<setting id="oppo_ip">10.0.1.77</setting>');
  });

  it("preserves settings we do not own and lets our values win", () => {
    const existing =
      '<settings version="2">' +
      '<setting id="addon_language">de_DE</setting>' +
      '<setting id="oppo_ip">1.1.1.1</setting>' +
      "</settings>";
    const xml = mergeSettingsXml(existing, { oppo_ip: "10.0.1.77", tv_backend: "adb" });
    expect(xml).toContain('<setting id="addon_language">de_DE</setting>'); // preserved
    expect(xml).toContain('<setting id="oppo_ip">10.0.1.77</setting>'); // ours wins
    expect(xml).toContain('<setting id="tv_backend">adb</setting>'); // ours added
  });

  it("refuses (throws) for a malformed or non-settings file", () => {
    expect(() => mergeSettingsXml("<advancedsettings/>", { oppo_ip: "x" })).toThrow(
      /refusing to overwrite/,
    );
  });
});

describe("parseSettingsXml", () => {
  it("parses a settings document into an id->value map", () => {
    const obj = parseSettingsXml(
      '<settings version="2"><setting id="oppo_ip">10.0.1.77</setting>' +
        '<setting id="tv_backend">adb</setting></settings>',
    );
    expect(obj).toEqual({ oppo_ip: "10.0.1.77", tv_backend: "adb" });
  });

  it("returns {} for empty or whitespace input (no settings written yet)", () => {
    expect(parseSettingsXml(null)).toEqual({});
    expect(parseSettingsXml("")).toEqual({});
    expect(parseSettingsXml("   ")).toEqual({});
  });

  it("round-trips with serializeSettingsXml", () => {
    const settings = { oppo_ip: "10.0.1.77", tv_backend: "adb" };
    expect(parseSettingsXml(serializeSettingsXml(settings))).toEqual(settings);
  });

  it("refuses (throws) for a malformed or non-settings document", () => {
    expect(() => parseSettingsXml("<advancedsettings/>")).toThrow(/refusing to read/);
  });
});
