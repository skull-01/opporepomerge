import { describe, expect, it } from "vitest";
import { ADDON_DATA_SETTINGS_REL, serializeSettingsXml } from "./settings_xml";

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
});
